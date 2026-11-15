from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from tpk.blanko import buat_blanko_xlsx, baca_blanko, impor_blanko_murid
from tpk.extensions import db
from tpk.models import (
    KELAS_CHOICES,
    ROLE_CHOICES,
    KriteriaPenilaian,
    KunciTesGelombang,
    Murid,
    PenilaianWawancara,
    Pengaturan,
    SesiTesMurid,
    SoalTes,
    SoalWawancara,
    User,
)
from tpk.psikotes_import import (
    baca_psikotes_file,
    buat_blanko_psikotes_xlsx,
    impor_skor_psikotes,
)
from tpk.soal_import import baca_soal_file, buat_blanko_soal_xlsx, impor_soal_tes
from tpk.utils import (
    DEFAULT_PASSWORD_MURID,
    DEFAULT_PASSWORD_ORTU,
    ANALISIS_MIN_JAWAB,
    ANALISIS_P_MAX,
    ANALISIS_P_MIN,
    analisis_soal_tes,
    rekap_analisis_soal_per_kelas,
    buat_username_dari_nama,
    daftar_kisi_kisi,
    get_bobot_penilaian,
    get_daftar_gelombang,
    get_gelombang_aktif,
    get_kunci_tes,
    alokasi_penempatan_kuota,
    get_kuota_kelas,
    get_semua_bobot_kelas,
    get_semua_kuota_kelas,
    get_tahun_ajaran,
    hitung_terisi_kelas,
    is_gelombang_kosong,
    label_gelombang,
    normalisasi_gelombang,
    PSIKOTES_MAX,
    PSIKOTES_MIN,
    PSIKOTES_SKALA_MAX,
    PSIKOTES_SKALA_MIN,
    GELOMBANG_KOSONG,
    pastikan_akun_ortu,
    role_required,
    set_setting,
    sinkronkan_akun_ortu,
    sisa_kuota_kelas,
    tambah_gelombang_ke_daftar,
    tampilkan_kisi_kisi,
)
import io
import re
from datetime import datetime

DEFAULT_PASSWORD_ADMIN = "admin123"
DEFAULT_PASSWORD_GURU = "guru123"


def _password_default_role(role: str) -> str:
    if role == "admin":
        return DEFAULT_PASSWORD_ADMIN
    if role in ("guru", "guru_soal"):
        return DEFAULT_PASSWORD_GURU
    if role == "orang_tua":
        return DEFAULT_PASSWORD_ORTU
    return DEFAULT_PASSWORD_MURID


def _normalize_username(value: str) -> str:
    text = (value or "").strip().lower()
    text = re.sub(r"[^a-z0-9._-]", "", text)
    return text

admin_bp = Blueprint("admin", __name__)


def _filter_tahun_gelombang(query, tahun=None, gelombang=None):
    tahun = tahun if tahun is not None else get_tahun_ajaran()
    if tahun:
        query = query.filter(
            (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None))
        )
    if gelombang:
        g = normalisasi_gelombang(gelombang)
        if is_gelombang_kosong(g):
            query = query.filter(Murid.gelombang.is_(None) | (Murid.gelombang == ""))
        else:
            query = query.filter(Murid.gelombang == g)
    return query


def _jumlah_murid_per_gelombang(tahun=None) -> dict:
    """Hitung peserta per gelombang (termasuk tanpa gelombang)."""
    tahun = tahun or get_tahun_ajaran()
    rows = (
        db.session.query(Murid.gelombang, func.count(Murid.id))
        .filter((Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)))
        .group_by(Murid.gelombang)
        .all()
    )
    hasil = {}
    tanpa = 0
    for g, n in rows:
        if g is None or str(g).strip() == "":
            tanpa += int(n)
        else:
            key = normalisasi_gelombang(g)
            hasil[key] = hasil.get(key, 0) + int(n)
    if tanpa:
        hasil[GELOMBANG_KOSONG] = tanpa
    return hasil


def _hapus_satu_murid(murid: Murid) -> None:
    """Hapus murid + akun login murid & ortu (cascade jawaban/sesi/penilaian)."""
    ortu = murid.ortu_user
    user = murid.user
    if user and user.role == "murid":
        db.session.delete(user)
    else:
        db.session.delete(murid)
    if ortu and ortu.role == "orang_tua":
        db.session.delete(ortu)


@admin_bp.route("/")
@login_required
@role_required("admin")
def dashboard():
    gelombang = normalisasi_gelombang(request.args.get("gelombang", get_gelombang_aktif()))
    tahun = get_tahun_ajaran()
    base = _filter_tahun_gelombang(Murid.query, tahun, gelombang)
    total_murid = base.count()
    total_guru = User.query.filter_by(role="guru").count()
    total_soal = SoalTes.query.filter_by(is_active=True).count()
    sudah_dinilai = base.filter(Murid.status.in_(["dinilai", "ditetapkan"])).count()
    per_kelas_q = db.session.query(Murid.pilihan_kelas_1, func.count(Murid.id)).filter(
        (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None))
    )
    if gelombang:
        per_kelas_q = per_kelas_q.filter(Murid.gelombang == gelombang)
    per_kelas = per_kelas_q.group_by(Murid.pilihan_kelas_1).all()

    per_gelombang = (
        db.session.query(Murid.gelombang, func.count(Murid.id))
        .filter((Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)))
        .group_by(Murid.gelombang)
        .all()
    )
    terbaru = base.order_by(Murid.created_at.desc()).limit(8).all()
    return render_template(
        "admin/dashboard.html",
        total_murid=total_murid,
        total_guru=total_guru,
        total_soal=total_soal,
        sudah_dinilai=sudah_dinilai,
        per_kelas=per_kelas,
        per_gelombang=per_gelombang,
        terbaru=terbaru,
        kelas_map=dict(KELAS_CHOICES),
        gelombang=gelombang,
        daftar_gelombang=get_daftar_gelombang(),
        tahun_ajaran=tahun,
    )


@admin_bp.route("/murid")
@login_required
@role_required("admin")
def murid_list():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    kelas = request.args.get("kelas", "")
    raw_gelombang = request.args.get("gelombang", get_gelombang_aktif())
    gelombang = normalisasi_gelombang(raw_gelombang)
    tahun = get_tahun_ajaran()
    query = _filter_tahun_gelombang(
        Murid.query.join(User, Murid.user_id == User.id), tahun, gelombang
    )
    if q:
        query = query.filter(
            (User.nama_lengkap.ilike(f"%{q}%"))
            | (Murid.nisn.ilike(f"%{q}%"))
            | (User.username.ilike(f"%{q}%"))
        )
    if status:
        query = query.filter(Murid.status == status)
    if kelas:
        query = query.filter(Murid.pilihan_kelas_1 == kelas)
    items = query.order_by(Murid.created_at.desc()).all()
    jumlah_per_gelombang = _jumlah_murid_per_gelombang(tahun)
    return render_template(
        "admin/murid_list.html",
        items=items,
        q=q,
        status=status,
        kelas=kelas,
        gelombang=gelombang,
        kelas_choices=KELAS_CHOICES,
        daftar_gelombang=get_daftar_gelombang(),
        tahun_ajaran=tahun,
        jumlah_per_gelombang=jumlah_per_gelombang,
        gelombang_kosong=GELOMBANG_KOSONG,
    )


