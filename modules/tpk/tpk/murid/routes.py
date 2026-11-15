from datetime import datetime

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required

from tpk.extensions import db
from tpk.models import JawabanTes, KELAS_CHOICES, Murid, SesiTesMurid, SoalTes
from tpk.utils import (
    daftar_kisi_kisi,
    get_bobot_penilaian,
    get_kunci_tes,
    get_tahun_ajaran,
    kunci_tes_session_key,
    normalisasi_gelombang,
    role_required,
    tampilkan_kisi_kisi,
)

murid_bp = Blueprint("murid", __name__)


def _get_murid():
    return Murid.query.filter_by(user_id=current_user.id).first_or_404()


def _paksa_jika_menunggu_keluar():
    """Jika sudah submit tapi belum password keluar, kunci di layar keluar."""
    kelas = session.get("tes_menunggu_keluar")
    if not kelas:
        return None
    endpoint = (request.endpoint or "")
    if endpoint in (
        "murid.tes_kelas",
        "murid.tes_keluar",
        "murid.tes_heartbeat",
        "murid.tes_autosave",
    ):
        return None
    return redirect(url_for("murid.tes_kelas", kelas=kelas))


def _gelombang_murid(murid: Murid) -> str:
    return normalisasi_gelombang(murid.gelombang) or "1"


def _tahun_murid(murid: Murid) -> str:
    return murid.tahun_ajaran or get_tahun_ajaran()


def _jenis_tes(murid: Murid) -> str:
    return "susulan" if murid.is_tes_susulan else "reguler"


def _sudah_masuk_tes(murid: Murid) -> bool:
    key = kunci_tes_session_key(
        _tahun_murid(murid), _gelombang_murid(murid), _jenis_tes(murid)
    )
    return bool(session.get(key))


def _set_masuk_tes(murid: Murid) -> None:
    key = kunci_tes_session_key(
        _tahun_murid(murid), _gelombang_murid(murid), _jenis_tes(murid)
    )
    session[key] = True
    session["tes_lock_mode"] = True


def _clear_masuk_tes(murid: Murid) -> None:
    key = kunci_tes_session_key(
        _tahun_murid(murid), _gelombang_murid(murid), _jenis_tes(murid)
    )
    session.pop(key, None)
    session.pop("tes_lock_mode", None)
    session.pop("tes_menunggu_keluar", None)


def _pastikan_sesi(murid: Murid, kelas: str) -> SesiTesMurid:
    sesi = SesiTesMurid.query.filter_by(
        murid_id=murid.id, kelas_tujuan=kelas
    ).first()
    ua = (request.headers.get("User-Agent") or "")[:250]
    if not sesi:
        sesi = SesiTesMurid(
            murid_id=murid.id,
            kelas_tujuan=kelas,
            status="aktif",
            user_agent=ua,
            last_seen_at=datetime.utcnow(),
        )
        db.session.add(sesi)
    else:
        sesi.last_seen_at = datetime.utcnow()
        if ua:
            sesi.user_agent = ua
    db.session.commit()
    return sesi


def _upsert_jawaban(murid: Murid, soals: list, form_get) -> int:
    """Simpan/update jawaban tanpa menghapus jawaban yang tidak dikirim."""
    terjawab = 0
    existing = {
        j.soal_id: j
        for j in JawabanTes.query.filter(
            JawabanTes.murid_id == murid.id,
            JawabanTes.soal_id.in_([s.id for s in soals]),
        ).all()
    }
    for soal in soals:
        jawab = (form_get(f"soal_{soal.id}") or "").upper()
        if jawab not in ("A", "B", "C", "D"):
            continue
        row = existing.get(soal.id)
        if row:
            row.jawaban = jawab
            row.is_benar = jawab == soal.jawaban_benar
            row.submitted_at = datetime.utcnow()
        else:
            db.session.add(
                JawabanTes(
                    murid_id=murid.id,
                    soal_id=soal.id,
                    jawaban=jawab,
                    is_benar=(jawab == soal.jawaban_benar),
                )
            )
        terjawab += 1
    return terjawab


