"""Read a daftar nilai workbook into a student roster.

Expected shape, matching DAFTAR NILAI INFORMATIKA GANJIL:
- one worksheet per class (7.1, 7.2, ...), or one sheet with class section rows
- a header row that contains a name column (Nama / Nama Siswa / Nama Peserta Didik)
- optional NIS / NISN and L/P columns
"""

import re

import pandas as pd

CLASS_RE = re.compile(r"(?:kelas\s*)?([7-9])\s*[\.\-]\s*(\d+)", re.IGNORECASE)
ROMAN = (("viii", "8"), ("vii", "7"), ("ix", "9"))

NAMA_HEADERS = ("nama peserta didik", "nama siswa", "nama lengkap", "nama")
NIS_HEADERS = ("nisn", "nis", "no induk")
JK_HEADERS = ("l/p", "l / p", "jk", "jenis kelamin", "kelamin")
ORTU_HEADERS = ("nama orang tua", "nama orangtua", "orang tua", "nama wali", "wali murid")


def normalize_name(value):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text


def name_key(value):
    return normalize_name(value).casefold()


def nama_dengan_gelar(nama, gelar):
    nama = normalize_name(nama)
    gelar = normalize_name(gelar)
    if not gelar or nama.casefold().endswith(gelar.casefold()):
        return nama
    return f"{nama}, {gelar}"


def lepaskan_gelar(nama, gelar):
    nama = normalize_name(nama)
    gelar = normalize_name(gelar)
    if not gelar:
        return nama
    for akhir in (f", {gelar}", f" {gelar}"):
        if nama.casefold().endswith(akhir.casefold()) and len(nama) > len(akhir):
            return nama[: -len(akhir)].strip(" ,")
    return nama


def normalize_class(value):
    text = str(value or "").strip().lower()
    if not text or text == "nan":
        return None
    for roman, digit in ROMAN:
        text = text.replace(roman, digit)
    match = CLASS_RE.search(text)
    if not match:
        return None
    return f"{match.group(1)}.{int(match.group(2))}"


