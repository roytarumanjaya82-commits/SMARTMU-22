from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from tpk.extensions import db
from tpk.models import (
    KELAS_CHOICES,
    SESI_WAWANCARA,
    JawabanWawancara,
    Murid,
    PenilaianWawancara,
    SoalWawancara,
)
from tpk.utils import (
    get_daftar_gelombang,
    get_gelombang_aktif,
    get_tahun_ajaran,
    label_gelombang,
    normalisasi_gelombang,
    role_required,
)

guru_bp = Blueprint("guru", __name__)


def _kelas_guru():
    return current_user.kelas_penguji


def _soal_aktif(kelas):
    return (
        SoalWawancara.query.filter_by(kelas_tujuan=kelas, is_active=True)
        .order_by(SoalWawancara.urutan, SoalWawancara.id)
        .all()
    )


def _murid_gelombang(gelombang=None):
    tahun = get_tahun_ajaran()
    gelombang = normalisasi_gelombang(gelombang or get_gelombang_aktif())
    query = Murid.query.filter(
        (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None))
    )
    if gelombang:
        query = query.filter(Murid.gelombang == gelombang)
    calon = query.all()
    calon = sorted(calon, key=lambda m: (m.user.nama_lengkap or "").lower())
    return calon, gelombang, tahun


def _penilaian_map(kelas, murid_ids=None):
    """Satu penilaian per murid untuk sesi kelas ini."""
    rows = PenilaianWawancara.query.filter_by(kelas_tujuan=kelas).all()
    hasil = {}
    for p in rows:
        if murid_ids is not None and p.murid_id not in murid_ids:
            continue
        prev = hasil.get(p.murid_id)
        if prev is None or p.nilai_akhir >= prev.nilai_akhir:
            hasil[p.murid_id] = p
    return hasil


@guru_bp.route("/")
@login_required
@role_required("guru")
def dashboard():
    kelas = _kelas_guru()
    gelombang = request.args.get("gelombang")
    calon, gelombang, tahun = _murid_gelombang(gelombang)
    penilaian_map = _penilaian_map(kelas, {m.id for m in calon})
    sudah = len(penilaian_map)
    belum = max(len(calon) - sudah, 0)
    return render_template(
        "guru/dashboard.html",
        calon=calon,
        sudah=sudah,
        belum=belum,
        total_murid=len(calon),
        kelas=kelas,
        kelas_label=dict(KELAS_CHOICES).get(kelas, kelas),
        total_sesi=len(SESI_WAWANCARA),
        gelombang=gelombang,
        daftar_gelombang=get_daftar_gelombang(),
        tahun_ajaran=tahun,
        label_gelombang=label_gelombang,
    )


@guru_bp.route("/penilaian")
@login_required
@role_required("guru")
def penilaian_list():
    return redirect(url_for("guru.soal_wawancara"))


@guru_bp.route("/soal-wawancara")
@login_required
@role_required("guru")
def soal_wawancara():
    """Daftar penilaian sesi wawancara kelas guru untuk murid per gelombang."""
    kelas = _kelas_guru()
    soal_list = _soal_aktif(kelas)
    total_bobot = sum(s.bobot or 0 for s in soal_list)
    calon, gelombang, tahun = _murid_gelombang(request.args.get("gelombang"))
    penilaian_map = _penilaian_map(kelas, {m.id for m in calon})
    sudah = sum(1 for m in calon if m.id in penilaian_map)
    return render_template(
        "guru/soal_wawancara.html",
        items=soal_list,
        calon=calon,
        penilaian_map=penilaian_map,
        total_bobot=total_bobot,
        sudah=sudah,
        belum=len(calon) - sudah,
        kelas_label=dict(KELAS_CHOICES).get(kelas, kelas),
        total_sesi=len(SESI_WAWANCARA),
        gelombang=gelombang,
        daftar_gelombang=get_daftar_gelombang(),
        tahun_ajaran=tahun,
        label_gelombang=label_gelombang,
    )