def _jumlah_terjawab(murid: Murid, soals: list) -> int:
    ids = {s.id for s in soals}
    return sum(1 for j in murid.jawaban_tes if j.soal_id in ids)


@murid_bp.route("/")
@login_required
@role_required("murid")
def dashboard():
    blok = _paksa_jika_menunggu_keluar()
    if blok:
        return blok
    murid = _get_murid()
    bobot_tes, bobot_ww, bobot_psiko = get_bobot_penilaian()
    return render_template(
        "murid/dashboard.html",
        murid=murid,
        bobot_tes=bobot_tes,
        bobot_wawancara=bobot_ww,
        bobot_psikotes=bobot_psiko,
        kelas_choices=KELAS_CHOICES,
        nilai_tes=murid.nilai_tes_per_kelas(),
    )


@murid_bp.route("/profil", methods=["GET", "POST"])
@login_required
@role_required("murid")
def profil():
    blok = _paksa_jika_menunggu_keluar()
    if blok:
        return blok
    murid = _get_murid()
    if request.method == "POST":
        if murid.status == "ditetapkan":
            flash("Data tidak bisa diubah setelah kelas ditetapkan.", "warning")
            return redirect(url_for("murid.profil"))

        murid.tempat_lahir = request.form.get("tempat_lahir", "").strip() or None
        murid.jenis_kelamin = request.form.get("jenis_kelamin") or None
        murid.alamat = request.form.get("alamat", "").strip() or None
        murid.no_hp = request.form.get("no_hp", "").strip() or None
        murid.nama_ortu = request.form.get("nama_ortu", "").strip() or None
        murid.no_hp_ortu = request.form.get("no_hp_ortu", "").strip() or None
        murid.asal_sekolah = request.form.get("asal_sekolah", "").strip() or None
        pilihan1 = request.form.get("pilihan_kelas_1")
        pilihan2 = request.form.get("pilihan_kelas_2") or None
        if pilihan1 in dict(KELAS_CHOICES):
            murid.pilihan_kelas_1 = pilihan1
        if pilihan2 == pilihan1:
            flash("Pilihan kelas 2 tidak boleh sama dengan pilihan 1.", "danger")
        else:
            murid.pilihan_kelas_2 = pilihan2 if pilihan2 in dict(KELAS_CHOICES) else None
            current_user.nama_lengkap = (
                request.form.get("nama_lengkap", "").strip() or current_user.nama_lengkap
            )
            db.session.commit()
            flash("Profil diperbarui.", "success")
        return redirect(url_for("murid.profil"))

    return render_template("murid/profil.html", murid=murid, kelas_choices=KELAS_CHOICES)


