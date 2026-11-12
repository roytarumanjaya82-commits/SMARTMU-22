"""Tambah kolom aktif pada tabel soal jika belum ada."""
from __future__ import annotations

import sys
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from koding.config import Config  # noqa: E402


def main():
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=DictCursor,
        charset="utf8mb4",
    )
    with conn.cursor() as cur:
        cur.execute("SHOW COLUMNS FROM soal LIKE 'aktif'")
        if cur.fetchone():
            print("OK: kolom soal.aktif sudah ada")
        else:
            cur.execute(
                """
                ALTER TABLE soal
                ADD COLUMN aktif TINYINT(1) NOT NULL DEFAULT 0
                AFTER bobot
                """
            )
            conn.commit()
            print("OK: kolom soal.aktif ditambahkan (default nonaktif)")
        # Pastikan default kolom = nonaktif
        cur.execute("ALTER TABLE soal MODIFY aktif TINYINT(1) NOT NULL DEFAULT 0")
        cur.execute("ALTER TABLE ujian MODIFY aktif TINYINT(1) NOT NULL DEFAULT 0")
        conn.commit()
        print("OK: default ujian.aktif & soal.aktif = 0")
    conn.close()


if __name__ == "__main__":
    main()
