"""Akun guru mengikuti tabel guru di Presensi. Guru pengampu, piket, dan BK dapat login."""

import pymysql
from werkzeug.security import check_password_hash, generate_password_hash

from pengaturan import (
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    PRESENSI_DATABASE,
)

SANDI_AWAL = "guruSMPM22"


def _rapi(nama):
    return " ".join(str(nama or "").split())


def _koneksi():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=PRESENSI_DATABASE,
        charset="utf8mb4",
    )


def siapkan():
    """Pastikan setiap guru aktif punya username sesuai namanya dan password awal."""
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW COLUMNS FROM guru LIKE 'username'")
            if cur.fetchone() is None:
                cur.execute("ALTER TABLE guru ADD COLUMN username VARCHAR(150) NULL")
                cur.execute("ALTER TABLE guru ADD COLUMN password_hash VARCHAR(255) NULL")
            for kolom, tipe in (
                ("gelar", "VARCHAR(80) NULL"),
                ("jabatan", "VARCHAR(80) NULL"),
                ("tugas", "VARCHAR(200) NULL"),
            ):
                cur.execute("SHOW COLUMNS FROM guru LIKE %s", (kolom,))
                if cur.fetchone() is None:
                    cur.execute(f"ALTER TABLE guru ADD COLUMN {kolom} {tipe}")
            cur.execute("SELECT id, nama, username, password_hash FROM guru WHERE aktif = 1")
            for guru_id, nama, username, sandi in cur.fetchall():
                akun = _rapi(nama)
                if username != akun:
                    cur.execute("UPDATE guru SET username = %s WHERE id = %s", (akun, guru_id))
                if not sandi:
                    cur.execute(
                        "UPDATE guru SET password_hash = %s WHERE id = %s",
                        (generate_password_hash(SANDI_AWAL), guru_id),
                    )
        conn.commit()
    finally:
        conn.close()


def daftar_akun():
    """Akun guru aktif: nama tampilan, username login, tanpa hash password."""
    siapkan()
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, nama, gelar, username
                FROM guru
                WHERE aktif = 1
                ORDER BY nama
                """
            )
            hasil = []
            for guru_id, nama, gelar, username in cur.fetchall():
                tampil = _rapi(nama)
                gelar = _rapi(gelar)
                if gelar and not tampil.casefold().endswith(gelar.casefold()):
                    tampil = f"{tampil}, {gelar}"
                hasil.append({
                    "id": guru_id,
                    "nama": tampil,
                    "username": username or _rapi(nama),
                })
            return hasil
    finally:
        conn.close()


def reset(guru_id):
    siapkan()
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT nama FROM guru WHERE id = %s AND aktif = 1", (guru_id,))
            row = cur.fetchone()
            if not row:
                return None
            akun = _rapi(row[0])
            cur.execute(
                "UPDATE guru SET username = %s, password_hash = %s WHERE id = %s",
                (akun, generate_password_hash(SANDI_AWAL), guru_id),
            )
        conn.commit()
        return akun
    finally:
        conn.close()


def punya_mapel(guru_id):
    """Guru mengampu sekurang-kurangnya satu mata pelajaran."""
    if not guru_id:
        return False
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM guru_kelas
                WHERE guru_id = %s AND TRIM(mapel) <> ''
                LIMIT 1
                """,
                (guru_id,),
            )
            return cur.fetchone() is not None
    except Exception:
        return False
    finally:
        conn.close()


def mengajar_bk(guru_id):
    """Guru BK adalah yang mengampu mapel BK atau jabatannya guru BK."""
    if not guru_id:
        return False
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM guru_kelas
                WHERE guru_id = %s
                  AND (
                    LOWER(TRIM(mapel)) = 'bk'
                    OR LOWER(mapel) LIKE '%%bimbingan%%'
                  )
                LIMIT 1
                """,
                (guru_id,),
            )
            if cur.fetchone():
                return True
            cur.execute("SELECT jabatan, tugas FROM guru WHERE id = %s AND aktif = 1", (guru_id,))
            row = cur.fetchone()
            if not row:
                return False
            teks = f"{row[0] or ''} {row[1] or ''}".casefold()
            return "guru bk" in teks or "bimbingan" in teks
    except Exception:
        return False
    finally:
        conn.close()


def ganti_sandi(guru_id, lama, baru):
    """None jika berhasil, selain itu pesan kesalahan."""
    lama = lama or ""
    baru = baru or ""
    if not guru_id:
        return "Akun guru tidak ditemukan."
    if len(baru) < 6:
        return "Password baru minimal 6 karakter."
    if len(baru) > 72:
        return "Password baru maksimal 72 karakter."
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash FROM guru WHERE id = %s AND aktif = 1",
                (guru_id,),
            )
            row = cur.fetchone()
            if not row or not row[0]:
                return "Akun guru tidak ditemukan."
            try:
                cocok = check_password_hash(row[0], lama)
            except ValueError:
                cocok = False
            if not cocok:
                return "Password saat ini tidak sesuai."
            cur.execute(
                "UPDATE guru SET password_hash = %s WHERE id = %s",
                (generate_password_hash(baru), guru_id),
            )
        conn.commit()
        return None
    finally:
        conn.close()


def cari(username, password):
    """Dict akun jika guru piket atau guru BK, 'bukan_piket' jika sandi benar tetapi tidak berhak, selain itu None."""
    akun = _rapi(username)
    if not akun or not password:
        return None
    siapkan()
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, nama, username, password_hash
                FROM guru
                WHERE aktif = 1 AND LOWER(username) = LOWER(%s)
                LIMIT 1
                """,
                (akun,),
            )
            row = cur.fetchone()
            if not row or not row[3]:
                return None
            try:
                cocok = check_password_hash(row[3], password)
            except ValueError:
                return None
            if not cocok:
                return None
            cur.execute("SELECT 1 FROM guru_piket WHERE guru_id = %s LIMIT 1", (row[0],))
            piket = cur.fetchone() is not None
        bk = mengajar_bk(row[0])
        mengampu = punya_mapel(row[0])
        if piket:
            peran = "guru_piket"
        elif bk:
            peran = "guru_bk"
        elif mengampu:
            peran = "guru_pengampu"
        else:
            return "bukan_piket"
        return {
            "id": row[0],
            "nama": row[1],
            "username": row[2],
            "role": peran,
        }
    finally:
        conn.close()


def id_piket():
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT guru_id FROM guru_piket")
            return {row[0] for row in cur.fetchall()}
    finally:
        conn.close()
