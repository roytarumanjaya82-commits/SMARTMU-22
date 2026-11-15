"""Guru pembuat soal: hanya boleh kelola soal tes tertulis untuk kelas yang ditugaskan."""

import io

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required

from tpk.extensions import db
from tpk.models import KELAS_CHOICES, SoalTes
from tpk.soal_import import baca_soal_file, buat_blanko_soal_xlsx, impor_soal_tes
from tpk.utils import role_required

guru_soal_bp = Blueprint("guru_soal", __name__)


def _kelas_tugas() -> str:
    return current_user.kelas_penguji or ""


def _pastikan_kelas_sendiri(kelas: str) -> bool:
    return kelas == _kelas_tugas() and kelas in dict(KELAS_CHOICES)


def _soal_milik_kelas(soal: SoalTes) -> bool:
    return soal.kelas_tujuan == _kelas_tugas()


@guru_soal_bp.route("/")
@guru_soal_bp.route("/soal", methods=["GET", "POST"])
@login_required
@role_required("guru_soal")
def soal_list():
    from tpk.media import simpan_gambar_base64, simpan_gambar_file

    kelas = _kelas_tugas()
    if kelas not in dict(KELAS_CHOICES):
        flash(
            "Akun belum ditugaskan ke kelas soal. Hubungi admin.",
            "danger",
        )
        return render_template(
            "guru_soal/soal_list.html",
            items=[],
            kelas=kelas,
            kelas_label="-",
            jumlah=0,
        )

    if request.method == "POST":
        pertanyaan = request.form.get("pertanyaan", "").strip()
        opsi_a = request.form.get("opsi_a", "").strip()
        opsi_b = request.form.get("opsi_b", "").strip()
        opsi_c = request.form.get("opsi_c", "").strip()
        opsi_d = request.form.get("opsi_d", "").strip()
        jawaban_benar = request.form.get("jawaban_benar", "A").upper()
        bobot = int(request.form.get("bobot") or 1)
        gambar_path = None
        try:
            if request.files.get("gambar_file") and request.files["gambar_file"].filename:
                gambar_path = simpan_gambar_file(request.files["gambar_file"])
            elif request.form.get("gambar_paste"):
                gambar_path = simpan_gambar_base64(request.form.get("gambar_paste"))
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("guru_soal.soal_list"))

        if not pertanyaan and gambar_path:
            pertanyaan = "Lihat gambar soal"
        if not pertanyaan:
            flash("Isi pertanyaan atau tempel/upload gambar soal.", "danger")
            return redirect(url_for("guru_soal.soal_list"))
        if not all([opsi_a, opsi_b, opsi_c, opsi_d]) or jawaban_benar not in "ABCD":
            flash("Opsi A–D dan jawaban benar wajib diisi.", "danger")
            return redirect(url_for("guru_soal.soal_list"))

        soal = SoalTes(
            kelas_tujuan=kelas,
            pertanyaan=pertanyaan,
            gambar=gambar_path,
            opsi_a=opsi_a,
            opsi_b=opsi_b,
            opsi_c=opsi_c,
            opsi_d=opsi_d,
            jawaban_benar=jawaban_benar,
            bobot=bobot,
        )
        db.session.add(soal)
        db.session.commit()
        flash(f"Soal kelas {dict(KELAS_CHOICES)[kelas]} berhasil ditambahkan.", "success")
        return redirect(url_for("guru_soal.soal_list"))

    items = (
        SoalTes.query.filter_by(kelas_tujuan=kelas)
        .order_by(SoalTes.id.desc())
        .all()
    )
    jumlah = SoalTes.query.filter_by(kelas_tujuan=kelas, is_active=True).count()
    return render_template(
        "guru_soal/soal_list.html",
        items=items,
        kelas=kelas,
        kelas_label=dict(KELAS_CHOICES).get(kelas, kelas),
        jumlah=jumlah,
    )


