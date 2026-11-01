"""Siapkan database MySQL untuk seluruh portal SMARTMU 22."""

import sys
from pathlib import Path

import pymysql
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pengaturan import (  # noqa: E402
    ERAPOR_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    PRESENSI_DATABASE,
    SMARTMU_DATABASE,
)


def koneksi(database=None):
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database,
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )


def ada_tabel(cur, skema, tabel):
    cur.execute(
        """SELECT COUNT(*) AS n FROM information_schema.tables
           WHERE table_schema=%s AND table_name=%s""",
        (skema, tabel),
    )
    return cur.fetchone()["n"] > 0


def siapkan_portal(cur):
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{SMARTMU_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cur.execute(f"USE `{SMARTMU_DATABASE}`")
    cur.execute(
        """CREATE TABLE IF NOT EXISTS pengguna (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            nama VARCHAR(150) NOT NULL,
            role ENUM('admin','guru','musyrif','bk','orang_tua') NOT NULL DEFAULT 'guru',
            aktif TINYINT NOT NULL DEFAULT 1
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS bk_dokumen (
            id TINYINT PRIMARY KEY,
            isi LONGTEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )"""
    )
    cur.execute("SELECT id FROM pengguna WHERE username=%s", ("admin",))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO pengguna (username, password_hash, nama, role) VALUES (%s,%s,%s,'admin')",
            ("admin", generate_password_hash("admin123"), "Administrator SMARTMU"),
        )
        print("Akun portal dibuat: admin / admin123")
    else:
        print("Akun portal admin sudah ada.")


def siapkan_presensi(cur):
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{PRESENSI_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cur.execute(f"USE `{PRESENSI_DATABASE}`")
    cur.execute(
        """CREATE TABLE IF NOT EXISTS kelas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nama_kelas VARCHAR(50) NOT NULL UNIQUE
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS siswa (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nis VARCHAR(30) NULL,
            nama VARCHAR(150) NOT NULL,
            jenis_kelamin VARCHAR(5) NULL,
            kelas_id INT NOT NULL,
            CONSTRAINT fk_siswa_kelas FOREIGN KEY (kelas_id) REFERENCES kelas(id)
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS presensi (
            id INT AUTO_INCREMENT PRIMARY KEY,
            siswa_id INT NOT NULL,
            tanggal DATE NOT NULL,
            status VARCHAR(20) NOT NULL,
            keterangan VARCHAR(255) DEFAULT '',
            UNIQUE KEY uq_siswa_tanggal (siswa_id, tanggal),
            CONSTRAINT fk_presensi_siswa FOREIGN KEY (siswa_id) REFERENCES siswa(id)
        )"""
    )
    cur.execute("SELECT COUNT(*) AS n FROM kelas")
    if cur.fetchone()["n"] == 0:
        for tingkat in (7, 8, 9):
            for nomor in range(1, 6):
                cur.execute(
                    "INSERT INTO kelas (nama_kelas) VALUES (%s)",
                    (f"{tingkat}.{nomor}",),
                )
        print("Kelas presensi 7.1–9.5 dibuat. Siswa diisi dari menu Data Siswa.")
    else:
        print("Data presensi sudah ada.")


def siapkan_tahfidz():
    folder = str(ROOT / "modules" / "tahfidz")
    sys.path.insert(0, folder)
    from init_db import run

    run()


def siapkan_inventaris():
    from muat_inventaris import muat

    muat()
    print("Database inventaris siap.")


def siapkan_erapor(cur):
    if ada_tabel(cur, ERAPOR_DATABASE, "users"):
        print("Database eRapor sudah ada, tidak diisi ulang.")
        return
    folder = str(ROOT / "modules" / "erapor")
    sys.path.insert(0, folder)
    from seed import main

    print("Mengisi eRapor (data contoh sekolah). Mohon tunggu...")
    main()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    conn = koneksi()
    try:
        with conn.cursor() as cur:
            siapkan_portal(cur)
            siapkan_presensi(cur)
            siapkan_erapor(cur)
    finally:
        conn.close()
    siapkan_tahfidz()
    siapkan_inventaris()
    print("Selesai. Jalankan: python app.py")
    print("Buka http://127.0.0.1:5000  lalu masuk dengan admin / admin123")


if __name__ == "__main__":
    try:
        main()
    except pymysql.MySQLError as galat:
        print("Gagal terhubung ke MySQL:", galat, file=sys.stderr)
        print("Periksa MySQL sudah jalan, lalu sesuaikan file .env", file=sys.stderr)
        sys.exit(1)