@admin_bp.route("/murid/blanko/unduh")
@login_required
@role_required("admin")
def unduh_blanko_murid():
    content = buat_blanko_xlsx()
    return send_file(
        io.BytesIO(content),
        as_attachment=True,
        download_name="blanko_murid_tpk_smartmu22.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@admin_bp.route("/murid/blanko/upload", methods=["POST"])
@login_required
@role_required("admin")
def upload_blanko_murid():
    file = request.files.get("blanko_file")
    if not file or not file.filename:
        flash("Pilih file blanko terlebih dahulu.", "danger")
        return redirect(url_for("admin.murid_list"))

    rows, error = baca_blanko(file)
    if error:
        flash(error, "danger")
        return redirect(url_for("admin.murid_list"))
    if not rows:
        flash("Tidak ada baris data yang bisa diimpor.", "warning")
        return redirect(url_for("admin.murid_list"))

    hasil = impor_blanko_murid(rows)
    parts = []
    if hasil.get("sukses"):
        parts.append(f"{hasil['sukses']} data baru")
    if hasil.get("diperbarui"):
        parts.append(f"{hasil['diperbarui']} diperbarui")
    if hasil.get("dilewati"):
        parts.append(f"{hasil['dilewati']} dilewati")
    if parts:
        flash("Upload selesai: " + ", ".join(parts) + ".", "success")
    if hasil.get("gelombang"):
        labels = ", ".join(label_gelombang(g) for g in hasil["gelombang"])
        flash(
            f"Gelombang terunggah: {labels}. "
            "Gelombang lama tetap tersimpan dan tidak dihapus.",
            "info",
        )
    if hasil["gagal"]:
        preview = " | ".join(hasil["gagal"][:3])
        more = f" (+{len(hasil['gagal']) - 3} lainnya)" if len(hasil["gagal"]) > 3 else ""
        flash(f"{len(hasil['gagal'])} baris gagal: {preview}{more}", "warning")
    if not parts and not hasil["gagal"]:
        flash("Tidak ada data yang diproses.", "info")
    gelombang_redirect = (
        hasil["gelombang"][0] if hasil.get("gelombang") else get_gelombang_aktif()
    )
    return redirect(url_for("admin.murid_list", gelombang=gelombang_redirect))


@admin_bp.route("/murid/gelombang/hapus", methods=["POST"])
@login_required
@role_required("admin")
def hapus_murid_gelombang():
    """Hapus seluruh peserta (akun + nilai) dalam satu gelombang tahun ajaran aktif."""
    gelombang = normalisasi_gelombang(request.form.get("gelombang"))
    konfirmasi = (request.form.get("konfirmasi") or "").strip().upper()
    tahun = get_tahun_ajaran()

    if not gelombang:
        flash("Pilih gelombang yang akan dihapus.", "danger")
        return redirect(url_for("admin.murid_list"))

    if is_gelombang_kosong(gelombang):
        expected = "HAPUS TANPA GELOMBANG"
    else:
        expected = f"HAPUS GELOMBANG {gelombang}".upper()

    if konfirmasi != expected:
        flash(f"Konfirmasi salah. Ketik tepat: {expected}", "danger")
        return redirect(url_for("admin.murid_list", gelombang=gelombang))

    murids = _filter_tahun_gelombang(Murid.query, tahun, gelombang).all()
    if not murids:
        flash(
            f"Tidak ada peserta di {label_gelombang(gelombang)} "
            f"tahun ajaran {tahun}.",
            "warning",
        )
        return redirect(url_for("admin.murid_list", gelombang=gelombang))

    jumlah = len(murids)
    try:
        for murid in murids:
            _hapus_satu_murid(murid)
        db.session.commit()
        # Slot gelombang tetap ada agar bisa diisi ulang (kecuali tanpa gelombang)
        if not is_gelombang_kosong(gelombang):
            tambah_gelombang_ke_daftar(gelombang)
        flash(
            f"{jumlah} peserta di {label_gelombang(gelombang)} "
            f"(TA {tahun}) berhasil dihapus."
            + (
                " Slot gelombang tetap tersedia."
                if not is_gelombang_kosong(gelombang)
                else ""
            ),
            "success",
        )
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        flash(f"Gagal menghapus peserta gelombang: {exc}", "danger")
        return redirect(url_for("admin.murid_list", gelombang=gelombang))

    redirect_g = get_gelombang_aktif() if is_gelombang_kosong(gelombang) else gelombang
    return redirect(url_for("admin.murid_list", gelombang=redirect_g))


@admin_bp.route("/murid/ortu/sinkron", methods=["POST"])
@login_required
@role_required("admin")
def sinkron_akun_ortu():
    """Buat akun login orang tua dari data murid yang sudah diunggah."""
    gelombang = normalisasi_gelombang(
        request.form.get("gelombang") or get_gelombang_aktif()
    )
    tahun = get_tahun_ajaran()
    murids = _filter_tahun_gelombang(Murid.query, tahun, gelombang).all()
    if not murids:
        flash(
            f"Tidak ada murid di {label_gelombang(gelombang)} untuk disinkronkan.",
            "warning",
        )
        return redirect(url_for("admin.murid_list", gelombang=gelombang))

    hasil = sinkronkan_akun_ortu(murids)
    flash(
        f"Akun orang tua disinkronkan: {hasil['dibuat']} dibuat, "
        f"{hasil['diperbarui']} diperbarui. "
        f"Username: ortu.namaanak · Password awal: {DEFAULT_PASSWORD_ORTU}",
        "success",
    )
    return redirect(url_for("admin.murid_list", gelombang=gelombang))


def _buat_nisn_otomatis_admin() -> str:
    """NISN sementara unik jika admin tidak mengisi."""
    base = f"9{datetime.utcnow().strftime('%y%m%d%H%M%S')}"
    kandidat = base[:20]
    n = 1
    while Murid.query.filter_by(nisn=kandidat).first():
        kandidat = f"{base[:16]}{n}"[:20]
        n += 1
    return kandidat


@admin_bp.route("/murid/tambah", methods=["GET", "POST"])
@login_required
@role_required("admin")
def murid_tambah():
    """Tambah satu murid secara manual (sama seperti hasil upload blanko)."""
    gelombang_default = normalisasi_gelombang(
        request.args.get("gelombang")
        or request.form.get("gelombang")
        or get_gelombang_aktif()
    )
    if is_gelombang_kosong(gelombang_default):
        gelombang_default = get_gelombang_aktif()
    tahun = get_tahun_ajaran()

    if request.method == "POST":
        nama = (request.form.get("nama_lengkap") or "").strip()
        jk = (request.form.get("jenis_kelamin") or "").strip().upper()
        asal = (request.form.get("asal_sekolah") or "").strip()
        gelombang = normalisasi_gelombang(request.form.get("gelombang"))
        nisn = re.sub(r"[^\dA-Za-z]", "", (request.form.get("nisn") or "").strip())
        pilihan1 = request.form.get("pilihan_kelas_1") or "reguler"
        pilihan2 = request.form.get("pilihan_kelas_2") or None
        nama_ortu = (request.form.get("nama_ortu") or "").strip() or None
        no_hp_ortu = (request.form.get("no_hp_ortu") or "").strip() or None
        alamat = (request.form.get("alamat") or "").strip() or None
        nomor_urut = (request.form.get("nomor_urut") or "").strip() or None

        if not nama or jk not in ("L", "P") or not asal or not gelombang or is_gelombang_kosong(gelombang):
            flash(
                "Lengkapi data wajib: nama, jenis kelamin, asal sekolah, dan gelombang.",
                "danger",
            )
            return redirect(url_for("admin.murid_tambah", gelombang=gelombang_default))

        if pilihan1 not in dict(KELAS_CHOICES):
            flash("Pilihan kelas 1 tidak valid.", "danger")
            return redirect(url_for("admin.murid_tambah", gelombang=gelombang))

        if pilihan2 and pilihan2 not in dict(KELAS_CHOICES):
            pilihan2 = None

        if not nisn:
            nisn = _buat_nisn_otomatis_admin()
        elif Murid.query.filter_by(nisn=nisn).first():
            flash(f"NISN {nisn} sudah terdaftar.", "danger")
            return redirect(url_for("admin.murid_tambah", gelombang=gelombang))

        try:
            username = buat_username_dari_nama(nama)
            user = User(
                username=username,
                nama_lengkap=nama,
                role="murid",
                is_active_user=True,
            )
            user.set_password(DEFAULT_PASSWORD_MURID)
            db.session.add(user)
            db.session.flush()

            murid = Murid(
                user_id=user.id,
                nisn=nisn,
                nomor_urut=nomor_urut,
                tahun_ajaran=tahun,
                gelombang=gelombang,
                jenis_kelamin=jk,
                alamat=alamat,
                nama_ortu=nama_ortu,
                no_hp_ortu=no_hp_ortu,
                asal_sekolah=asal,
                pilihan_kelas_1=pilihan1,
                pilihan_kelas_2=pilihan2,
                status="terdaftar",
            )
            db.session.add(murid)
            db.session.flush()
            pastikan_akun_ortu(murid, commit=False)
            tambah_gelombang_ke_daftar(gelombang)
            db.session.commit()
            flash(
                f"Murid {nama} ditambahkan ke {label_gelombang(gelombang)}. "
                f"Login: {username} / {DEFAULT_PASSWORD_MURID}.",
                "success",
            )
            return redirect(url_for("admin.murid_detail", murid_id=murid.id))
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            flash(f"Gagal menambah murid: {exc}", "danger")
            return redirect(url_for("admin.murid_tambah", gelombang=gelombang))

    return render_template(
        "admin/murid_form.html",
        gelombang=gelombang_default,
        daftar_gelombang=get_daftar_gelombang(),
        kelas_choices=KELAS_CHOICES,
        tahun_ajaran=tahun,
        default_password_murid=DEFAULT_PASSWORD_MURID,
        default_password_ortu=DEFAULT_PASSWORD_ORTU,
    )


@admin_bp.route("/murid/<int:murid_id>/hapus", methods=["POST"])
@login_required
@role_required("admin")
def hapus_murid(murid_id):
    """Hapus satu murid (akun + nilai terkait)."""
    murid = Murid.query.get_or_404(murid_id)
    gelombang = murid.gelombang or get_gelombang_aktif()
    nama = murid.user.nama_lengkap if murid.user else murid.nisn
    nisn = murid.nisn
    konfirmasi = (request.form.get("konfirmasi") or "").strip().upper()
    expected = f"HAPUS {nisn}".upper()

    # Konfirmasi ketat jika dikirim; jika tidak, cukup tombol confirm di UI
    if konfirmasi and konfirmasi != expected:
        flash(f"Konfirmasi salah. Ketik tepat: {expected}", "danger")
        return redirect(url_for("admin.murid_detail", murid_id=murid_id))

    try:
        _hapus_satu_murid(murid)
        db.session.commit()
        flash(f"Murid {nama} (NISN {nisn}) berhasil dihapus.", "success")
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        flash(f"Gagal menghapus murid: {exc}", "danger")
        return redirect(url_for("admin.murid_detail", murid_id=murid_id))

    return redirect(url_for("admin.murid_list", gelombang=gelombang))


@admin_bp.route("/murid/<int:murid_id>")
@login_required
@role_required("admin")
def murid_detail(murid_id):
    murid = Murid.query.get_or_404(murid_id)
    terisi = hitung_terisi_kelas()
    kuota = get_semua_kuota_kelas()
    kuota_info = {
        kode: {
            "kuota": kuota.get(kode, 0),
            "terisi": terisi.get(kode, 0),
            "sisa": (
                None
                if kuota.get(kode, 0) <= 0
                else max(kuota.get(kode, 0) - terisi.get(kode, 0), 0)
            ),
        }
        for kode, _ in KELAS_CHOICES
    }
    return render_template(
        "admin/murid_detail.html",
        murid=murid,
        kelas_choices=KELAS_CHOICES,
        default_password_ortu=DEFAULT_PASSWORD_ORTU,
        kuota_info=kuota_info,
    )


@admin_bp.route("/murid/<int:murid_id>/tetapkan", methods=["POST"])
@login_required
@role_required("admin")
def tetapkan_kelas(murid_id):
    murid = Murid.query.get_or_404(murid_id)
    kelas = request.form.get("kelas_ditetapkan")
    catatan = request.form.get("catatan_admin", "").strip()
    paksa = request.form.get("paksa_kuota") == "1"
    if kelas not in dict(KELAS_CHOICES):
        flash("Kelas tidak valid.", "danger")
        return redirect(url_for("admin.murid_detail", murid_id=murid_id))

    # Cek kuota (abaikan jika murid sudah di kelas yang sama)
    kuota = get_kuota_kelas(kelas)
    if kuota > 0 and murid.kelas_ditetapkan != kelas:
        terisi = hitung_terisi_kelas().get(kelas, 0)
        if terisi >= kuota and not paksa:
            flash(
                f"Kuota kelas {dict(KELAS_CHOICES)[kelas]} penuh "
                f"({terisi}/{kuota}). Centang 'Paksa tetapkan' jika tetap ingin menempatkan.",
                "warning",
            )
            return redirect(url_for("admin.murid_detail", murid_id=murid_id))

    murid.kelas_ditetapkan = kelas
    rekomendasi = murid.rekomendasi_kelas_label
    skor = murid.nilai_rekomendasi()
    kelas_rek = murid.rekomendasi_kelas()
    bobot_tes, bobot_ww, bobot_psiko = get_bobot_penilaian(kelas_rek)
    catatan_otomatis = (
        f"Rekomendasi sistem kelas {rekomendasi} "
        f"(bobot tes {bobot_tes}% + wawancara {bobot_ww}% + psikotes {bobot_psiko}%)"
        + (f" · skor {skor}" if skor is not None else "")
        + "."
    )
    murid.catatan_admin = catatan or catatan_otomatis
    murid.status = "ditetapkan"
    db.session.commit()
    sisa = sisa_kuota_kelas(kelas)
    msg = f"Kelas {dict(KELAS_CHOICES)[kelas]} berhasil ditetapkan."
    if sisa is not None:
        msg += f" Sisa kuota: {sisa}."
    flash(msg, "success")
    return redirect(url_for("admin.murid_detail", murid_id=murid_id))


@admin_bp.route("/guru", methods=["GET", "POST"])
@login_required
@role_required("admin")
def guru_list():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        nama = request.form.get("nama_lengkap", "").strip()
        kelas = request.form.get("kelas_penguji")
        password = request.form.get("password", "guru123") or "guru123"
        juga_soal = request.form.get("juga_pembuat_soal") == "1"

        if not username or not nama or kelas not in dict(KELAS_CHOICES):
            flash("Data guru tidak lengkap.", "danger")
        else:
            existing = User.query.filter_by(username=username).first()
            if existing and existing.role == "guru_soal":
                existing.role = "guru"
                existing.juga_pembuat_soal = True
                existing.nama_lengkap = nama
                existing.kelas_penguji = kelas
                existing.set_password(password)
                existing.is_active_user = True
                db.session.commit()
                flash(
                    "Akun pembuat soal dilengkapi sebagai guru penguji "
                    "(username & password sama).",
                    "success",
                )
            elif existing:
                flash("Username sudah dipakai.", "danger")
            else:
                guru = User(
                    username=username,
                    nama_lengkap=nama,
                    email=None,
                    role="guru",
                    kelas_penguji=kelas,
                    juga_pembuat_soal=juga_soal,
                )
                guru.set_password(password)
                db.session.add(guru)
                db.session.commit()
                if juga_soal:
                    flash(
                        "Guru penguji ditambahkan dan bisa login ke bank soal "
                        "dengan username/password yang sama.",
                        "success",
                    )
                else:
                    flash("Guru penguji berhasil ditambahkan.", "success")
        return redirect(url_for("admin.guru_list"))

    items = User.query.filter_by(role="guru").order_by(User.nama_lengkap).all()
    return render_template("admin/guru_list.html", items=items, kelas_choices=KELAS_CHOICES)


@admin_bp.route("/guru/<int:user_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def guru_toggle(user_id):
    guru = User.query.get_or_404(user_id)
    if guru.role != "guru":
        flash("Bukan akun guru.", "danger")
    else:
        guru.is_active_user = not guru.is_active_user
        db.session.commit()
        flash("Status guru diperbarui.", "success")
    return redirect(url_for("admin.guru_list"))


@admin_bp.route("/guru-soal", methods=["GET", "POST"])
@login_required
@role_required("admin")
def guru_soal_list():
    """Akun guru pembuat soal: satu kelas tugas, hanya akses bank soal kelas itu.

    Username boleh sama dengan guru penguji — akses digabung ke akun yang sama.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        nama = request.form.get("nama_lengkap", "").strip()
        kelas = request.form.get("kelas_penguji")
        password = request.form.get("password", "guru123") or "guru123"

        if not username or not nama or kelas not in dict(KELAS_CHOICES):
            flash("Lengkapi username, nama, dan kelas soal yang ditugaskan.", "danger")
        else:
            existing = User.query.filter_by(username=username).first()
            if existing and existing.role == "guru":
                existing.juga_pembuat_soal = True
                existing.nama_lengkap = nama or existing.nama_lengkap
                existing.kelas_penguji = kelas
                existing.set_password(password)
                existing.is_active_user = True
                db.session.commit()
                flash(
                    f"Akses pembuat soal ditambahkan ke akun guru penguji "
                    f"{username} (password ikut diperbarui).",
                    "success",
                )
            elif existing:
                flash("Username sudah dipakai.", "danger")
            else:
                user = User(
                    username=username,
                    nama_lengkap=nama,
                    email=None,
                    role="guru_soal",
                    kelas_penguji=kelas,
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash(
                    f"Guru pembuat soal {dict(KELAS_CHOICES)[kelas]} ditambahkan. "
                    f"Login: {username} / {password}",
                    "success",
                )
        return redirect(url_for("admin.guru_soal_list"))

    items = (
        User.query.filter(
            db.or_(
                User.role == "guru_soal",
                db.and_(User.role == "guru", User.juga_pembuat_soal.is_(True)),
            )
        )
        .order_by(User.kelas_penguji, User.nama_lengkap)
        .all()
    )
    return render_template(
        "admin/guru_soal_list.html",
        items=items,
        kelas_choices=KELAS_CHOICES,
    )


@admin_bp.route("/guru-soal/<int:user_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def guru_soal_toggle(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "guru" and user.juga_pembuat_soal:
        user.juga_pembuat_soal = False
        db.session.commit()
        flash("Akses pembuat soal pada akun guru penguji dinonaktifkan.", "success")
    elif user.role == "guru_soal":
        user.is_active_user = not user.is_active_user
        db.session.commit()
        flash("Status akun diperbarui.", "success")
    else:
        flash("Bukan akun guru pembuat soal.", "danger")
    return redirect(url_for("admin.guru_soal_list"))


@admin_bp.route("/soal", methods=["GET", "POST"])
@login_required
@role_required("admin")
def soal_list():
    from tpk.media import (
        lengkapi_teks_opsi,
        proses_gambar_opsi,
        simpan_gambar_base64,
        simpan_gambar_file,
    )

    if request.method == "POST":
        kelas_tujuan = request.form.get("kelas_tujuan")
        pertanyaan = request.form.get("pertanyaan", "").strip()
        jawaban_benar = request.form.get("jawaban_benar", "A").upper()
        bobot = int(request.form.get("bobot") or 1)
        gambar_path = None
        try:
            if request.files.get("gambar_file") and request.files["gambar_file"].filename:
                gambar_path = simpan_gambar_file(request.files["gambar_file"])
            elif request.form.get("gambar_paste"):
                gambar_path = simpan_gambar_base64(request.form.get("gambar_paste"))
            gambar_opsi = proses_gambar_opsi(request)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("admin.soal_list", kelas=kelas_tujuan or None))

        opsi = {
            h: lengkapi_teks_opsi(request.form.get(f"opsi_{h}", ""), gambar_opsi.get(h), h)
            for h in ("a", "b", "c", "d")
        }
        if not pertanyaan and gambar_path:
            pertanyaan = "Lihat gambar soal"
        if kelas_tujuan not in dict(KELAS_CHOICES) or not pertanyaan:
            flash("Lengkapi kelas, pertanyaan (atau gambar), dan opsi A–D.", "danger")
            return redirect(url_for("admin.soal_list", kelas=kelas_tujuan or None))
        if not all(opsi.values()) or jawaban_benar not in "ABCD":
            flash("Tiap opsi A–D wajib teks atau gambar.", "danger")
            return redirect(url_for("admin.soal_list", kelas=kelas_tujuan or None))

        soal = SoalTes(
            kelas_tujuan=kelas_tujuan,
            pertanyaan=pertanyaan,
            gambar=gambar_path,
            opsi_a=opsi["a"],
            opsi_b=opsi["b"],
            opsi_c=opsi["c"],
            opsi_d=opsi["d"],
            gambar_opsi_a=gambar_opsi.get("a"),
            gambar_opsi_b=gambar_opsi.get("b"),
            gambar_opsi_c=gambar_opsi.get("c"),
            gambar_opsi_d=gambar_opsi.get("d"),
            jawaban_benar=jawaban_benar,
            bobot=bobot,
        )
        db.session.add(soal)
        db.session.commit()
        flash("Soal berhasil ditambahkan (teks/gambar soal & opsi didukung).", "success")
        return redirect(url_for("admin.soal_list", kelas=soal.kelas_tujuan))

    kelas = request.args.get("kelas", "")
    query = SoalTes.query
    if kelas:
        query = query.filter_by(kelas_tujuan=kelas)
    items = query.order_by(SoalTes.kelas_tujuan, SoalTes.id).all()
    jumlah_per_kelas = {
        kode: SoalTes.query.filter_by(kelas_tujuan=kode, is_active=True).count()
        for kode, _ in KELAS_CHOICES
    }
    return render_template(
        "admin/soal_list.html",
        items=items,
        kelas=kelas,
        kelas_choices=KELAS_CHOICES,
        jumlah_per_kelas=jumlah_per_kelas,
    )


@admin_bp.route("/soal/blanko")
@login_required
@role_required("admin")
def unduh_blanko_soal():
    kelas = request.args.get("kelas", "olimpiade")
    if kelas not in dict(KELAS_CHOICES):
        kelas = "olimpiade"
    content = buat_blanko_soal_xlsx(kelas)
    return send_file(
        io.BytesIO(content),
        as_attachment=True,
        download_name=f"blanko_soal_tes_{kelas}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@admin_bp.route("/soal/upload", methods=["POST"])
@login_required
@role_required("admin")
def upload_soal():
    kelas_default = request.form.get("kelas_tujuan", "").strip()
    file = request.files.get("soal_file")
    if not file or not file.filename:
        flash("Pilih file soal (.xlsx / .csv).", "danger")
        return redirect(url_for("admin.soal_list", kelas=kelas_default or None))

    rows, error = baca_soal_file(file)
    if error:
        flash(error, "danger")
        return redirect(url_for("admin.soal_list", kelas=kelas_default or None))
    if not rows:
        flash("Tidak ada baris soal yang bisa diimpor.", "warning")
        return redirect(url_for("admin.soal_list", kelas=kelas_default or None))

    hasil = impor_soal_tes(rows, kelas_default=kelas_default)
    if hasil["sukses"]:
        flash(f"{hasil['sukses']} soal berhasil diunggah.", "success")
    if hasil["dilewati"]:
        flash(f"{hasil['dilewati']} baris contoh dilewati.", "info")
    if hasil["gagal"]:
        preview = " | ".join(hasil["gagal"][:3])
        flash(f"{len(hasil['gagal'])} baris gagal: {preview}", "warning")
    return redirect(url_for("admin.soal_list", kelas=kelas_default or None))


@admin_bp.route("/soal/<int:soal_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def soal_toggle(soal_id):
    soal = SoalTes.query.get_or_404(soal_id)
    soal.is_active = not soal.is_active
    db.session.commit()
    flash("Status soal diperbarui.", "success")
    return redirect(url_for("admin.soal_list", kelas=soal.kelas_tujuan))


@admin_bp.route("/soal/<int:soal_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def soal_edit(soal_id):
    """Edit soal: teks Arab, opsi, dan gambar (upload / tempel snipping tool)."""
    from tpk.media import (
        hapus_gambar_soal,
        lengkapi_teks_opsi,
        proses_gambar_opsi,
        simpan_gambar_base64,
        simpan_gambar_file,
    )

    soal = SoalTes.query.get_or_404(soal_id)
    if request.method == "POST":
        soal.kelas_tujuan = request.form.get("kelas_tujuan") or soal.kelas_tujuan
        pertanyaan = request.form.get("pertanyaan", "").strip()
        soal.jawaban_benar = request.form.get("jawaban_benar", "A").upper()
        soal.bobot = int(request.form.get("bobot") or 1)
        soal.materi = (request.form.get("materi") or "").strip() or None
        soal.indikator = (request.form.get("indikator") or "").strip() or None
        soal.level_kognitif = (
            request.form.get("level_kognitif") or ""
        ).strip() or None

        try:
            if request.form.get("hapus_gambar"):
                hapus_gambar_soal(soal.gambar)
                soal.gambar = None
            elif request.files.get("gambar_file") and request.files["gambar_file"].filename:
                baru = simpan_gambar_file(request.files["gambar_file"])
                if baru:
                    hapus_gambar_soal(soal.gambar)
                    soal.gambar = baru
            elif request.form.get("gambar_paste"):
                baru = simpan_gambar_base64(request.form.get("gambar_paste"))
                if baru:
                    hapus_gambar_soal(soal.gambar)
                    soal.gambar = baru
            gambar_opsi = proses_gambar_opsi(
                request,
                {
                    "a": soal.gambar_opsi_a,
                    "b": soal.gambar_opsi_b,
                    "c": soal.gambar_opsi_c,
                    "d": soal.gambar_opsi_d,
                },
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("admin.soal_edit", soal_id=soal.id))

        soal.gambar_opsi_a = gambar_opsi.get("a")
        soal.gambar_opsi_b = gambar_opsi.get("b")
        soal.gambar_opsi_c = gambar_opsi.get("c")
        soal.gambar_opsi_d = gambar_opsi.get("d")
        soal.opsi_a = lengkapi_teks_opsi(request.form.get("opsi_a", ""), soal.gambar_opsi_a, "a")
        soal.opsi_b = lengkapi_teks_opsi(request.form.get("opsi_b", ""), soal.gambar_opsi_b, "b")
        soal.opsi_c = lengkapi_teks_opsi(request.form.get("opsi_c", ""), soal.gambar_opsi_c, "c")
        soal.opsi_d = lengkapi_teks_opsi(request.form.get("opsi_d", ""), soal.gambar_opsi_d, "d")

        if not pertanyaan and soal.gambar:
            pertanyaan = "Lihat gambar soal"
        if not pertanyaan or soal.kelas_tujuan not in dict(KELAS_CHOICES):
            flash("Pertanyaan (atau gambar) dan kelas wajib diisi.", "danger")
            return redirect(url_for("admin.soal_edit", soal_id=soal.id))
        if not all([soal.opsi_a, soal.opsi_b, soal.opsi_c, soal.opsi_d]):
            flash("Tiap opsi A–D wajib teks atau gambar.", "danger")
            return redirect(url_for("admin.soal_edit", soal_id=soal.id))

        soal.pertanyaan = pertanyaan
        db.session.commit()
        flash("Soal diperbarui.", "success")
        return redirect(url_for("admin.soal_list", kelas=soal.kelas_tujuan))

    return render_template(
        "admin/soal_edit.html", soal=soal, kelas_choices=KELAS_CHOICES
    )


@admin_bp.route("/soal-wawancara", methods=["GET", "POST"])
@login_required
@role_required("admin")
def soal_wawancara_list():
    if request.method == "POST":
        soal = SoalWawancara(
            kelas_tujuan=request.form.get("kelas_tujuan"),
            aspek=request.form.get("aspek", "").strip() or None,
            pertanyaan=request.form.get("pertanyaan", "").strip(),
            panduan=request.form.get("panduan", "").strip() or None,
            bobot=int(request.form.get("bobot") or 12),
            urutan=int(request.form.get("urutan") or 1),
        )
        if soal.kelas_tujuan not in dict(KELAS_CHOICES) or not soal.pertanyaan:
            flash("Data soal wawancara belum lengkap.", "danger")
        else:
            db.session.add(soal)
            db.session.commit()
            flash("Soal wawancara berhasil ditambahkan.", "success")
        return redirect(url_for("admin.soal_wawancara_list", kelas=soal.kelas_tujuan))

    kelas = request.args.get("kelas", "")
    query = SoalWawancara.query
    if kelas:
        query = query.filter_by(kelas_tujuan=kelas)
    items = query.order_by(SoalWawancara.kelas_tujuan, SoalWawancara.urutan, SoalWawancara.id).all()
    return render_template(
        "admin/soal_wawancara_list.html",
        items=items,
        kelas=kelas,
        kelas_choices=KELAS_CHOICES,
    )


@admin_bp.route("/soal-wawancara/<int:soal_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def soal_wawancara_toggle(soal_id):
    soal = SoalWawancara.query.get_or_404(soal_id)
    soal.is_active = not soal.is_active
    db.session.commit()
    flash("Status soal wawancara diperbarui.", "success")
    return redirect(url_for("admin.soal_wawancara_list", kelas=soal.kelas_tujuan))


@admin_bp.route("/kriteria", methods=["GET", "POST"])
@login_required
@role_required("admin")
def kriteria_list():
    if request.method == "POST":
        bobot = int(request.form.get("bobot") or 20)
        item = KriteriaPenilaian(
            kelas_tujuan=request.form.get("kelas_tujuan"),
            nama_kriteria=request.form.get("nama_kriteria", "").strip(),
            deskripsi=request.form.get("deskripsi", "").strip() or None,
            bobot=bobot,
            skor_maks=bobot,  # skor maks = bobot agar total kelas 100
        )
        if item.kelas_tujuan not in dict(KELAS_CHOICES) or not item.nama_kriteria:
            flash("Data kriteria belum lengkap.", "danger")
        else:
            db.session.add(item)
            db.session.commit()
            flash("Kriteria berhasil ditambahkan.", "success")
        return redirect(url_for("admin.kriteria_list", kelas=item.kelas_tujuan))

    kelas = request.args.get("kelas", "")
    query = KriteriaPenilaian.query
    if kelas:
        query = query.filter_by(kelas_tujuan=kelas)
    items = query.order_by(KriteriaPenilaian.kelas_tujuan, KriteriaPenilaian.id).all()
    total_bobot_per_kelas = {}
    for value, _label in KELAS_CHOICES:
        total_bobot_per_kelas[value] = (
            db.session.query(db.func.coalesce(db.func.sum(KriteriaPenilaian.bobot), 0))
            .filter_by(kelas_tujuan=value, is_active=True)
            .scalar()
        )
    return render_template(
        "admin/kriteria_list.html",
        items=items,
        kelas=kelas,
        kelas_choices=KELAS_CHOICES,
        total_bobot_per_kelas=total_bobot_per_kelas,
    )


@admin_bp.route("/kriteria/<int:kriteria_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def kriteria_toggle(kriteria_id):
    item = KriteriaPenilaian.query.get_or_404(kriteria_id)
    item.is_active = not item.is_active
    db.session.commit()
    flash("Status kriteria diperbarui.", "success")
    return redirect(url_for("admin.kriteria_list", kelas=item.kelas_tujuan))


def _murid_hasil_context():
    gelombang = normalisasi_gelombang(
        request.args.get("gelombang", get_gelombang_aktif())
    )
    tahun = get_tahun_ajaran()
    items = (
        _filter_tahun_gelombang(
            Murid.query.join(User, Murid.user_id == User.id), tahun, gelombang
        )
        .order_by(User.nama_lengkap.asc())
        .all()
    )
    bobot_tes, bobot_ww, bobot_psiko = get_bobot_penilaian()
    return {
        "items": items,
        "kelas_choices": KELAS_CHOICES,
        "kelas_keys": [k for k, _ in KELAS_CHOICES],
        "gelombang": gelombang,
        "daftar_gelombang": get_daftar_gelombang(),
        "tahun_ajaran": tahun,
        "bobot_tes": bobot_tes,
        "bobot_wawancara": bobot_ww,
        "bobot_psikotes": bobot_psiko,
        "bobot_kelas": get_semua_bobot_kelas(),
    }


@admin_bp.route("/hasil")
@login_required
@role_required("admin")
def hasil():
    """Alias ke laporan gabungan (rekomendasi kelas)."""
    gelombang = request.args.get("gelombang")
    if gelombang:
        return redirect(url_for("admin.hasil_gabungan", gelombang=gelombang))
    return redirect(url_for("admin.hasil_gabungan"))


@admin_bp.route("/tes-kunci", methods=["GET", "POST"])
@login_required
@role_required("admin")
def tes_kunci():
    """Kelola password masuk & keluar soal per gelombang (reguler / susulan)."""
    tahun = get_tahun_ajaran()
    gelombang = normalisasi_gelombang(
        request.values.get("gelombang") or get_gelombang_aktif()
    )
    jenis = request.values.get("jenis") or "reguler"
    if jenis not in ("reguler", "susulan"):
        jenis = "reguler"
    kunci = get_kunci_tes(tahun, gelombang, jenis)

    if request.method == "POST":
        aksi = request.form.get("aksi") or "simpan"
        gelombang = normalisasi_gelombang(
            request.form.get("gelombang") or gelombang
        )
        jenis = request.form.get("jenis") or jenis
        if jenis not in ("reguler", "susulan"):
            jenis = "reguler"
        kunci = get_kunci_tes(tahun, gelombang, jenis)
        if aksi == "simpan":
            masuk = (request.form.get("password_masuk") or "").strip()
            keluar = (request.form.get("password_keluar") or "").strip()
            if not masuk or not keluar:
                flash("Password masuk dan keluar wajib diisi.", "danger")
            else:
                kunci.password_masuk = masuk
                kunci.password_keluar = keluar
                kunci.is_aktif = request.form.get("is_aktif") == "1"
                db.session.commit()
                flash(
                    f"Password {kunci.jenis_label} {label_gelombang(gelombang)} disimpan.",
                    "success",
                )
        return redirect(
            url_for("admin.tes_kunci", gelombang=gelombang, jenis=jenis)
        )

    semua = (
        KunciTesGelombang.query.filter_by(tahun_ajaran=tahun)
        .order_by(KunciTesGelombang.gelombang, KunciTesGelombang.jenis)
        .all()
    )
    return render_template(
        "admin/tes_kunci.html",
        kunci=kunci,
        semua=semua,
        gelombang=gelombang,
        jenis=jenis,
        daftar_gelombang=get_daftar_gelombang(),
        tahun_ajaran=tahun,
    )


@admin_bp.route("/tes-susulan", methods=["GET", "POST"])
@login_required
@role_required("admin")
def tes_susulan():
    """Daftar murid berhalangan hadir & penjadwalan tes susulan."""
    from datetime import datetime as dt

    tahun = get_tahun_ajaran()
    gelombang = normalisasi_gelombang(
        request.values.get("gelombang") or get_gelombang_aktif()
    )
    kunci = get_kunci_tes(tahun, gelombang, "susulan")

    if request.method == "POST":
        aksi = request.form.get("aksi")
        if aksi == "buka_kunci":
            masuk = (request.form.get("password_masuk") or "").strip() or kunci.password_masuk
            keluar = (request.form.get("password_keluar") or "").strip() or kunci.password_keluar
            kunci.password_masuk = masuk
            kunci.password_keluar = keluar
            kunci.is_aktif = request.form.get("is_aktif") == "1"
            db.session.commit()
            flash(
                f"Pengaturan tes susulan {label_gelombang(gelombang)} disimpan.",
                "success",
            )
            return redirect(url_for("admin.tes_susulan", gelombang=gelombang))

        murid_id = request.form.get("murid_id", type=int)
        murid = Murid.query.get_or_404(murid_id) if murid_id else None
        if not murid:
            flash("Murid tidak ditemukan.", "danger")
            return redirect(url_for("admin.tes_susulan", gelombang=gelombang))

        if aksi == "tandai":
            alasan = (request.form.get("alasan_susulan") or "").strip() or None
            tgl_raw = (request.form.get("tanggal_susulan") or "").strip()
            tgl = None
            if tgl_raw:
                try:
                    tgl = dt.strptime(tgl_raw, "%Y-%m-%d").date()
                except ValueError:
                    flash("Format tanggal susulan tidak valid.", "danger")
                    return redirect(url_for("admin.tes_susulan", gelombang=gelombang))
            murid.is_tes_susulan = True
            murid.alasan_susulan = alasan
            murid.tanggal_susulan = tgl
            if murid.status in ("terdaftar", "draft", "tes_selesai"):
                # Belum selesai penuh / belum tes → status menunggu susulan
                if not murid.tes_tertulis_selesai():
                    murid.status = "tes_susulan"
            db.session.commit()
            flash(
                f"{murid.user.nama_lengkap} ditandai tes susulan.",
                "success",
            )
        elif aksi == "batal":
            murid.is_tes_susulan = False
            murid.alasan_susulan = None
            murid.tanggal_susulan = None
            if murid.status == "tes_susulan":
                murid.status = "terdaftar"
            db.session.commit()
            flash(f"Status susulan {murid.user.nama_lengkap} dibatalkan.", "info")

        return redirect(url_for("admin.tes_susulan", gelombang=gelombang))

    base = _filter_tahun_gelombang(Murid.query.join(User, Murid.user_id == User.id), tahun, gelombang)
    susulan = (
        base.filter(Murid.is_tes_susulan.is_(True))
        .order_by(User.nama_lengkap)
        .all()
    )
    kandidat = (
        base.filter(
            or_(Murid.is_tes_susulan.is_(False), Murid.is_tes_susulan.is_(None)),
            Murid.status.in_(["terdaftar", "draft", "tes_susulan", "tes_selesai"]),
        )
        .order_by(User.nama_lengkap)
        .all()
    )
    # Hanya yang belum selesai penuh sebagai kandidat utama
    kandidat = [m for m in kandidat if not m.tes_tertulis_selesai()]
    return render_template(
        "admin/tes_susulan.html",
        items=susulan,
        kandidat=kandidat,
        kunci=kunci,
        gelombang=gelombang,
        daftar_gelombang=get_daftar_gelombang(),
        tahun_ajaran=tahun,
    )


@admin_bp.route("/tes-monitoring")
@login_required
@role_required("admin")
def tes_monitoring():
    """Monitor pengerjaan soal murid per gelombang."""
    tahun = get_tahun_ajaran()
    gelombang = normalisasi_gelombang(
        request.args.get("gelombang") or get_gelombang_aktif()
    )
    kelas = request.args.get("kelas") or ""
    status = request.args.get("status") or ""
    jalur = request.args.get("jalur") or ""

    query = (
        SesiTesMurid.query.join(Murid)
        .filter(
            (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)),
            Murid.gelombang == gelombang,
        )
    )
    if kelas in dict(KELAS_CHOICES):
        query = query.filter(SesiTesMurid.kelas_tujuan == kelas)
    if status in ("aktif", "selesai"):
        query = query.filter(SesiTesMurid.status == status)
    if jalur == "susulan":
        query = query.filter(Murid.is_tes_susulan.is_(True))
    elif jalur == "reguler":
        query = query.filter(
            or_(Murid.is_tes_susulan.is_(False), Murid.is_tes_susulan.is_(None))
        )

    items = query.order_by(
        SesiTesMurid.last_seen_at.desc(), SesiTesMurid.id.desc()
    ).all()

    # Lengkapi progress terjawab
    rows = []
    for s in items:
        jumlah_soal = SoalTes.query.filter_by(
            kelas_tujuan=s.kelas_tujuan, is_active=True
        ).count()
        terjawab = s.murid.jumlah_jawaban_kelas(s.kelas_tujuan) if s.murid else 0
        rows.append(
            {
                "sesi": s,
                "murid": s.murid,
                "jumlah_soal": jumlah_soal,
                "terjawab": terjawab,
            }
        )

    kunci = get_kunci_tes(tahun, gelombang, "reguler")
    kunci_susulan = get_kunci_tes(tahun, gelombang, "susulan")
    ringkas = {
        "aktif": SesiTesMurid.query.join(Murid)
        .filter(
            (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)),
            Murid.gelombang == gelombang,
            SesiTesMurid.status == "aktif",
        )
        .count(),
        "selesai": SesiTesMurid.query.join(Murid)
        .filter(
            (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)),
            Murid.gelombang == gelombang,
            SesiTesMurid.status == "selesai",
        )
        .count(),
        "online": sum(1 for r in rows if r["sesi"].online),
        "susulan": Murid.query.filter(
            (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)),
            Murid.gelombang == gelombang,
            Murid.is_tes_susulan.is_(True),
        ).count(),
    }
    return render_template(
        "admin/tes_monitoring.html",
        rows=rows,
        ringkas=ringkas,
        kunci=kunci,
        kunci_susulan=kunci_susulan,
        gelombang=gelombang,
        kelas=kelas,
        status=status,
        jalur=jalur,
        daftar_gelombang=get_daftar_gelombang(),
        kelas_choices=KELAS_CHOICES,
        tahun_ajaran=tahun,
    )


@admin_bp.route("/tes-monitoring/<int:sesi_id>/reset", methods=["POST"])
@login_required
@role_required("admin")
def tes_monitoring_reset(sesi_id):
    """Reset sesi agar murid bisa lanjut; jawaban tersimpan tidak dihapus."""
    from datetime import datetime

    sesi = SesiTesMurid.query.get_or_404(sesi_id)
    sesi.status = "aktif"
    sesi.selesai_at = None
    sesi.butuh_password_keluar = False
    sesi.reset_count = (sesi.reset_count or 0) + 1
    sesi.last_seen_at = datetime.utcnow()
    catatan = (sesi.catatan_pelanggaran or "").strip()
    baris = (
        f"{datetime.utcnow().isoformat(timespec='seconds')}Z · "
        f"RESET oleh admin {current_user.username} (jawaban tetap)"
    )
    sesi.catatan_pelanggaran = (catatan + "\n" + baris).strip()[-2000:]
    db.session.commit()
    flash(
        f"Sesi {sesi.kelas_label} murid "
        f"{sesi.murid.user.nama_lengkap if sesi.murid and sesi.murid.user else sesi.murid_id} "
        f"direset. Jawaban yang sudah diisi tetap ada.",
        "success",
    )
    gelombang = normalisasi_gelombang(
        request.form.get("gelombang")
        or (sesi.murid.gelombang if sesi.murid else get_gelombang_aktif())
    )
    return redirect(url_for("admin.tes_monitoring", gelombang=gelombang))


@admin_bp.route("/tes-cetak-hasil")
@login_required
@role_required("admin")
def tes_cetak_hasil():
    """Cetak hasil tes tertulis seluruh peserta per gelombang."""
    ctx = _murid_hasil_context()
    return render_template("admin/tes_cetak_hasil.html", **ctx)


@admin_bp.route("/analisis-soal")
@login_required
@role_required("admin")
def analisis_soal():
    """Analisis tingkat kebenaran & sebaran jawaban per soal + rekap per kelas."""
    tahun = get_tahun_ajaran()
    gelombang = normalisasi_gelombang(
        request.args.get("gelombang") or get_gelombang_aktif()
    )
    kelas = request.args.get("kelas") or ""
    rows = analisis_soal_tes(tahun, gelombang, kelas)
    rekap_kelas = rekap_analisis_soal_per_kelas(rows)
    return render_template(
        "admin/analisis_soal.html",
        rows=rows,
        rekap_kelas=rekap_kelas,
        gelombang=gelombang,
        kelas=kelas,
        daftar_gelombang=get_daftar_gelombang(),
        kelas_choices=KELAS_CHOICES,
        tahun_ajaran=tahun,
        kriteria={
            "min_jawab": ANALISIS_MIN_JAWAB,
            "p_min": ANALISIS_P_MIN,
            "p_max": ANALISIS_P_MAX,
        },
    )


@admin_bp.route("/kisi-kisi", methods=["GET", "POST"])
@login_required
@role_required("admin")
def kisi_kisi():
    """Kisi-kisi soal: kelola tampilan untuk ortu/murid + cetak."""
    kelas = request.args.get("kelas") or request.form.get("kelas") or ""
    if request.method == "POST":
        aksi = request.form.get("aksi")
        if aksi == "publikasi":
            set_setting(
                "tampilkan_kisi_kisi",
                "1" if request.form.get("tampilkan_kisi_kisi") == "1" else "0",
                "Tampilkan kisi-kisi ke ortu & murid",
            )
            flash("Pengaturan publikasi kisi-kisi disimpan.", "success")
            return redirect(url_for("admin.kisi_kisi", kelas=kelas or None))
        if aksi == "update_kisi":
            soal_id = request.form.get("soal_id", type=int)
            soal = SoalTes.query.get_or_404(soal_id)
            soal.materi = (request.form.get("materi") or "").strip() or None
            soal.indikator = (request.form.get("indikator") or "").strip() or None
            soal.level_kognitif = (
                request.form.get("level_kognitif") or ""
            ).strip() or None
            db.session.commit()
            flash(f"Kisi-kisi soal #{soal.id} diperbarui.", "success")
            return redirect(
                url_for("admin.kisi_kisi", kelas=soal.kelas_tujuan)
            )

    items = daftar_kisi_kisi(kelas)
    return render_template(
        "admin/kisi_kisi.html",
        items=items,
        kelas=kelas,
        kelas_choices=KELAS_CHOICES,
        tampilkan=tampilkan_kisi_kisi(),
    )


@admin_bp.route("/hasil/tes-tertulis")
@login_required
@role_required("admin")
def hasil_tes_tertulis():
    ctx = _murid_hasil_context()
    return render_template("admin/hasil_tes_tertulis.html", **ctx)


@admin_bp.route("/hasil/wawancara")
@login_required
@role_required("admin")
def hasil_wawancara():
    ctx = _murid_hasil_context()
    return render_template("admin/hasil_wawancara.html", **ctx)


@admin_bp.route("/hasil/gabungan")
@login_required
@role_required("admin")
def hasil_gabungan():
    ctx = _murid_hasil_context()
    return render_template("admin/hasil_gabungan.html", **ctx)


@admin_bp.route("/penempatan", methods=["GET", "POST"])
@login_required
@role_required("admin")
def penempatan_akhir():
    """Laporan akhir penempatan: usulan skor+kuota → ACC admin → pindah kelas."""
    from datetime import datetime

    tahun = get_tahun_ajaran()
    gelombang = request.values.get("gelombang") or ""
    if gelombang:
        gelombang = normalisasi_gelombang(gelombang)

    if request.method == "POST":
        aksi = request.form.get("aksi")
        gelombang_form = request.form.get("gelombang") or gelombang
        if gelombang_form:
            gelombang_form = normalisasi_gelombang(gelombang_form)

        if aksi == "generate":
            hasil = alokasi_penempatan_kuota(
                tahun, gelombang_form or None
            )
            flash(
                f"Usulan penempatan dibuat: {hasil['diusulkan']} murid. "
                f"Dilewati (sudah ACC/belum skor): {hasil['dilewati']}. "
                f"Tanpa slot kuota: {hasil['tanpa_slot']}.",
                "success" if hasil["diusulkan"] else "warning",
            )
            return redirect(
                url_for(
                    "admin.penempatan_akhir",
                    gelombang=gelombang_form or None,
                )
            )

        murid_id = request.form.get("murid_id", type=int)
        murid = Murid.query.get_or_404(murid_id) if murid_id else None

        if aksi == "acc" and murid:
            kelas = murid.kelas_usulan
            if not kelas or kelas not in dict(KELAS_CHOICES):
                flash("Belum ada usulan kelas. Generate usulan dulu.", "danger")
            else:
                kuota = get_kuota_kelas(kelas)
                if kuota > 0 and murid.kelas_ditetapkan != kelas:
                    terisi = hitung_terisi_kelas(tahun).get(kelas, 0)
                    if terisi >= kuota and not request.form.get("paksa_kuota"):
                        flash(
                            f"Kuota {dict(KELAS_CHOICES)[kelas]} penuh. "
                            "Centang paksa jika tetap ACC.",
                            "warning",
                        )
                        return redirect(
                            url_for(
                                "admin.penempatan_akhir",
                                gelombang=gelombang_form or None,
                            )
                        )
                murid.kelas_ditetapkan = kelas
                murid.acc_penempatan = True
                murid.acc_at = datetime.utcnow()
                murid.status = "ditetapkan"
                if not (murid.catatan_admin or "").strip():
                    murid.catatan_admin = (
                        f"ACC penempatan ke {dict(KELAS_CHOICES)[kelas]} "
                        f"(skor {murid.skor_penempatan})."
                    )
                db.session.commit()
                flash(
                    f"ACC: {murid.user.nama_lengkap} → {dict(KELAS_CHOICES)[kelas]}.",
                    "success",
                )

        elif aksi == "acc_semua":
            query = Murid.query.filter(
                (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)),
                Murid.kelas_usulan.isnot(None),
                Murid.acc_penempatan.is_(False),
            )
            if gelombang_form:
                query = query.filter(Murid.gelombang == gelombang_form)
            count = 0
            skip = 0
            for m in query.all():
                kelas = m.kelas_usulan
                if kelas not in dict(KELAS_CHOICES):
                    skip += 1
                    continue
                kuota = get_kuota_kelas(kelas)
                if kuota > 0:
                    terisi = hitung_terisi_kelas(tahun).get(kelas, 0)
                    if terisi >= kuota:
                        skip += 1
                        continue
                m.kelas_ditetapkan = kelas
                m.acc_penempatan = True
                m.acc_at = datetime.utcnow()
                m.status = "ditetapkan"
                count += 1
                db.session.flush()
            db.session.commit()
            flash(
                f"ACC massal: {count} murid ditetapkan. Dilewati (kuota/data): {skip}.",
                "success" if count else "warning",
            )

        elif aksi == "pindah" and murid:
            kelas_baru = request.form.get("kelas_baru")
            paksa = request.form.get("paksa_kuota") == "1"
            if kelas_baru not in dict(KELAS_CHOICES):
                flash("Kelas tujuan tidak valid.", "danger")
            else:
                kuota = get_kuota_kelas(kelas_baru)
                if kuota > 0 and murid.kelas_ditetapkan != kelas_baru:
                    terisi = hitung_terisi_kelas(tahun).get(kelas_baru, 0)
                    if terisi >= kuota and not paksa:
                        flash(
                            f"Kuota {dict(KELAS_CHOICES)[kelas_baru]} penuh. "
                            "Centang paksa untuk memindahkan.",
                            "warning",
                        )
                        return redirect(
                            url_for(
                                "admin.penempatan_akhir",
                                gelombang=gelombang_form or None,
                            )
                        )
                lama = murid.kelas_ditetapkan
                murid.kelas_ditetapkan = kelas_baru
                murid.kelas_usulan = kelas_baru
                murid.acc_penempatan = True
                murid.acc_at = datetime.utcnow()
                murid.status = "ditetapkan"
                catatan = (murid.catatan_admin or "").strip()
                baris = (
                    f"Dipindah admin dari "
                    f"{dict(KELAS_CHOICES).get(lama, lama or '-')} "
                    f"ke {dict(KELAS_CHOICES)[kelas_baru]}."
                )
                murid.catatan_admin = (catatan + "\n" + baris).strip() if catatan else baris
                db.session.commit()
                flash(
                    f"{murid.user.nama_lengkap} dipindah ke "
                    f"{dict(KELAS_CHOICES)[kelas_baru]}.",
                    "success",
                )

        return redirect(
            url_for("admin.penempatan_akhir", gelombang=gelombang_form or None)
        )

    query = (
        Murid.query.join(User, Murid.user_id == User.id)
        .filter((Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)))
    )
    if gelombang:
        query = query.filter(Murid.gelombang == gelombang)
    items = query.order_by(
        Murid.gelombang.asc(),
        Murid.skor_penempatan.desc(),
        User.nama_lengkap.asc(),
    ).all()

    terisi = hitung_terisi_kelas(tahun)
    kuota = get_semua_kuota_kelas()
    kuota_info = {
        kode: {
            "kuota": kuota.get(kode, 0),
            "terisi": terisi.get(kode, 0),
            "sisa": (
                None
                if kuota.get(kode, 0) <= 0
                else max(kuota.get(kode, 0) - terisi.get(kode, 0), 0)
            ),
            "usulan": sum(1 for m in items if m.kelas_usulan == kode and not m.acc_penempatan),
        }
        for kode, _ in KELAS_CHOICES
    }
    ringkas = {
        "total": len(items),
        "usulan": sum(1 for m in items if m.kelas_usulan and not m.acc_penempatan),
        "acc": sum(1 for m in items if m.acc_penempatan or m.status == "ditetapkan"),
        "belum": sum(
            1
            for m in items
            if not m.kelas_usulan and not m.acc_penempatan and m.status != "ditetapkan"
        ),
    }
    return render_template(
        "admin/penempatan_akhir.html",
        items=items,
        kuota_info=kuota_info,
        ringkas=ringkas,
        gelombang=gelombang,
        daftar_gelombang=get_daftar_gelombang(),
        kelas_choices=KELAS_CHOICES,
        tahun_ajaran=tahun,
    )


@admin_bp.route("/psikotes", methods=["GET", "POST"])
@login_required
@role_required("admin")
def psikotes_list():
    """Input skor psikotes murid (masuk ke nilai gabungan)."""
    gelombang = normalisasi_gelombang(
        request.args.get("gelombang")
        or request.form.get("gelombang")
        or get_gelombang_aktif()
    )
    tahun = get_tahun_ajaran()
    items = (
        _filter_tahun_gelombang(
            Murid.query.join(User, Murid.user_id == User.id), tahun, gelombang
        )
        .order_by(User.nama_lengkap.asc())
        .all()
    )
    # Data lama tanpa gelombang: tampilkan agar bisa diisi / di-assign
    menampilkan_belum_gelombang = False
    if not items:
        items = (
            Murid.query.join(User, Murid.user_id == User.id)
            .filter((Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)))
            .filter(Murid.gelombang.is_(None) | (Murid.gelombang == ""))
            .order_by(User.nama_lengkap.asc())
            .all()
        )
        menampilkan_belum_gelombang = bool(items)

    if request.method == "POST":
        updated = 0
        for murid in items:
            raw = (request.form.get(f"nilai_{murid.id}") or "").strip()
            catatan = (request.form.get(f"catatan_{murid.id}") or "").strip() or None
            if raw == "":
                if murid.nilai_psikotes is not None or murid.catatan_psikotes:
                    # biarkan kosong = tidak diubah kecuali ada flag clear? keep previous
                    if request.form.get(f"clear_{murid.id}"):
                        murid.nilai_psikotes = None
                        murid.catatan_psikotes = None
                        updated += 1
                continue
            try:
                nilai = float(raw.replace(",", "."))
            except ValueError:
                flash(
                    f"Nilai psikotes tidak valid untuk {murid.user.nama_lengkap}.",
                    "danger",
                )
                continue
            # Form manual memakai skala 1–100 (hasil setelah konversi blanko)
            if nilai < PSIKOTES_SKALA_MIN or nilai > PSIKOTES_SKALA_MAX:
                flash(
                    f"Nilai psikotes {murid.user.nama_lengkap} harus "
                    f"{PSIKOTES_SKALA_MIN}–{PSIKOTES_SKALA_MAX}.",
                    "danger",
                )
                continue
            murid.nilai_psikotes = round(nilai, 2)
            murid.catatan_psikotes = catatan
            if not murid.gelombang:
                murid.gelombang = gelombang
            if not murid.tahun_ajaran:
                murid.tahun_ajaran = tahun
            updated += 1
        db.session.commit()
        flash(f"{updated} skor psikotes disimpan.", "success")
        return redirect(url_for("admin.psikotes_list", gelombang=gelombang))

    bobot_tes, bobot_ww, bobot_psiko = get_bobot_penilaian()
    return render_template(
        "admin/psikotes_list.html",
        items=items,
        gelombang=gelombang,
        daftar_gelombang=get_daftar_gelombang(),
        tahun_ajaran=tahun,
        bobot_tes=bobot_tes,
        bobot_wawancara=bobot_ww,
        bobot_psikotes=bobot_psiko,
        menampilkan_belum_gelombang=menampilkan_belum_gelombang,
    )


@admin_bp.route("/psikotes/blanko/unduh")
@login_required
@role_required("admin")
def unduh_blanko_psikotes():
    gelombang = normalisasi_gelombang(
        request.args.get("gelombang") or get_gelombang_aktif()
    )
    tahun = get_tahun_ajaran()
    content = buat_blanko_psikotes_xlsx(gelombang, tahun)
    return send_file(
        io.BytesIO(content),
        as_attachment=True,
        download_name=f"blanko_psikotes_g{gelombang}_{tahun.replace('/', '-')}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@admin_bp.route("/psikotes/upload", methods=["POST"])
@login_required
@role_required("admin")
def upload_psikotes():
    gelombang = normalisasi_gelombang(
        request.form.get("gelombang") or get_gelombang_aktif()
    )
    file = request.files.get("psikotes_file")
    if not file or not file.filename:
        flash("Pilih file skor psikotes (.xlsx / .csv).", "danger")
        return redirect(url_for("admin.psikotes_list", gelombang=gelombang))

    rows, error = baca_psikotes_file(file)
    if error:
        flash(error, "danger")
        return redirect(url_for("admin.psikotes_list", gelombang=gelombang))
    if not rows:
        flash("Tidak ada baris skor yang bisa diimpor.", "warning")
        return redirect(url_for("admin.psikotes_list", gelombang=gelombang))

    hasil = impor_skor_psikotes(rows, gelombang)
    parts = []
    if hasil.get("sukses"):
        parts.append(
            f"{hasil['sukses']} skor dikonversi {PSIKOTES_MIN}–{PSIKOTES_MAX} "
            f"→ skala {PSIKOTES_SKALA_MIN}–{PSIKOTES_SKALA_MAX}"
        )
    if hasil.get("assigned"):
        parts.append(f"{hasil['assigned']} murid di-assign ke {label_gelombang(gelombang)}")
    if hasil.get("dilewati"):
        parts.append(f"{hasil['dilewati']} dilewati")
    if parts:
        flash("Upload psikotes: " + ", ".join(parts) + ".", "success")
    if hasil["gagal"]:
        preview = " | ".join(hasil["gagal"][:3])
        more = f" (+{len(hasil['gagal']) - 3} lainnya)" if len(hasil["gagal"]) > 3 else ""
        flash(f"{len(hasil['gagal'])} baris gagal: {preview}{more}", "warning")
    if not parts and not hasil["gagal"]:
        flash("Tidak ada data skor yang diproses.", "info")
    return redirect(url_for("admin.psikotes_list", gelombang=gelombang))


@admin_bp.route("/laporan/murid/<int:murid_id>")
@login_required
@role_required("admin")
def laporan_individu(murid_id):
    murid = Murid.query.get_or_404(murid_id)
    bobot_tes, bobot_ww, bobot_psiko = get_bobot_penilaian()
    return render_template(
        "admin/laporan_individu.html",
        murid=murid,
        kelas_choices=KELAS_CHOICES,
        nilai_per_kelas=murid.nilai_wawancara_per_kelas(),
        nilai_tes=murid.nilai_tes_per_kelas(),
        nilai_gabungan=murid.skor_gabungan_per_kelas(),
        ringkas_tes=murid.ringkas_tes_tertulis(),
        bobot_tes=bobot_tes,
        bobot_wawancara=bobot_ww,
        bobot_psikotes=bobot_psiko,
        bobot_kelas=get_semua_bobot_kelas(),
    )



CETAK_AKUN_ROLES = (
    ("guru", "Guru Penguji"),
    ("guru_soal", "Guru Pembuat Soal"),
    ("murid", "Murid"),
    ("orang_tua", "Orang Tua Murid"),
)


@admin_bp.route("/pengguna")
@login_required
@role_required("admin")
def pengguna_list():
    """Kelola akun admin, guru penguji, dan murid."""
    role = (request.args.get("role") or "").strip().lower()
    q = (request.args.get("q") or "").strip()
    status = (request.args.get("status") or "").strip()

    query = User.query
    if role in dict(ROLE_CHOICES):
        query = query.filter_by(role=role)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                User.username.ilike(like),
                User.nama_lengkap.ilike(like),
            )
        )
    if status == "aktif":
        query = query.filter_by(is_active_user=True)
    elif status == "nonaktif":
        query = query.filter_by(is_active_user=False)

    items = query.order_by(User.role.asc(), User.nama_lengkap.asc()).all()
    ringkas = {
        "admin": User.query.filter_by(role="admin").count(),
        "guru": User.query.filter_by(role="guru").count(),
        "guru_soal": User.query.filter_by(role="guru_soal").count(),
        "murid": User.query.filter_by(role="murid").count(),
        "orang_tua": User.query.filter_by(role="orang_tua").count(),
    }
    return render_template(
        "admin/pengguna_list.html",
        items=items,
        role=role,
        q=q,
        status=status,
        ringkas=ringkas,
        role_choices=ROLE_CHOICES,
        kelas_choices=KELAS_CHOICES,
        daftar_gelombang=get_daftar_gelombang(),
        tahun_ajaran=get_tahun_ajaran(),
        gelombang_aktif=get_gelombang_aktif(),
        default_passwords={
            "admin": DEFAULT_PASSWORD_ADMIN,
            "guru": DEFAULT_PASSWORD_GURU,
            "guru_soal": DEFAULT_PASSWORD_GURU,
            "murid": DEFAULT_PASSWORD_MURID,
            "orang_tua": DEFAULT_PASSWORD_ORTU,
        },
    )


@admin_bp.route("/pengguna/cetak-akun")
@login_required
@role_required("admin")
def pengguna_cetak_akun():
    """Tampilkan daftar username + password default per level untuk dicetak PDF."""
    role = (request.args.get("role") or "").strip().lower()
    gelombang = normalisasi_gelombang(request.args.get("gelombang", ""))
    tahun = get_tahun_ajaran()
    password_default = _password_default_role(role) if role else ""

    rows = []
    if role in dict(CETAK_AKUN_ROLES):
        if role in ("guru", "guru_soal"):
            if role == "guru_soal":
                users = (
                    User.query.filter(
                        db.or_(
                            User.role == "guru_soal",
                            db.and_(User.role == "guru", User.juga_pembuat_soal.is_(True)),
                        )
                    )
                    .order_by(User.kelas_penguji.asc(), User.nama_lengkap.asc())
                    .all()
                )
            else:
                users = (
                    User.query.filter_by(role=role)
                    .order_by(User.kelas_penguji.asc(), User.nama_lengkap.asc())
                    .all()
                )
            for u in users:
                detail = u.kelas_label
                if role == "guru_soal":
                    detail = f"Kelas soal: {u.kelas_label}"
                    if u.role == "guru":
                        detail += " · gabung penguji"
                elif role == "guru":
                    detail = f"Kelas penguji: {u.kelas_label}"
                    if u.juga_pembuat_soal:
                        detail += " · juga pembuat soal"
                rows.append(
                    {
                        "nama": u.nama_lengkap,
                        "username": u.username,
                        "password": password_default,
                        "detail": detail,
                        "status": "Aktif" if u.is_active_user else "Nonaktif",
                    }
                )
        elif role == "murid":
            query = Murid.query.join(User, Murid.user_id == User.id).filter(
                User.role == "murid"
            )
            query = _filter_tahun_gelombang(query, tahun, gelombang or None)
            murids = query.order_by(User.nama_lengkap.asc()).all()
            for m in murids:
                rows.append(
                    {
                        "nama": m.user.nama_lengkap if m.user else "-",
                        "username": m.user.username if m.user else "-",
                        "password": password_default,
                        "detail": f"NISN {m.nisn} · {label_gelombang(m.gelombang)}",
                        "status": "Aktif"
                        if (m.user and m.user.is_active_user)
                        else "Nonaktif",
                    }
                )
        elif role == "orang_tua":
            query = (
                User.query.join(Murid, Murid.ortu_user_id == User.id)
                .filter(User.role == "orang_tua")
            )
            if tahun:
                query = query.filter(
                    (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None))
                )
            if gelombang:
                query = query.filter(Murid.gelombang == gelombang)
            users = query.order_by(User.nama_lengkap.asc()).all()
            for u in users:
                anak = u.anak_asuh
                if anak and anak.user:
                    detail = (
                        f"Anak: {anak.user.nama_lengkap} · NISN {anak.nisn} · "
                        f"{label_gelombang(anak.gelombang)}"
                    )
                else:
                    detail = "Belum terhubung ke anak"
                rows.append(
                    {
                        "nama": u.nama_lengkap,
                        "username": u.username,
                        "password": password_default,
                        "detail": detail,
                        "status": "Aktif" if u.is_active_user else "Nonaktif",
                    }
                )

    return render_template(
        "admin/pengguna_cetak_akun.html",
        role=role,
        gelombang=gelombang,
        rows=rows,
        cetak_roles=CETAK_AKUN_ROLES,
        daftar_gelombang=get_daftar_gelombang(),
        tahun_ajaran=tahun,
        password_default=password_default,
        role_label=dict(CETAK_AKUN_ROLES).get(role, ""),
    )


@admin_bp.route("/pengguna/tambah", methods=["POST"])
@login_required
@role_required("admin")
def pengguna_tambah():
    role = (request.form.get("role") or "").strip().lower()
    nama = (request.form.get("nama_lengkap") or "").strip()
    username = _normalize_username(request.form.get("username", ""))
    password = (request.form.get("password") or "").strip() or _password_default_role(role)
    kelas_penguji = request.form.get("kelas_penguji") or None

    if role not in dict(ROLE_CHOICES):
        flash("Peran pengguna tidak valid.", "danger")
        return redirect(url_for("admin.pengguna_list"))
    if role == "orang_tua":
        flash(
            "Akun orang tua dibuat otomatis dari Data Murid "
            "(tombol Sinkronkan Akun Orang Tua), bukan ditambah manual.",
            "warning",
        )
        return redirect(url_for("admin.pengguna_list", role="orang_tua"))
    if not nama:
        flash("Nama lengkap wajib diisi.", "danger")
        return redirect(url_for("admin.pengguna_list", role=role))
    if not username:
        username = buat_username_dari_nama(nama)
    if User.query.filter_by(username=username).first():
        flash("Username sudah dipakai.", "danger")
        return redirect(url_for("admin.pengguna_list", role=role))
    if role in ("guru", "guru_soal") and kelas_penguji not in dict(KELAS_CHOICES):
        flash(
            "Kelas wajib dipilih untuk guru penguji / guru pembuat soal.",
            "danger",
        )
        return redirect(url_for("admin.pengguna_list", role=role))

    try:
        user = User(
            username=username,
            nama_lengkap=nama,
            email=None,
            role=role,
            kelas_penguji=kelas_penguji if role in ("guru", "guru_soal") else None,
            is_active_user=True,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == "murid":
            nisn = (request.form.get("nisn") or "").strip()
            if not nisn:
                nisn = f"TMP{user.id:06d}"
            if Murid.query.filter_by(nisn=nisn).first():
                db.session.rollback()
                flash("NISN sudah dipakai.", "danger")
                return redirect(url_for("admin.pengguna_list", role=role))
            gelombang = normalisasi_gelombang(
                request.form.get("gelombang") or get_gelombang_aktif()
            )
            pilihan = request.form.get("pilihan_kelas_1") or "reguler"
            if pilihan not in dict(KELAS_CHOICES):
                pilihan = "reguler"
            murid = Murid(
                user_id=user.id,
                nisn=nisn,
                tahun_ajaran=get_tahun_ajaran(),
                gelombang=gelombang,
                jenis_kelamin=(request.form.get("jenis_kelamin") or "").strip() or None,
                asal_sekolah=(request.form.get("asal_sekolah") or "").strip() or None,
                pilihan_kelas_1=pilihan,
                status="terdaftar",
            )
            db.session.add(murid)
            db.session.flush()
            pastikan_akun_ortu(murid, commit=False)

        db.session.commit()
        if role == "murid":
            tambah_gelombang_ke_daftar(
                normalisasi_gelombang(
                    request.form.get("gelombang") or get_gelombang_aktif()
                )
            )
        flash(
            f"Akun {dict(ROLE_CHOICES)[role]} '{username}' berhasil ditambahkan. "
            f"Password: {password}",
            "success",
        )
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        flash(f"Gagal menambah pengguna: {exc}", "danger")

    return redirect(url_for("admin.pengguna_list", role=role))


@admin_bp.route("/pengguna/<int:user_id>/username", methods=["POST"])
@login_required
@role_required("admin")
def pengguna_ganti_username(user_id):
    user = User.query.get_or_404(user_id)
    username_baru = _normalize_username(request.form.get("username_baru", ""))
    role_filter = request.form.get("role_filter") or user.role

    if not username_baru:
        flash("Username baru tidak boleh kosong.", "danger")
        return redirect(url_for("admin.pengguna_list", role=role_filter))
    if username_baru == user.username:
        flash("Username tidak berubah.", "info")
        return redirect(url_for("admin.pengguna_list", role=role_filter))
    bentrok = User.query.filter(
        User.username == username_baru, User.id != user.id
    ).first()
    if bentrok:
        flash("Username sudah dipakai pengguna lain.", "danger")
        return redirect(url_for("admin.pengguna_list", role=role_filter))

    lama = user.username
    user.username = username_baru
    db.session.commit()
    flash(f"Username '{lama}' diganti menjadi '{username_baru}'.", "success")
    return redirect(url_for("admin.pengguna_list", role=role_filter))


@admin_bp.route("/pengguna/<int:user_id>/reset-password", methods=["POST"])
@login_required
@role_required("admin")
def pengguna_reset_password(user_id):
    user = User.query.get_or_404(user_id)
    role_filter = request.form.get("role_filter") or user.role
    password_baru = (request.form.get("password_baru") or "").strip()
    if not password_baru:
        password_baru = _password_default_role(user.role)
    if len(password_baru) < 4:
        flash("Password minimal 4 karakter.", "danger")
        return redirect(url_for("admin.pengguna_list", role=role_filter))

    user.set_password(password_baru)
    db.session.commit()
    flash(
        f"Password '{user.username}' direset menjadi: {password_baru}",
        "success",
    )
    return redirect(url_for("admin.pengguna_list", role=role_filter))


@admin_bp.route("/pengguna/<int:user_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def pengguna_toggle(user_id):
    user = User.query.get_or_404(user_id)
    role_filter = request.form.get("role_filter") or user.role
    if user.id == current_user.id:
        flash("Anda tidak dapat menonaktifkan akun sendiri.", "danger")
        return redirect(url_for("admin.pengguna_list", role=role_filter))
    user.is_active_user = not user.is_active_user
    db.session.commit()
    status = "diaktifkan" if user.is_active_user else "dinonaktifkan"
    flash(f"Akun '{user.username}' berhasil {status}.", "success")
    return redirect(url_for("admin.pengguna_list", role=role_filter))


@admin_bp.route("/pengguna/<int:user_id>/update", methods=["POST"])
@login_required
@role_required("admin")
def pengguna_update(user_id):
    user = User.query.get_or_404(user_id)
    role_filter = request.form.get("role_filter") or user.role
    nama = (request.form.get("nama_lengkap") or "").strip()
    kelas_penguji = request.form.get("kelas_penguji") or None

    if not nama:
        flash("Nama lengkap wajib diisi.", "danger")
        return redirect(url_for("admin.pengguna_list", role=role_filter))

    user.nama_lengkap = nama
    if user.role in ("guru", "guru_soal"):
        if kelas_penguji in dict(KELAS_CHOICES):
            user.kelas_penguji = kelas_penguji
    db.session.commit()
    flash(f"Data '{user.username}' berhasil diperbarui.", "success")
    return redirect(url_for("admin.pengguna_list", role=role_filter))


@admin_bp.route("/backup")
@login_required
@role_required("admin")
def backup_database():
    from flask import current_app

    db_name = current_app.config.get("MYSQL_DATABASE", "tpk_smartmu22")
    return render_template(
        "admin/backup.html",
        db_name=db_name,
        tahun_ajaran=get_tahun_ajaran(),
    )


@admin_bp.route("/backup/unduh")
@login_required
@role_required("admin")
def backup_unduh():
    from tpk.db_backup import buat_backup_sql

    try:
        content, filename = buat_backup_sql()
    except Exception as exc:  # noqa: BLE001
        flash(f"Gagal membuat backup: {exc}", "danger")
        return redirect(url_for("admin.backup_database"))

    return send_file(
        io.BytesIO(content),
        as_attachment=True,
        download_name=filename,
        mimetype="application/sql",
    )


@admin_bp.route("/backup/restore", methods=["POST"])
@login_required
@role_required("admin")
def backup_restore():
    from tpk.db_backup import restore_dari_sql

    konfirmasi = (request.form.get("konfirmasi") or "").strip().upper()
    if konfirmasi != "RESTORE DATABASE":
        flash('Konfirmasi salah. Ketik tepat: RESTORE DATABASE', "danger")
        return redirect(url_for("admin.backup_database"))

    file = request.files.get("backup_file")
    if not file or not file.filename:
        flash("Pilih file backup .sql terlebih dahulu.", "danger")
        return redirect(url_for("admin.backup_database"))

    filename = file.filename.lower()
    if not (filename.endswith(".sql") or filename.endswith(".txt")):
        flash("Format file harus .sql", "danger")
        return redirect(url_for("admin.backup_database"))

    raw = file.read()
    if not raw or len(raw) < 20:
        flash("File backup kosong atau tidak valid.", "danger")
        return redirect(url_for("admin.backup_database"))

    try:
        hasil = restore_dari_sql(raw)
        flash(
            f"Restore berhasil. {hasil['statements']} perintah SQL dijalankan. "
            "Silakan login ulang jika sesi terputus.",
            "success",
        )
    except Exception as exc:  # noqa: BLE001
        flash(f"Restore gagal: {exc}", "danger")

    return redirect(url_for("admin.backup_database"))


def _simpan_pengaturan(kunci: str, nilai: str, keterangan: str = None) -> None:
    if not nilai and nilai != "0":
        return
    row = Pengaturan.query.filter_by(kunci=kunci).first()
    if row:
        row.nilai = nilai
        if keterangan:
            row.keterangan = keterangan
    else:
        db.session.add(Pengaturan(kunci=kunci, nilai=nilai, keterangan=keterangan))


@admin_bp.route("/pengaturan", methods=["GET", "POST"])
@login_required
@role_required("admin")
def pengaturan():
    if request.method == "POST":
        for key in (
            "tahun_ajaran",
            "gelombang_aktif",
            "daftar_gelombang",
            "bobot_tes_tertulis",
            "bobot_wawancara",
            "bobot_psikotes",
            "batas_lulus",
        ):
            val = request.form.get(key, "").strip()
            if key == "gelombang_aktif":
                val = normalisasi_gelombang(val)
            if key == "daftar_gelombang" and val:
                _simpan_pengaturan(key, val)
                db.session.flush()
                tahun = request.form.get("tahun_ajaran", "").strip() or get_tahun_ajaran()
                q = Murid.query.with_entities(Murid.gelombang).distinct()
                if tahun:
                    q = q.filter(
                        (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None))
                    )
                existing_db = [
                    normalisasi_gelombang(g) for (g,) in q.all() if g
                ]
                tambah_gelombang_ke_daftar(*existing_db)
                continue
            if val or val == "0":
                _simpan_pengaturan(key, val)

        # Bobot khusus per kelas (boleh berbeda antar kelas)
        for kode, label in KELAS_CHOICES:
            for prefix, ket in (
                ("bobot_tes", "Bobot tes tertulis"),
                ("bobot_wawancara", "Bobot wawancara"),
                ("bobot_psikotes", "Bobot psikotes"),
            ):
                form_key = f"{prefix}_{kode}"
                val = (request.form.get(form_key) or "").strip()
                if val == "":
                    continue
                _simpan_pengaturan(
                    form_key,
                    val,
                    f"{ket} kelas {label}",
                )
            # Kuota penempatan per kelas
            kuota_val = (request.form.get(f"kuota_{kode}") or "").strip()
            if kuota_val != "":
                try:
                    kuota_int = max(0, int(float(kuota_val)))
                except ValueError:
                    kuota_int = 0
                _simpan_pengaturan(
                    f"kuota_{kode}",
                    str(kuota_int),
                    f"Kuota penempatan kelas {label}",
                )

        db.session.commit()
        flash(
            "Pengaturan disimpan (bobot & kuota per kelas).",
            "success",
        )
        return redirect(url_for("admin.pengaturan"))

    settings = {p.kunci: p.nilai for p in Pengaturan.query.all()}
    bobot_kelas = get_semua_bobot_kelas()
    terisi = hitung_terisi_kelas()
    kuota_kelas = get_semua_kuota_kelas()
    return render_template(
        "admin/pengaturan.html",
        settings=settings,
        kelas_choices=KELAS_CHOICES,
        bobot_kelas=bobot_kelas,
        kuota_kelas=kuota_kelas,
        terisi_kelas=terisi,
    )