from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from tpk.extensions import db
from tpk.models import KELAS_CHOICES, Murid, User
from tpk.utils import (
    DEFAULT_PASSWORD_MURID,
    DEFAULT_PASSWORD_ORTU,
    buat_username_dari_nama,
    pastikan_akun_ortu,
    redirect_by_role,
    role_required,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    username_awal = (request.args.get("username") or "").strip().lower().replace(" ", "")
    dari_smartmu = request.args.get("dari") == "smartmu"

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower().replace(" ", "")
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.is_active_user and user.check_password(password):
            login_user(user)
            flash(f"Selamat datang, {user.nama_lengkap}!", "success")
            return redirect_by_role(user)
        flash("Username atau password salah.", "danger")
        username_awal = username
        dari_smartmu = False

    return render_template(
        "auth/login.html",
        username_awal=username_awal,
        dari_smartmu=dari_smartmu,
    )


@auth_bp.route("/register", methods=["GET", "POST"])
@role_required("admin")
def register():
    if request.method == "POST":
        nama_lengkap = request.form.get("nama_lengkap", "").strip()
        nisn = request.form.get("nisn", "").strip()
        pilihan1 = request.form.get("pilihan_kelas_1")
        pilihan2 = request.form.get("pilihan_kelas_2") or None

        errors = []
        if not all([nama_lengkap, nisn, pilihan1]):
            errors.append("Lengkapi data wajib (nama, NISN, pilihan kelas).")
        if Murid.query.filter_by(nisn=nisn).first():
            errors.append("NISN sudah terdaftar.")
        if pilihan2 and pilihan2 == pilihan1:
            errors.append("Pilihan kelas 1 dan 2 tidak boleh sama.")

        if errors:
            for e in errors:
                flash(e, "danger")
        else:
            username = buat_username_dari_nama(nama_lengkap)
            user = User(
                username=username,
                nama_lengkap=nama_lengkap,
                email=None,
                role="murid",
            )
            user.set_password(DEFAULT_PASSWORD_MURID)
            db.session.add(user)
            db.session.flush()

            tanggal_lahir = request.form.get("tanggal_lahir") or None
            murid = Murid(
                user_id=user.id,
                nisn=nisn,
                tempat_lahir=request.form.get("tempat_lahir", "").strip() or None,
                tanggal_lahir=datetime.strptime(tanggal_lahir, "%Y-%m-%d").date()
                if tanggal_lahir
                else None,
                jenis_kelamin=request.form.get("jenis_kelamin") or None,
                alamat=request.form.get("alamat", "").strip() or None,
                no_hp=request.form.get("no_hp", "").strip() or None,
                nama_ortu=request.form.get("nama_ortu", "").strip() or None,
                no_hp_ortu=request.form.get("no_hp_ortu", "").strip() or None,
                asal_sekolah=request.form.get("asal_sekolah", "").strip() or None,
                pilihan_kelas_1=pilihan1,
                pilihan_kelas_2=pilihan2,
                status="terdaftar",
            )
            db.session.add(murid)
            db.session.flush()
            ortu, _ = pastikan_akun_ortu(murid, commit=False)
            db.session.commit()
            flash(
                f"Pendaftaran berhasil. Username murid: {username} · Password: {DEFAULT_PASSWORD_MURID}. "
                f"Login orang tua: {ortu.username} · Password: {DEFAULT_PASSWORD_ORTU}",
                "success",
            )
            return redirect(url_for("admin.murid_list"))

    return render_template(
        "auth/register.html",
        kelas_choices=KELAS_CHOICES,
        default_password=DEFAULT_PASSWORD_MURID,
    )


@auth_bp.route("/logout")
@login_required
def logout():
    dari_portal = session.pop("dari_portal", None)
    logout_user()
    flash("Anda telah keluar.", "info")
    if dari_portal:
        return redirect("/")
    return redirect(url_for("auth.login"))
