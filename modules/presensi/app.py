from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from datetime import datetime, timedelta
import calendar
import json
import os
import mimetypes
import re
import secrets
import time
from pathlib import Path

from import_excel import (
    lepaskan_gelar,
    nama_dengan_gelar,
    name_key,
    normalize_class,
    normalize_name,
    parse_workbook,
)

mimetypes.add_type("application/manifest+json", ".webmanifest")

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.secret_key = os.environ.get("SECRET_KEY", "smpm22_pamulang_secret")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "0") == "1",
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_NAME="smartmu_presensi",
    SESSION_COOKIE_PATH="/presensi",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=14),
)

GAGAL_LOGIN = {}

def aman_next(nilai):
    if nilai and nilai.startswith("/") and not nilai.startswith("//") and "\\" not in nilai:
        akar = request.script_root or ""
        if akar and nilai != akar and not nilai.startswith(akar + "/"):
            return akar + nilai
        return nilai
    return url_for("index")

def sama_rahasia(kiri, kanan):
    kiri = (kiri or "").encode()
    kanan = (kanan or "").encode()
    if len(kiri) != len(kanan):
        return False
    return secrets.compare_digest(kiri, kanan)

def token_csrf():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]

def cek_csrf():
    origin = request.headers.get("Origin", "")
    if origin and origin != request.host_url.rstrip("/"):
        abort(400)
    kiriman = request.form.get("csrf", "")
    tersimpan = session.get("csrf", "")
    if not tersimpan or not sama_rahasia(tersimpan, kiriman):
        abort(400)

KODE_ORTU = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def cocokkan_ortu(username, password):
    nama = (username or "").strip()
    if not nama or not password:
        return None
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, password_ortu FROM siswa
        WHERE LOWER(username_ortu) = LOWER(%s) AND aktif = 1 AND password_ortu IS NOT NULL
        LIMIT 1
    """, (nama,))
    siswa = cursor.fetchone()
    conn.close()
    if not siswa or not siswa["password_ortu"]:
        return None
    try:
        cocok = check_password_hash(siswa["password_ortu"], password)
    except ValueError:
        return None
    return siswa["id"] if cocok else None

def siswa_dengan_kode(nis, kode):
    nis = (nis or "").strip()
    kode = (kode or "").strip().upper()
    if not nis or not kode:
        return None
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nama, kode_ortu, username_ortu FROM siswa
        WHERE nis = %s AND aktif = 1 AND kode_ortu IS NOT NULL
        ORDER BY tahun DESC
        LIMIT 1
    """, (nis,))
    siswa = cursor.fetchone()
    conn.close()
    if siswa and sama_rahasia(kode, (siswa["kode_ortu"] or "").upper()):
        return siswa
    return None

def username_ortu_valid(nama, siswa_id):
    nama = " ".join((nama or "").split())
    if not re.fullmatch(r"[\w .'\-]{3,150}", nama, re.UNICODE):
        return "Username 3 sampai 150 karakter: huruf, angka, spasi, titik, atau garis."
    if nama.lower() == (os.environ.get("AUTH_USERNAME") or "").lower():
        return "Username itu tidak bisa dipakai."
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM siswa WHERE LOWER(username_ortu) = LOWER(%s) AND id <> %s LIMIT 1",
        (nama, siswa_id),
    )
    bentrok = cursor.fetchone()
    conn.close()
    if bentrok:
        return "Username sudah dipakai. Pilih yang lain."
    return ""

def simpan_akun_ortu(siswa_id, username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE siswa SET username_ortu = %s, password_ortu = %s WHERE id = %s",
        (username.strip(), generate_password_hash(password), siswa_id),
    )
    conn.commit()
    conn.close()

def kunci_ip(awalan):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    return awalan + ip

def terkunci(kunci):
    return GAGAL_LOGIN.get(kunci, {"n": 0, "sampai": 0})["sampai"] > time.time()

def catat_gagal(kunci):
    sekarang = time.time()
    catatan = GAGAL_LOGIN.get(kunci, {"n": 0, "sampai": 0})
    catatan["n"] += 1
    if catatan["n"] >= 8:
        catatan["sampai"] = sekarang + 15 * 60
        catatan["n"] = 0
    GAGAL_LOGIN[kunci] = catatan

def kode_ortu_baru(terpakai):
    while True:
        kode = "".join(secrets.choice(KODE_ORTU) for _ in range(6))
        if kode not in terpakai:
            terpakai.add(kode)
            return kode

@app.context_processor
def sisipkan_csrf():
    if session.get("masuk") or session.get("ortu_id"):
        return {"csrf": token_csrf()}
    return {"csrf": session.get("csrf", "")}

@app.after_request
def prefiks_tautan(respons):
    akar = request.script_root
    jenis = (respons.content_type or "").lower()
    if not akar or "text/html" not in jenis:
        return respons
    import re
    pola = re.compile(r"""(?P<awal>\b(?:href|action|src)\s*=\s*)(?P<kutip>['"])/(?P<jalur>[^'"]*)""")

    def ganti(cocok):
        jalur = cocok.group("jalur")
        if jalur.startswith(akar.strip("/") + "/"):
            return cocok.group(0)
        return f"{cocok.group('awal')}{cocok.group('kutip')}{akar}/{jalur}"

    tubuh = pola.sub(ganti, respons.get_data(as_text=True))
    respons.set_data(tubuh)
    return respons

@app.before_request
def jaga_akses():
    publik = request.endpoint in ("login", "daftar_ortu", "lupa_ortu", "static", "service_worker", "offline") or request.path.startswith("/static/")
    try:
        from sso import baca, boleh_data
        data = baca(request)
    except Exception:
        data = None
    if data and data.get("role") == "orang_tua":
        session["ortu_portal"] = True
        session["dari_portal"] = True
        session["ortu_nama"] = " ".join((data.get("username") or "").split())
        try:
            from portal.kelas_ortu import anak_ikut_tahfidz
            session["ikut_tahfidz"] = anak_ikut_tahfidz(session["ortu_nama"], data.get("id"))
        except Exception:
            session["ikut_tahfidz"] = False
        session.permanent = True
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(32)
        if not session.get("ortu_id"):
            anak = id_anak_pertama(session["ortu_nama"])
            if anak:
                session["ortu_id"] = anak
        if request.endpoint in ("static", "service_worker", "offline") or request.path.startswith("/static/"):
            return None
        if request.endpoint not in ("ortu_pengumuman", "ortu_hasil", "ortu_keluar"):
            return redirect("/presensi/ortu/pengumuman")
        if request.method == "POST":
            cek_csrf()
        return None
    if data and data.get("role") in {"guru_piket", "guru_bk", "guru_pengampu"}:
        session["guru_piket"] = data.get("role") == "guru_piket"
        session["guru_bk"] = data.get("role") == "guru_bk"
        session["guru_pengampu"] = data.get("role") == "guru_pengampu"
        session["guru_id"] = data.get("id")
        session["masuk"] = True
        session["dari_portal"] = True
        session.permanent = True
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(32)
        if data.get("role") == "guru_piket":
            try:
                from portal.guru_akun import mengajar_bk, punya_mapel
                session["guru_bk"] = mengajar_bk(data.get("id"))
                session["guru_mapel"] = punya_mapel(data.get("id"))
            except Exception:
                session["guru_bk"] = False
                session["guru_mapel"] = False
        else:
            session["guru_mapel"] = True
        if request.endpoint in ("static", "service_worker", "offline") or request.path.startswith("/static/"):
            return None
        if data.get("role") == "guru_piket":
            boleh = ("input_presensi", "tata_tertib", "laporan_harian", "rekap_bulanan", "hasil_belajar", "ganti_password_guru", "keluar")
            if request.endpoint not in boleh:
                return redirect("/presensi/presensi")
        elif request.endpoint not in ("hasil_belajar", "ganti_password_guru", "keluar"):
            tujuan = "/bk/" if data.get("role") == "guru_bk" else "/presensi/hasil-belajar"
            return redirect(tujuan)
        if request.method == "POST":
            cek_csrf()
        return None
    for kunci in ("guru_piket", "guru_bk", "guru_pengampu", "guru_mapel", "guru_id"):
        session.pop(kunci, None)
    if data and not boleh_data(data, "presensi"):
        if session.get("dari_portal"):
            session.pop("masuk", None)
            session.pop("dari_portal", None)
            session.pop("csrf", None)
        if not publik and not session.get("ortu_id"):
            return redirect("/?akses=presensi")
    elif data and not session.get("masuk") and not session.get("ortu_id") and not publik:
        session.permanent = True
        session["masuk"] = True
        session["dari_portal"] = True
        session["csrf"] = secrets.token_urlsafe(32)
    if request.endpoint in ("login", "daftar_ortu", "lupa_ortu", "ortu", "static", "service_worker", "offline") or request.path.startswith("/static/"):
        return None
    if session.get("ortu_id") and not session.get("masuk"):
        menu_ortu = ("ortu_pengumuman", "ortu_hasil", "ortu_keluar") if session.get("ortu_portal") else ("ortu_presensi", "ortu_tugas", "ortu_ulangan", "ortu_pengumuman", "ortu_keluar")
        if request.endpoint not in menu_ortu:
            return redirect(url_for("ortu_pengumuman" if session.get("ortu_portal") else "ortu_presensi"))
        if request.method == "POST":
            cek_csrf()
        return None
    if not session.get("masuk"):
        tujuan = request.full_path if request.query_string else request.path
        if tujuan.endswith("?"):
            tujuan = tujuan[:-1]
        return redirect(url_for("login", next=tujuan))
    if not (request.endpoint or "").startswith("ortu"):
        from sso import cegah_ubah
        tertahan = cegah_ubah(request, {"login", "daftar_ortu", "lupa_ortu", "keluar"})
        if tertahan is not None:
            return tertahan
    if request.method == "POST":
        origin = request.headers.get("Origin", "")
        if origin and origin != request.host_url.rstrip("/"):
            abort(400)
        kiriman = request.form.get("csrf", "")
        tersimpan = session.get("csrf", "")
        if not tersimpan or not sama_rahasia(tersimpan, kiriman):
            abort(400)
    return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("masuk"):
        return redirect(url_for("index"))
    if session.get("ortu_id"):
        return redirect(url_for("ortu_presensi"))
    token_csrf()
    salah = False
    if request.method == "POST":
        if not sama_rahasia(session.get("csrf", ""), request.form.get("csrf", "")):
            abort(400)
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
        sekarang = time.time()
        catatan = GAGAL_LOGIN.get(ip, {"n": 0, "sampai": 0})
        if catatan["sampai"] > sekarang:
            salah = True
        else:
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            akun = os.environ.get("AUTH_USERNAME", "")
            hash_tersimpan = os.environ.get("AUTH_PASSWORD_HASH", "")
            cocok = (
                bool(akun)
                and bool(hash_tersimpan)
                and sama_rahasia(username, akun)
                and check_password_hash(hash_tersimpan, password)
            )
            if cocok:
                session.clear()
                session.permanent = True
                session["masuk"] = True
                session["csrf"] = secrets.token_urlsafe(32)
                GAGAL_LOGIN.pop(ip, None)
                return redirect(aman_next(request.form.get("next") or request.args.get("next")))
            ortu_id = cocokkan_ortu(username, password)
            if ortu_id:
                session.clear()
                session.permanent = True
                session["ortu_id"] = ortu_id
                session["csrf"] = secrets.token_urlsafe(32)
                GAGAL_LOGIN.pop(ip, None)
                return redirect(url_for("ortu_presensi"))
            catatan["n"] += 1
            if catatan["n"] >= 8:
                catatan["sampai"] = sekarang + 15 * 60
                catatan["n"] = 0
            GAGAL_LOGIN[ip] = catatan
            salah = True
    lanjut = aman_next(request.values.get("next", "/"))
    return render_template("login.html", salah=salah, csrf=session["csrf"], next=lanjut)

@app.route("/daftar", methods=["GET", "POST"])
def daftar_ortu():
    if session.get("masuk"):
        return redirect(url_for("index"))
    if session.get("ortu_id"):
        return redirect(url_for("ortu_presensi"))
    token_csrf()
    pesan = ""
    if request.method == "POST":
        cek_csrf()
        kunci = kunci_ip("daftar:")
        if terkunci(kunci):
            pesan = "Terlalu banyak percobaan. Coba lagi nanti."
        else:
            siswa = siswa_dengan_kode(request.form.get("nis"), request.form.get("kode"))
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            ulang = request.form.get("ulang", "")
            if siswa is None:
                catat_gagal(kunci)
                pesan = "NIS atau kode sekolah tidak cocok."
            elif siswa["username_ortu"]:
                pesan = "Akun untuk siswa ini sudah ada. Masuk, atau atur ulang jika lupa."
            else:
                pesan = username_ortu_valid(username, siswa["id"])
                if not pesan and (len(password) < 6 or len(password) > 72):
                    pesan = "Password minimal 6 karakter."
                if not pesan and password != ulang:
                    pesan = "Password dan ulangan password tidak sama."
                if not pesan:
                    simpan_akun_ortu(siswa["id"], username, password)
                    GAGAL_LOGIN.pop(kunci, None)
                    flash("Akun tersimpan. Silakan masuk dengan username dan password yang baru dibuat.", "success")
                    return redirect(url_for("login"))
    return render_template("akun_ortu.html", mode="daftar", pesan=pesan, csrf=session["csrf"])

@app.route("/lupa", methods=["GET", "POST"])
def lupa_ortu():
    if session.get("masuk"):
        return redirect(url_for("index"))
    if session.get("ortu_id"):
        return redirect(url_for("ortu_presensi"))
    token_csrf()
    pesan = ""
    if request.method == "POST":
        cek_csrf()
        kunci = kunci_ip("lupa:")
        if terkunci(kunci):
            pesan = "Terlalu banyak percobaan. Coba lagi nanti."
        else:
            siswa = siswa_dengan_kode(request.form.get("nis"), request.form.get("kode"))
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            ulang = request.form.get("ulang", "")
            if siswa is None:
                catat_gagal(kunci)
                pesan = "NIS atau kode sekolah tidak cocok."
            else:
                pesan = username_ortu_valid(username, siswa["id"])
                if not pesan and (len(password) < 6 or len(password) > 72):
                    pesan = "Password minimal 6 karakter."
                if not pesan and password != ulang:
                    pesan = "Password dan ulangan password tidak sama."
                if not pesan:
                    simpan_akun_ortu(siswa["id"], username, password)
                    GAGAL_LOGIN.pop(kunci, None)
                    flash("Username dan password diperbarui. Silakan masuk.", "success")
                    return redirect(url_for("login"))
    return render_template("akun_ortu.html", mode="lupa", pesan=pesan, csrf=session["csrf"])

