from urllib.parse import quote

import pymysql
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from pengaturan import (
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    SECRET_KEY,
    SMARTMU_DATABASE,
)
from sso import baca, hapus, pasang

MODUL = (
    {
        "href": "/presensi/",
        "nama": "Presensi",
        "ringkas": "Presensi harian, laporan piket, hasil belajar, dan akun orang tua.",
        "warna": "#0f6e56",
    },
    {
        "href": "/erapor/",
        "nama": "eRapor",
        "ringkas": "Rapor digital: nilai mapel, ekskul, tahfiz, leger, dan cetak.",
        "warna": "#1d4ed8",
    },
    {
        "href": "/tahfidz/",
        "nama": "Tahfidz",
        "ringkas": "Setoran realtime, laporan murid, dan akun orang tua.",
        "warna": "#0c4f3b",
    },
    {
        "href": "/bk/",
        "nama": "Rapor BK",
        "ringkas": "Rapor bimbingan konseling. Isinya tersimpan di MySQL.",
        "warna": "#9a7424",
    },
    {
        "href": "/inventaris/",
        "nama": "Inventaris",
        "ringkas": "Data barang, peminjaman, laporan, dan cadangan Google Drive.",
        "warna": "#b45309",
    },
)


def _koneksi():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=SMARTMU_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def tujuan_aman(nilai):
    if not nilai or not nilai.startswith("/") or nilai.startswith("//"):
        return url_for("beranda")
    return nilai


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SESSION_COOKIE_NAME"] = "smartmu_portal"
    app.config["SESSION_COOKIE_PATH"] = "/"

    @app.context_processor
    def sisip():
        return {"modul_list": MODUL, "sso": baca(request)}

    @app.after_request
    def segarkan_sso(respon):
        if session.get("user_id") and not baca(request):
            pasang(
                respon,
                {
                    "username": session.get("username"),
                    "nama": session.get("nama"),
                    "role": session.get("role"),
                },
            )
        return respon

    @app.route("/")
    def beranda():
        if not session.get("user_id"):
            return redirect(url_for("masuk"))
        return render_template("home.html")

    @app.route("/login", methods=["GET", "POST"])
    def masuk():
        if session.get("user_id"):
            return redirect(tujuan_aman(request.args.get("next")))
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            nxt = tujuan_aman(request.form.get("next"))
            try:
                conn = _koneksi()
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT * FROM pengguna WHERE username=%s AND aktif=1",
                            (username,),
                        )
                        user = cur.fetchone()
                finally:
                    conn.close()
            except pymysql.MySQLError:
                flash("Database belum siap. Jalankan python init_db.py di folder aplikasi.", "error")
                return render_template("login.html", next=request.form.get("next") or "")
            if not user or not check_password_hash(user["password_hash"], password):
                flash("Username atau kata sandi salah.", "error")
                return render_template("login.html", next=request.form.get("next") or "")
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["nama"] = user["nama"]
            session["role"] = user["role"]
            respon = redirect(nxt)
            return pasang(
                respon,
                {
                    "username": user["username"],
                    "nama": user["nama"],
                    "role": user["role"],
                },
            )
        return render_template("login.html", next=request.args.get("next") or "")

    @app.route("/logout")
    def keluar():
        session.clear()
        flash("Anda telah keluar dari SMARTMU.", "info")
        respon = redirect(url_for("masuk"))
        hapus(respon)
        return respon

    return app


def tautan_masuk(request):
    tujuan = request.script_root + request.full_path
    if tujuan.endswith("?"):
        tujuan = tujuan[:-1]
    return "/login?next=" + quote(tujuan, safe="/?=&")