def parse_nis(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return "" if text.lower() == "nan" else text


def parse_jk(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().upper()
    if text in ("L", "LAKI-LAKI", "LAKI", "M"):
        return "L"
    if text in ("P", "PEREMPUAN", "W"):
        return "P"
    return None


def _header_index(cells, names, lewati=()):
    normalized = [re.sub(r"\s+", " ", str(cell or "")).strip().lower() for cell in cells]
    for wanted in names:
        for index, cell in enumerate(normalized):
            if cell in lewati:
                continue
            if cell == wanted or cell.startswith(wanted + " "):
                return index
    return None


def _row_values(row):
    values = []
    for cell in row:
        if cell is None or (isinstance(cell, float) and pd.isna(cell)):
            values.append("")
        else:
            values.append(cell)
    return values


def _is_section_row(values):
    texts = [str(v).strip() for v in values if str(v).strip()]
    if len(texts) != 1:
        return None
    return normalize_class(texts[0])


def parse_workbook(file_obj):
    sheets = pd.read_excel(file_obj, sheet_name=None, header=None, dtype=object)
    students = []
    notes = []

    for sheet_name, frame in sheets.items():
        current_class = normalize_class(sheet_name)
        columns = None
        found_header = False
        sheet_count = 0

        for row in frame.itertuples(index=False, name=None):
            values = _row_values(row)
            section = _is_section_row(values)
            if section:
                current_class = section
                columns = None
                continue

            nama_at = _header_index(values, NAMA_HEADERS, lewati=ORTU_HEADERS)
            if nama_at is not None:
                # A data row can contain the word "nama" inside a student's name.
                # Treat the row as a header only when the name cell is exactly a header label.
                label = re.sub(r"\s+", " ", str(values[nama_at] or "")).strip().lower()
                if label in NAMA_HEADERS:
                    columns = {
                        "nama": nama_at,
                        "nis": _header_index(values, NIS_HEADERS),
                        "jk": _header_index(values, JK_HEADERS),
                        "kelas": _header_index(values, ("kelas",)),
                        "ortu": _header_index(values, ORTU_HEADERS),
                    }
                    found_header = True
                    continue

            if not columns:
                continue

            nama = normalize_name(values[columns["nama"]]) if columns["nama"] < len(values) else ""
            if not nama or name_key(nama) in ("nama", "nama siswa", "jumlah", "total"):
                continue
            if nama.lower().startswith("jumlah"):
                continue

            row_class = current_class
            if columns.get("kelas") is not None and columns["kelas"] < len(values):
                row_class = normalize_class(values[columns["kelas"]]) or current_class
            if not row_class:
                notes.append(f"Sheet '{sheet_name}': '{nama}' dilewati karena kelas tidak dikenali.")
                continue
            current_class = row_class

            nis = ""
            if columns["nis"] is not None and columns["nis"] < len(values):
                nis = parse_nis(values[columns["nis"]])
            jk = None
            if columns["jk"] is not None and columns["jk"] < len(values):
                jk = parse_jk(values[columns["jk"]])
            ortu = ""
            if columns.get("ortu") is not None and columns["ortu"] < len(values):
                ortu = normalize_name(values[columns["ortu"]])
                if ortu.lower() in ("nama orang tua", "orang tua", "-", "—"):
                    ortu = ""

            students.append({
                "kelas": current_class,
                "nama": nama,
                "nis": nis,
                "jk": jk,
                "ortu": ortu,
            })
            sheet_count += 1

        if not found_header:
            notes.append(f"Sheet '{sheet_name}' dilewati: kolom Nama tidak ditemukan.")
        elif sheet_count == 0:
            notes.append(f"Sheet '{sheet_name}' tidak berisi siswa.")

    return students, notes


def buat_blanko(password_awal="ortuSMPM22"):
    """Blanko unggah siswa. Nama orang tua menjadi username akun orang tua."""
    from io import BytesIO

    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter

    buku = Workbook()
    lembar = buku.active
    lembar.title = "Siswa"
    judul = ("No", "NIS", "Nama", "L/P", "Kelas", "Nama Orang Tua")
    lembar.append(judul)
    for sel in lembar[1]:
        sel.font = Font(bold=True, color="FFFFFF")
        sel.fill = PatternFill("solid", fgColor="1F7A4D")
    lembar.append((1, "26277001", "Contoh Siswa", "P", "7.1", "Contoh Orang Tua"))
    for indeks, lebar in enumerate((8, 16, 32, 8, 12, 32), start=1):
        lembar.column_dimensions[get_column_letter(indeks)].width = lebar
    lembar.freeze_panes = "A2"
    petunjuk = [
        "Petunjuk: isi satu baris untuk setiap siswa. Kelas ditulis seperti 7.1, 8.2, atau 9.3.",
        "Nama Orang Tua menjadi username akun orang tua, sama seperti di portal Tahfidz.",
        f"Password awal akun orang tua sama dengan portal Tahfidz: {password_awal}",
        "Satu nama orang tua boleh dipakai untuk beberapa anak. Mereka masuk dengan username dan password yang sama.",
        "Hapus baris contoh sebelum mengunggah. Siswa yang tidak ada di file akan dinonaktifkan, tetapi riwayat presensi tetap tersimpan.",
        "Jika kelas anak ada di Tahfidz, orang tua melihat Laporan Tahfidz, Laporan Lengkap, Pengumuman, dan Hasil Belajar. Jika belum, yang tampil hanya Pengumuman dan Hasil Belajar.",
    ]
    for nomor, teks in enumerate(petunjuk, start=4):
        lembar[f"A{nomor}"] = teks
        lembar[f"A{nomor}"].font = Font(italic=True, color="1F7A4D")
    simpanan = BytesIO()
    buku.save(simpanan)
    return simpanan.getvalue()


HARI_GURU = {
    "senin": 0,
    "selasa": 1,
    "rabu": 2,
    "kamis": 3,
    "jumat": 4,
    "jum'at": 4,
    "sabtu": 5,
    "minggu": 6,
}


def pecah_daftar_kelas(teks):
    if not teks or str(teks).strip().upper() == "F":
        return []
    teks = str(teks).replace("&", ",")
    teks = re.sub(r"(\d\.\d)\.", r"\1,", teks)
    hasil = []
    for bagian in teks.split(","):
        bagian = bagian.strip()
        rentang = re.match(r"(\d+)\.(\d+)\s*-\s*(\d+)\.(\d+)", bagian)
        if rentang:
            awal, dari, akhir, sampai = (int(angka) for angka in rentang.groups())
            if awal == akhir:
                hasil.extend(f"{awal}.{n}" for n in range(dari, sampai + 1))
            continue
        rentang = re.match(r"(\d+)\.(\d+)\s*-\s*(\d+)$", bagian)
        if rentang:
            tingkat, dari, sampai = (int(angka) for angka in rentang.groups())
            hasil.extend(f"{tingkat}.{n}" for n in range(dari, sampai + 1))
            continue
        satu = normalize_class(bagian)
        if satu:
            hasil.append(satu)
    return hasil


def pecah_mapel(teks):
    if not teks or str(teks).strip().lower() in ("-", "—"):
        return []
    hasil = []
    for bagian in re.split(r"\s*;\s*", str(teks)):
        bagian = bagian.strip()
        if not bagian:
            continue
        if ":" in bagian:
            label, kelas = bagian.split(":", 1)
        else:
            label, kelas = "", bagian
        label = normalize_name(label)
        if label.lower() == "mapel":
            label = ""
        hasil.append([label[:40], pecah_daftar_kelas(kelas)])
    return hasil


def pecah_piket(teks):
    if not teks or str(teks).strip().lower() in ("-", "—"):
        return []
    hasil = []
    for nama, urutan in re.findall(r"(senin|selasa|rabu|kamis|jumat|jum'at|sabtu|minggu)\s*([1-3])", str(teks), re.I):
        hari = HARI_GURU[nama.lower()]
        if hari > 4:
            continue
        hasil.append([hari, int(urutan)])
    return hasil


def _teks_sel(nilai):
    return normalize_name(nilai)


def _baris_penugasan(frame):
    baris = [_row_values(row) for row in frame.itertuples(index=False, name=None)]
    mulai = None
    for indeks, values in enumerate(baris):
        kiri = _teks_sel(values[0]).lower() if values else ""
        kanan = _teks_sel(values[1]).lower() if len(values) > 1 else ""
        if kiri == "kelas" and kanan.startswith("wali"):
            mulai = indeks + 1
            break
    if mulai is None:
        return None
    wali = {}
    indeks = mulai
    while indeks < len(baris):
        values = baris[indeks]
        kiri = _teks_sel(values[0]) if values else ""
        if not kiri or kiri.lower() in ("guru piket", "hari") or kiri.lower().startswith("petunjuk"):
            break
        kelas = normalize_class(kiri)
        nama = _teks_sel(values[1]) if len(values) > 1 else ""
        if kelas:
            wali[kelas] = "" if nama.lower() in ("-", "—") else nama[:120]
        indeks += 1
    piket = None
    while indeks < len(baris):
        values = baris[indeks]
        kiri = _teks_sel(values[0]).lower() if values else ""
        if kiri == "hari":
            piket = []
            indeks += 1
            break
        indeks += 1
    if piket is not None:
        while indeks < len(baris):
            values = baris[indeks]
            kiri = _teks_sel(values[0]).lower() if values else ""
            if kiri not in HARI_GURU:
                break
            hari = HARI_GURU[kiri]
            if hari > 4:
                indeks += 1
                continue
            for urutan in (1, 2, 3):
                nama = _teks_sel(values[urutan]) if len(values) > urutan else ""
                piket.append({
                    "hari": hari,
                    "urutan": urutan,
                    "nama": "" if nama.lower() in ("-", "—") else nama[:120],
                })
            indeks += 1
    return {"wali": wali, "piket": piket}


def parse_guru(file_obj):
    sheets = pd.read_excel(file_obj, sheet_name=None, header=None, dtype=object)
    guru = []
    notes = []
    penugasan = None
    for sheet_name, frame in sheets.items():
        lembar = _baris_penugasan(frame)
        if lembar is not None:
            penugasan = lembar
            continue
        columns = None
        found_header = False
        jumlah = 0
        for row in frame.itertuples(index=False, name=None):
            values = _row_values(row)
            if columns is None:
                nama_at = _header_index(values, ("nama guru", "nama"))
                if nama_at is None:
                    continue
                label = re.sub(r"\s+", " ", str(values[nama_at] or "")).strip().lower()
                if label not in ("nama guru", "nama"):
                    continue
                columns = {
                    "nama": nama_at,
                    "gelar": _header_index(values, ("gelar",)),
                    "jabatan": _header_index(values, ("jabatan",)),
                    "tugas": _header_index(values, ("tugas",)),
                    "kelas": _header_index(values, ("kelas yang diampu", "kelas diampu")),
                    "mapel": _header_index(values, ("mata pelajaran", "mapel")),
                    "wali": _header_index(values, ("wali kelas",)),
                    "piket": _header_index(values, ("jadwal piket",)),
                }
                found_header = True
                continue
            nama = normalize_name(values[columns["nama"]]) if columns["nama"] < len(values) else ""
            if not nama or name_key(nama) in ("nama", "nama guru", "contoh guru", "jumlah", "total"):
                continue
            if nama.lower().startswith("petunjuk"):
                continue

            def ambil(kunci, batas):
                indeks = columns.get(kunci)
                if indeks is None or indeks >= len(values):
                    return ""
                teks = normalize_name(values[indeks])
                return "" if teks.lower() in ("-", "—") else teks[:batas]

            def utuh(kunci):
                indeks = columns.get(kunci)
                if indeks is None or indeks >= len(values):
                    return None
                return normalize_name(values[indeks])

            kelas_teks = utuh("kelas")
            mapel_teks = utuh("mapel")
            if mapel_teks:
                mapel = pecah_mapel(mapel_teks)
            elif kelas_teks is not None:
                mapel = [["", pecah_daftar_kelas(kelas_teks)]] if kelas_teks else []
            elif columns.get("mapel") is not None or columns.get("kelas") is not None:
                mapel = []
            else:
                mapel = None
            wali_teks = utuh("wali")
            piket_teks = utuh("piket")
            gelar = ambil("gelar", 80)
            guru.append({
                "nama": lepaskan_gelar(nama, gelar)[:120],
                "gelar": gelar,
                "jabatan": ambil("jabatan", 80),
                "tugas": ambil("tugas", 200),
                "mapel": mapel,
                "wali": None if wali_teks is None else pecah_daftar_kelas(wali_teks),
                "piket": None if piket_teks is None else pecah_piket(piket_teks),
                "mapel_teks": mapel_teks or "",
                "wali_teks": wali_teks or "",
                "piket_teks": piket_teks or "",
            })
            jumlah += 1
        if not found_header:
            notes.append(f"Sheet '{sheet_name}' dilewati: kolom Nama Guru tidak ditemukan.")
        elif jumlah == 0:
            notes.append(f"Sheet '{sheet_name}' tidak berisi guru.")
    return guru, notes, penugasan
