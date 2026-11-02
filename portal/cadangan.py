"""Cadangan SQL untuk database portal SMARTMU, dan pemulihan dari berkas itu."""

import os
import re
from datetime import datetime

import pymysql
from pymysql.cursors import SSCursor

from pengaturan import (
    ERAPOR_DATABASE,
    INVENTARIS_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    PRESENSI_DATABASE,
    SMARTMU_DATABASE,
    TAHFIDZ_DATABASE,
)

PENANDA = "-- Cadangan SMARTMU 22"
BATAS_BERKAS = 256 * 1024 * 1024
_NAMA = re.compile(r"^[A-Za-z0-9_]+$")
_AWAL = re.compile(r"^([A-Za-z]+)\b")
_BUAT_TABEL = re.compile(
    r"^CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`([A-Za-z0-9_]+)`",
    re.I,
)
_BUAT_VIEW = re.compile(
    r"^CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+`([A-Za-z0-9_]+)`",
    re.I,
)
_DILARANG = re.compile(
    r"\b("
    r"INTO\s+OUTFILE|INTO\s+DUMPFILE|LOAD_FILE|LOAD\s+DATA|"
    r"GRANT|REVOKE|CREATE\s+USER|DROP\s+USER|ALTER\s+USER|DROP\s+DATABASE|"
    r"SHUTDOWN|PREPARE|EXECUTE|DEALLOCATE|INSTALL|UNINSTALL|"
    r"CHANGE\s+MASTER|SET\s+PASSWORD|FLUSH|KILL|SYSTEM"
    r")\b",
    re.I,
)
_SISTEM = re.compile(
    r"\b(mysql|information_schema|performance_schema|sys)\s*\.",
    re.I,
)


class CadanganError(Exception):
    pass


def basis():
    urutan = (
        ("Portal dan Rapor BK", SMARTMU_DATABASE),
        ("Presensi", PRESENSI_DATABASE),
        ("eRapor", ERAPOR_DATABASE),
        ("Tahfidz", TAHFIDZ_DATABASE),
        ("Inventaris", INVENTARIS_DATABASE),
    )
    hasil = []
    sudah = set()
    for judul, nama in urutan:
        if not _NAMA.fullmatch(nama or "") or nama in sudah:
            continue
        sudah.add(nama)
        hasil.append({"judul": judul, "nama": nama})
    return hasil


def nama_diizinkan():
    return [item["nama"] for item in basis()]


def _koneksi(database=None, kamus=False):
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database,
        charset="utf8mb4",
        autocommit=False,
        local_infile=False,
        cursorclass=pymysql.cursors.DictCursor if kamus else pymysql.cursors.Cursor,
    )


def info_database():
    daftar = basis()
    nama = [item["nama"] for item in daftar]
    conn = _koneksi(kamus=True)
    try:
        with conn.cursor() as cur:
            tanda = ",".join(["%s"] * len(nama))
            cur.execute(
                f"""SELECT table_schema AS nama, COUNT(*) AS tabel,
                           COALESCE(SUM(data_length + index_length), 0) AS ukuran
                    FROM information_schema.tables
                    WHERE table_schema IN ({tanda})
                    GROUP BY table_schema""",
                nama,
            )
            baris = {row["nama"]: row for row in cur.fetchall()}
    finally:
        conn.close()
    for item in daftar:
        ketemu = baris.get(item["nama"])
        item["ada"] = ketemu is not None
        item["tabel"] = int(ketemu["tabel"]) if ketemu else 0
        item["ukuran"] = int(ketemu["ukuran"]) if ketemu else 0
    return daftar


def format_ukuran(jumlah):
    if jumlah < 1024 * 1024:
        return f"{jumlah / 1024:.0f} KB"
    teks = f"{jumlah / 1024 / 1024:.1f} MB"
    return teks.replace(".", ",")


def nama_berkas(daftar_nama):
    cap = datetime.now().strftime("%Y%m%d-%H%M")
    if len(daftar_nama) == 1:
        return f"smartmu-{daftar_nama[0]}-{cap}.sql"
    return f"smartmu-cadangan-{cap}.sql"


def _kutip(nama):
    if not _NAMA.fullmatch(nama):
        raise CadanganError("Nama database tidak valid.")
    return f"`{nama}`"


def _tulis_tabel(berkas, conn, tabel):
    with conn.cursor() as cur:
        cur.execute(f"SHOW CREATE TABLE {_kutip(tabel)}")
        definisi = cur.fetchone()[1]
    berkas.write(f"DROP TABLE IF EXISTS {_kutip(tabel)};\n")
    berkas.write(definisi)
    berkas.write(";\n")
    with conn.cursor(SSCursor) as cur:
        cur.execute(f"SELECT * FROM {_kutip(tabel)}")
        kolom = [item[0] for item in cur.description]
        kepala = ", ".join(_kutip(nama) for nama in kolom)
        kelompok = []

        def simpan():
            if not kelompok:
                return
            berkas.write(f"INSERT INTO {_kutip(tabel)} ({kepala}) VALUES\n")
            berkas.write(",\n".join(kelompok))
            berkas.write(";\n")
            kelompok.clear()

        for baris in cur:
            nilai = ", ".join(conn.escape(nilai) for nilai in baris)
            kelompok.append(f"({nilai})")
            if len(kelompok) >= 100:
                simpan()
        simpan()
    berkas.write("\n")


