import os
from contextlib import contextmanager
from datetime import datetime
import calendar

import pymysql
from flask import Flask, flash, redirect, render_template, request, url_for

from pengaturan import (
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    PRESENSI_DATABASE,
    SECRET_KEY,
)
from portal import tautan_masuk
from sso import baca

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SESSION_COOKIE_NAME"] = "smartmu_presensi"
app.config["SESSION_COOKIE_PATH"] = "/presensi"


@app.before_request
def wajib_masuk():
    if request.endpoint == "static":
        return None
    if baca(request):
        return None
    return redirect(tautan_masuk(request))


@contextmanager
def db_cursor():
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD or os.getenv("MYSQL_PASSWORD", ""),
        database=PRESENSI_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.route("/")
def index():
    with db_cursor() as cur:
        cur.execute("SELECT * FROM kelas ORDER BY nama_kelas ASC")
        daftar_kelas = cur.fetchall()
    return render_template("index.html", kelas_list=daftar_kelas)


@app.route("/presensi", methods=["GET", "POST"])
def input_presensi():
    with db_cursor() as cur:
        selected_kelas = request.args.get("kelas_id")
        selected_tanggal = request.args.get("tanggal", datetime.now().strftime("%Y-%m-%d"))

        if request.method == "POST":
            selected_kelas = request.form.get("kelas_id")
            selected_tanggal = request.form.get("tanggal")
            cur.execute("SELECT id FROM siswa WHERE kelas_id = %s", (selected_kelas,))
            siswa_list = cur.fetchall()
            for siswa in siswa_list:
                status = request.form.get(f"status_{siswa['id']}", "Hadir")
                keterangan = request.form.get(f"ket_{siswa['id']}", "")
                cur.execute(
                    """
                    INSERT INTO presensi (siswa_id, tanggal, status, keterangan)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = VALUES(status), keterangan = VALUES(keterangan)
                    """,
                    (siswa["id"], selected_tanggal, status, keterangan),
                )
            flash("Data presensi berhasil disimpan.", "success")
            return redirect(url_for("input_presensi", kelas_id=selected_kelas, tanggal=selected_tanggal))

        cur.execute("SELECT * FROM kelas ORDER BY nama_kelas ASC")
        daftar_kelas = cur.fetchall()
        siswa_presensi = []
        if selected_kelas:
            cur.execute(
                """
                SELECT s.id, s.nis, s.nama, s.jenis_kelamin,
                       COALESCE(p.status, 'Hadir') as status,
                       COALESCE(p.keterangan, '') as keterangan
                FROM siswa s
                LEFT JOIN presensi p ON s.id = p.siswa_id AND p.tanggal = %s
                WHERE s.kelas_id = %s
                ORDER BY s.nama ASC
                """,
                (selected_tanggal, selected_kelas),
            )
            siswa_presensi = cur.fetchall()
    return render_template(
        "presensi.html",
        kelas_list=daftar_kelas,
        siswa_list=siswa_presensi,
        selected_kelas=selected_kelas,
        selected_tanggal=selected_tanggal,
    )