@guru_bp.route("/penilaian/<int:murid_id>", methods=["GET", "POST"])
@login_required
@role_required("guru")
def nilai_murid(murid_id):
    """Input nilai sesi wawancara kelas guru untuk satu murid."""
    kelas = _kelas_guru()
    murid = Murid.query.get_or_404(murid_id)
    soal_list = _soal_aktif(kelas)
    total_bobot = sum(s.bobot or 0 for s in soal_list)

    penilaian = (
        PenilaianWawancara.query.filter_by(murid_id=murid.id, kelas_tujuan=kelas)
        .order_by(PenilaianWawancara.id.desc())
        .first()
    )

    if request.method == "POST":
        if not soal_list:
            flash("Belum ada soal wawancara aktif. Hubungi admin.", "warning")
            return redirect(url_for("guru.soal_wawancara", gelombang=murid.gelombang))
        if total_bobot != 100:
            flash(
                f"Total bobot soal wawancara kelas ini {total_bobot}, harus 100. Hubungi admin.",
                "danger",
            )
            return redirect(url_for("guru.nilai_murid", murid_id=murid.id))

        if not penilaian:
            penilaian = PenilaianWawancara(
                murid_id=murid.id,
                guru_id=current_user.id,
                kelas_tujuan=kelas,
            )
            db.session.add(penilaian)
            db.session.flush()
        else:
            penilaian.guru_id = current_user.id
            JawabanWawancara.query.filter_by(penilaian_id=penilaian.id).delete()

        nilai_akhir = 0.0
        for soal in soal_list:
            jawaban_text = request.form.get(f"jawaban_{soal.id}", "").strip() or None
            raw = request.form.get(f"skor_{soal.id}", "0")
            try:
                skor = float(raw)
            except ValueError:
                skor = 0
            skor = max(0, min(skor, float(soal.bobot or 0)))
            nilai_akhir += skor
            db.session.add(
                JawabanWawancara(
                    penilaian_id=penilaian.id,
                    soal_id=soal.id,
                    jawaban_murid=jawaban_text,
                    skor=skor,
                )
            )

        penilaian.catatan = request.form.get("catatan", "").strip() or None
        penilaian.nilai_akhir = round(nilai_akhir, 2)
        penilaian.rekomendasi = "dinilai"
        murid.sinkronkan_status_wawancara()

        db.session.commit()
        flash(
            f"Nilai sesi wawancara {dict(KELAS_CHOICES).get(kelas, kelas)} tersimpan: "
            f"{penilaian.nilai_akhir}/100. Progress murid: {murid.progress_wawancara_label}. "
            f"Rekomendasi saat ini: {murid.rekomendasi_kelas_label}.",
            "success",
        )
        return redirect(url_for("guru.soal_wawancara", gelombang=murid.gelombang or ""))

    jawaban_tersimpan = {}
    if penilaian:
        jawaban_tersimpan = {j.soal_id: j for j in penilaian.jawaban_soal}

    return render_template(
        "guru/nilai_form.html",
        murid=murid,
        penilaian=penilaian,
        soal_list=soal_list,
        jawaban_tersimpan=jawaban_tersimpan,
        total_bobot=total_bobot,
        kelas=kelas,
        kelas_label=dict(KELAS_CHOICES).get(kelas, kelas),
        nilai_per_kelas=murid.nilai_wawancara_per_kelas(),
        kelas_choices=KELAS_CHOICES,
        tahun_ajaran=get_tahun_ajaran(),
        label_gelombang=label_gelombang,
    )


@guru_bp.route("/hasil")
@login_required
@role_required("guru")
def hasil():
    kelas = _kelas_guru()
    calon, gelombang, tahun = _murid_gelombang(request.args.get("gelombang"))
    murid_ids = {m.id for m in calon}
    items = (
        PenilaianWawancara.query.filter_by(kelas_tujuan=kelas)
        .order_by(PenilaianWawancara.nilai_akhir.desc())
        .all()
    )
    items = [p for p in items if p.murid_id in murid_ids]
    return render_template(
        "guru/hasil.html",
        items=items,
        kelas_label=dict(KELAS_CHOICES).get(kelas, kelas),
        gelombang=gelombang,
        daftar_gelombang=get_daftar_gelombang(),
        tahun_ajaran=tahun,
        label_gelombang=label_gelombang,
    )