@murid_bp.route("/tes", methods=["GET", "POST"])
@login_required
@role_required("murid")
def tes():
    """Daftar sesi tes + kunci password masuk."""
    blok = _paksa_jika_menunggu_keluar()
    if blok:
        return blok
    murid = _get_murid()
    if murid.status == "ditetapkan":
        flash("Kelas sudah ditetapkan. Tes tidak lagi tersedia.", "info")
        return redirect(url_for("murid.dashboard"))

    tahun = _tahun_murid(murid)
    gelombang = _gelombang_murid(murid)
    jenis = _jenis_tes(murid)
    kunci = get_kunci_tes(tahun, gelombang, jenis)
    sudah_masuk = _sudah_masuk_tes(murid)

    if request.method == "POST":
        aksi = request.form.get("aksi")
        if aksi == "masuk":
            if not kunci.is_aktif:
                if jenis == "susulan":
                    flash(
                        "Tes susulan belum dibuka admin. Tunggu jadwal susulan.",
                        "warning",
                    )
                else:
                    flash(
                        "Pengerjaan soal belum dibuka admin untuk gelombang ini.",
                        "warning",
                    )
            elif (request.form.get("password_masuk") or "").strip() == kunci.password_masuk:
                _set_masuk_tes(murid)
                flash("Password masuk benar. Silakan kerjakan soal.", "success")
                return redirect(url_for("murid.tes"))
            else:
                flash("Password masuk salah. Minta password dari pengawas/admin.", "danger")
            return redirect(url_for("murid.tes"))

    nilai_tes = murid.nilai_tes_per_kelas()
    sesi_map = murid._sesi_tes_map()
    sesi = []
    for kode, label in KELAS_CHOICES:
        jumlah_soal = SoalTes.query.filter_by(kelas_tujuan=kode, is_active=True).count()
        st = sesi_map.get(kode)
        terjawab = murid.jumlah_jawaban_kelas(kode)
        sesi.append(
            {
                "kode": kode,
                "label": label,
                "jumlah_soal": jumlah_soal,
                "nilai": nilai_tes.get(kode),
                "selesai": kode in nilai_tes,
                "terjawab": terjawab,
                "status_sesi": st.status if st else None,
                "butuh_keluar": bool(st and st.butuh_password_keluar),
            }
        )
    return render_template(
        "murid/tes.html",
        murid=murid,
        sesi=sesi,
        progress=murid.progress_tes_label,
        sudah_masuk=sudah_masuk,
        kunci_aktif=kunci.is_aktif,
        tahun=tahun,
        gelombang=gelombang,
        jenis_tes=jenis,
        menunggu_keluar=bool(session.get("tes_menunggu_keluar")),
    )


@murid_bp.route("/tes/<kelas>", methods=["GET", "POST"])
@login_required
@role_required("murid")
def tes_kelas(kelas):
    """Kerjakan soal dalam mode terkunci."""
    murid = _get_murid()
    if murid.status == "ditetapkan":
        flash("Kelas sudah ditetapkan. Tes tidak lagi tersedia.", "info")
        return redirect(url_for("murid.dashboard"))
    if kelas not in dict(KELAS_CHOICES):
        flash("Kelas soal tidak valid.", "danger")
        return redirect(url_for("murid.tes"))
    if not _sudah_masuk_tes(murid):
        flash("Masukkan password masuk soal terlebih dahulu.", "warning")
        return redirect(url_for("murid.tes"))

    kunci = get_kunci_tes(
        _tahun_murid(murid), _gelombang_murid(murid), _jenis_tes(murid)
    )
    if not kunci.is_aktif:
        flash("Pengerjaan soal ditutup admin.", "warning")
        return redirect(url_for("murid.tes"))

    soals = (
        SoalTes.query.filter_by(kelas_tujuan=kelas, is_active=True)
        .order_by(SoalTes.id)
        .all()
    )
    sesi = _pastikan_sesi(murid, kelas)

    # Setelah submit: hanya boleh keluar dengan password keluar
    if sesi.status == "selesai" and sesi.butuh_password_keluar:
        session["tes_menunggu_keluar"] = kelas
        return render_template(
            "murid/tes_keluar.html",
            murid=murid,
            kelas=kelas,
            kelas_label=dict(KELAS_CHOICES)[kelas],
            lock_mode=True,
        )

    if sesi.status == "selesai" and not sesi.butuh_password_keluar:
        flash("Sesi ini sudah disubmit. Minta admin mereset jika perlu mengerjakan lagi.", "info")
        return redirect(url_for("murid.tes"))

    sudah = {j.soal_id: j for j in murid.jawaban_tes if j.soal_id}
    locked_final = murid.status in ("dinilai", "ditetapkan")

    if request.method == "POST":
        if locked_final:
            flash("Tes terkunci.", "warning")
            return redirect(url_for("murid.tes_kelas", kelas=kelas))
        if not soals:
            flash("Soal untuk kelas ini belum tersedia.", "warning")
            return redirect(url_for("murid.tes"))

        _upsert_jawaban(murid, soals, request.form.get)
        db.session.flush()
        db.session.refresh(murid)
        terjawab = _jumlah_terjawab(murid, soals)
        if terjawab < len(soals):
            db.session.commit()
            flash(
                f"Masih ada soal belum dijawab ({terjawab}/{len(soals)}). "
                "Jawaban tersimpan, lengkapi semua sebelum submit.",
                "danger",
            )
            return redirect(url_for("murid.tes_kelas", kelas=kelas))

        sesi.status = "selesai"
        sesi.selesai_at = datetime.utcnow()
        sesi.butuh_password_keluar = True
        sesi.last_seen_at = datetime.utcnow()
        if murid.status not in ("dinilai", "ditetapkan", "wawancara"):
            if murid.tes_tertulis_selesai():
                murid.status = "tes_selesai"
            elif murid.is_tes_susulan:
                murid.status = "tes_susulan"
            else:
                murid.status = "terdaftar"
        db.session.commit()
        session["tes_menunggu_keluar"] = kelas
        flash(
            f"Jawaban {dict(KELAS_CHOICES)[kelas]} terkirim. "
            "Masukkan password keluar dari pengawas untuk meninggalkan layar soal.",
            "success",
        )
        return redirect(url_for("murid.tes_kelas", kelas=kelas))

    return render_template(
        "murid/tes_kelas.html",
        murid=murid,
        soals=soals,
        sudah=sudah,
        locked=locked_final,
        kelas=kelas,
        kelas_label=dict(KELAS_CHOICES)[kelas],
        lock_mode=True,
        terjawab=_jumlah_terjawab(murid, soals),
        sesi=sesi,
    )


