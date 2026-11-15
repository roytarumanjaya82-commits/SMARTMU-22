"""Import skor psikotes dari Excel/CSV berdasarkan gelombang."""

from __future__ import annotations

import csv
import io
import re
from typing import Any, Optional

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from tpk.extensions import db
from tpk.models import Murid, User
from tpk.utils import (
    PSIKOTES_MAX,
    PSIKOTES_MIN,
    PSIKOTES_SKALA_MAX,
    konversi_psikotes_ke_skala_100,
    get_tahun_ajaran,
    label_gelombang,
    normalisasi_gelombang,
)

HEADER_ALIASES = {
    "nisn": ["nisn", "no_nisn", "nomor_nisn"],
    "nama": ["nama", "nama_lengkap", "nama_murid", "siswa"],
    "nilai": [
        "nilai",
        "nilai_psikotes",
        "skor",
        "skor_psikotes",
        "hasil_psikotes",
        "psikotes",
    ],
    "catatan": ["catatan", "catatan_psikotes", "keterangan", "notes"],
}


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _clean_nisn(value: Any) -> Optional[str]:
    text = _clean(value)
    if not text:
        return None
    if re.fullmatch(r"\d+\.0+", text):
        text = text.split(".")[0]
    text = re.sub(r"[^\dA-Za-z]", "", text)
    return text or None


def _parse_nilai(value: Any) -> tuple[Optional[float], Optional[str]]:
    text = _clean(value)
    if not text:
        return None, None
    text = text.replace(",", ".")
    try:
        nilai = float(text)
    except ValueError:
        return None, "nilai tidak valid"
    if nilai < PSIKOTES_MIN or nilai > PSIKOTES_MAX:
        return None, f"nilai harus {PSIKOTES_MIN}–{PSIKOTES_MAX}"
    return round(nilai, 2), None


def _map_header(headers: list) -> dict:
    mapped = {}
    normalized = {
        _clean(h).lower().replace(" ", "_"): i for i, h in enumerate(headers)
    }
    for field, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                mapped[field] = normalized[alias]
                break
    return mapped


def _murid_untuk_blanko(tahun: str, gelombang: str) -> list[Murid]:
    gelombang = normalisasi_gelombang(gelombang)
    q = (
        Murid.query.join(User, Murid.user_id == User.id)
        .filter((Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)))
        .filter(Murid.gelombang == gelombang)
        .order_by(User.nama_lengkap.asc())
    )
    items = q.all()
    if items:
        return items
    # Fallback: murid belum punya gelombang (data lama) agar blanko tetap bisa diisi
    return (
        Murid.query.join(User, Murid.user_id == User.id)
        .filter((Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)))
        .filter(Murid.gelombang.is_(None) | (Murid.gelombang == ""))
        .order_by(User.nama_lengkap.asc())
        .all()
    )


def buat_blanko_psikotes_xlsx(gelombang: str, tahun: Optional[str] = None) -> bytes:
    tahun = tahun or get_tahun_ajaran()
    gelombang = normalisasi_gelombang(gelombang)
    items = _murid_untuk_blanko(tahun, gelombang)

    wb = Workbook()
    ws = wb.active
    ws.title = "Skor Psikotes"
    headers = ["nisn", "nama", "nilai_psikotes", "catatan"]
    header_fill = PatternFill("solid", fgColor="1F6B3A")
    header_font = Font(color="FFFFFF", bold=True)
    wajib_fill = PatternFill("solid", fgColor="FFF4E5")

    for col, h in enumerate(headers, start=1):
        cell = ws.cell(1, col, h)
        cell.font = header_font
        cell.fill = header_fill

    for row_idx, murid in enumerate(items, start=2):
        ws.cell(row_idx, 1, murid.nisn)
        ws.cell(row_idx, 2, murid.user.nama_lengkap if murid.user else "")
        # Kolom nilai dikosongkan: isi skor mentah 0–165; sistem konversi ke 1–100 saat upload
        nilai_cell = ws.cell(row_idx, 3, "")
        nilai_cell.fill = wajib_fill
        ws.cell(row_idx, 4, murid.catatan_psikotes or "")

    if not items:
        ws.cell(2, 1, "0012345678")
        ws.cell(2, 2, "Contoh Nama Murid")
        ws.cell(2, 3, 85)
        ws.cell(2, 4, "Opsional")
        for col in range(1, 5):
            ws.cell(2, col).fill = wajib_fill

    widths = [16, 36, 16, 40]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws2 = wb.create_sheet("Petunjuk")
    ws2["A1"] = f"Blanko skor psikotes · Tahun Ajaran {tahun} · {label_gelombang(gelombang)}"
    ws2["A2"] = f"Kolom wajib: nisn, nilai_psikotes (skor MENTAH {PSIKOTES_MIN}–{PSIKOTES_MAX})."
    ws2["A3"] = (
        f"Saat upload, sistem otomatis mengubah skor mentah ke skala "
        f"1–{PSIKOTES_SKALA_MAX} dengan rumus (nilai/{PSIKOTES_MAX})×{PSIKOTES_SKALA_MAX}."
    )
    ws2["A4"] = "Match berdasarkan NISN pada gelombang yang dipilih saat upload."
    ws2["A5"] = "Murid tanpa gelombang (data lama) ikut ter-assign ke gelombang upload."
    ws2["A6"] = "Kolom nama hanya membantu pengecekan; tidak mengubah data nama."
    ws2["A7"] = "Kosongkan nilai untuk melewati baris (tidak mengubah skor)."
    ws2["A8"] = "Jangan isi skor yang sudah skala 100 — isi selalu skor mentah 0–165."
    ws2["A9"] = "Format file: .xlsx atau .csv"
    ws2.column_dimensions["A"].width = 90

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _rows_to_records(rows: list) -> tuple[list[dict], Optional[str]]:
    if not rows:
        return [], "File kosong."
    # cari baris header
    header_row_idx = None
    mapped = {}
    for i, row in enumerate(rows[:10]):
        headers = [_clean(h) for h in row]
        mapped = _map_header(headers)
        if "nisn" in mapped and "nilai" in mapped:
            header_row_idx = i
            break
    if header_row_idx is None:
        return [], "Kolom wajib tidak ditemukan: nisn, nilai_psikotes."

    data = []
    for row in rows[header_row_idx + 1 :]:
        if not row or all(v is None or str(v).strip() == "" for v in row):
            continue
        rec = {
            "nisn": row[mapped["nisn"]] if mapped["nisn"] < len(row) else None,
            "nama": row[mapped["nama"]] if "nama" in mapped and mapped["nama"] < len(row) else None,
            "nilai": row[mapped["nilai"]] if mapped["nilai"] < len(row) else None,
            "catatan": (
                row[mapped["catatan"]]
                if "catatan" in mapped and mapped["catatan"] < len(row)
                else None
            ),
        }
        data.append(rec)
    if not data:
        return [], "Tidak ada baris data skor yang bisa dibaca."
    return data, None


