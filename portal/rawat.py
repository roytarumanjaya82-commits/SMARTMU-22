"""Status maintenance seluruh portal SMARTMU."""

import threading
import time

import pymysql

from pengaturan import (
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    SMARTMU_DATABASE,
)

_KUNCI = "maintenance"
_UMUR = 2.0
_gembok = threading.Lock()
_cache = {"siap": False, "nilai": False, "saat": 0.0}
_tabel_siap = False


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
                """CREATE TABLE IF NOT EXISTS pengaturan (
                    kunci VARCHAR(40) PRIMARY KEY,
                    nilai VARCHAR(255) NOT NULL
                )"""
            )
    finally:
        conn.close()
    _tabel_siap = True


def _baca():
    pastikan_tabel()
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT nilai FROM pengaturan WHERE kunci=%s", (_KUNCI,))
            baris = cur.fetchone()
    finally:
        conn.close()
    return bool(baris and baris["nilai"] == "1")


def aktif():
    sekarang = time.monotonic()
    with _gembok:
        if _cache["siap"] and sekarang - _cache["saat"] < _UMUR:
            return _cache["nilai"]
    try:
        nilai = _baca()
    except pymysql.MySQLError:
        return False
    with _gembok:
        _cache.update(siap=True, nilai=nilai, saat=time.monotonic())
    return nilai


def atur(nyala):
    nilai = "1" if nyala else "0"
    pastikan_tabel()
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO pengaturan (kunci, nilai) VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE nilai=VALUES(nilai)""",
                (_KUNCI, nilai),
            )
    finally:
        conn.close()
    with _gembok:
        _cache.update(siap=True, nilai=bool(nyala), saat=time.monotonic())
