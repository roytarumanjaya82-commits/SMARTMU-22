from sqlalchemy import inspect, text

from tpk.extensions import db


def sync_schema():
    """Tambah kolom/tabel baru tanpa migrasi formal."""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    if "soal_wawancara" in tables:
        cols = {c["name"] for c in inspector.get_columns("soal_wawancara")}
        if "bobot" not in cols:
            db.session.execute(
                text("ALTER TABLE soal_wawancara ADD COLUMN bobot INTEGER DEFAULT 12")
            )
            db.session.commit()

    if "soal_tes" in tables:
        cols = {c["name"] for c in inspector.get_columns("soal_tes")}
        if "gambar" not in cols:
            db.session.execute(
                text("ALTER TABLE soal_tes ADD COLUMN gambar VARCHAR(255) NULL")
            )
            db.session.commit()
        if "materi" not in cols:
            db.session.execute(
                text("ALTER TABLE soal_tes ADD COLUMN materi VARCHAR(200) NULL")
            )
            db.session.commit()
        if "indikator" not in cols:
            db.session.execute(
                text("ALTER TABLE soal_tes ADD COLUMN indikator TEXT NULL")
            )
            db.session.commit()
        if "level_kognitif" not in cols:
            db.session.execute(
                text(
                    "ALTER TABLE soal_tes ADD COLUMN level_kognitif VARCHAR(20) NULL"
                )
            )
            db.session.commit()
        for kolom in ("gambar_opsi_a", "gambar_opsi_b", "gambar_opsi_c", "gambar_opsi_d"):
            if kolom not in cols:
                try:
                    db.session.execute(
                        text(f"ALTER TABLE soal_tes ADD COLUMN {kolom} VARCHAR(255) NULL")
                    )
                    db.session.commit()
                except Exception:  # noqa: BLE001
                    db.session.rollback()
                else:
                    cols.add(kolom)
        # Perpanjang opsi agar muat teks Arab / kalimat panjang
        for col_name in ("opsi_a", "opsi_b", "opsi_c", "opsi_d"):
            try:
                db.session.execute(
                    text(f"ALTER TABLE soal_tes MODIFY COLUMN {col_name} TEXT NOT NULL")
                )
                db.session.commit()
            except Exception:  # noqa: BLE001
                db.session.rollback()

    if "murid" in tables:
        cols = {c["name"] for c in inspector.get_columns("murid")}
        if "nomor_urut" not in cols:
            db.session.execute(text("ALTER TABLE murid ADD COLUMN nomor_urut VARCHAR(20) NULL"))
            db.session.commit()
        if "alamat_ortu" not in cols:
            db.session.execute(text("ALTER TABLE murid ADD COLUMN alamat_ortu TEXT NULL"))
            db.session.commit()
        if "gelombang" not in cols:
            db.session.execute(text("ALTER TABLE murid ADD COLUMN gelombang VARCHAR(50) NULL"))
            db.session.commit()
        if "tahun_ajaran" not in cols:
            db.session.execute(
                text("ALTER TABLE murid ADD COLUMN tahun_ajaran VARCHAR(20) NULL")
            )
            db.session.commit()
        if "ortu_user_id" not in cols:
            db.session.execute(
                text("ALTER TABLE murid ADD COLUMN ortu_user_id INTEGER NULL")
            )
            db.session.commit()
            try:
                db.session.execute(
                    text(
                        "ALTER TABLE murid ADD CONSTRAINT uq_murid_ortu_user "
                        "UNIQUE (ortu_user_id)"
                    )
                )
                db.session.commit()
            except Exception:  # noqa: BLE001
                db.session.rollback()
            try:
                db.session.execute(
                    text(
                        "ALTER TABLE murid ADD CONSTRAINT fk_murid_ortu_user "
                        "FOREIGN KEY (ortu_user_id) REFERENCES users(id)"
                    )
                )
                db.session.commit()
            except Exception:  # noqa: BLE001
                db.session.rollback()
        if "nilai_psikotes" not in cols:
            db.session.execute(
                text("ALTER TABLE murid ADD COLUMN nilai_psikotes FLOAT NULL")
            )
            db.session.commit()
        if "catatan_psikotes" not in cols:
            db.session.execute(
                text("ALTER TABLE murid ADD COLUMN catatan_psikotes TEXT NULL")
            )
            db.session.commit()
        if "is_tes_susulan" not in cols:
            db.session.execute(
                text(
                    "ALTER TABLE murid ADD COLUMN is_tes_susulan "
                    "TINYINT(1) DEFAULT 0"
                )
            )
            db.session.commit()
        if "alasan_susulan" not in cols:
            db.session.execute(
                text("ALTER TABLE murid ADD COLUMN alasan_susulan TEXT NULL")
            )
            db.session.commit()
        if "tanggal_susulan" not in cols:
            db.session.execute(
                text("ALTER TABLE murid ADD COLUMN tanggal_susulan DATE NULL")
            )
            db.session.commit()
        if "kelas_usulan" not in cols:
            db.session.execute(
                text("ALTER TABLE murid ADD COLUMN kelas_usulan VARCHAR(30) NULL")
            )
            db.session.commit()
        if "skor_penempatan" not in cols:
            db.session.execute(
                text("ALTER TABLE murid ADD COLUMN skor_penempatan FLOAT NULL")
            )
            db.session.commit()
        if "acc_penempatan" not in cols:
            db.session.execute(
                text(
                    "ALTER TABLE murid ADD COLUMN acc_penempatan "
                    "TINYINT(1) DEFAULT 0"
                )
            )
            db.session.commit()
        if "acc_at" not in cols:
            db.session.execute(
                text("ALTER TABLE murid ADD COLUMN acc_at DATETIME NULL")
            )
            db.session.commit()

    if "kunci_tes_gelombang" in tables:
        cols = {c["name"] for c in inspector.get_columns("kunci_tes_gelombang")}
        if "jenis" not in cols:
            try:
                db.session.execute(
                    text(
                        "ALTER TABLE kunci_tes_gelombang "
                        "ADD COLUMN jenis VARCHAR(20) NOT NULL DEFAULT 'reguler'"
                    )
                )
                db.session.commit()
            except Exception:  # noqa: BLE001
                db.session.rollback()
            # Unique lama (tahun+gelombang) diganti lewat create_all / abaikan jika gagal
            try:
                db.session.execute(
                    text(
                        "ALTER TABLE kunci_tes_gelombang "
                        "DROP INDEX uq_kunci_tes_tahun_gelombang"
                    )
                )
                db.session.commit()
            except Exception:  # noqa: BLE001
                db.session.rollback()
            try:
                db.session.execute(
                    text(
                        "ALTER TABLE kunci_tes_gelombang "
                        "ADD UNIQUE KEY uq_kunci_tes_tahun_gelombang_jenis "
                        "(tahun_ajaran, gelombang, jenis)"
                    )
                )
                db.session.commit()
            except Exception:  # noqa: BLE001
                db.session.rollback()

    if "users" in tables:
        cols = {c["name"] for c in inspector.get_columns("users")}
        if "juga_pembuat_soal" not in cols:
            try:
                db.session.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN juga_pembuat_soal "
                        "TINYINT(1) NOT NULL DEFAULT 0"
                    )
                )
                db.session.commit()
            except Exception:  # noqa: BLE001
                db.session.rollback()

    db.create_all()