def baca_psikotes_file(file_storage) -> tuple[list[dict], Optional[str]]:
    filename = (file_storage.filename or "").lower()
    if filename.endswith(".xlsx"):
        wb = load_workbook(file_storage, data_only=True)
        ws = None
        for name in wb.sheetnames:
            if "petunjuk" in name.lower():
                continue
            ws = wb[name]
            break
        if ws is None:
            ws = wb.active
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        return _rows_to_records(rows)
    if filename.endswith(".csv"):
        raw = file_storage.read()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        sample = text[:2048]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ";" if sample.count(";") > sample.count(",") else ","
        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        rows = [list(r) for r in reader]
        return _rows_to_records(rows)
    return [], "Format tidak didukung. Gunakan .xlsx atau .csv"


def _cari_murid(nisn: str, tahun: str, gelombang: str) -> Optional[Murid]:
    gelombang = normalisasi_gelombang(gelombang)
    base = Murid.query.filter(
        Murid.nisn == nisn,
        (Murid.tahun_ajaran == tahun) | (Murid.tahun_ajaran.is_(None)),
    )
    murid = base.filter(Murid.gelombang == gelombang).first()
    if murid:
        return murid
    # Data lama tanpa gelombang: boleh diisi dan di-assign ke gelombang upload
    return base.filter(
        Murid.gelombang.is_(None) | (Murid.gelombang == "")
    ).first()


def impor_skor_psikotes(
    rows: list[dict], gelombang: str, tahun: Optional[str] = None
) -> dict:
    tahun = tahun or get_tahun_ajaran()
    gelombang = normalisasi_gelombang(gelombang)
    sukses = 0
    dilewati = 0
    gagal = []
    assigned = 0

    for idx, row in enumerate(rows, start=1):
        nisn = _clean_nisn(row.get("nisn"))
        nama_contoh = _clean(row.get("nama"))
        # lewati baris contoh template
        if nisn == "0012345678" or (
            nama_contoh == "Contoh Nama Murid" and _clean(row.get("nilai")) in ("85", "85.0")
        ):
            dilewati += 1
            continue

        if not nisn:
            gagal.append(f"Baris {idx}: NISN kosong.")
            continue

        nilai_raw = row.get("nilai")
        if _clean(nilai_raw) == "":
            dilewati += 1
            continue

        nilai, err = _parse_nilai(nilai_raw)
        if err:
            gagal.append(f"Baris {idx} (NISN {nisn}): {err}.")
            continue

        murid = _cari_murid(nisn, tahun, gelombang)
        if not murid:
            gagal.append(
                f"Baris {idx}: NISN {nisn} tidak ditemukan di {label_gelombang(gelombang)} "
                "(atau murid tanpa gelombang)."
            )
            continue

        catatan = _clean(row.get("catatan")) or None
        if not murid.gelombang:
            murid.gelombang = gelombang
            assigned += 1
        if not murid.tahun_ajaran:
            murid.tahun_ajaran = tahun
        # Skor mentah 0–165 → disimpan sebagai skala 1–100
        murid.nilai_psikotes = konversi_psikotes_ke_skala_100(nilai)
        murid.catatan_psikotes = catatan
        sukses += 1

    if sukses:
        db.session.commit()
    return {
        "sukses": sukses,
        "dilewati": dilewati,
        "assigned": assigned,
        "gagal": gagal,
    }
