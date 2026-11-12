"""Tambah kolom file materi (PDF/DOC/PPT) jika belum ada."""
import sys
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from koding.config import Config  # noqa: E402

COLUMNS = {
    "file_nama": "VARCHAR(255) NULL",
    "file_path": "VARCHAR(500) NULL",
    "file_tipe": "VARCHAR(20) NULL",
    "file_ukuran": "INT NULL",
}


def main():
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COLUMN_NAME FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA=%s AND TABLE_NAME='materi'
                """,
                (Config.MYSQL_DB,),
            )
            existing = {r[0] for r in cur.fetchall()}
            after = "contoh_kode"
            for name, typedef in COLUMNS.items():
                if name in existing:
                    print(f"OK sudah ada: {name}")
                    continue
                cur.execute(
                    f"ALTER TABLE materi ADD COLUMN {name} {typedef} AFTER {after}"
                )
                print(f"Ditambahkan: {name}")
                after = name
        print("Migrasi materi file selesai.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
