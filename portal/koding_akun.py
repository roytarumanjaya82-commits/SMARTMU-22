"""Autentikasi akun Kelas Koding (murid/guru) dari database koding_smpm22."""

import pymysql
from pymysql.cursors import DictCursor
from werkzeug.security import check_password_hash

from pengaturan import (
    KODING_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
)


def _koneksi():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=KODING_DATABASE,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )


def cari(username: str, password: str):
    """Kembalikan dict akun koding jika username/password cocok, selain itu None."""
    username = (username or "").strip()
    if not username or not password:
        return None
    try:
        conn = _koneksi()
    except pymysql.MySQLError:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, password_hash, nama_lengkap, role
                FROM users
                WHERE username=%s AND aktif=1
                LIMIT 1
                """,
                (username,),
            )
            user = cur.fetchone()
            if not user or not check_password_hash(user["password_hash"], password):
                return None
            if user["role"] == "siswa":
                cur.execute(
                    """
                    SELECT s.nis, k.nama_kelas, k.tingkat
                    FROM siswa s
                    LEFT JOIN kelas k ON k.id=s.kelas_id
                    WHERE s.user_id=%s
                    LIMIT 1
                    """,
                    (user["id"],),
                )
                siswa = cur.fetchone()
                if not siswa:
                    return None
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "nama": user["nama_lengkap"],
                    "role": "siswa_koding",
                    "nis": siswa.get("nis") or user["username"],
                    "nama_kelas": siswa.get("nama_kelas"),
                    "tingkat": siswa.get("tingkat") or "7",
                }
            if user["role"] == "guru":
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "nama": user["nama_lengkap"],
                    "role": "guru_koding",
                }
            return None
    finally:
        conn.close()
