from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from tpk.extensions import db
from tpk.models import KELAS_CHOICES
from tpk.utils import (
    daftar_kisi_kisi,
    get_bobot_penilaian,
    role_required,
    tampilkan_kisi_kisi,
)

ortu_bp = Blueprint("ortu", __name__)


def _anak_murid():
    murid = getattr(current_user, "anak_asuh", None)
    if not murid:
        flash("Akun orang tua belum terhubung ke data anak.", "danger")
        return None
    return murid


@ortu_bp.route("/")
@login_required
@role_required("orang_tua")
def dashboard():
    murid = _anak_murid()
    if not murid:
        return render_template("ortu/dashboard.html", murid=None)
    bobot_tes, bobot_ww, bobot_psiko = get_bobot_penilaian()
    return render_template(
        "ortu/dashboard.html",
        murid=murid,
        kelas_choices=KELAS_CHOICES,
        nilai_per_kelas=murid.nilai_wawancara_per_kelas(),
        bobot_tes=bobot_tes,
        bobot_wawancara=bobot_ww,
        bobot_psikotes=bobot_psiko,
        ringkas_tes=murid.ringkas_tes_tertulis(),
        nilai_tes=murid.nilai_tes_per_kelas(),
    )


@ortu_bp.route("/laporan")
@login_required
@role_required("orang_tua")
def laporan():
    return redirect(url_for("ortu.laporan_gabungan"))


@ortu_bp.route("/laporan/tes-tertulis")
@login_required
@role_required("orang_tua")
def laporan_tes():
    murid = _anak_murid()
    if not murid:
        return redirect(url_for("ortu.dashboard"))
    return render_template(
        "ortu/laporan_tes.html",
        murid=murid,
        kelas_choices=KELAS_CHOICES,
        nilai_tes=murid.nilai_tes_per_kelas(),
        ringkas_tes=murid.ringkas_tes_tertulis(),
        tampilkan_kisi=tampilkan_kisi_kisi(),
    )


@ortu_bp.route("/kisi-kisi")
@login_required
@role_required("orang_tua")
def kisi_kisi():
    murid = _anak_murid()
    if not murid:
        return redirect(url_for("ortu.dashboard"))
    kelas = request.args.get("kelas") or ""
    return render_template(
        "shared/kisi_kisi.html",
        items=daftar_kisi_kisi(kelas) if tampilkan_kisi_kisi() else [],
        kelas=kelas,
        kelas_choices=KELAS_CHOICES,
        tampilkan=tampilkan_kisi_kisi(),
        back_url=url_for("ortu.laporan_tes"),
    )


@ortu_bp.route("/laporan/wawancara")
@login_required
@role_required("orang_tua")
def laporan_wawancara():
    murid = _anak_murid()
    if not murid:
        return redirect(url_for("ortu.dashboard"))
    return render_template(
        "ortu/laporan_wawancara.html",
        murid=murid,
        kelas_choices=KELAS_CHOICES,
        nilai_per_kelas=murid.nilai_wawancara_per_kelas(),
    )


@ortu_bp.route("/laporan/gabungan")
@login_required
@role_required("orang_tua")
def laporan_gabungan():
    murid = _anak_murid()
    if not murid:
        return redirect(url_for("ortu.dashboard"))
    bobot_tes, bobot_ww, bobot_psiko = get_bobot_penilaian()
    return render_template(
        "ortu/laporan_gabungan.html",
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


@ortu_bp.route("/password", methods=["GET", "POST"])
@login_required
@role_required("orang_tua")
def ganti_password():
    if request.method == "POST":
        lama = request.form.get("password_lama") or ""
        baru = (request.form.get("password_baru") or "").strip()
        ulang = (request.form.get("password_ulang") or "").strip()

        if not current_user.check_password(lama):
            flash("Password lama tidak sesuai.", "danger")
        elif len(baru) < 4:
            flash("Password baru minimal 4 karakter.", "danger")
        elif baru != ulang:
            flash("Konfirmasi password baru tidak sama.", "danger")
        else:
            current_user.set_password(baru)
            db.session.commit()
            flash("Password berhasil diganti.", "success")
            return redirect(url_for("ortu.dashboard"))
    return render_template("ortu/password.html")