@app.route("/keluar", methods=["POST"])
def keluar():
    session.clear()
    return redirect("/logout")

@app.route("/sw.js")
def service_worker():
    respons = send_file(Path(app.root_path) / "static" / "sw.js", mimetype="application/javascript")
    respons.headers["Cache-Control"] = "no-cache"
    respons.headers["Service-Worker-Allowed"] = "/presensi/"
    return respons

@app.route("/offline")
def offline():
    return render_template("offline.html")

JENIS_PELANGGARAN = [
    "Seragam tidak lengkap",
    "Atribut tidak sesuai",
    "Rambut tidak sesuai",
    "Kuku tidak sesuai",
    "Sepatu tidak sesuai",
    "Membawa HP",
    "Tidak mengikuti upacara",
    "Keluar tanpa izin",
    "Tidak membawa perlengkapan",
    "Bersikap tidak sopan",
    "Lainnya",
]

def get_db_connection():
    try:
        from pengaturan import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USER, PRESENSI_DATABASE
        host, port, user, password, database = (
            MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, PRESENSI_DATABASE,
        )
    except Exception:
        host = os.environ.get("DB_HOST", "127.0.0.1")
        port = int(os.environ.get("DB_PORT", "3306"))
        user = os.environ.get("DB_USER", "root")
        password = os.environ.get("DB_PASSWORD", "")
        database = os.environ.get("DB_NAME", "db_presensi_smpm22")
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )
    ensure_schema(conn)
    return conn