@guru_soal_bp.route("/soal/blanko")
@login_required
@role_required("guru_soal")
def unduh_blanko_soal():
    kelas = _kelas_tugas()
    if not _pastikan_kelas_sendiri(kelas):
        flash("Kelas tugas tidak valid.", "danger")
        return redirect(url_for("guru_soal.soal_list"))
    content = buat_blanko_soal_xlsx(kelas)
    return send_file(
        io.BytesIO(content),
        as_attachment=True,
        download_name=f"blanko_soal_tes_{kelas}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@guru_soal_bp.route("/soal/upload", methods=["POST"])
@login_required
@role_required("guru_soal")
def upload_soal():
    kelas = _kelas_tugas()
    if not _pastikan_kelas_sendiri(kelas):
        flash("Kelas tugas tidak valid.", "danger")
        return redirect(url_for("guru_soal.soal_list"))

    file = request.files.get("soal_file")
    if not file or not file.filename:
        flash("Pilih file soal (.xlsx / .csv).", "danger")
        return redirect(url_for("guru_soal.soal_list"))

    rows, error = baca_soal_file(file)
    if error:
        flash(error, "danger")
        return redirect(url_for("guru_soal.soal_list"))
    if not rows:
        flash("Tidak ada baris soal yang bisa diimpor.", "warning")
        return redirect(url_for("guru_soal.soal_list"))

    # Paksa semua baris ke kelas tugas guru (abaikan kelas di file lain)
    for row in rows:
        if isinstance(row, dict):
            row["kelas_tujuan"] = kelas

    hasil = impor_soal_tes(rows, kelas_default=kelas)
    if hasil["sukses"]:
        flash(f"{hasil['sukses']} soal kelas {dict(KELAS_CHOICES)[kelas]} diunggah.", "success")
    if hasil["dilewati"]:
        flash(f"{hasil['dilewati']} baris contoh dilewati.", "info")
    if hasil["gagal"]:
        preview = " | ".join(hasil["gagal"][:3])
        flash(f"{len(hasil['gagal'])} baris gagal: {preview}", "warning")
    return redirect(url_for("guru_soal.soal_list"))


@guru_soal_bp.route("/soal/<int:soal_id>/toggle", methods=["POST"])
@login_required
@role_required("guru_soal")
def soal_toggle(soal_id):
    soal = SoalTes.query.get_or_404(soal_id)
    if not _soal_milik_kelas(soal):
        flash("Anda hanya boleh mengelola soal kelas Anda.", "danger")
        return redirect(url_for("guru_soal.soal_list"))
    soal.is_active = not soal.is_active
    db.session.commit()
    flash("Status soal diperbarui.", "success")
    return redirect(url_for("guru_soal.soal_list"))


@guru_soal_bp.route("/soal/<int:soal_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("guru_soal")
def soal_edit(soal_id):
    from tpk.media import hapus_gambar_soal, simpan_gambar_base64, simpan_gambar_file

    soal = SoalTes.query.get_or_404(soal_id)
    if not _soal_milik_kelas(soal):
        flash("Anda hanya boleh mengelola soal kelas Anda.", "danger")
        return redirect(url_for("guru_soal.soal_list"))

    kelas = _kelas_tugas()
    if request.method == "POST":
        # Kelas tidak boleh diganti ke kelas lain
        pertanyaan = request.form.get("pertanyaan", "").strip()
        soal.opsi_a = request.form.get("opsi_a", "").strip()
        soal.opsi_b = request.form.get("opsi_b", "").strip()
        soal.opsi_c = request.form.get("opsi_c", "").strip()
        soal.opsi_d = request.form.get("opsi_d", "").strip()
        soal.jawaban_benar = request.form.get("jawaban_benar", "A").upper()
        soal.bobot = int(request.form.get("bobot") or 1)
        soal.kelas_tujuan = kelas

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
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("guru_soal.soal_edit", soal_id=soal.id))

        if not pertanyaan and soal.gambar:
            pertanyaan = "Lihat gambar soal"
        if not pertanyaan:
            flash("Pertanyaan (atau gambar) wajib diisi.", "danger")
            return redirect(url_for("guru_soal.soal_edit", soal_id=soal.id))
        if not all([soal.opsi_a, soal.opsi_b, soal.opsi_c, soal.opsi_d]):
            flash("Opsi A–D wajib diisi.", "danger")
            return redirect(url_for("guru_soal.soal_edit", soal_id=soal.id))
        if soal.jawaban_benar not in "ABCD":
            flash("Jawaban benar harus A/B/C/D.", "danger")
            return redirect(url_for("guru_soal.soal_edit", soal_id=soal.id))

        soal.pertanyaan = pertanyaan
        db.session.commit()
        flash("Soal diperbarui.", "success")
        return redirect(url_for("guru_soal.soal_list"))

    return render_template(
        "guru_soal/soal_edit.html",
        soal=soal,
        kelas=kelas,
        kelas_label=dict(KELAS_CHOICES).get(kelas, kelas),
    )