@murid_bp.route("/tes/<kelas>/autosave", methods=["POST"])
@login_required
@role_required("murid")
def tes_autosave(kelas):
    murid = _get_murid()
    if not _sudah_masuk_tes(murid) or kelas not in dict(KELAS_CHOICES):
        return jsonify({"ok": False, "error": "unauthorized"}), 403
    sesi = SesiTesMurid.query.filter_by(
        murid_id=murid.id, kelas_tujuan=kelas
    ).first()
    if not sesi or sesi.status != "aktif":
        return jsonify({"ok": False, "error": "sesi_tidak_aktif"}), 400

    soals = SoalTes.query.filter_by(kelas_tujuan=kelas, is_active=True).all()
    data = request.get_json(silent=True) or {}
    answers = data.get("jawaban") or {}

    def form_get(key):
        # key: soal_12
        sid = key.replace("soal_", "")
        return answers.get(sid) or answers.get(key)

    _upsert_jawaban(murid, soals, form_get)
    sesi.last_seen_at = datetime.utcnow()
    db.session.commit()
    return jsonify(
        {
            "ok": True,
            "terjawab": _jumlah_terjawab(murid, soals),
            "total": len(soals),
        }
    )


@murid_bp.route("/tes/<kelas>/heartbeat", methods=["POST"])
@login_required
@role_required("murid")
def tes_heartbeat(kelas):
    murid = _get_murid()
    if not _sudah_masuk_tes(murid):
        return jsonify({"ok": False}), 403
    sesi = SesiTesMurid.query.filter_by(
        murid_id=murid.id, kelas_tujuan=kelas
    ).first()
    if not sesi:
        return jsonify({"ok": False}), 404

    payload = request.get_json(silent=True) or {}
    sesi.last_seen_at = datetime.utcnow()
    if payload.get("pelanggaran"):
        sesi.pelanggaran = (sesi.pelanggaran or 0) + 1
        catatan = (sesi.catatan_pelanggaran or "").strip()
        baris = f"{datetime.utcnow().isoformat(timespec='seconds')}Z · {payload.get('alasan') or 'keluar layar/aplikasi'}"
        sesi.catatan_pelanggaran = (catatan + "\n" + baris).strip()[-2000:]
    db.session.commit()
    return jsonify(
        {
            "ok": True,
            "status": sesi.status,
            "pelanggaran": sesi.pelanggaran,
            "reset_count": sesi.reset_count or 0,
        }
    )


