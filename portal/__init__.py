import os
import secrets
import tempfile
from urllib.parse import quote

import pymysql
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash

from portal import akun as akun_db
from portal import cadangan as cadangan_db

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
        "kunci": "presensi",
        "href": "/presensi/",
        "nama": "Presensi",
        "ringkas": "Presensi harian, laporan piket, hasil belajar, dan akun orang tua.",
        "warna": "#0f6e56",
    },
    {
        "kunci": "erapor",
        "href": "/erapor/",
        "nama": "eRapor",
        "ringkas": "Rapor digital: nilai mapel, ekskul, tahfiz, leger, dan cetak.",
        "warna": "#1d4ed8",
    },
    {
        "kunci": "tahfidz",
        "href": "/tahfidz/",
        "nama": "Tahfidz",
        "ringkas": "Setoran realtime, laporan murid, dan akun orang tua.",
        "warna": "#0c4f3b",
    },
    {
        "kunci": "bk",
        "href": "/bk/",
        "nama": "Rapor BK",
        "ringkas": "Rapor bimbingan konseling. Isinya tersimpan di MySQL.",
        "warna": "#9a7424",
    },
    {
        "kunci": "inventaris",
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
    app.config["MAX_CONTENT_LENGTH"] = cadangan_db.BATAS_BERKAS

    def modul_terlihat():
        if session.get("role") == "orang_tua":
            return tuple(modul for modul in MODUL if modul["kunci"] == "tahfidz")
        if session.get("role") == "admin":
            return MODUL
        if not session.get("user_id"):
            return MODUL
        try:
            punya = set(akun_db.akses(session["user_id"]))
        except pymysql.MySQLError:
            return ()
        return tuple(modul for modul in MODUL if modul["kunci"] in punya)

    @app.context_processor
    def sisip():
        return {"modul_list": modul_terlihat(), "sso": baca(request), "portal_opsi": akun_db.PORTAL}

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

    @app.before_request
    def kenali_orang_tua():
        if session.get("role") == "orang_tua":
            return None
        data = baca(request)
        if not data or data.get("role") != "orang_tua":
            return None
        session["user_id"] = data.get("id") or data.get("username")
        session["username"] = data.get("username")
        session["nama"] = data.get("nama")
        session["role"] = "orang_tua"
        session["asal"] = "tahfidz_ortu"
        return None

    @app.route("/")
    def beranda():
        if not session.get("user_id"):
            return redirect(url_for("masuk"))
        kunci = request.args.get("akses")
        if kunci in akun_db.NAMA_PORTAL:
            flash(f"Akun ini tidak dapat membuka {akun_db.NAMA_PORTAL[kunci]}.", "error")
        if session.get("role") == "orang_tua":
            return redirect("/tahfidz/")
        return render_template("home.html")

    @app.route("/login", methods=["GET", "POST"])
    def masuk():
        if session.get("user_id"):
            if session.get("role") == "orang_tua":
                return redirect("/tahfidz/")
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
            if user and not check_password_hash(user["password_hash"], password):
                flash("Username atau kata sandi salah.", "error")
                return render_template("login.html", next=request.form.get("next") or "")
            if not user:
                ortu = akun_db.cari_orang_tua(username, password)
                if not ortu:
                    flash("Username atau kata sandi salah.", "error")
                    return render_template("login.html", next=request.form.get("next") or "")
                session.clear()
                session["user_id"] = ortu["id"]
                session["username"] = ortu["username"]
                session["nama"] = ortu["nama_lengkap"]
                session["role"] = "orang_tua"
                session["asal"] = "tahfidz_ortu"
                tujuan = "/tahfidz/"
                return pasang(
                    redirect(tujuan),
                    {
                        "id": ortu["id"],
                        "username": ortu["username"],
                        "nama": ortu["nama_lengkap"],
                        "role": "orang_tua",
                    },
                )
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["nama"] = user["nama"]
            session["role"] = user["role"]
            if user["role"] != "admin":
                kunci = nxt.strip("/").split("/", 1)[0]
                if kunci in akun_db.NAMA_PORTAL and kunci not in akun_db.akses(user["id"]):
                    flash(f"Akun ini tidak dapat membuka {akun_db.NAMA_PORTAL[kunci]}.", "error")
                    nxt = url_for("beranda")
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
        for nama, jalur in (
            ("smartmu_presensi", "/presensi"),
            ("smartmu_erapor", "/erapor"),
            ("smartmu_tahfidz", "/tahfidz"),
            ("smartmu_bk", "/bk"),
            ("smartmu_inventaris", "/inventaris"),
            ("remember_token", "/inventaris"),
        ):
            respon.delete_cookie(nama, path=jalur)
        return respon

    def wajib_admin():
        if not session.get("user_id"):
            return redirect(url_for("masuk", next=request.path))
        if session.get("role") != "admin":
            flash("Hanya admin yang dapat membuka halaman ini.", "error")
            return redirect(url_for("beranda"))
        return None

    def token_akun():
        session["akun_token"] = secrets.token_urlsafe(24)
        return session["akun_token"]

    def token_akun_sah():
        token = session.get("akun_token") or ""
        kiriman = request.form.get("token") or ""
        return bool(token) and secrets.compare_digest(token, kiriman)

    @app.route("/pengguna")
    def pengguna():
        tolak = wajib_admin()
        if tolak:
            return tolak
        try:
            akun = akun_db.ambil(session["user_id"])
            baris = akun_db.daftar()
        except pymysql.MySQLError:
            flash("Database belum siap. Jalankan python init_db.py di folder aplikasi.", "error")
            return redirect(url_for("beranda"))
        if not akun:
            flash("Akun admin tidak ditemukan.", "error")
            return redirect(url_for("beranda"))
        return render_template(
            "pengguna.html",
            akun=akun,
            daftar=baris,
            peran=akun_db.PERAN,
            token=token_akun(),
        )

    @app.route("/pengguna/<int:pengguna_id>")
    def ubah_pengguna(pengguna_id):
        tolak = wajib_admin()
        if tolak:
            return tolak
        if pengguna_id == session.get("user_id"):
            return redirect(url_for("pengguna") + "#akun-saya")
        try:
            orang = akun_db.ambil(pengguna_id)
        except pymysql.MySQLError:
            flash("Database belum siap. Jalankan python init_db.py di folder aplikasi.", "error")
            return redirect(url_for("beranda"))
        if not orang:
            flash("Pengguna tidak ditemukan.", "error")
            return redirect(url_for("pengguna"))
        return render_template(
            "pengguna_ubah.html",
            orang=orang,
            peran=akun_db.PERAN,
            token=token_akun(),
        )

    @app.route("/pengguna/<int:pengguna_id>", methods=["POST"])
    def simpan_pengguna(pengguna_id):
        tolak = wajib_admin()
        if tolak:
            return tolak
        tujuan = url_for("pengguna") if pengguna_id == session.get("user_id") else url_for(
            "ubah_pengguna", pengguna_id=pengguna_id
        )
        if not token_akun_sah():
            flash("Halaman kadaluarsa. Buka ulang formulir, lalu simpan lagi.", "error")
            return redirect(tujuan)
        sandi_baru = request.form.get("sandi_baru") or ""
        sandi_ulang = request.form.get("sandi_ulang") or ""
        sendiri = pengguna_id == session.get("user_id")
        try:
            sebelum = akun_db.ambil(pengguna_id)
            if not sebelum:
                raise akun_db.AkunError("Pengguna tidak ditemukan.")
            if sendiri and not akun_db.kata_sandi_cocok(pengguna_id, request.form.get("sandi_lama")):
                raise akun_db.AkunError("Kata sandi saat ini salah.")
            username = akun_db.periksa_username(request.form.get("username"))
            password = None
            if sandi_baru or sandi_ulang:
                password = akun_db.periksa_password(sandi_baru, sandi_ulang)
            pilihan = None
            akses_berubah = False
            if not sendiri and sebelum["role"] != "admin":
                pilihan = akun_db.saring(request.form.getlist("portal"))
                akses_berubah = set(pilihan) != set(sebelum["akses"])
            if password is None and username == sebelum["username"]:
                hasil = sebelum
                if not akses_berubah:
                    raise akun_db.AkunError("Tidak ada perubahan.")
            else:
                hasil = akun_db.ubah(pengguna_id, username, password)
            if akses_berubah:
                akun_db.simpan_akses(pengguna_id, pilihan)
        except akun_db.AkunError as exc:
            flash(str(exc), "info" if str(exc) == "Tidak ada perubahan." else "error")
            return redirect(tujuan)
        except pymysql.MySQLError:
            flash("Perubahan gagal disimpan.", "error")
            return redirect(tujuan)
        if password and hasil["username"] != sebelum["username"]:
            pesan = "Username dan kata sandi diperbarui."
        elif password:
            pesan = "Kata sandi diperbarui."
        elif hasil["username"] != sebelum["username"]:
            pesan = "Username diperbarui."
        else:
            pesan = "Portal yang boleh dibuka sudah diperbarui."
        flash(pesan, "info")
        if sendiri:
            session["username"] = hasil["username"]
            respon = redirect(url_for("pengguna"))
            return pasang(
                respon,
                {
                    "username": hasil["username"],
                    "nama": session.get("nama"),
                    "role": session.get("role"),
                },
            )
        return redirect(url_for("pengguna"))

    @app.route("/pengguna/tambah", methods=["POST"])
    def tambah_pengguna():
        tolak = wajib_admin()
        if tolak:
            return tolak
        if not token_akun_sah():
            flash("Halaman kadaluarsa. Buka ulang formulir, lalu simpan lagi.", "error")
            return redirect(url_for("pengguna"))
        try:
            password = akun_db.periksa_password(
                request.form.get("sandi_baru") or "",
                request.form.get("sandi_ulang") or "",
            )
            akun_db.buat(
                request.form.get("nama"),
                request.form.get("username"),
                password,
                request.form.getlist("portal"),
            )
        except akun_db.AkunError as exc:
            flash(str(exc), "error")
            return redirect(url_for("pengguna"))
        except pymysql.MySQLError:
            flash("Pengguna gagal ditambahkan.", "error")
            return redirect(url_for("pengguna"))
        flash("Pengguna ditambahkan. Username itu hanya membuka portal yang dicentang.", "info")
        return redirect(url_for("pengguna"))

    @app.route("/cadangan")
    def cadangan():
        tolak = wajib_admin()
        if tolak:
            return tolak
        session["pulih_token"] = secrets.token_urlsafe(24)
        try:
            daftar = cadangan_db.info_database()
        except pymysql.MySQLError:
            flash("Database belum siap. Jalankan python init_db.py di folder aplikasi.", "error")
            daftar = []
        return render_template(
            "cadangan.html",
            daftar=daftar,
            token=session["pulih_token"],
            format_ukuran=cadangan_db.format_ukuran,
        )

    @app.route("/cadangan/unduh")
    @app.route("/cadangan/unduh/<nama>")
    def unduh_cadangan(nama=None):
        tolak = wajib_admin()
        if tolak:
            return tolak
        if nama:
            if nama not in cadangan_db.nama_diizinkan():
                flash("Database itu bukan bagian dari SMARTMU.", "error")
                return redirect(url_for("cadangan"))
            pilihan = [nama]
        else:
            pilihan = [item["nama"] for item in cadangan_db.info_database() if item["ada"]]
        if not pilihan:
            flash("Tidak ada database yang dapat dicadangkan.", "error")
            return redirect(url_for("cadangan"))
        fd, jalur = tempfile.mkstemp(suffix=".sql", prefix="smartmu-cadangan-")
        os.close(fd)
        try:
            cadangan_db.tulis(jalur, pilihan)
        except cadangan_db.CadanganError as exc:
            os.remove(jalur)
            flash(str(exc), "error")
            return redirect(url_for("cadangan"))
        except Exception:
            os.remove(jalur)
            flash("Cadangan gagal dibuat.", "error")
            return redirect(url_for("cadangan"))

        respon = send_file(
            jalur,
            as_attachment=True,
            download_name=cadangan_db.nama_berkas(pilihan),
            mimetype="application/sql",
        )

        def bersihkan():
            try:
                os.remove(jalur)
            except OSError:
                pass

        respon.call_on_close(bersihkan)
        return respon

    @app.route("/cadangan/pulihkan", methods=["POST"])
    def pulihkan_cadangan():
        tolak = wajib_admin()
        if tolak:
            return tolak
        token = session.get("pulih_token") or ""
        kiriman = request.form.get("token") or ""
        if not token or not secrets.compare_digest(token, kiriman):
            flash("Halaman kadaluarsa. Buka ulang halaman cadangan, lalu unggah lagi.", "error")
            return redirect(url_for("cadangan"))
        if request.form.get("setuju") != "ya":
            flash("Centang persetujuan sebelum memulihkan cadangan.", "error")
            return redirect(url_for("cadangan"))
        berkas = request.files.get("berkas")
        if not berkas or not berkas.filename:
            flash("Pilih berkas cadangan berformat .sql.", "error")
            return redirect(url_for("cadangan"))
        if not berkas.filename.lower().endswith(".sql"):
            flash("Berkas harus berakhiran .sql.", "error")
            return redirect(url_for("cadangan"))
        fd, jalur = tempfile.mkstemp(suffix=".sql", prefix="smartmu-pulih-")
        try:
            with os.fdopen(fd, "wb") as tujuan:
                while True:
                    potong = berkas.stream.read(1024 * 1024)
                    if not potong:
                        break
                    tujuan.write(potong)
            cadangan_db.pulihkan(jalur)
        except cadangan_db.CadanganError as exc:
            flash(str(exc), "error")
            return redirect(url_for("cadangan"))
        except Exception:
            flash("Berkas cadangan tidak dapat dipulihkan.", "error")
            return redirect(url_for("cadangan"))
        finally:
            try:
                os.remove(jalur)
            except OSError:
                pass
        flash("Cadangan berhasil dipulihkan.", "info")
        return redirect(url_for("cadangan"))

    @app.errorhandler(RequestEntityTooLarge)
    def berkas_terlalu_besar(_exc):
        flash("Berkas cadangan terlalu besar. Batasnya 256 MB.", "error")
        return redirect(url_for("cadangan"))

    return app


def tautan_masuk(request):
    tujuan = request.script_root + request.full_path
    if tujuan.endswith("?"):
        tujuan = tujuan[:-1]
    return "/login?next=" + quote(tujuan, safe="/?=&")