@app.route("/laporan-harian")
def laporan_harian():
    tanggal = request.args.get("tanggal", datetime.now().strftime("%Y-%m-%d"))
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT k.nama_kelas, s.nis, s.nama, p.status, p.keterangan
            FROM presensi p
            JOIN siswa s ON p.siswa_id = s.id
            JOIN kelas k ON s.kelas_id = k.id
            WHERE p.tanggal = %s
            ORDER BY k.nama_kelas, s.nama
            """,
            (tanggal,),
        )
        laporan = cur.fetchall()
    return render_template("laporan_harian.html", laporan=laporan, tanggal=tanggal)


@app.route("/rekap-bulanan")
def rekap_bulanan():
    with db_cursor() as cur:
        cur.execute("SELECT * FROM kelas ORDER BY nama_kelas ASC")
        daftar_kelas = cur.fetchall()
        kelas_id = request.args.get("kelas_id")
        bulan = int(request.args.get("bulan", datetime.now().month))
        tahun = int(request.args.get("tahun", datetime.now().year))
        rekap_data = []
        days_in_month = calendar.monthrange(tahun, bulan)[1]
        days = list(range(1, days_in_month + 1))
        if kelas_id:
            cur.execute(
                "SELECT id, nis, nama FROM siswa WHERE kelas_id = %s ORDER BY nama ASC",
                (kelas_id,),
            )
            siswa_list = cur.fetchall()
            for siswa in siswa_list:
                row = {"nama": siswa["nama"], "nis": siswa["nis"], "presensi": {}, "H": 0, "I": 0, "S": 0, "A": 0}
                cur.execute(
                    """
                    SELECT DAY(tanggal) as hari, status
                    FROM presensi
                    WHERE siswa_id = %s AND MONTH(tanggal) = %s AND YEAR(tanggal) = %s
                    """,
                    (siswa["id"], bulan, tahun),
                )
                for rek in cur.fetchall():
                    st = (rek["status"] or " ")[0]
                    row["presensi"][rek["hari"]] = st
                    if st == "H":
                        row["H"] += 1
                    elif st == "I":
                        row["I"] += 1
                    elif st == "S":
                        row["S"] += 1
                    elif st == "A":
                        row["A"] += 1
                rekap_data.append(row)
    return render_template(
        "rekap_bulanan.html",
        kelas_list=daftar_kelas,
        rekap_data=rekap_data,
        days=days,
        selected_kelas=kelas_id,
        bulan=bulan,
        tahun=tahun,
    )


@app.route("/master", methods=["GET", "POST"])
def master():
    with db_cursor() as cur:
        if request.method == "POST":
            aksi = request.form.get("aksi")
            if aksi == "kelas":
                nama = (request.form.get("nama_kelas") or "").strip()
                if nama:
                    cur.execute("SELECT id FROM kelas WHERE nama_kelas=%s", (nama,))
                    if cur.fetchone():
                        flash("Nama kelas itu sudah ada.", "warning")
                    else:
                        cur.execute("INSERT INTO kelas (nama_kelas) VALUES (%s)", (nama,))
                        flash("Kelas ditambahkan.", "success")
            elif aksi == "siswa":
                nama = (request.form.get("nama") or "").strip()
                nis = (request.form.get("nis") or "").strip()
                jk = request.form.get("jenis_kelamin") or ""
                kelas_id = request.form.get("kelas_id")
                if nama and kelas_id:
                    cur.execute(
                        "INSERT INTO siswa (nis, nama, jenis_kelamin, kelas_id) VALUES (%s,%s,%s,%s)",
                        (nis, nama, jk, kelas_id),
                    )
                    flash("Siswa ditambahkan.", "success")
                else:
                    flash("Nama siswa dan kelas wajib diisi.", "warning")
            elif aksi == "hapus_siswa":
                cur.execute("DELETE FROM presensi WHERE siswa_id=%s", (request.form.get("siswa_id"),))
                cur.execute("DELETE FROM siswa WHERE id=%s", (request.form.get("siswa_id"),))
                flash("Siswa dihapus.", "success")
            return redirect(url_for("master", kelas_id=request.form.get("kelas_id") or request.args.get("kelas_id")))

        cur.execute("SELECT * FROM kelas ORDER BY nama_kelas ASC")
        daftar_kelas = cur.fetchall()
        kelas_id = request.args.get("kelas_id")
        siswa = []
        if kelas_id:
            cur.execute(
                "SELECT * FROM siswa WHERE kelas_id=%s ORDER BY nama ASC",
                (kelas_id,),
            )
            siswa = cur.fetchall()
    return render_template("master.html", kelas_list=daftar_kelas, siswa_list=siswa, selected_kelas=kelas_id)