def ensure_schema(conn):
    if getattr(ensure_schema, "done", False):
        return
    cursor = conn.cursor()
    cursor.execute("SHOW COLUMNS FROM siswa LIKE 'aktif'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE siswa ADD COLUMN aktif TINYINT(1) NOT NULL DEFAULT 1")
        conn.commit()
    cursor.execute("SHOW COLUMNS FROM siswa LIKE 'tahun'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE siswa ADD COLUMN tahun INT NOT NULL DEFAULT 2026")
        conn.commit()
    cursor.execute("SHOW COLUMNS FROM presensi LIKE 'terlambat'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE presensi ADD COLUMN terlambat TINYINT(1) NOT NULL DEFAULT 0")
        conn.commit()
    for column, ddl in (
        ("jam_terlambat", "ALTER TABLE presensi ADD COLUMN jam_terlambat VARCHAR(5) NOT NULL DEFAULT ''"),
        ("izin_pulang", "ALTER TABLE presensi ADD COLUMN izin_pulang TINYINT(1) NOT NULL DEFAULT 0"),
        ("jam_pulang", "ALTER TABLE presensi ADD COLUMN jam_pulang VARCHAR(5) NOT NULL DEFAULT ''"),
        ("alasan_pulang", "ALTER TABLE presensi ADD COLUMN alasan_pulang VARCHAR(255) NOT NULL DEFAULT ''"),
    ):
        cursor.execute("SHOW COLUMNS FROM presensi LIKE %s", (column,))
        if cursor.fetchone() is None:
            cursor.execute(ddl)
            conn.commit()
    cursor.execute("SHOW TABLES LIKE 'pelanggaran'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE pelanggaran (
                id INT AUTO_INCREMENT PRIMARY KEY,
                siswa_id INT NOT NULL,
                tanggal DATE NOT NULL,
                jenis VARCHAR(80) NOT NULL,
                keterangan VARCHAR(255) NOT NULL DEFAULT '',
                KEY idx_pelanggaran_tanggal (tanggal),
                KEY idx_pelanggaran_siswa (siswa_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    cursor.execute("SHOW TABLES LIKE 'laporan_piket'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE laporan_piket (
                tanggal DATE PRIMARY KEY,
                tim_penyambut VARCHAR(80) NOT NULL DEFAULT '',
                guru_hadir VARCHAR(40) NOT NULL DEFAULT '',
                guru_tidak_hadir VARCHAR(120) NOT NULL DEFAULT '',
                guru_pelatihan VARCHAR(40) NOT NULL DEFAULT '',
                guru_terlambat VARCHAR(120) NOT NULL DEFAULT '',
                guru_izin_pulang VARCHAR(40) NOT NULL DEFAULT '',
                kelas_kosong VARCHAR(40) NOT NULL DEFAULT '',
                catatan TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    cursor.execute("SHOW TABLES LIKE 'guru'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE guru (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nama VARCHAR(120) NOT NULL,
                urutan INT NOT NULL,
                aktif TINYINT(1) NOT NULL DEFAULT 1,
                UNIQUE KEY uniq_guru_nama (nama)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    cursor.execute("SHOW TABLES LIKE 'guru_kelas'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE guru_kelas (
                guru_id INT NOT NULL,
                kelas_id INT NOT NULL,
                mapel VARCHAR(40) NOT NULL DEFAULT '',
                PRIMARY KEY (guru_id, kelas_id, mapel)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    cursor.execute("SHOW COLUMNS FROM guru_kelas LIKE 'mapel'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE guru_kelas DROP PRIMARY KEY")
        cursor.execute("ALTER TABLE guru_kelas ADD COLUMN mapel VARCHAR(40) NOT NULL DEFAULT ''")
        cursor.execute("ALTER TABLE guru_kelas ADD PRIMARY KEY (guru_id, kelas_id, mapel)")
        conn.commit()
    cursor.execute("SHOW COLUMNS FROM kelas LIKE 'wali_guru_id'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE kelas ADD COLUMN wali_guru_id INT NULL")
        conn.commit()
    cursor.execute("SHOW TABLES LIKE 'presensi_guru'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE presensi_guru (
                guru_id INT NOT NULL,
                tanggal DATE NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'Hadir',
                alasan VARCHAR(120) NOT NULL DEFAULT '',
                terlambat TINYINT(1) NOT NULL DEFAULT 0,
                izin_pulang TINYINT(1) NOT NULL DEFAULT 0,
                PRIMARY KEY (guru_id, tanggal)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    cursor.execute("SELECT nama, urutan FROM guru")
    sudah = cursor.fetchall()
    punya_nama = {row[0] for row in sudah}
    punya_urutan = {row[1] for row in sudah}
    for urutan, nama in enumerate(DAFTAR_GURU, start=1):
        if nama in punya_nama or urutan in punya_urutan:
            continue
        cursor.execute(
            "INSERT INTO guru (nama, urutan, aktif) VALUES (%s, %s, 1)",
            (nama, urutan),
        )
    conn.commit()
    cursor.execute("SHOW TABLES LIKE 'guru_piket'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE guru_piket (
                hari TINYINT NOT NULL,
                urutan TINYINT NOT NULL,
                guru_id INT NOT NULL,
                PRIMARY KEY (hari, urutan)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    isi_dari_jadwal(cursor)
    isi_piket(cursor)
    conn.commit()
    cursor.execute("SHOW COLUMNS FROM siswa LIKE 'kode_ortu'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE siswa ADD COLUMN kode_ortu VARCHAR(8) NULL")
        cursor.execute("CREATE UNIQUE INDEX uniq_siswa_kode ON siswa (kode_ortu)")
        conn.commit()
    cursor.execute("SHOW COLUMNS FROM siswa LIKE 'username_ortu'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE siswa ADD COLUMN username_ortu VARCHAR(150) NULL")
        cursor.execute("ALTER TABLE siswa ADD COLUMN password_ortu VARCHAR(255) NULL")
        conn.commit()
    else:
        cursor.execute("SHOW INDEX FROM siswa WHERE Key_name = 'uniq_siswa_username_ortu'")
        if cursor.fetchone() is not None:
            cursor.execute("ALTER TABLE siswa DROP INDEX uniq_siswa_username_ortu")
            conn.commit()
        cursor.execute(
            "SELECT CHARACTER_MAXIMUM_LENGTH FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'siswa' AND COLUMN_NAME = 'username_ortu'"
        )
        ukuran = cursor.fetchone()
        if ukuran and ukuran[0] and int(ukuran[0]) < 150:
            cursor.execute("ALTER TABLE siswa MODIFY username_ortu VARCHAR(150) NULL")
            conn.commit()
    cursor.execute("SHOW COLUMNS FROM siswa LIKE 'nama_orang_tua'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE siswa ADD COLUMN nama_orang_tua VARCHAR(150) NULL")
        conn.commit()
    cursor.execute("SHOW TABLES LIKE 'hasil_belajar'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE hasil_belajar (
                id INT AUTO_INCREMENT PRIMARY KEY,
                kelas_id INT NOT NULL,
                tanggal DATE NOT NULL,
                mapel VARCHAR(60) NOT NULL,
                materi VARCHAR(800) NOT NULL DEFAULT '',
                tugas VARCHAR(400) NOT NULL DEFAULT '',
                ulangan TINYINT(1) NOT NULL DEFAULT 0,
                ulangan_ket VARCHAR(200) NOT NULL DEFAULT '',
                UNIQUE KEY uniq_hasil (kelas_id, tanggal, mapel)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    cursor.execute("SHOW COLUMNS FROM hasil_belajar LIKE 'ulangan'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE hasil_belajar ADD COLUMN ulangan TINYINT(1) NOT NULL DEFAULT 0")
        cursor.execute("ALTER TABLE hasil_belajar ADD COLUMN ulangan_ket VARCHAR(200) NOT NULL DEFAULT ''")
        conn.commit()
    cursor.execute("SHOW TABLES LIKE 'catatan_ortu'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE catatan_ortu (
                siswa_id INT NOT NULL,
                tanggal DATE NOT NULL,
                catatan VARCHAR(400) NOT NULL,
                PRIMARY KEY (siswa_id, tanggal)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    cursor.execute("SHOW TABLES LIKE 'pengumuman'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE pengumuman (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tanggal DATE NOT NULL,
                judul VARCHAR(120) NOT NULL,
                isi TEXT NOT NULL,
                kelas_id INT NULL,
                KEY idx_pengumuman_tanggal (tanggal)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    cursor.execute("SHOW TABLES LIKE 'pengumuman_kelas'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE pengumuman_kelas (
                pengumuman_id INT NOT NULL,
                kelas_id INT NOT NULL,
                PRIMARY KEY (pengumuman_id, kelas_id),
                KEY idx_pengumuman_kelas_kelas (kelas_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        cursor.execute("""
            INSERT IGNORE INTO pengumuman_kelas (pengumuman_id, kelas_id)
            SELECT id, kelas_id FROM pengumuman WHERE kelas_id IS NOT NULL
        """)
        conn.commit()
    ensure_schema.done = True

DAFTAR_GURU = [
    "Ikhsan Saepul Munir, S.Pd.",
    "Yunus Anis, M.Pd.",
    "Roni Boan Elarika, M. Pd.",
    "Indratni Khair, S.Ag.",
    "Rohidah, S. Pd.",
    "Susilistari, SE.",
    "Roy Tarumanjaya, S.Kom.",
    "Mulyadi Hikmah, S.Kom., S.Pd.",
    "Deny Asmara, S.Pd.",
    "Maryono, S.Pd.",
    "Rina Herliani, S.Pd.",
    "Faizal Haizar, S.H.I.",
    "Eda Nurhaedah, S.Pd.",
    "Ilham",
    "Faizah Adisty, M.Pd.",
    "Jamsiah, S.Pd.",
    "Nurul Mizani, S.Pd.",
    "Ade Julia Safitri, S.Pd.I",
    "Bhisma Satria Pamungkas, S.P.",
    "Mauliza Ahmad, S.Pd",
    "Agita Daimon, S.Pd.",
    "Alriefan Rachmadi, S.Pd.",
    "Sa`diah Sari Hasanah, S.Pd.",
    "Nelsa Nurul Hamidah, S.Pd.",
    "Agus Salim, M.Pd.",
    "Hermanida, S.Pd.",
    "Yoga Parenta, M.Pd.",
    "Susilo Meisyarjo, Amd.Kom",
    "Meutia Khanza, M.Pd.",
    "Muhammad Sofyan",
]

PIKET_HARIAN = {
    0: ["Yunus Anis, M.Pd.", "Eda Nurhaedah, S.Pd.", "Maryono, S.Pd."],
    1: ["Meutia Khanza, M.Pd.", "Agus Salim, M.Pd.", "Sa`diah Sari Hasanah, S.Pd."],
    2: ["Yoga Parenta, M.Pd.", "Jamsiah, S.Pd.", "Susilo Meisyarjo, Amd.Kom"],
    3: ["Roy Tarumanjaya, S.Kom.", "Hermanida, S.Pd.", "Bhisma Satria Pamungkas, S.P."],
    4: ["Nelsa Nurul Hamidah, S.Pd.", "Agita Daimon, S.Pd.", "Mauliza Ahmad, S.Pd"],
}

def guru_piket_hari(cursor, tanggal):
    if isinstance(tanggal, str):
        tanggal = datetime.strptime(tanggal, "%Y-%m-%d")
    hari = tanggal.weekday()
    if hari > 4:
        return []
    cursor.execute("""
        SELECT g.nama
        FROM guru_piket p
        JOIN guru g ON g.id = p.guru_id AND g.aktif = 1
        WHERE p.hari = %s
        ORDER BY p.urutan
    """, (hari,))
    return [row["nama"] for row in cursor.fetchall()]

NAMA_HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
NAMA_BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

def pecah_kelas(teks):
    if not teks or str(teks).strip().upper() == "F":
        return []
    teks = str(teks).replace("&", ",")
    import re
    teks = re.sub(r"(\d\.\d)\.", r"\1,", teks)
    hasil = []
    for bagian in teks.split(","):
        bagian = bagian.strip()
        rentang = re.match(r"(\d+)\.(\d+)\s*-\s*(\d+)\.(\d+)", bagian)
        if rentang:
            awal, dari, akhir, sampai = (int(angka) for angka in rentang.groups())
            if awal == akhir:
                hasil.extend(f"{awal}.{n}" for n in range(dari, sampai + 1))
            continue
        rentang = re.match(r"(\d+)\.(\d+)\s*-\s*(\d+)$", bagian)
        if rentang:
            tingkat, dari, sampai = (int(angka) for angka in rentang.groups())
            hasil.extend(f"{tingkat}.{n}" for n in range(dari, sampai + 1))
            continue
        satu = re.match(r"(\d+)\.(\d+)", bagian)
        if satu:
            hasil.append(f"{int(satu.group(1))}.{int(satu.group(2))}")
    return hasil

def cocok_guru(nama_jadwal, daftar):
    import re
    gelar = {"spd", "sag", "spdi", "shi", "se", "skom", "mpd", "sp", "amd", "amdkom", "kom", "pd", "ag"}

    def token(nama):
        bersih = re.sub(r"[^a-z0-9 ]", " ", nama.lower().replace("`", ""))
        return [kata for kata in bersih.split() if kata not in gelar]

    cari = token(nama_jadwal)
    if not cari:
        return None
    for guru in daftar:
        punya = token(guru["nama"])
        if punya[0] == cari[0] and (len(punya) == 1 or len(cari) == 1 or punya[1][:4] == cari[1][:4]):
            return guru
    satu = [guru for guru in daftar if token(guru["nama"])[:1] == cari[:1]]
    if len(satu) == 1:
        return satu[0]
    calon = [
        guru for guru in daftar
        if token(guru["nama"]) and len(cari[0]) >= 4 and token(guru["nama"])[0][:4] == cari[0][:4]
    ]
    if len(calon) == 1:
        return calon[0]
    return None

JADWAL_MENGAJAR = [
    ("Yunus Anis, M.Pd.", "Al Islam", "8.1. 8.2, 8.3, 8.4, 8.5, 9.5"),
    ("Roni Boan Elarika, M. Pd.", "Bahasa Indonesia", "7.1, 7.2, 8.4, 8.5, 9.1, 9.2"),
    ("Indratni Khair, S.Ag.", "Al Islam", ""),
    ("Rohidah, S. Pd.", "Bhs. Inggris", "8.2, 8.3"),
    ("Susilistari, SE.", "IPS Terpadu", "7.1- 7.6, 8.1, 8.2"),
    ("Roy Tarumanjaya, S.Kom.", "Informatika", "7.1 - 7.6, 8.4, 8.5, 9.1 - 9.5"),
    ("Roy Tarumanjaya, S.Kom.", "Koding", "7.5, 8.5"),
    ("Mulyadi Hikmah, S.Kom.", "PJOK", "7.1 - 7.6, 8.1 - 8.5, 9.1 - 9.5"),
    ("Deny Asmara, S.Pd.", "Bahasa Indonesia", "8.3, 9.3, 9.4, 9.5"),
    ("Maryono, S.Pd.", "Bahasa Inggris", "7.5, 8.4, 8.5 & 9.1 - 9.5"),
    ("Rina Herliani, S.Pd.", "IPA Terpadu", "7.1, 7.2, 9.1 - 9.5"),
    ("Faizal Haizar, S.H.I.", "Al Islam", "9.1, 9.2, 9.4"),
    ("Eda Nurhaedah, S.Pd.", "Matematika", "8.1, 8.2, 8.3, 8.4, 8.5, 9.5"),
    ("Ilham", "Tapak Suci", "7.1 - 7.6, 8.1 - 8.5, 9.1 - 9.5"),
    ("Faizah Adisty, M.Pd.", "Matematika", "7.4 -7.6, 9.1 - 9.4"),
    ("Jamsiah, S.Pd.", "PPKn", "7.1, 7.2, 7.3, 7.6, 8.1 - 8.5, 9.1 - 9.5"),
    ("Nurul Mizani, S.Pd.", "Bahasa Indonesia", "7.3, 7.4, 7.5, 7.6, 8.1, 8.2"),
    ("Ade Julia Safitri, S.Pd.I", "Bahasa Arab", "7.1 - 7.6, 8.1 - 8.5, 9.1 - 9.5"),
    ("Bhisma Satria Pamungkas, S.P.", "Seni Budaya", "7.1 - 7.6, 8.1 - 8.5, 9.1 - 9.5"),
    ("Mauliza Ahmad, S.Pd", "IPA Terpadu", "7.3 - 7.5, 8.2 - 8.5"),
    ("Agita Daimon, S.Pd.", "Kemuhammadiyahan", "7.1 - 7.6, 8.1 - 8.5, 9.1 - 9.5"),
    ("Alriefan Rachmadi, S.Pd.", "IPS Terpadu", "8.3 - 8.5, 9.1 - 9.5"),
    ("Sa`diah Sari Hasanah, S.Pd.", "BK", "8.3 - 8.5, 9.1 - 9.5"),
    ("Nelsa Nurul Hamidah, S.Pd.", "BK", "7.1 - 7.6 & 8.1, 8.2"),
    ("Agus Salim, M.Pd.", "Tahfidz", "7.3, 8.3, 9.3"),
    ("Hermanida, S.Pd.", "Tahfidz", "7.3, 8.3, 9.3"),
    ("Yoga Parenta, M.Pd.", "IPA Terpadu", "7.6, 8.1"),
    ("Yoga Parenta, M.Pd.", "Matematika", "7.1, 7.2, 7.3"),
    ("Susilo Meisyarjo, Amd.Kom", "Informatika", "8.1, 8.2, 8.3"),
    ("Susilo Meisyarjo, Amd.Kom", "Koding", "7.1, 7.2, 7.3, 7.4, 7.6"),
    ("Susilo Meisyarjo, Amd.Kom", "Desain Grafis", "7.5, 8.5"),
    ("Susilo Meisyarjo, Amd.Kom", "Broadcasting", "7.5, 8.5"),
    ("Meutia Khanza, M.Pd.", "Bahasa Inggris", "7.1, 7.2, 7.3, 7.4, 7.6, 8.1"),
    ("Muhammad Sofyan", "PPKn", "7.4, 7.5"),
]

WALI_KELAS = [
    ("7.1", "Roni Boan Elarika, M.Pd."),
    ("7.2", "Susilistari, S.E."),
    ("7.3", "Ade Julia Safitri, S.Pd.I."),
    ("7.4", "Rina Herliani, S.Pd."),
    ("7.5", "Roy Tarumanjay, S.Kom"),
    ("7.6", "Agita Daimon, S.Pd."),
    ("8.1", "Nurul Mizani, S.Pd."),
    ("8.2", "Jamsiyah, S.Pd."),
    ("8.3", "Yunus Anis, M.Pd."),
    ("8.4", "Mauliza Ahmad, S.Pd."),
    ("8.5", "Mulyadi Hikmah, S.Kom"),
    ("9.1", "Maryono, S.Pd."),
    ("9.2", "Bhisma Satria P, S.P."),
    ("9.3", "Indratni Khair, S.Ag."),
    ("9.4", "Alriefan Rachmadi, S.Pd."),
    ("9.5", "Rina Herliani, S.Pd."),
]

def isi_piket(cursor):
    cursor.execute("SELECT COUNT(*) FROM guru_piket")
    if cursor.fetchone()[0]:
        return
    cursor.execute("SELECT id, nama FROM guru WHERE aktif = 1")
    daftar = [{"id": row[0], "nama": row[1]} for row in cursor.fetchall()]
    for hari, nama_list in PIKET_HARIAN.items():
        for urutan, nama in enumerate(nama_list, start=1):
            guru = cocok_guru(nama, daftar)
            if guru is None:
                continue
            cursor.execute(
                "INSERT INTO guru_piket (hari, urutan, guru_id) VALUES (%s, %s, %s)",
                (hari, urutan, guru["id"]),
            )

def isi_dari_jadwal(cursor):
    cursor.execute("SELECT COUNT(*) FROM guru_kelas")
    if cursor.fetchone()[0]:
        return
    cursor.execute("SELECT id, nama FROM guru WHERE aktif = 1")
    daftar = [{"id": row[0], "nama": row[1]} for row in cursor.fetchall()]
    cursor.execute("SELECT id, nama_kelas FROM kelas")
    kelas = {row[1]: row[0] for row in cursor.fetchall()}
    for nama, mapel, teks in JADWAL_MENGAJAR:
        guru = cocok_guru(nama, daftar)
        if guru is None:
            continue
        for nama_kelas in pecah_kelas(teks):
            kelas_id = kelas.get(nama_kelas)
            if kelas_id is None:
                continue
            cursor.execute(
                "INSERT IGNORE INTO guru_kelas (guru_id, kelas_id, mapel) VALUES (%s, %s, %s)",
                (guru["id"], kelas_id, mapel),
            )
    cursor.execute("SELECT COUNT(*) FROM kelas WHERE wali_guru_id IS NOT NULL")
    if cursor.fetchone()[0]:
        return
    for nama_kelas, nama in WALI_KELAS:
        guru = cocok_guru(nama, daftar)
        kelas_id = kelas.get(nama_kelas)
        if guru and kelas_id:
            cursor.execute("UPDATE kelas SET wali_guru_id = %s WHERE id = %s", (guru["id"], kelas_id))

def urut_kelas(nama):
    bagian = []
    for pecah in str(nama).split("."):
        bagian.append(int(pecah) if pecah.isdigit() else pecah)
    return bagian

def label_hari(tanggal):
    if isinstance(tanggal, str):
        tanggal = datetime.strptime(tanggal, "%Y-%m-%d")
    return f"{NAMA_HARI[tanggal.weekday()]}, {tanggal.day} {NAMA_BULAN[tanggal.month]} {tanggal.year}"

def tahun_ajaran_dari(tanggal):
    if isinstance(tanggal, str):
        tanggal = datetime.strptime(tanggal, "%Y-%m-%d")
    return tanggal.year if tanggal.month >= 7 else tanggal.year - 1

def import_tmp_dir():
    path = Path(os.environ.get("IMPORT_TMP", str(Path(__file__).resolve().parent / "_tmp")))
    path.mkdir(parents=True, exist_ok=True)
    return path

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kelas ORDER BY nama_kelas ASC")
    daftar_kelas = cursor.fetchall()
    conn.close()
    return render_template('index.html', kelas_list=daftar_kelas)

# Form Input Presensi Harian Guru Piket
@app.route('/presensi', methods=['GET', 'POST'])
def input_presensi():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    selected_kelas = request.args.get('kelas_id')
    selected_tanggal = request.args.get('tanggal', datetime.now().strftime('%Y-%m-%d'))
    
    if request.method == 'POST':
        selected_kelas = request.form.get('kelas_id')
        selected_tanggal = request.form.get('tanggal')
        
        ajaran = tahun_ajaran_dari(selected_tanggal)
        cursor.execute(
            "SELECT id FROM siswa WHERE kelas_id = %s AND tahun = %s AND aktif = 1",
            (selected_kelas, ajaran),
        )
        siswa_list = cursor.fetchall()
        
        for siswa in siswa_list:
            status = request.form.get(f'status_{siswa["id"]}', 'Hadir')
            keterangan = request.form.get(f'ket_{siswa["id"]}', '')
            terlambat = 1 if status == 'Hadir' and request.form.get(f'terlambat_{siswa["id"]}') else 0
            jam_terlambat = request.form.get(f'jam_terlambat_{siswa["id"]}', '')[:5] if terlambat else ''
            izin_pulang = 1 if status == 'Hadir' and request.form.get(f'pulang_{siswa["id"]}') else 0
            jam_pulang = request.form.get(f'jam_pulang_{siswa["id"]}', '')[:5] if izin_pulang else ''
            alasan_pulang = request.form.get(f'alasan_pulang_{siswa["id"]}', '')[:255] if izin_pulang else ''
            
            cursor.execute("""
                INSERT INTO presensi (siswa_id, tanggal, status, keterangan, terlambat, jam_terlambat, izin_pulang, jam_pulang, alasan_pulang)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    status = VALUES(status),
                    keterangan = VALUES(keterangan),
                    terlambat = VALUES(terlambat),
                    jam_terlambat = VALUES(jam_terlambat),
                    izin_pulang = VALUES(izin_pulang),
                    jam_pulang = VALUES(jam_pulang),
                    alasan_pulang = VALUES(alasan_pulang)
            """, (
                siswa['id'], selected_tanggal, status, keterangan, terlambat,
                jam_terlambat, izin_pulang, jam_pulang, alasan_pulang,
            ))
            
        conn.commit()
        flash('Data presensi berhasil disimpan!', 'success')
        return redirect(url_for('input_presensi', kelas_id=selected_kelas, tanggal=selected_tanggal))

    cursor.execute("SELECT * FROM kelas ORDER BY nama_kelas ASC")
    daftar_kelas = cursor.fetchall()
    
    siswa_presensi = []
    if selected_kelas:
        cursor.execute("""
            SELECT s.id, s.nis, s.nama, s.jenis_kelamin, 
                   COALESCE(p.status, 'Hadir') as status, 
                   COALESCE(p.keterangan, '') as keterangan,
                   COALESCE(p.terlambat, 0) as terlambat,
                   COALESCE(p.jam_terlambat, '') as jam_terlambat,
                   COALESCE(p.izin_pulang, 0) as izin_pulang,
                   COALESCE(p.jam_pulang, '') as jam_pulang,
                   COALESCE(p.alasan_pulang, '') as alasan_pulang
            FROM siswa s
            LEFT JOIN presensi p ON s.id = p.siswa_id AND p.tanggal = %s
            WHERE s.kelas_id = %s AND s.tahun = %s AND s.aktif = 1
            ORDER BY s.nama ASC
        """, (selected_tanggal, selected_kelas, tahun_ajaran_dari(selected_tanggal)))
        siswa_presensi = cursor.fetchall()
        
    conn.close()
    return render_template('presensi.html', kelas_list=daftar_kelas, siswa_list=siswa_presensi, 
                           selected_kelas=selected_kelas, selected_tanggal=selected_tanggal)

# Laporan Harian
@app.route('/laporan-harian', methods=['GET', 'POST'])
def laporan_harian():
    tanggal = request.values.get('tanggal', datetime.now().strftime('%Y-%m-%d'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cursor.execute("""
            INSERT INTO laporan_piket (tanggal, tim_penyambut, kelas_kosong, catatan)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                tim_penyambut = VALUES(tim_penyambut),
                kelas_kosong = VALUES(kelas_kosong),
                catatan = VALUES(catatan)
        """, (
            tanggal,
            request.form.get('tim_penyambut', '')[:80],
            request.form.get('kelas_kosong', '')[:40],
            request.form.get('catatan', '').strip(),
        ))
        for guru_id in request.form.getlist('guru_id'):
            status = request.form.get(f'gstatus_{guru_id}', 'Hadir')
            if status not in ('Hadir', 'Tidak Hadir', 'Pelatihan'):
                status = 'Hadir'
            terlambat = 1 if status == 'Hadir' and request.form.get(f'gterlambat_{guru_id}') else 0
            izin_pulang = 1 if status == 'Hadir' and request.form.get(f'gpulang_{guru_id}') else 0
            alasan = request.form.get(f'galasan_{guru_id}', '')[:120] if status != 'Hadir' else ''
            cursor.execute("""
                INSERT INTO presensi_guru (guru_id, tanggal, status, alasan, terlambat, izin_pulang)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    status = VALUES(status),
                    alasan = VALUES(alasan),
                    terlambat = VALUES(terlambat),
                    izin_pulang = VALUES(izin_pulang)
            """, (guru_id, tanggal, status, alasan, terlambat, izin_pulang))
        conn.commit()
        flash('Laporan harian piket disimpan.', 'success')
        conn.close()
        return redirect(url_for('laporan_harian', tanggal=tanggal))

    cursor.execute("""
        SELECT k.nama_kelas, s.nama, p.status, p.keterangan, p.terlambat,
               p.jam_terlambat, p.izin_pulang, p.jam_pulang, p.alasan_pulang
        FROM presensi p
        JOIN siswa s ON p.siswa_id = s.id
        JOIN kelas k ON s.kelas_id = k.id
        WHERE p.tanggal = %s
        ORDER BY k.nama_kelas, s.nama
    """, (tanggal,))
    laporan = cursor.fetchall()
    cursor.execute("""
        SELECT k.nama_kelas, s.nama, p.jenis, p.keterangan
        FROM pelanggaran p
        JOIN siswa s ON p.siswa_id = s.id
        JOIN kelas k ON s.kelas_id = k.id
        WHERE p.tanggal = %s
        ORDER BY k.nama_kelas, s.nama, p.id
    """, (tanggal,))
    pelanggaran = cursor.fetchall()
    cursor.execute("SELECT * FROM laporan_piket WHERE tanggal = %s", (tanggal,))
    piket = cursor.fetchone() or {
        "tim_penyambut": "", "kelas_kosong": "", "catatan": "",
    }
    cursor.execute("""
        SELECT g.id, g.nama, g.urutan,
               p.status, p.alasan, p.terlambat, p.izin_pulang
        FROM guru g
        LEFT JOIN presensi_guru p ON p.guru_id = g.id AND p.tanggal = %s
        WHERE g.aktif = 1
        ORDER BY g.urutan, g.nama
    """, (tanggal,))
    daftar_guru = cursor.fetchall()
    cursor.execute("""
        SELECT gk.guru_id, gk.mapel, k.nama_kelas
        FROM guru_kelas gk
        JOIN kelas k ON k.id = gk.kelas_id
    """)
    kelas_guru = {}
    for row in cursor.fetchall():
        kelas_guru.setdefault(row["guru_id"], {}).setdefault(row["mapel"] or "", []).append(row["nama_kelas"])
    for guru in daftar_guru:
        bagian = []
        for mapel, nama_kelas in kelas_guru.get(guru["id"], {}).items():
            daftar = ", ".join(sorted(set(nama_kelas), key=urut_kelas))
            bagian.append(f"{mapel}: {daftar}" if mapel else daftar)
        guru["kelas"] = "; ".join(bagian)
        if guru["status"] is None:
            guru["status"] = "Hadir"
            guru["alasan"] = ""
            guru["terlambat"] = 0
            guru["izin_pulang"] = 0
    cursor.execute("SELECT COUNT(*) AS n FROM presensi_guru WHERE tanggal = %s", (tanggal,))
    sudah_guru = cursor.fetchone()["n"] > 0
    nama_piket = guru_piket_hari(cursor, tanggal)
    conn.close()

    terlambat = [row for row in laporan if row["status"] == "Hadir" and row["terlambat"]]
    pulang = [row for row in laporan if row["status"] == "Hadir" and row["izin_pulang"]]
    tidak_hadir = [row for row in laporan if row["status"] in ("Sakit", "Izin", "Alpa")]
    per_kelas = {}
    for row in tidak_hadir:
        per_kelas.setdefault(row["nama_kelas"], []).append(row)

    kelas_absen = sorted(per_kelas.items(), key=lambda item: urut_kelas(item[0]))
    sakit = sum(1 for row in tidak_hadir if row["status"] == "Sakit")
    izin = sum(1 for row in tidak_hadir if row["status"] == "Izin")
    alpa = sum(1 for row in tidak_hadir if row["status"] == "Alpa")

    return render_template(
        'laporan_harian.html',
        tanggal=tanggal,
        hari_tanggal=label_hari(tanggal),
        terlambat=terlambat,
        pulang=pulang,
        tidak_hadir=tidak_hadir,
        kelas_absen=kelas_absen,
        sakit=sakit,
        izin=izin,
        alpa=alpa,
        pelanggaran=pelanggaran,
        piket=piket,
        guru_piket=nama_piket,
        daftar_guru=daftar_guru,
        sudah_guru=sudah_guru,
        guru_hadir=sum(1 for guru in daftar_guru if sudah_guru and guru["status"] == "Hadir"),
        guru_absen=[guru for guru in daftar_guru if sudah_guru and guru["status"] == "Tidak Hadir"],
        guru_pelatihan=[guru for guru in daftar_guru if sudah_guru and guru["status"] == "Pelatihan"],
        guru_telat=[guru for guru in daftar_guru if sudah_guru and guru["status"] == "Hadir" and guru["terlambat"]],
        guru_pulang=[guru for guru in daftar_guru if sudah_guru and guru["status"] == "Hadir" and guru["izin_pulang"]],
    )

NAMA_BULAN = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

def rekap_satu_bulan(cursor, kelas_id, bulan, tahun):
    ajaran = tahun if bulan >= 7 else tahun - 1
    cursor.execute(
        "SELECT id, nis, nama FROM siswa WHERE kelas_id = %s AND tahun = %s AND aktif = 1 ORDER BY nama ASC",
        (kelas_id, ajaran),
    )
    siswa_list = cursor.fetchall()
    catatan = {}
    if siswa_list:
        ids = [siswa["id"] for siswa in siswa_list]
        tanda = ", ".join(["%s"] * len(ids))
        cursor.execute(
            f"""
            SELECT siswa_id, DAY(tanggal) AS hari, status, terlambat
            FROM presensi
            WHERE siswa_id IN ({tanda}) AND MONTH(tanggal) = %s AND YEAR(tanggal) = %s
            """,
            (*ids, bulan, tahun),
        )
        for rekaman in cursor.fetchall():
            catatan.setdefault(rekaman["siswa_id"], []).append(rekaman)
    rekap_data = []
    for siswa in siswa_list:
        row = {"nama": siswa["nama"], "nis": siswa["nis"], "presensi": {}, "H": 0, "T": 0, "I": 0, "S": 0, "A": 0}
        for rekaman in catatan.get(siswa["id"], []):
            huruf = rekaman["status"][0]
            if rekaman["status"] == "Hadir" and rekaman["terlambat"]:
                row["presensi"][rekaman["hari"]] = "T"
                row["H"] += 1
                row["T"] += 1
            else:
                row["presensi"][rekaman["hari"]] = huruf
                if huruf == "H":
                    row["H"] += 1
                elif huruf == "I":
                    row["I"] += 1
                elif huruf == "S":
                    row["S"] += 1
                elif huruf == "A":
                    row["A"] += 1
        rekap_data.append(row)
    jumlah_hari = calendar.monthrange(tahun, bulan)[1]
    return {
        "bulan": bulan,
        "nama_bulan": NAMA_BULAN[bulan],
        "days": list(range(1, jumlah_hari + 1)),
        "rekap_data": rekap_data,
    }

# Laporan Rekap Bulanan per Kelas
@app.route('/rekap-bulanan')
def rekap_bulanan():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kelas ORDER BY nama_kelas ASC")
    daftar_kelas = sorted(cursor.fetchall(), key=lambda row: urut_kelas(row["nama_kelas"]))
    kelas_id = request.args.get("kelas_id", "")
    try:
        tahun = int(request.args.get("tahun", datetime.now().year))
    except ValueError:
        tahun = datetime.now().year
    if "kelas_id" in request.args:
        bulan_terpilih = []
        for nilai in request.args.getlist("bulan"):
            if str(nilai).isdigit() and 1 <= int(nilai) <= 12:
                bulan_terpilih.append(int(nilai))
        bulan_terpilih = sorted(set(bulan_terpilih))
        if kelas_id and not bulan_terpilih:
            flash("Pilih minimal satu bulan.", "danger")
    else:
        bulan_terpilih = [datetime.now().month]
    rekap_bulan = []
    if str(kelas_id).isdigit() and bulan_terpilih:
        for bulan in bulan_terpilih:
            rekap_bulan.append(rekap_satu_bulan(cursor, kelas_id, bulan, tahun))
    conn.close()
    return render_template(
        "rekap_bulanan.html",
        kelas_list=daftar_kelas,
        rekap_bulan=rekap_bulan,
        selected_kelas=kelas_id,
        bulan_terpilih=bulan_terpilih,
        nama_bulan=NAMA_BULAN,
        tahun=tahun,
    )

def build_import_plan(cursor, students, ajaran):
    cursor.execute("""
        SELECT s.id, s.nis, s.nama, s.jenis_kelamin, s.kelas_id, s.tahun, s.aktif, s.nama_orang_tua, k.nama_kelas
        FROM siswa s
        LEFT JOIN kelas k ON k.id = s.kelas_id
    """)
    existing = cursor.fetchall()
    by_nis = {}
    by_name = {}
    for row in existing:
        nis = (row["nis"] or "").strip()
        if nis:
            by_nis.setdefault(nis, []).append(row)
        by_name.setdefault(name_key(row["nama"]), []).append(row)

    used_ids = set()
    plan = []
    for student in students:
        match = None
        if student["nis"] and len(by_nis.get(student["nis"], [])) == 1:
            match = by_nis[student["nis"]][0]
        if match is None:
            named = [row for row in by_name.get(name_key(student["nama"]), []) if row["id"] not in used_ids]
            if len(named) == 1:
                match = named[0]
        if match is not None and match["id"] in used_ids:
            plan.append({**student, "action": "lewati", "alasan": "Siswa ini sudah tercatat di baris lain."})
            continue
        if match is not None:
            used_ids.add(match["id"])
            changed = (
                (student["nis"] and (match["nis"] or "").strip() != student["nis"])
                or match["nama"] != student["nama"]
                or (student["jk"] and match["jenis_kelamin"] != student["jk"])
                or (match["nama_kelas"] or "") != student["kelas"]
                or match["tahun"] != ajaran
                or not match["aktif"]
                or (student.get("ortu") and (match.get("nama_orang_tua") or "") != student.get("ortu"))
            )
            plan.append({**student, "action": "ubah" if changed else "tetap", "id": match["id"]})
        else:
            plan.append({**student, "action": "baru"})

    keluar = []
    for row in existing:
        if row["tahun"] == ajaran and row["aktif"] and row["id"] not in used_ids:
            keluar.append({"nama": row["nama"], "kelas": row["nama_kelas"] or ""})
    return plan, keluar

def kelas_id_for(cursor, nama_kelas, cache):
    if nama_kelas in cache:
        return cache[nama_kelas]
    cursor.execute("SELECT id FROM kelas WHERE nama_kelas = %s", (nama_kelas,))
    row = cursor.fetchone()
    if row:
        cache[nama_kelas] = row["id"]
        return row["id"]
    cursor.execute("INSERT INTO kelas (nama_kelas) VALUES (%s)", (nama_kelas,))
    cache[nama_kelas] = cursor.lastrowid
    return cursor.lastrowid

def apply_import_plan(cursor, plan, ajaran):
    cache = {}
    kept_ids = []
    for item in plan:
        if item["action"] == "lewati":
            continue
        kelas_id = kelas_id_for(cursor, item["kelas"], cache)
        jk = item["jk"] or "L"
        ortu = " ".join((item.get("ortu") or "").split())
        sandi = item.get("sandi_ortu")
        if item["action"] == "baru":
            cursor.execute("""
                INSERT INTO siswa (nis, nama, jenis_kelamin, kelas_id, tahun, aktif, nama_orang_tua, username_ortu, password_ortu)
                VALUES (%s, %s, %s, %s, %s, 1, %s, %s, %s)
            """, (item["nis"] or None, item["nama"], jk, kelas_id, ajaran, ortu or None, ortu or None, sandi))
            kept_ids.append(cursor.lastrowid)
        else:
            cursor.execute("""
                UPDATE siswa
                SET nama = %s,
                    nis = COALESCE(NULLIF(%s, ''), nis),
                    jenis_kelamin = COALESCE(%s, jenis_kelamin),
                    kelas_id = %s,
                    tahun = %s,
                    aktif = 1,
                    password_ortu = IF(%s = '' OR username_ortu = %s, password_ortu, %s),
                    nama_orang_tua = IF(%s = '', nama_orang_tua, %s),
                    username_ortu = IF(%s = '', username_ortu, %s)
                WHERE id = %s
            """, (
                item["nama"], item["nis"], item["jk"], kelas_id, ajaran,
                ortu, ortu, sandi, ortu, ortu or None, ortu, ortu or None, item["id"],
            ))
            kept_ids.append(item["id"])
    if kept_ids:
        placeholders = ", ".join(["%s"] * len(kept_ids))
        cursor.execute(
            f"UPDATE siswa SET aktif = 0 WHERE tahun = %s AND aktif = 1 AND id NOT IN ({placeholders})",
            (ajaran, *kept_ids),
        )
    return len(kept_ids)

def koneksi_tahfidz():
    from pengaturan import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USER, TAHFIDZ_DATABASE
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=TAHFIDZ_DATABASE,
    )

def password_awal_ortu():
    try:
        conn = koneksi_tahfidz()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key = %s",
            ("parent_default_password",),
        )
        row = cursor.fetchone()
        conn.close()
        if row and row[0] and str(row[0]).strip():
            return str(row[0]).strip()
    except Exception:
        pass
    return "ortuSMPM22"

def hubungkan_orang_tua(plan):
    """Buat akun Tahfidz dari nama orang tua dan hubungkan siswa yang NIS-nya sama."""
    kelompok = {}
    for item in plan:
        if item.get("action") == "lewati":
            continue
        nama = " ".join((item.get("ortu") or "").split())
        if nama:
            kelompok.setdefault(nama, []).append((item.get("nis") or "").strip())
    if not kelompok:
        return 0, []
    sandi = generate_password_hash(password_awal_ortu())
    conn = koneksi_tahfidz()
    cursor = conn.cursor(dictionary=True)
    dibuat = 0
    masalah = []
    try:
        for nama, daftar_nis in kelompok.items():
            cursor.execute("SELECT id, role FROM users WHERE LOWER(username) = LOWER(%s)", (nama,))
            ada = cursor.fetchone()
            if ada and ada["role"] != "orang_tua":
                masalah.append(nama)
                continue
            if ada:
                user_id = ada["id"]
                cursor.execute("UPDATE users SET aktif = 1 WHERE id = %s", (user_id,))
            else:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, nama_lengkap, role, must_change_password) "
                    "VALUES (%s, %s, %s, 'orang_tua', 1)",
                    (nama, sandi, nama),
                )
                user_id = cursor.lastrowid
                dibuat += 1
            for nis in daftar_nis:
                if not nis:
                    continue
                cursor.execute(
                    "UPDATE siswa SET orang_tua_user_id = %s WHERE nis = %s AND aktif = 1",
                    (user_id, nis),
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return dibuat, masalah

def id_anak_pertama(nama):
    nama = " ".join((nama or "").split())
    if not nama:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM siswa
        WHERE aktif = 1 AND (LOWER(nama_orang_tua) = LOWER(%s) OR LOWER(username_ortu) = LOWER(%s))
        ORDER BY tahun DESC, id
        LIMIT 1
    """, (nama, nama))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def keluarga_ortu():
    if not session.get("ortu_id") and not session.get("ortu_nama"):
        return []
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    nama = " ".join((session.get("ortu_nama") or "").split())
    if not nama and session.get("ortu_id"):
        cursor.execute(
            "SELECT COALESCE(nama_orang_tua, username_ortu, '') AS nama FROM siswa WHERE id = %s",
            (session["ortu_id"],),
        )
        row = cursor.fetchone()
        nama = " ".join(((row or {}).get("nama") or "").split())
    if nama:
        cursor.execute("""
            SELECT s.id, s.nama, s.nis, s.kelas_id, k.nama_kelas
            FROM siswa s
            JOIN kelas k ON k.id = s.kelas_id
            WHERE s.aktif = 1 AND (
                LOWER(s.nama_orang_tua) = LOWER(%s)
                OR LOWER(s.username_ortu) = LOWER(%s)
                OR s.id = %s
            )
            ORDER BY k.nama_kelas, s.nama
        """, (nama, nama, session.get("ortu_id") or 0))
    else:
        cursor.execute("""
            SELECT s.id, s.nama, s.nis, s.kelas_id, k.nama_kelas
            FROM siswa s
            JOIN kelas k ON k.id = s.kelas_id
            WHERE s.id = %s AND s.aktif = 1
        """, (session["ortu_id"],))
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route('/import-siswa/blanko')
def unduh_blanko_siswa():
    from io import BytesIO
    from import_excel import buat_blanko
    isi = buat_blanko(password_awal_ortu())
    return send_file(
        BytesIO(isi),
        as_attachment=True,
        download_name="blanko_data_siswa.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

@app.route('/import-siswa', methods=['GET', 'POST'])
def import_siswa():
    ajaran_default = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1
    if request.method == 'GET':
        return render_template('import_siswa.html', ajaran=ajaran_default, preview=None, password_awal=password_awal_ortu())

    upload = request.files.get('berkas')
    try:
        ajaran = int(request.form.get('ajaran', ajaran_default))
    except ValueError:
        flash('Tahun ajaran tidak valid.', 'danger')
        return redirect(url_for('import_siswa'))
    if upload is None or not upload.filename.lower().endswith(('.xlsx', '.xlsm')):
        flash('Pilih file Excel daftar nilai (.xlsx).', 'danger')
        return redirect(url_for('import_siswa'))

    students, notes = parse_workbook(upload)
    if not students:
        flash('Tidak ada siswa yang terbaca. Pastikan ada kolom No, NIS, Nama, L/P, dan Kelas.', 'danger')
        return render_template('import_siswa.html', ajaran=ajaran, preview=None, notes=notes, password_awal=password_awal_ortu())
    if any(siswa.get("ortu") for siswa in students):
        sandi = generate_password_hash(password_awal_ortu())
        for siswa in students:
            siswa["sandi_ortu"] = sandi if siswa.get("ortu") else None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    plan, keluar = build_import_plan(cursor, students, ajaran)
    conn.close()

    token = secrets.token_urlsafe(18)
    payload = {"ajaran": ajaran, "plan": plan}
    (import_tmp_dir() / f"{token}.json").write_text(json.dumps(payload), encoding="utf-8")

    counts = {key: sum(1 for item in plan if item["action"] == key) for key in ("baru", "ubah", "tetap", "lewati")}
    per_kelas = {}
    for item in plan:
        if item["action"] == "lewati":
            continue
        per_kelas[item["kelas"]] = per_kelas.get(item["kelas"], 0) + 1
    return render_template(
        'import_siswa.html',
        ajaran=ajaran,
        preview={
            "token": token,
            "counts": counts,
            "keluar": keluar,
            "per_kelas": sorted(per_kelas.items()),
            "ubah": [item for item in plan if item["action"] == "ubah"][:30],
            "baru": [item for item in plan if item["action"] == "baru"][:30],
            "ortu": len({item.get("ortu") for item in plan if item.get("ortu") and item["action"] != "lewati"}),
        },
        notes=notes,
        password_awal=password_awal_ortu(),
    )

@app.route('/import-siswa/simpan', methods=['POST'])
def simpan_import_siswa():
    token = request.form.get('token', '')
    path = import_tmp_dir() / f"{token}.json"
    if not token or not path.is_file() or path.parent != import_tmp_dir():
        flash('Pratinjau impor sudah tidak berlaku. Unggah file lagi.', 'danger')
        return redirect(url_for('import_siswa'))
    payload = json.loads(path.read_text(encoding="utf-8"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        apply_import_plan(cursor, payload["plan"], int(payload["ajaran"]))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
        path.unlink(missing_ok=True)
    flash(f"Data siswa tahun ajaran {payload['ajaran']}/{payload['ajaran'] + 1} berhasil diimpor.", 'success')
    try:
        akun_baru, masalah = hubungkan_orang_tua(payload["plan"])
    except Exception:
        flash("Data siswa tersimpan, tetapi akun orang tua di Tahfidz belum terhubung. Coba unggah lagi.", "warning")
    else:
        if akun_baru:
            flash(
                f"{akun_baru} akun orang tua baru dibuat. Username adalah nama orang tua. "
                f"Password awal sama dengan portal Tahfidz ({password_awal_ortu()}).",
                "success",
            )
        if masalah:
            flash(
                "Nama ini sudah dipakai akun staf, jadi tidak dijadikan akun orang tua: " + ", ".join(masalah),
                "warning",
            )
    return redirect(url_for('import_siswa'))

def cari_nama_guru(nama, daftar):
    if not nama:
        return None
    kunci = name_key(nama)
    for guru in daftar:
        if name_key(guru["nama"]) == kunci or name_key(nama_dengan_gelar(guru["nama"], guru.get("gelar"))) == kunci:
            return guru
    return cocok_guru(nama, daftar)

def muat_cetak_guru(cursor):
    from portal.guru_akun import siapkan
    siapkan()
    cursor.execute("SELECT * FROM kelas")
    daftar_kelas = sorted(cursor.fetchall(), key=lambda row: urut_kelas(row["nama_kelas"]))
    cursor.execute(
        "SELECT id, nama, urutan, gelar, jabatan, tugas FROM guru WHERE aktif = 1 ORDER BY urutan, nama"
    )
    daftar_guru = cursor.fetchall()
    cursor.execute("""
        SELECT gk.guru_id, gk.mapel, k.nama_kelas
        FROM guru_kelas gk
        JOIN kelas k ON k.id = gk.kelas_id
    """)
    mapel_grup = {}
    for row in cursor.fetchall():
        mapel_grup.setdefault(row["guru_id"], {}).setdefault(row["mapel"] or "", []).append(row["nama_kelas"])
    cursor.execute("SELECT hari, urutan, guru_id FROM guru_piket")
    piket = {(row["hari"], row["urutan"]): row["guru_id"] for row in cursor.fetchall()}
    return daftar_guru, daftar_kelas, mapel_grup, piket

def rencanakan_guru(cursor, baris, penugasan=None):
    from portal.guru_akun import siapkan
    siapkan()
    cursor.execute("SELECT id, nama, gelar, jabatan, tugas, aktif FROM guru")
    ada = cursor.fetchall()
    cursor.execute("SELECT id, nama_kelas, wali_guru_id FROM kelas")
    kelas_rows = cursor.fetchall()
    kelas_ada = set()
    wali_sekarang = {}
    for row in kelas_rows:
        kunci = normalize_class(row["nama_kelas"]) or row["nama_kelas"]
        kelas_ada.add(kunci)
        if row["wali_guru_id"]:
            wali_sekarang[kunci] = row["wali_guru_id"]
    cursor.execute("""
        SELECT gk.guru_id, gk.mapel, k.nama_kelas
        FROM guru_kelas gk
        JOIN kelas k ON k.id = gk.kelas_id
    """)
    mapel_sekarang = {}
    for row in cursor.fetchall():
        kunci = normalize_class(row["nama_kelas"]) or row["nama_kelas"]
        mapel_sekarang.setdefault(row["guru_id"], set()).add((normalize_name(row["mapel"])[:40], kunci))
    cursor.execute("SELECT hari, urutan, guru_id FROM guru_piket")
    piket_sekarang = {(row["hari"], row["urutan"]): row["guru_id"] for row in cursor.fetchall()}
    terpakai = set()
    sudah = set()
    rencana = []
    for item in baris:
        kunci = name_key(item["nama"])
        if kunci in sudah:
            rencana.append({**item, "action": "lewati", "alasan": "Nama ini sudah ada di baris lain."})
            continue
        cocok = cocok_guru(item["nama"], [guru for guru in ada if guru["id"] not in terpakai])
        if cocok:
            terpakai.add(cocok["id"])
            sudah.add(kunci)
            sudah.add(name_key(cocok["nama"]))
            berubah = (
                (cocok["nama"] or "") != item["nama"]
                or (cocok.get("gelar") or "") != item["gelar"]
                or (cocok.get("jabatan") or "") != item["jabatan"]
                or (cocok.get("tugas") or "") != item["tugas"]
                or not cocok["aktif"]
            )
            rencana.append({**item, "action": "ubah" if berubah else "tetap", "id": cocok["id"]})
        else:
            sudah.add(kunci)
            rencana.append({**item, "action": "baru"})

    catatan = []
    dilihat = set()

    def catat(teks):
        if teks not in dilihat:
            dilihat.add(teks)
            catatan.append(teks)

    tidak_ada = set()
    ubah_mapel = 0
    for item in rencana:
        if item.get("mapel") is None:
            continue
        bersih = []
        for label, daftar in item["mapel"]:
            kelas = []
            for nama_kelas in daftar:
                if nama_kelas in kelas_ada:
                    kelas.append(nama_kelas)
                else:
                    tidak_ada.add(nama_kelas)
            bersih.append([label, kelas])
        item["mapel"] = bersih
        if not item.get("id"):
            continue
        target = {(label, nama_kelas) for label, daftar in bersih for nama_kelas in daftar}
        if target != mapel_sekarang.get(item["id"], set()):
            ubah_mapel += 1
            if item["action"] == "tetap":
                item["action"] = "ubah"
    for nama_kelas in sorted(tidak_ada, key=urut_kelas):
        catat(f"Kelas {nama_kelas} tidak ada di database, jadi tidak disimpan.")

    calon = ada + [
        {"id": None, "nama": item["nama"]}
        for item in rencana
        if item["action"] != "lewati"
    ]
    if penugasan:
        susunan = {"wali": penugasan.get("wali") or {}, "piket": penugasan.get("piket")}
    else:
        susunan = {"wali": None, "piket": None}
        if any(item.get("wali") is not None for item in rencana):
            wali = {}
            for item in rencana:
                if item["action"] == "lewati" or item.get("wali") is None:
                    continue
                for nama_kelas in item["wali"]:
                    if nama_kelas in kelas_ada:
                        wali[nama_kelas] = item["nama"]
                    else:
                        tidak_ada.add(nama_kelas)
            dalam_file = {item["id"] for item in rencana if item.get("id")}
            for nama_kelas, guru_id in wali_sekarang.items():
                if guru_id in dalam_file and nama_kelas not in wali:
                    wali[nama_kelas] = ""
            susunan["wali"] = wali
        if any(item.get("piket") is not None for item in rencana):
            piket = {}
            for item in rencana:
                if item["action"] == "lewati" or item.get("piket") is None:
                    continue
                for hari, urutan in item["piket"]:
                    piket[(int(hari), int(urutan))] = item["nama"]
            dalam_file = {item["id"] for item in rencana if item.get("id")}
            for kunci, guru_id in piket_sekarang.items():
                if guru_id in dalam_file and kunci not in piket:
                    piket[kunci] = ""
            susunan["piket"] = [
                {"hari": hari, "urutan": urutan, "nama": nama}
                for (hari, urutan), nama in sorted(piket.items())
            ]
    for nama_kelas in sorted(tidak_ada, key=urut_kelas):
        catat(f"Kelas {nama_kelas} tidak ada di database, jadi tidak disimpan.")

    def tandai(guru_id):
        for item in rencana:
            if item["action"] == "tetap" and item.get("id") == guru_id:
                item["action"] = "ubah"

    ubah_wali = 0
    if susunan.get("wali") is not None:
        for nama_kelas, nama in list(susunan["wali"].items()):
            if nama_kelas not in kelas_ada:
                catat(f"Kelas {nama_kelas} tidak ada di database, jadi wali kelas tidak disimpan.")
                susunan["wali"].pop(nama_kelas, None)
                continue
            guru = cari_nama_guru(nama, calon) if nama else None
            if nama and guru is None:
                catat(f"Wali kelas {nama_kelas} tidak dikenali dan tidak diubah.")
                susunan["wali"].pop(nama_kelas, None)
                continue
            target_id = guru.get("id") if guru else None
            if target_id != wali_sekarang.get(nama_kelas):
                ubah_wali += 1
                tandai(target_id)
                tandai(wali_sekarang.get(nama_kelas))
    ubah_piket = 0
    if susunan.get("piket") is not None:
        tetap = []
        for slot in susunan["piket"]:
            nama = slot.get("nama") or ""
            guru = cari_nama_guru(nama, calon) if nama else None
            if nama and guru is None:
                catat("Ada nama guru piket yang tidak dikenali. Slot itu tidak diubah.")
                continue
            target_id = guru.get("id") if guru else None
            kunci = (int(slot["hari"]), int(slot["urutan"]))
            if target_id != piket_sekarang.get(kunci):
                ubah_piket += 1
                tandai(target_id)
                tandai(piket_sekarang.get(kunci))
            tetap.append({"hari": kunci[0], "urutan": kunci[1], "nama": nama})
        susunan["piket"] = tetap
    pakai = any(item.get("mapel") is not None for item in rencana) or bool(penugasan)
    if not pakai:
        susunan = None
    ringkas = {"pakai": pakai, "mapel": ubah_mapel, "wali": ubah_wali, "piket": ubah_piket}
    return rencana, catatan, susunan, ringkas

def terapkan_guru(cursor, rencana):
    cursor.execute("SELECT COALESCE(MAX(urutan), 0) AS urutan FROM guru")
    urutan = cursor.fetchone()["urutan"] or 0
    for item in rencana:
        if item["action"] == "lewati":
            continue
        if item["action"] == "baru":
            urutan += 1
            cursor.execute(
                """
                INSERT INTO guru (nama, urutan, aktif, gelar, jabatan, tugas)
                VALUES (%s, %s, 1, %s, %s, %s)
                """,
                (item["nama"], urutan, item["gelar"] or None, item["jabatan"] or None, item["tugas"] or None),
            )
            item["id"] = cursor.lastrowid
        else:
            cursor.execute(
                """
                UPDATE guru
                SET nama = %s, aktif = 1, gelar = %s, jabatan = %s, tugas = %s
                WHERE id = %s
                """,
                (item["nama"], item["gelar"] or None, item["jabatan"] or None, item["tugas"] or None, item["id"]),
            )

def terapkan_penugasan(cursor, rencana, penugasan):
    cursor.execute("SELECT id, nama_kelas FROM kelas")
    kelas_id = {}
    for row in cursor.fetchall():
        kelas_id[normalize_class(row["nama_kelas"]) or row["nama_kelas"]] = row["id"]
    cursor.execute("SELECT id, nama, gelar FROM guru WHERE aktif = 1")
    daftar = cursor.fetchall()
    catatan = []
    dilihat = set()

    def catat(teks):
        if teks not in dilihat:
            dilihat.add(teks)
            catatan.append(teks)

    for item in rencana:
        if item["action"] == "lewati" or item.get("mapel") is None or not item.get("id"):
            continue
        cursor.execute("DELETE FROM guru_kelas WHERE guru_id = %s", (item["id"],))
        sudah = set()
        for label, daftar_kelas in item["mapel"] or []:
            for nama_kelas in daftar_kelas:
                kid = kelas_id.get(nama_kelas)
                kunci = (item["id"], kid, label)
                if not kid or kunci in sudah:
                    continue
                sudah.add(kunci)
                cursor.execute(
                    "INSERT INTO guru_kelas (guru_id, kelas_id, mapel) VALUES (%s, %s, %s)",
                    (item["id"], kid, label),
                )
    if not penugasan:
        return catatan
    if penugasan.get("wali") is not None:
        for nama_kelas, nama in penugasan["wali"].items():
            kid = kelas_id.get(nama_kelas)
            if not kid:
                continue
            guru = cari_nama_guru(nama, daftar) if nama else None
            if nama and guru is None:
                catat(f"Wali kelas {nama_kelas} tidak dikenali dan tidak diubah.")
                continue
            cursor.execute(
                "UPDATE kelas SET wali_guru_id = %s WHERE id = %s",
                (guru["id"] if guru else None, kid),
            )
    if penugasan.get("piket") is not None:
        for slot in penugasan["piket"]:
            nama = slot.get("nama") or ""
            guru = cari_nama_guru(nama, daftar) if nama else None
            if nama and guru is None:
                catat("Ada nama guru piket yang tidak dikenali. Slot itu tidak diubah.")
                continue
            if guru:
                cursor.execute(
                    """
                    INSERT INTO guru_piket (hari, urutan, guru_id) VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE guru_id = VALUES(guru_id)
                    """,
                    (int(slot["hari"]), int(slot["urutan"]), guru["id"]),
                )
            else:
                cursor.execute(
                    "DELETE FROM guru_piket WHERE hari = %s AND urutan = %s",
                    (int(slot["hari"]), int(slot["urutan"])),
                )
    return catatan

@app.route('/import-guru/blanko')
def unduh_blanko_guru():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    berkas = excel_data_guru(*muat_cetak_guru(cursor))
    conn.close()
    return send_file(
        berkas,
        as_attachment=True,
        download_name="blanko_data_guru.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

@app.route('/import-guru', methods=['GET', 'POST'])
def import_guru():
    if request.method == 'GET':
        return render_template('import_guru.html', preview=None)
    upload = request.files.get('berkas')
    if upload is None or not upload.filename.lower().endswith(('.xlsx', '.xlsm')):
        flash('Pilih file Excel guru (.xlsx).', 'danger')
        return redirect(url_for('import_guru'))
    from import_excel import parse_guru
    guru, notes, penugasan = parse_guru(upload)
    if not guru:
        flash('Tidak ada guru yang terbaca. Unggah file hasil Cetak Excel dari menu Guru.', 'danger')
        return render_template('import_guru.html', preview=None, notes=notes)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    rencana, catatan, susunan, ringkas = rencanakan_guru(cursor, guru, penugasan)
    conn.close()
    token = secrets.token_urlsafe(18)
    (import_tmp_dir() / f"guru-{token}.json").write_text(
        json.dumps({"jenis": "guru", "plan": rencana, "penugasan": susunan}, ensure_ascii=False),
        encoding="utf-8",
    )
    counts = {key: sum(1 for item in rencana if item["action"] == key) for key in ("baru", "ubah", "tetap", "lewati")}
    return render_template(
        'import_guru.html',
        preview={
            "token": token,
            "counts": counts,
            "ubah": [item for item in rencana if item["action"] == "ubah"][:40],
            "baru": [item for item in rencana if item["action"] == "baru"][:40],
            "ringkas": ringkas,
        },
        notes=notes + catatan,
    )

@app.route('/import-guru/simpan', methods=['POST'])
def simpan_import_guru():
    token = request.form.get('token', '')
    path = import_tmp_dir() / f"guru-{token}.json"
    if not token or not path.is_file() or path.parent != import_tmp_dir():
        flash('Pratinjau impor sudah tidak berlaku. Unggah file lagi.', 'danger')
        return redirect(url_for('import_guru'))
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("jenis") != "guru":
        path.unlink(missing_ok=True)
        flash('Pratinjau impor sudah tidak berlaku. Unggah file lagi.', 'danger')
        return redirect(url_for('import_guru'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        terapkan_guru(cursor, payload["plan"])
        catatan = terapkan_penugasan(cursor, payload["plan"], payload.get("penugasan"))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
        path.unlink(missing_ok=True)
    from portal.guru_akun import SANDI_AWAL, siapkan
    siapkan()
    baru = sum(1 for item in payload["plan"] if item["action"] == "baru")
    flash('Data guru berhasil diimpor.', 'success')
    if any(item.get("mapel") is not None for item in payload["plan"]) or payload.get("penugasan"):
        flash('Kelas yang diampu, wali kelas, dan jadwal piket ikut disimpan.', 'success')
    if baru:
        flash(f"{baru} guru baru ditambahkan. Username adalah nama guru. Password awal {SANDI_AWAL}.", 'success')
    for teks in catatan:
        flash(teks, 'warning')
    return redirect(url_for('guru'))

@app.route('/tata-tertib', methods=['GET', 'POST'])
def tata_tertib():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    tanggal = request.values.get('tanggal', datetime.now().strftime('%Y-%m-%d'))
    kelas_id = request.values.get('kelas_id') or ''

    if request.method == 'POST' and request.form.get('aksi') == 'hapus':
        cursor.execute("DELETE FROM pelanggaran WHERE id = %s", (request.form.get('id'),))
        conn.commit()
        flash('Catatan pelanggaran dihapus.', 'success')
        conn.close()
        return redirect(url_for('tata_tertib', tanggal=tanggal, kelas_id=kelas_id))

    if request.method == 'POST':
        siswa_id = request.form.get('siswa_id')
        jenis = request.form.get('jenis', '').strip()
        keterangan = request.form.get('keterangan', '').strip()[:255]
        if jenis not in JENIS_PELANGGARAN:
            flash('Pilih jenis pelanggaran.', 'danger')
        elif not siswa_id:
            flash('Pilih siswa yang melanggar.', 'danger')
        else:
            cursor.execute(
                "INSERT INTO pelanggaran (siswa_id, tanggal, jenis, keterangan) VALUES (%s, %s, %s, %s)",
                (siswa_id, tanggal, jenis, keterangan),
            )
            conn.commit()
            flash('Pelanggaran tata tertib tercatat.', 'success')
            conn.close()
            return redirect(url_for('tata_tertib', tanggal=tanggal, kelas_id=kelas_id))

    cursor.execute("SELECT * FROM kelas ORDER BY nama_kelas ASC")
    daftar_kelas = cursor.fetchall()
    siswa_list = []
    if kelas_id:
        cursor.execute("""
            SELECT id, nis, nama FROM siswa
            WHERE kelas_id = %s AND tahun = %s AND aktif = 1
            ORDER BY nama ASC
        """, (kelas_id, tahun_ajaran_dari(tanggal)))
        siswa_list = cursor.fetchall()

    sql = """
        SELECT p.id, k.nama_kelas, s.nis, s.nama, p.jenis, p.keterangan
        FROM pelanggaran p
        JOIN siswa s ON p.siswa_id = s.id
        JOIN kelas k ON s.kelas_id = k.id
        WHERE p.tanggal = %s
    """
    params = [tanggal]
    if kelas_id:
        sql += " AND s.kelas_id = %s"
        params.append(kelas_id)
    sql += " ORDER BY k.nama_kelas, s.nama, p.id"
    cursor.execute(sql, params)
    catatan = cursor.fetchall()
    conn.close()
    return render_template(
        'tata_tertib.html',
        kelas_list=daftar_kelas,
        siswa_list=siswa_list,
        catatan=catatan,
        jenis_list=JENIS_PELANGGARAN,
        tanggal=tanggal,
        selected_kelas=kelas_id,
    )

def excel_data_guru(daftar_guru, daftar_kelas, mapel_grup, piket_terpilih):
    from io import BytesIO

    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wali = {}
    for kelas in daftar_kelas:
        if kelas.get("wali_guru_id"):
            wali.setdefault(kelas["wali_guru_id"], []).append(kelas["nama_kelas"])
    for guru_id in wali:
        wali[guru_id] = sorted(wali[guru_id], key=urut_kelas)
    piket = {}
    for (hari, urutan), guru_id in piket_terpilih.items():
        if hari < len(NAMA_HARI):
            piket.setdefault(guru_id, []).append(f"{NAMA_HARI[hari]} {urutan}")
    nama_guru = {guru["id"]: nama_dengan_gelar(guru["nama"], guru.get("gelar")) for guru in daftar_guru}

    buku = Workbook()
    lembar = buku.active
    lembar.title = "Data Guru"
    judul = (
        "No", "Nama Guru", "Gelar", "Jabatan", "Tugas",
        "Kelas yang Diampu", "Mata Pelajaran", "Wali Kelas", "Jadwal Piket",
    )
    lembar.append(judul)
    for sel in lembar[1]:
        sel.font = Font(bold=True, color="FFFFFF")
        sel.fill = PatternFill("solid", fgColor="1F7A4D")
        sel.alignment = Alignment(wrap_text=True, vertical="center")
    for nomor, guru in enumerate(daftar_guru, start=1):
        kelompok = mapel_grup.get(guru["id"], {})
        kelas_nama = sorted(
            {kelas for daftar in kelompok.values() for kelas in daftar},
            key=urut_kelas,
        )
        mapel = []
        for nama_mapel, daftar in sorted(kelompok.items()):
            label = nama_mapel or "Mapel"
            mapel.append(f"{label}: {', '.join(sorted(daftar, key=urut_kelas))}")
        lembar.append((
            nomor,
            nama_dengan_gelar(guru["nama"], guru.get("gelar")),
            guru.get("gelar") or "",
            guru.get("jabatan") or "",
            guru.get("tugas") or "",
            ", ".join(kelas_nama),
            "; ".join(mapel),
            ", ".join(wali.get(guru["id"], [])),
            ", ".join(piket.get(guru["id"], [])),
        ))
    for indeks, lebar in enumerate((6, 42, 18, 22, 36, 28, 36, 18, 28), start=1):
        lembar.column_dimensions[get_column_letter(indeks)].width = lebar
    for baris in lembar.iter_rows(min_row=2, max_col=9):
        for sel in baris:
            sel.alignment = Alignment(wrap_text=True, vertical="top")
    lembar.auto_filter.ref = f"A1:I{lembar.max_row}"
    lembar.freeze_panes = "A2"

    tugas = buku.create_sheet("Penugasan")
    tugas["A1"] = "Wali kelas"
    tugas["A1"].font = Font(bold=True, size=14)
    tugas.append(())
    tugas.append(("Kelas", "Wali kelas"))
    for sel in tugas[3]:
        sel.font = Font(bold=True, color="FFFFFF")
        sel.fill = PatternFill("solid", fgColor="1F7A4D")
    for kelas in daftar_kelas:
        tugas.append((kelas["nama_kelas"], nama_guru.get(kelas.get("wali_guru_id"), "")))
    mulai_piket = tugas.max_row + 2
    tugas.cell(mulai_piket, 1, "Guru piket").font = Font(bold=True, size=14)
    kepala = mulai_piket + 1
    for kolom, teks in enumerate(("Hari", "Piket 1", "Piket 2", "Piket 3"), start=1):
        sel = tugas.cell(kepala, kolom, teks)
        sel.font = Font(bold=True, color="FFFFFF")
        sel.fill = PatternFill("solid", fgColor="1F7A4D")
    for hari in range(5):
        tugas.append((
            NAMA_HARI[hari],
            nama_guru.get(piket_terpilih.get((hari, 1)), ""),
            nama_guru.get(piket_terpilih.get((hari, 2)), ""),
            nama_guru.get(piket_terpilih.get((hari, 3)), ""),
        ))
    for indeks, lebar in enumerate((16, 42, 42, 42), start=1):
        tugas.column_dimensions[get_column_letter(indeks)].width = lebar

    simpanan = BytesIO()
    buku.save(simpanan)
    simpanan.seek(0)
    return simpanan


@app.route('/guru/cetak')
def cetak_guru():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    berkas = excel_data_guru(*muat_cetak_guru(cursor))
    conn.close()
    return send_file(
        berkas,
        as_attachment=True,
        download_name="data_guru_kelas_penugasan.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def admin_presensi():
    try:
        from sso import baca
        data = baca(request)
    except Exception:
        data = None
    if data and data.get("role") == "admin":
        return True
    return bool(session.get("masuk") and not session.get("dari_portal"))


@app.route('/guru', methods=['GET', 'POST'])
def guru():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST" and request.form.get("aksi") == "reset_akun":
        if not admin_presensi():
            flash("Hanya admin yang dapat mereset akun guru.", "danger")
        else:
            from portal.guru_akun import SANDI_AWAL, reset as reset_akun_guru

            guru_id = request.form.get("guru_id", "")
            nama = reset_akun_guru(int(guru_id)) if str(guru_id).isdigit() else None
            if nama:
                flash(f"Password akun {nama} direset menjadi {SANDI_AWAL}.", "success")
            else:
                flash("Guru tidak ditemukan.", "danger")
        conn.close()
        return redirect(url_for("guru"))

    if request.method == 'POST' and request.form.get('aksi') == 'piket':
        cursor.execute("DELETE FROM guru_piket")
        for hari in range(5):
            for urutan in range(1, 4):
                guru_id = request.form.get(f"piket_{hari}_{urutan}", "")
                if str(guru_id).isdigit():
                    cursor.execute(
                        "INSERT INTO guru_piket (hari, urutan, guru_id) VALUES (%s, %s, %s)",
                        (hari, urutan, int(guru_id)),
                    )
        conn.commit()
        flash('Jadwal guru piket disimpan.', 'success')
        conn.close()
        return redirect(url_for('guru'))

    if request.method == 'POST' and request.form.get('aksi') == 'tambah':
        nama = request.form.get('nama_baru', '').strip()[:120]
        if not nama:
            flash('Nama guru belum diisi.', 'danger')
        else:
            cursor.execute("SELECT COALESCE(MAX(urutan), 0) + 1 AS urutan FROM guru")
            urutan = cursor.fetchone()["urutan"]
            try:
                cursor.execute(
                    "INSERT INTO guru (nama, urutan, aktif) VALUES (%s, %s, 1)",
                    (nama, urutan),
                )
                conn.commit()
                flash('Guru ditambahkan.', 'success')
            except mysql.connector.IntegrityError:
                flash('Nama guru itu sudah ada.', 'danger')
        conn.close()
        return redirect(url_for('guru'))

    if request.method == 'POST':
        for guru_id in request.form.getlist('guru_id'):
            nama = " ".join(request.form.get(f'nama_{guru_id}', '').split())
            if nama:
                cursor.execute("SELECT gelar FROM guru WHERE id = %s", (guru_id,))
                ada = cursor.fetchone()
                gelar_lama = (ada or {}).get("gelar") or ""
                dasar = lepaskan_gelar(nama, gelar_lama)
                if gelar_lama and dasar != nama:
                    nama_simpan, gelar_simpan = dasar[:120], gelar_lama
                elif gelar_lama:
                    nama_simpan, gelar_simpan = nama[:120], ""
                else:
                    nama_simpan, gelar_simpan = nama[:120], ""
                cursor.execute(
                    "UPDATE guru SET nama = %s, gelar = %s WHERE id = %s",
                    (nama_simpan, gelar_simpan or None, guru_id),
                )
            cursor.execute("SELECT kelas_id, mapel FROM guru_kelas WHERE guru_id = %s", (guru_id,))
            mapel_lama = {}
            for row in cursor.fetchall():
                mapel_lama.setdefault(row["kelas_id"], []).append(row["mapel"])
            cursor.execute("DELETE FROM guru_kelas WHERE guru_id = %s", (guru_id,))
            for kelas_id in request.form.getlist(f'kelas_{guru_id}'):
                kelas_id = int(kelas_id)
                for mapel in mapel_lama.get(kelas_id) or [""]:
                    cursor.execute(
                        "INSERT INTO guru_kelas (guru_id, kelas_id, mapel) VALUES (%s, %s, %s)",
                        (guru_id, kelas_id, mapel),
                    )
        for kelas_id, guru_id in request.form.items():
            if not kelas_id.startswith("wali_"):
                continue
            guru_id = int(guru_id) if str(guru_id).isdigit() else None
            cursor.execute("UPDATE kelas SET wali_guru_id = %s WHERE id = %s", (guru_id, int(kelas_id[5:])))
        conn.commit()
        flash('Penugasan guru ke kelas disimpan.', 'success')
        conn.close()
        return redirect(url_for('guru'))

    cursor.execute("SELECT * FROM kelas")
    daftar_kelas = sorted(cursor.fetchall(), key=lambda row: urut_kelas(row["nama_kelas"]))
    from portal.guru_akun import siapkan
    siapkan()
    cursor.execute(
        "SELECT id, nama, urutan, gelar, jabatan, tugas FROM guru WHERE aktif = 1 ORDER BY urutan, nama"
    )
    daftar_guru = cursor.fetchall()
    cursor.execute("""
        SELECT gk.guru_id, gk.kelas_id, gk.mapel, k.nama_kelas
        FROM guru_kelas gk
        JOIN kelas k ON k.id = gk.kelas_id
    """)
    terpilih = {}
    mapel_grup = {}
    for row in cursor.fetchall():
        terpilih.setdefault(row["guru_id"], set()).add(row["kelas_id"])
        mapel_grup.setdefault(row["guru_id"], {}).setdefault(row["mapel"] or "Mapel", []).append(row["nama_kelas"])
    for item in daftar_guru:
        item["nama_lengkap"] = nama_dengan_gelar(item["nama"], item.get("gelar"))
        item["kelas_ids"] = terpilih.get(item["id"], set())
        item["mapel"] = [
            {"nama": mapel, "kelas": ", ".join(sorted(nama_kelas, key=urut_kelas))}
            for mapel, nama_kelas in mapel_grup.get(item["id"], {}).items()
        ]
    cursor.execute("SELECT hari, urutan, guru_id FROM guru_piket")
    piket_terpilih = {(row["hari"], row["urutan"]): row["guru_id"] for row in cursor.fetchall()}
    from portal.guru_akun import SANDI_AWAL, id_piket

    conn.close()
    return render_template(
        'guru.html',
        guru_list=daftar_guru,
        kelas_list=daftar_kelas,
        hari_piket=NAMA_HARI[:5],
        piket_terpilih=piket_terpilih,
        piket_ids=id_piket(),
        boleh_reset=admin_presensi(),
        sandi_guru=SANDI_AWAL,
    )

def simpan_hasil_mapel(cursor, kelas_id, tanggal, mapel, materi, tugas, ulangan, ulangan_ket):
    if not materi and not tugas and not ulangan:
        cursor.execute(
            "DELETE FROM hasil_belajar WHERE kelas_id = %s AND tanggal = %s AND mapel = %s",
            (kelas_id, tanggal, mapel),
        )
        return
    cursor.execute("""
        INSERT INTO hasil_belajar (kelas_id, tanggal, mapel, materi, tugas, ulangan, ulangan_ket)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            materi = VALUES(materi),
            tugas = VALUES(tugas),
            ulangan = VALUES(ulangan),
            ulangan_ket = VALUES(ulangan_ket)
    """, (kelas_id, tanggal, mapel, materi, tugas, ulangan, ulangan_ket))

@app.route("/ganti-password", methods=["GET", "POST"])
def ganti_password_guru():
    if not session.get("guru_id"):
        flash("Halaman ini untuk akun guru.", "danger")
        return redirect(url_for("index"))
    if request.method == "POST":
        baru = request.form.get("password_baru") or ""
        ulang = request.form.get("password_konfirmasi") or ""
        if baru != ulang:
            flash("Konfirmasi password tidak cocok.", "danger")
        else:
            from portal.guru_akun import ganti_sandi

            pesan = ganti_sandi(session.get("guru_id"), request.form.get("password_lama") or "", baru)
            if pesan:
                flash(pesan, "danger")
            else:
                flash("Password berhasil diubah. Pakai password baru saat masuk lagi.", "success")
                return redirect(url_for("ganti_password_guru"))
    return render_template("ganti_password_guru.html")


def guru_yang_mengisi():
    if session.get("guru_id") and (
        session.get("guru_piket") or session.get("guru_bk") or session.get("guru_pengampu")
    ):
        return session.get("guru_id")
    return None


@app.route('/hasil-belajar', methods=['GET', 'POST'])
def hasil_belajar():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    guru_id = guru_yang_mengisi()
    if guru_id:
        cursor.execute(
            """
            SELECT DISTINCT k.id, k.nama_kelas
            FROM kelas k
            JOIN guru_kelas gk ON gk.kelas_id = k.id
            WHERE gk.guru_id = %s AND TRIM(gk.mapel) <> ''
            """,
            (guru_id,),
        )
    else:
        cursor.execute("SELECT id, nama_kelas FROM kelas")
    daftar_kelas = sorted(cursor.fetchall(), key=lambda row: urut_kelas(row["nama_kelas"]))
    kelas_boleh = {str(row["id"]) for row in daftar_kelas} if guru_id else None
    tanggal = request.values.get("tanggal") or datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
    except ValueError:
        tanggal = datetime.now().strftime("%Y-%m-%d")
    kelas_id = request.values.get("kelas_id", "")
    if guru_id and kelas_id and kelas_boleh is not None and kelas_id not in kelas_boleh:
        kelas_id = ""
    if guru_id and request.method == "POST" and request.form.get("aksi") in {"reset_ortu", "password_awal"}:
        conn.close()
        flash("Akun orang tua diubah oleh staf.", "danger")
        return redirect(url_for("hasil_belajar", kelas_id=kelas_id, tanggal=tanggal))
    if request.method == "POST" and request.form.get("aksi") == "reset_ortu":
        siswa_id = request.form.get("siswa_id", "")
        if str(siswa_id).isdigit():
            cursor.execute(
                "UPDATE siswa SET username_ortu = NULL, password_ortu = NULL WHERE id = %s",
                (siswa_id,),
            )
            conn.commit()
            flash("Akun orang tua direset. Mereka bisa daftar lagi dengan NIS dan kode sekolah.", "success")
        conn.close()
        return redirect(url_for("hasil_belajar", kelas_id=kelas_id, tanggal=tanggal))
    if request.method == "POST" and request.form.get("aksi") == "password_awal":
        siswa_id = request.form.get("siswa_id", "")
        if not str(siswa_id).isdigit():
            conn.close()
            return redirect(url_for("hasil_belajar", kelas_id=kelas_id, tanggal=tanggal))
        cursor.execute("SELECT id, nama, nis FROM siswa WHERE id = %s AND aktif = 1", (siswa_id,))
        siswa = cursor.fetchone()
        conn.close()
        if siswa is None:
            flash("Siswa tidak ditemukan.", "danger")
            return redirect(url_for("hasil_belajar", kelas_id=kelas_id, tanggal=tanggal))
        username = request.form.get("username", "").strip() or (siswa["nis"] or "")
        password = request.form.get("password", "")
        pesan = username_ortu_valid(username, siswa["id"])
        if not pesan and (len(password) < 6 or len(password) > 72):
            pesan = "Password awal minimal 6 karakter."
        if pesan:
            flash(pesan, "danger")
        else:
            simpan_akun_ortu(siswa["id"], username, password)
            flash(
                f"Password awal untuk {siswa['nama']} disimpan. Username: {username.strip()}. Password: {password}",
                "success",
            )
        return redirect(url_for("hasil_belajar", kelas_id=kelas_id, tanggal=tanggal))
    if request.method == "POST":
        kelas_id = request.form.get("kelas_id", "")
        if not str(kelas_id).isdigit() or (kelas_boleh is not None and kelas_id not in kelas_boleh):
            flash("Pilih kelas yang Anda ampu." if guru_id else "Pilih kelas dulu.", "danger")
            conn.close()
            return redirect(url_for("hasil_belajar", tanggal=tanggal))
        milik = None
        if guru_id:
            cursor.execute(
                """
                SELECT DISTINCT TRIM(mapel) AS mapel FROM guru_kelas
                WHERE guru_id = %s AND kelas_id = %s AND TRIM(mapel) <> ''
                """,
                (guru_id, kelas_id),
            )
            milik = {row["mapel"].casefold() for row in cursor.fetchall()}
        mapel_list = request.form.getlist("mapel")
        for indeks, mapel in enumerate(mapel_list):
            mapel = mapel.strip()[:60]
            if not mapel or (milik is not None and mapel.casefold() not in milik):
                continue
            materi = request.form.get(f"materi_{indeks}", "").strip()[:800]
            tugas = request.form.get(f"tugas_{indeks}", "").strip()[:400]
            ulangan = 1 if request.form.get(f"ulangan_{indeks}") else 0
            ulangan_ket = request.form.get(f"ulangan_ket_{indeks}", "").strip()[:200] if ulangan else ""
            simpan_hasil_mapel(cursor, kelas_id, tanggal, mapel, materi, tugas, ulangan, ulangan_ket)
        mapel_baru = request.form.get("mapel_baru", "").strip()[:60]
        materi_baru = request.form.get("materi_baru", "").strip()[:800]
        tugas_baru = request.form.get("tugas_baru", "").strip()[:400]
        ulangan_baru = 1 if request.form.get("ulangan_baru") else 0
        ulangan_ket_baru = request.form.get("ulangan_ket_baru", "").strip()[:200] if ulangan_baru else ""
        if mapel_baru and not guru_id:
            simpan_hasil_mapel(cursor, kelas_id, tanggal, mapel_baru, materi_baru, tugas_baru, ulangan_baru, ulangan_ket_baru)
        for siswa_id in request.form.getlist("siswa_id") if not guru_id else []:
            if not str(siswa_id).isdigit():
                continue
            catatan = request.form.get(f"catatan_{siswa_id}", "").strip()[:400]
            if catatan:
                cursor.execute("""
                    INSERT INTO catatan_ortu (siswa_id, tanggal, catatan)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE catatan = VALUES(catatan)
                """, (siswa_id, tanggal, catatan))
            else:
                cursor.execute(
                    "DELETE FROM catatan_ortu WHERE siswa_id = %s AND tanggal = %s",
                    (siswa_id, tanggal),
                )
        conn.commit()
        flash("Hasil belajar disimpan. Orang tua bisa melihatnya.", "success")
        conn.close()
        return redirect(url_for("hasil_belajar", kelas_id=kelas_id, tanggal=tanggal))

    mapel_isi = []
    siswa_list = []
    if str(kelas_id).isdigit():
        cursor.execute("""
            SELECT gk.mapel, GROUP_CONCAT(DISTINCT g.nama ORDER BY g.nama SEPARATOR ', ') AS guru
            FROM guru_kelas gk
            JOIN guru g ON g.id = gk.guru_id AND g.aktif = 1
            WHERE gk.kelas_id = %s AND gk.mapel <> ''
        """ + (" AND gk.guru_id = %s" if guru_id else "") + """
            GROUP BY gk.mapel
            ORDER BY gk.mapel
        """, (kelas_id, guru_id) if guru_id else (kelas_id,))
        jadwal = {row["mapel"]: row["guru"] for row in cursor.fetchall()}
        cursor.execute(
            "SELECT mapel, materi, tugas, ulangan, ulangan_ket FROM hasil_belajar WHERE kelas_id = %s AND tanggal = %s",
            (kelas_id, tanggal),
        )
        tersimpan = {row["mapel"]: row for row in cursor.fetchall()}
        tambahan = [] if guru_id else [nama for nama in tersimpan if nama not in jadwal]
        for mapel in list(jadwal) + tambahan:
            isi = tersimpan.get(mapel) or {}
            mapel_isi.append({
                "mapel": mapel,
                "guru": jadwal.get(mapel, ""),
                "materi": isi.get("materi", ""),
                "tugas": isi.get("tugas", ""),
                "ulangan": isi.get("ulangan", 0),
                "ulangan_ket": isi.get("ulangan_ket", ""),
            })
        if not guru_id:
            cursor.execute("""
                SELECT s.id, s.nis, s.nama, s.kode_ortu, s.username_ortu, COALESCE(c.catatan, '') AS catatan
                FROM siswa s
                LEFT JOIN catatan_ortu c ON c.siswa_id = s.id AND c.tanggal = %s
                WHERE s.kelas_id = %s AND s.tahun = %s AND s.aktif = 1
                ORDER BY s.nama
            """, (tanggal, kelas_id, tahun_ajaran_dari(tanggal)))
            siswa_list = cursor.fetchall()
            cursor.execute("SELECT kode_ortu FROM siswa WHERE kode_ortu IS NOT NULL")
            terpakai = {row["kode_ortu"] for row in cursor.fetchall()}
            for siswa in siswa_list:
                if siswa["kode_ortu"]:
                    continue
                kode = kode_ortu_baru(terpakai)
                cursor.execute("UPDATE siswa SET kode_ortu = %s WHERE id = %s", (kode, siswa["id"]))
                siswa["kode_ortu"] = kode
            conn.commit()
    conn.close()
    return render_template(
        "hasil_belajar.html",
        kelas_list=daftar_kelas,
        selected_kelas=kelas_id,
        tanggal=tanggal,
        mapel_isi=mapel_isi,
        siswa_list=siswa_list,
        halaman_ortu=url_for("ortu", _external=True),
        hanya_mapel=bool(guru_id),
    )

@app.route("/pengumuman", methods=["GET", "POST"])
def pengumuman():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST" and request.form.get("aksi") == "hapus":
        pengumuman_id = request.form.get("id", "")
        if str(pengumuman_id).isdigit():
            cursor.execute("DELETE FROM pengumuman_kelas WHERE pengumuman_id = %s", (pengumuman_id,))
            cursor.execute("DELETE FROM pengumuman WHERE id = %s", (pengumuman_id,))
            conn.commit()
            flash("Pengumuman dihapus.", "success")
        conn.close()
        return redirect(url_for("pengumuman"))
    if request.method == "POST":
        judul = request.form.get("judul", "").strip()[:120]
        isi = request.form.get("isi", "").strip()
        tanggal = request.form.get("tanggal") or datetime.now().strftime("%Y-%m-%d")
        try:
            datetime.strptime(tanggal, "%Y-%m-%d")
        except ValueError:
            tanggal = datetime.now().strftime("%Y-%m-%d")
        semua = request.form.get("semua_kelas") == "1"
        kelas_ids = []
        if not semua:
            for nilai in request.form.getlist("kelas_id"):
                if str(nilai).isdigit():
                    kelas_ids.append(int(nilai))
        if not judul or not isi:
            flash("Judul dan isi pengumuman wajib diisi.", "danger")
        else:
            cursor.execute(
                "INSERT INTO pengumuman (tanggal, judul, isi, kelas_id) VALUES (%s, %s, %s, NULL)",
                (tanggal, judul, isi),
            )
            pengumuman_id = cursor.lastrowid
            for kelas_id in kelas_ids:
                cursor.execute(
                    "INSERT INTO pengumuman_kelas (pengumuman_id, kelas_id) VALUES (%s, %s)",
                    (pengumuman_id, kelas_id),
                )
            conn.commit()
            flash("Pengumuman disimpan. Orang tua bisa melihatnya.", "success")
        conn.close()
        return redirect(url_for("pengumuman"))
    cursor.execute("SELECT id, nama_kelas FROM kelas")
    daftar_kelas = sorted(cursor.fetchall(), key=lambda row: urut_kelas(row["nama_kelas"]))
    cursor.execute("""
        SELECT p.id, p.tanggal, p.judul, p.isi,
               GROUP_CONCAT(DISTINCT k.nama_kelas ORDER BY k.nama_kelas SEPARATOR ', ') AS nama_kelas
        FROM pengumuman p
        LEFT JOIN pengumuman_kelas pk ON pk.pengumuman_id = p.id
        LEFT JOIN kelas k ON k.id = COALESCE(pk.kelas_id, p.kelas_id)
        GROUP BY p.id, p.tanggal, p.judul, p.isi
        ORDER BY p.tanggal DESC, p.id DESC
        LIMIT 40
    """)
    daftar = cursor.fetchall()
    conn.close()
    return render_template("pengumuman.html", kelas_list=daftar_kelas, daftar=daftar, tanggal=datetime.now().strftime("%Y-%m-%d"))

def data_ortu(butuh_presensi=False):
    if not session.get("ortu_id"):
        return None
    tanggal = request.args.get("tanggal") or datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
    except ValueError:
        tanggal = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id, s.nama, s.nis, k.nama_kelas, s.kelas_id
        FROM siswa s
        JOIN kelas k ON k.id = s.kelas_id
        WHERE s.id = %s AND s.aktif = 1
    """, (session["ortu_id"],))
    siswa = cursor.fetchone()
    if siswa is None:
        conn.close()
        session.pop("ortu_id", None)
        return None
    hasil = {"siswa": siswa, "tanggal": tanggal, "hari_tanggal": label_hari(tanggal)}
    if butuh_presensi:
        cursor.execute("""
            SELECT status, keterangan, terlambat, jam_terlambat, izin_pulang, jam_pulang, alasan_pulang
            FROM presensi
            WHERE siswa_id = %s AND tanggal = %s
        """, (siswa["id"], tanggal))
        hasil["anak"] = cursor.fetchone()
        cursor.execute("""
            SELECT jenis, keterangan FROM pelanggaran
            WHERE siswa_id = %s AND tanggal = %s
            ORDER BY id
        """, (siswa["id"], tanggal))
        hasil["pelanggaran"] = cursor.fetchall()
        cursor.execute(
            "SELECT catatan FROM catatan_ortu WHERE siswa_id = %s AND tanggal = %s",
            (siswa["id"], tanggal),
        )
        catatan = cursor.fetchone()
        hasil["catatan"] = catatan["catatan"] if catatan else ""
    else:
        cursor.execute("""
            SELECT mapel, materi, tugas, ulangan, ulangan_ket FROM hasil_belajar
            WHERE kelas_id = %s AND tanggal = %s AND (materi <> '' OR tugas <> '' OR ulangan = 1)
            ORDER BY mapel
        """, (siswa["kelas_id"], tanggal))
        hasil["pelajaran"] = cursor.fetchall()
    conn.close()
    return hasil

@app.route("/ortu", methods=["GET", "POST"])
def ortu():
    if session.get("ortu_id"):
        return redirect(url_for("ortu_presensi"))
    return redirect(url_for("login"))

@app.route("/ortu/presensi")
def ortu_presensi():
    data = data_ortu(butuh_presensi=True)
    if data is None:
        return redirect(url_for("login"))
    return render_template("ortu_presensi.html", **data)

@app.route("/ortu/tugas")
def ortu_tugas():
    data = data_ortu()
    if data is None:
        return redirect(url_for("login"))
    data["pr"] = [row for row in data["pelajaran"] if row["tugas"]]
    return render_template("ortu_tugas.html", **data)

@app.route("/ortu/ulangan")
def ortu_ulangan():
    data = data_ortu()
    if data is None:
        return redirect(url_for("login"))
    data["daftar_ulangan"] = [row for row in data["pelajaran"] if row["ulangan"]]
    return render_template("ortu_ulangan.html", **data)

def _pengumuman_untuk(cursor, kelas_ids):
    if not kelas_ids:
        return []
    tanda = ", ".join(["%s"] * len(kelas_ids))
    cursor.execute(f"""
        SELECT p.tanggal, p.judul, p.isi,
               GROUP_CONCAT(DISTINCT k.nama_kelas ORDER BY k.nama_kelas SEPARATOR ', ') AS nama_kelas
        FROM pengumuman p
        LEFT JOIN pengumuman_kelas pk ON pk.pengumuman_id = p.id
        LEFT JOIN kelas k ON k.id = COALESCE(pk.kelas_id, p.kelas_id)
        WHERE (
            NOT EXISTS (SELECT 1 FROM pengumuman_kelas x WHERE x.pengumuman_id = p.id)
            AND p.kelas_id IS NULL
        )
        OR p.kelas_id IN ({tanda})
        OR EXISTS (
            SELECT 1 FROM pengumuman_kelas y
            WHERE y.pengumuman_id = p.id AND y.kelas_id IN ({tanda})
        )
        GROUP BY p.id, p.tanggal, p.judul, p.isi
        ORDER BY p.tanggal DESC, p.id DESC
        LIMIT 40
    """, (*kelas_ids, *kelas_ids))
    return cursor.fetchall()

@app.route("/ortu/pengumuman")
def ortu_pengumuman():
    siswa_list = keluarga_ortu()
    if not siswa_list and not session.get("ortu_portal"):
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    daftar = _pengumuman_untuk(cursor, [siswa["kelas_id"] for siswa in siswa_list])
    conn.close()
    siswa = siswa_list[0] if siswa_list else None
    return render_template("ortu_pengumuman.html", siswa=siswa, siswa_list=siswa_list, daftar=daftar)

@app.route("/ortu/hasil-belajar")
def ortu_hasil():
    siswa_list = keluarga_ortu()
    if not siswa_list and not session.get("ortu_portal"):
        return redirect(url_for("login"))
    tanggal = request.args.get("tanggal") or datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
    except ValueError:
        tanggal = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    for siswa in siswa_list:
        cursor.execute("""
            SELECT mapel, materi, tugas, ulangan, ulangan_ket FROM hasil_belajar
            WHERE kelas_id = %s AND tanggal = %s AND (materi <> '' OR tugas <> '' OR ulangan = 1)
            ORDER BY mapel
        """, (siswa["kelas_id"], tanggal))
        siswa["pelajaran"] = cursor.fetchall()
    conn.close()
    return render_template(
        "ortu_hasil.html",
        siswa_list=siswa_list,
        tanggal=tanggal,
        hari_tanggal=label_hari(tanggal),
    )

@app.route("/ortu/keluar", methods=["POST"])
def ortu_keluar():
    dari_portal = bool(session.get("ortu_portal") or session.get("dari_portal"))
    session.pop("ortu_id", None)
    session.pop("ortu_portal", None)
    session.pop("ortu_nama", None)
    session.pop("ikut_tahfidz", None)
    session.pop("dari_portal", None)
    if dari_portal:
        return redirect("/logout")
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True, port=5000)