def tulis(jalur, daftar_nama, diizinkan=None):
    diizinkan = set(diizinkan or nama_diizinkan())
    pilihan = []
    for nama in daftar_nama:
        if nama not in diizinkan:
            raise CadanganError("Database itu bukan bagian dari SMARTMU.")
        if nama not in pilihan:
            pilihan.append(nama)
    if not pilihan:
        raise CadanganError("Tidak ada database yang dicadangkan.")
    with open(jalur, "w", encoding="utf-8", newline="\n") as berkas:
        berkas.write(PENANDA + "\n")
        berkas.write(f"-- {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        berkas.write("SET NAMES utf8mb4;\n")
        berkas.write("SET FOREIGN_KEY_CHECKS=0;\n")
        berkas.write("SET UNIQUE_CHECKS=0;\n")
        berkas.write("SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO';\n\n")
        for nama in pilihan:
            try:
                conn = _koneksi(nama)
            except pymysql.MySQLError as exc:
                pesan = exc.args[1] if len(exc.args) > 1 else exc
                raise CadanganError(f"Database {nama} tidak dapat dibaca. {pesan}") from exc
            try:
                with conn.cursor() as cur:
                    cur.execute("START TRANSACTION WITH CONSISTENT SNAPSHOT")
                    cur.execute("SHOW FULL TABLES")
                    tabel = [baris[0] for baris in cur.fetchall() if baris[1] == "BASE TABLE"]
                berkas.write(f"-- Database: {nama}\n")
                berkas.write(
                    f"CREATE DATABASE IF NOT EXISTS {_kutip(nama)} "
                    "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n"
                )
                berkas.write(f"USE {_kutip(nama)};\n\n")
                for satu in tabel:
                    _tulis_tabel(berkas, conn, satu)
                conn.commit()
            finally:
                conn.close()
        berkas.write("SET FOREIGN_KEY_CHECKS=1;\n")
        berkas.write("SET UNIQUE_CHECKS=1;\n")


def pecah_teks(data):
    buf = []
    mode = "kode"
    i = 0
    n = len(data)
    while i < n:
        c = data[i]
        nxt = data[i + 1] if i + 1 < n else ""
        if mode == "kode":
            if c == "-" and nxt == "-" and (i + 2 >= n or data[i + 2] in " \t"):
                mode = "garis"
                i += 2
                continue
            if c == "#":
                mode = "garis"
                i += 1
                continue
            if c == "/" and nxt == "*":
                if i + 2 < n and data[i + 2] == "!":
                    mode = "khusus"
                    i += 3
                    while i < n and data[i].isdigit():
                        i += 1
                    continue
                mode = "blok"
                i += 2
                continue
            if c in {"'", '"', "`"}:
                mode = c
                buf.append(c)
                i += 1
                continue
            if c == ";":
                stmt = "".join(buf).strip()
                buf = []
                if stmt:
                    yield stmt
                i += 1
                continue
            buf.append(c)
            i += 1
            continue
        if mode == "garis":
            if c in "\r\n":
                mode = "kode"
            i += 1
            continue
        if mode == "blok":
            if c == "*" and nxt == "/":
                mode = "kode"
                i += 2
                continue
            i += 1
            continue
        if mode == "khusus":
            if c == "*" and nxt == "/":
                mode = "kode"
                i += 2
                continue
            buf.append(c)
            i += 1
            continue
        buf.append(c)
        if c == "\\" and nxt:
            buf.append(nxt)
            i += 2
            continue
        if c == mode and nxt == mode and mode in {"'", '"', "`"}:
            buf.append(nxt)
            i += 2
            continue
        if c == mode:
            mode = "kode"
        i += 1
    stmt = "".join(buf).strip()
    if stmt:
        yield stmt


def _tanpa_literal(stmt):
    return re.sub(r"'(?:\\.|''|[^'])*'|\"(?:\\.|\"\"|[^\"])*\"", "''", stmt)


def _skema_sekarang(stmt, sekarang, diizinkan):
    bersih = _tanpa_literal(stmt).strip()
    if _DILARANG.search(bersih) or _SISTEM.search(bersih):
        raise CadanganError("Berkas berisi perintah SQL yang tidak diizinkan.")
    if re.search(r"\bGLOBAL\b|\bPERSIST\b|@@\s*global", bersih, re.I):
        raise CadanganError("Berkas berisi perintah SQL yang tidak diizinkan.")
    for nama in re.findall(r"`([A-Za-z0-9_]+)`\s*\.", bersih):
        if nama.lower() not in diizinkan:
            raise CadanganError("Berkas menyebut database di luar SMARTMU.")
    cocok = _AWAL.match(bersih)
    if not cocok:
        raise CadanganError("Ada perintah SQL yang tidak dikenali.")
    awal = cocok.group(1).upper()
    if awal == "USE":
        m = re.fullmatch(r"USE\s+`([A-Za-z0-9_]+)`|USE\s+([A-Za-z0-9_]+)", bersih, re.I)
        if not m:
            raise CadanganError("Perintah USE tidak valid.")
        nama = (m.group(1) or m.group(2)).lower()
        if nama not in diizinkan:
            raise CadanganError("Perintah USE mengarah ke database di luar SMARTMU.")
        return nama
    if awal == "CREATE" and re.match(r"CREATE\s+DATABASE\b", bersih, re.I):
        m = re.match(
            r"CREATE\s+DATABASE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?([A-Za-z0-9_]+)`?",
            bersih,
            re.I,
        )
        if not m or m.group(1).lower() not in diizinkan:
            raise CadanganError("CREATE DATABASE mengarah ke database di luar SMARTMU.")
        return sekarang
    if awal in {"SET", "START", "COMMIT", "BEGIN", "ROLLBACK"}:
        return sekarang
    if sekarang is None:
        raise CadanganError("Cadangan harus memuat USE sebelum mengubah tabel.")
    if awal == "CREATE":
        if not re.match(r"CREATE\s+(TABLE|OR\s+REPLACE\s+VIEW|VIEW)\b", bersih, re.I):
            raise CadanganError("Jenis CREATE itu tidak diizinkan.")
        return sekarang
    if awal == "DROP":
        if not re.match(r"DROP\s+(TABLE|VIEW)\b", bersih, re.I):
            raise CadanganError("Jenis DROP itu tidak diizinkan.")
        return sekarang
    if awal in {"INSERT", "LOCK", "UNLOCK"}:
        return sekarang
    if awal == "ALTER":
        if not re.match(
            r"ALTER\s+TABLE\s+.+\s+(DISABLE|ENABLE)\s+KEYS\s*$",
            bersih,
            re.I | re.S,
        ):
            raise CadanganError("ALTER hanya boleh DISABLE KEYS atau ENABLE KEYS.")
        return sekarang
    raise CadanganError("Ada perintah SQL yang tidak diizinkan.")


def _objek_dibuat(stmt):
    bersih = _tanpa_literal(stmt).strip()
    tabel = _BUAT_TABEL.match(bersih)
    if tabel:
        return "BASE TABLE", tabel.group(1)
    view = _BUAT_VIEW.match(bersih)
    if view:
        return "VIEW", view.group(1)
    return None


def pulihkan(jalur, diizinkan=None):
    if os.path.getsize(jalur) > BATAS_BERKAS:
        raise CadanganError("Berkas cadangan lebih besar dari 256 MB.")
    with open(jalur, "r", encoding="utf-8-sig", newline="") as berkas:
        isi = berkas.read()
    if "\x00" in isi:
        raise CadanganError("Berkas bukan cadangan SQL.")
    if not isi.strip():
        raise CadanganError("Berkas cadangan kosong.")
    lengkap = PENANDA in isi.splitlines()[0]
    boleh = {nama.lower(): nama for nama in (diizinkan or nama_diizinkan())}
    perintah = []
    sekarang = None
    dibuat = {}
    for stmt in pecah_teks(isi):
        sekarang = _skema_sekarang(stmt, sekarang, set(boleh))
        perintah.append((sekarang, stmt))
        if sekarang and re.match(r"USE\b", stmt.strip(), re.I):
            dibuat.setdefault(sekarang, [])
        objek = _objek_dibuat(stmt)
        if objek and sekarang:
            dibuat.setdefault(sekarang, []).append(objek)
    if not perintah:
        raise CadanganError("Tidak ada perintah SQL pada berkas.")
    conn = _koneksi()
    try:
        with conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS=0")
            if lengkap:
                _hapus_sisa(cur, dibuat, boleh)
            for _, stmt in perintah:
                cur.execute(stmt)
            cur.execute("SET FOREIGN_KEY_CHECKS=1")
        conn.commit()
    except pymysql.MySQLError as exc:
        conn.rollback()
        raise CadanganError(
            "Pemulihan terhenti. Sebagian tabel mungkin sudah berubah. "
            f"Pesan MySQL: {exc.args[1] if len(exc.args) > 1 else exc}"
        ) from exc
    finally:
        conn.close()


def _hapus_sisa(cur, dibuat, boleh):
    for skema, objek in dibuat.items():
        asli = boleh.get(skema)
        if not asli:
            continue
        dipertahankan = {nama.lower() for _, nama in objek}
        cur.execute(
            """SELECT table_name, table_type FROM information_schema.tables
               WHERE table_schema=%s""",
            (asli,),
        )
        for nama, jenis in cur.fetchall():
            if nama.lower() in dipertahankan:
                continue
            if jenis == "VIEW":
                cur.execute(f"DROP VIEW {_kutip(asli)}.{_kutip(nama)}")
            else:
                cur.execute(f"DROP TABLE {_kutip(asli)}.{_kutip(nama)}")
