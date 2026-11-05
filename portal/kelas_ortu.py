"""Menu orang tua mengikuti kelas anak di database Tahfidz."""

import pymysql

from pengaturan import (
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    PRESENSI_DATABASE,
    TAHFIDZ_DATABASE,
)


def _kunci(nama):
    return "".join(str(nama or "").split()).casefold().replace("-", ".")


def _koneksi(database):
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database,
        charset="utf8mb4",
    )


def anak_ikut_tahfidz(username, user_id=None):
    """Benar bila salah satu anak orang tua berada di kelas yang ada di Tahfidz."""
    username = " ".join(str(username or "").split())
    if not username and not user_id:
        return False
    try:
        conn = _koneksi(TAHFIDZ_DATABASE)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT nama FROM kelas WHERE aktif = 1")
                kelas_tahfidz = {_kunci(row[0]) for row in cur.fetchall()}
                kelas_tahfidz.discard("")
                cur.execute(
                    """
                    SELECT k.nama
                    FROM siswa s
                    JOIN kelas k ON k.id = s.kelas_id
                    JOIN users u ON u.id = s.orang_tua_user_id
                    WHERE s.aktif = 1 AND u.aktif = 1 AND u.role = 'orang_tua'
                      AND (u.id = %s OR LOWER(u.username) = LOWER(%s))
                    """,
                    (user_id or 0, username),
                )
                for (nama,) in cur.fetchall():
                    if _kunci(nama) in kelas_tahfidz:
                        return True
        finally:
            conn.close()
        if not username or not kelas_tahfidz:
            return False
        conn = _koneksi(PRESENSI_DATABASE)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT k.nama_kelas
                    FROM siswa s
                    JOIN kelas k ON k.id = s.kelas_id
                    WHERE s.aktif = 1 AND (
                        LOWER(s.nama_orang_tua) = LOWER(%s)
                        OR LOWER(s.username_ortu) = LOWER(%s)
                    )
                    """,
                    (username, username),
                )
                for (nama,) in cur.fetchall():
                    if _kunci(nama) in kelas_tahfidz:
                        return True
        finally:
            conn.close()
    except Exception:
        return False
    return False
