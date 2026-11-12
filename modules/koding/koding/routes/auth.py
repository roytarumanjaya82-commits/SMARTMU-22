from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from koding import db
from koding.auth_utils import verify_password, login_user, logout_user, current_user

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("public.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = db.query(
            "SELECT * FROM users WHERE username=%s AND aktif=1",
            (username,),
            one=True,
        )
        if not user or not verify_password(user["password_hash"], password):
            flash("Username atau password salah.", "danger")
            return render_template("auth/login.html")

        if not login_user(user):
            flash("Akun siswa belum terhubung ke kelas. Hubungi guru koding.", "danger")
            return render_template("auth/login.html")
        flash(f"Selamat datang, {user['nama_lengkap']}!", "success")
        nxt = request.args.get("next")
        if nxt:
            return redirect(nxt)
        return redirect(url_for("public.index"))

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Keluar dari Kelas Koding dan hapus sesi portal/SSO agar tidak langsung masuk lagi."""
    logout_user()
    from sso import hapus

    # Logout penuh lewat portal: bersihkan cookie portal + SSO + sesi koding.
    respon = redirect("/logout")
    hapus(respon)
    respon.delete_cookie("smartmu_koding", path="/koding")
    respon.delete_cookie("smartmu_koding", path="/")
    return respon
