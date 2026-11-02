"""Akun portal SMARTMU: username, kata sandi, dan portal yang boleh dibuka."""

import re

import pymysql
from werkzeug.security import check_password_hash, generate_password_hash

from pengaturan import (
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    SMARTMU_DATABASE,
    TAHFIDZ_DATABASE,
)

_USERNAME = re.compile(r"^[\w.\-]{3,50}$", re.UNICODE)
PERAN = {
    "admin": "Admin",
    "guru": "Guru",
    "musyrif": "Musyrif",
    "bk": "Rapor BK",
    "orang_tua": "Orang tua",
}
PORTAL = (
    ("presensi", "Presensi"),
    ("erapor", "eRapor"),
    ("tahfidz", "Tahfidz"),
    ("bk", "Rapor BK"),
    ("inventaris", "Inventaris"),
)
NAMA_PORTAL = dict(PORTAL)
_tabel_siap = False


class AkunError(Exception):
    pass


def _koneksi():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=SMARTMU_DATABASE,
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )


def pastikan_tabel():
    global _tabel_siap
    if _tabel_siap:
        return
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS pengguna_akses (
                    pengguna_id INT NOT NULL,
                    portal VARCHAR(20) NOT NULL,
                    PRIMARY KEY (pengguna_id, portal)
                )"""
            )
    finally:
        conn.close()
    _tabel_siap = True


def saring(pilihan):
    boleh = set(NAMA_PORTAL)
    hasil = []
    for kunci in pilihan or []:
        if kunci in boleh and kunci not in hasil:
            hasil.append(kunci)
    return hasil


def akses(pengguna_id):
    pastikan_tabel()
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT portal FROM pengguna_akses WHERE pengguna_id=%s ORDER BY portal",
                (pengguna_id,),
            )
            return [baris["portal"] for baris in cur.fetchall()]
    finally:
        conn.close()


def akses_username(username):
    pastikan_tabel()
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT a.portal
                   FROM pengguna_akses a
                   JOIN pengguna p ON p.id = a.pengguna_id
                   WHERE p.username=%s AND p.aktif=1 AND p.role<>'admin'""",
                (username,),
            )
            return {baris["portal"] for baris in cur.fetchall()}
    finally:
        conn.close()


def simpan_akses(pengguna_id, pilihan):
    pilihan = saring(pilihan)
    pastikan_tabel()
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pengguna_akses WHERE pengguna_id=%s", (pengguna_id,))
            for kunci in pilihan:
                cur.execute(
                    "INSERT INTO pengguna_akses (pengguna_id, portal) VALUES (%s, %s)",
                    (pengguna_id, kunci),
                )
    finally:
        conn.close()
    return pilihan


def _lengkapi(baris):
    if not baris:
        return baris
    if baris["role"] == "admin":
        baris["akses"] = [kunci for kunci, _nama in PORTAL]
        baris["semua"] = True
    else:
        baris["akses"] = akses(baris["id"])
        baris["semua"] = False
    baris["akses_nama"] = ", ".join(NAMA_PORTAL[kunci] for kunci in baris["akses"] if kunci in NAMA_PORTAL)
    return baris


def daftar():
    pastikan_tabel()
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, username, nama, role, aktif
                   FROM pengguna ORDER BY nama, username"""
            )
            baris = cur.fetchall()
    finally:
        conn.close()
    return [_lengkapi(orang) for orang in baris]


def ambil(pengguna_id):
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, nama, role, aktif FROM pengguna WHERE id=%s",
                (pengguna_id,),
            )
            return _lengkapi(cur.fetchone())
    finally:
        conn.close()


def buat(nama, username, password, pilihan):
    nama = (nama or "").strip()
    if len(nama) < 3 or len(nama) > 150:
        raise AkunError("Nama minimal 3 karakter.")
    username = periksa_username(username)
    if len(password or "") < 6:
        raise AkunError("Kata sandi baru minimal 6 karakter.")
    pilihan = saring(pilihan)
    if not pilihan:
        raise AkunError("Pilih minimal satu portal yang boleh dibuka.")
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM pengguna WHERE username=%s", (username,))
            if cur.fetchone():
                raise AkunError("Username sudah dipakai pengguna lain.")
            cur.execute(
                """INSERT INTO pengguna (username, password_hash, nama, role)
                   VALUES (%s, %s, %s, 'guru')""",
                (username, generate_password_hash(password), nama),
            )
            pengguna_id = cur.lastrowid
    except pymysql.IntegrityError as exc:
        raise AkunError("Username sudah dipakai pengguna lain.") from exc
    finally:
        conn.close()
    simpan_akses(pengguna_id, pilihan)
    return ambil(pengguna_id)


def cari_orang_tua(username, password):
    """Akun orang tua diambil dari pengguna Tahfidz, bukan dari tabel portal."""
    username = " ".join((username or "").split())
    if not username or not password:
        return None
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=TAHFIDZ_DATABASE,
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, username, password_hash, nama_lengkap, role, must_change_password
                   FROM users
                   WHERE LOWER(username)=LOWER(%s) AND role='orang_tua' AND aktif=1""",
                (username,),
            )
            orang = cur.fetchone()
    except pymysql.MySQLError:
        return None
    finally:
        conn.close()
    if not orang or not check_password_hash(orang["password_hash"], password):
        return None
    return orang


def kata_sandi_cocok(pengguna_id, password):
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash FROM pengguna WHERE id=%s",
                (pengguna_id,),
            )
            baris = cur.fetchone()
    finally:
        conn.close()
    if not baris:
        return False
    return check_password_hash(baris["password_hash"], password or "")


def periksa_username(username):
    username = (username or "").strip()
    if not _USERNAME.fullmatch(username):
        raise AkunError(
            "Username 3–50 karakter: huruf, angka, titik, garis bawah, atau tanda hubung."
        )
    return username


def periksa_password(password, ulang):
    if password != ulang:
        raise AkunError("Konfirmasi kata sandi tidak sama.")
    if len(password) < 6:
        raise AkunError("Kata sandi baru minimal 6 karakter.")
    return password


def ubah(pengguna_id, username, password=None):
    username = periksa_username(username)
    sekarang = ambil(pengguna_id)
    if not sekarang:
        raise AkunError("Pengguna tidak ditemukan.")
    if password is not None:
        if len(password) < 6:
            raise AkunError("Kata sandi baru minimal 6 karakter.")
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM pengguna WHERE username=%s AND id<>%s",
                (username, pengguna_id),
            )
            if cur.fetchone():
                raise AkunError("Username sudah dipakai pengguna lain.")
            if password is None:
                if username == sekarang["username"]:
                    raise AkunError("Tidak ada perubahan.")
                cur.execute(
                    "UPDATE pengguna SET username=%s WHERE id=%s",
                    (username, pengguna_id),
                )
            else:
                cur.execute(
                    "UPDATE pengguna SET username=%s, password_hash=%s WHERE id=%s",
                    (username, generate_password_hash(password), pengguna_id),
                )
    except pymysql.IntegrityError as exc:
        raise AkunError("Username sudah dipakai pengguna lain.") from exc
    finally:
        conn.close()
    return ambil(pengguna_id)