@murid_bp.route("/tes/keluar", methods=["POST"])
@login_required
@role_required("murid")
def tes_keluar():
    murid = _get_murid()
    kunci = get_kunci_tes(
        _tahun_murid(murid), _gelombang_murid(murid), _jenis_tes(murid)
    )
    password = (request.form.get("password_keluar") or "").strip()
    kelas = request.form.get("kelas") or session.get("tes_menunggu_keluar")

    if password != kunci.password_keluar:
        flash("Password keluar salah. Minta password dari pengawas/admin.", "danger")
        if kelas:
            return redirect(url_for("murid.tes_kelas", kelas=kelas))
        return redirect(url_for("murid.tes"))

    if kelas:
        sesi = SesiTesMurid.query.filter_by(
            murid_id=murid.id, kelas_tujuan=kelas
        ).first()
        if sesi:
            sesi.butuh_password_keluar = False
            sesi.last_seen_at = datetime.utcnow()
            db.session.commit()

    session.pop("tes_menunggu_keluar", None)
    # Password masuk tetap berlaku di gelombang ini agar bisa lanjut kelas lain
    session["tes_lock_mode"] = False

    # Setelah seluruh kelas selesai, lepas status susulan
    if murid.tes_tertulis_selesai() and murid.is_tes_susulan:
        murid.is_tes_susulan = False
        if murid.status == "tes_susulan":
            murid.status = "tes_selesai"
        db.session.commit()

    flash(
        "Password keluar benar. Anda boleh keluar dari layar soal / lanjut kelas lain.",
        "success",
    )
    return redirect(url_for("murid.tes"))


@murid_bp.route("/hasil")
@login_required
@role_required("murid")
def hasil():
    return redirect(url_for("murid.hasil_gabungan"))


@murid_bp.route("/hasil/tes-tertulis")
@login_required
@role_required("murid")
def hasil_tes():
    blok = _paksa_jika_menunggu_keluar()
    if blok:
        return blok
    murid = _get_murid()
    return render_template(
        "murid/hasil_tes.html",
        murid=murid,
        kelas_choices=KELAS_CHOICES,
        nilai_tes=murid.nilai_tes_per_kelas(),
        ringkas_tes=murid.ringkas_tes_tertulis(),
        tampilkan_kisi=tampilkan_kisi_kisi(),
    )


@murid_bp.route("/kisi-kisi")
@login_required
@role_required("murid")
def kisi_kisi():
    blok = _paksa_jika_menunggu_keluar()
    if blok:
        return blok
    kelas = request.args.get("kelas") or ""
    return render_template(
        "shared/kisi_kisi.html",
        items=daftar_kisi_kisi(kelas) if tampilkan_kisi_kisi() else [],
        kelas=kelas,
        kelas_choices=KELAS_CHOICES,
        tampilkan=tampilkan_kisi_kisi(),
        back_url=url_for("murid.hasil_tes"),
    )


@murid_bp.route("/hasil/wawancara")
@login_required
@role_required("murid")
def hasil_wawancara():
    blok = _paksa_jika_menunggu_keluar()
    if blok:
        return blok
    murid = _get_murid()
    return render_template(
        "murid/hasil_wawancara.html",
        murid=murid,
        kelas_choices=KELAS_CHOICES,
        nilai_per_kelas=murid.nilai_wawancara_per_kelas(),
    )


@murid_bp.route("/hasil/gabungan")
@login_required
@role_required("murid")
def hasil_gabungan():
    blok = _paksa_jika_menunggu_keluar()
    if blok:
        return blok
    murid = _get_murid()
    bobot_tes, bobot_ww, bobot_psiko = get_bobot_penilaian()
    return render_template(
        "murid/hasil_gabungan.html",
        murid=murid,
        kelas_choices=KELAS_CHOICES,
        nilai_per_kelas=murid.nilai_wawancara_per_kelas(),
        nilai_tes=murid.nilai_tes_per_kelas(),
        nilai_gabungan=murid.skor_gabungan_per_kelas(),
        ringkas_tes=murid.ringkas_tes_tertulis(),
        bobot_tes=bobot_tes,
        bobot_wawancara=bobot_ww,
        bobot_psikotes=bobot_psiko,
    )
