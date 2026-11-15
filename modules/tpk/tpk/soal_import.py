"""Import soal tes tertulis dari Excel/CSV."""

from __future__ import annotations

import csv
import io
from typing import Optional

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill

from tpk.extensions import db
from tpk.models import KELAS_CHOICES, SoalTes

HEADER_ALIASES = {
    "pertanyaan": ["pertanyaan", "soal", "question"],
    "opsi_a": ["opsi_a", "a", "pilihan_a"],
    "opsi_b": ["opsi_b", "b", "pilihan_b"],
    "opsi_c": ["opsi_c", "c", "pilihan_c"],
    "opsi_d": ["opsi_d", "d", "pilihan_d"],
    "jawaban_benar": ["jawaban_benar", "kunci", "jawaban", "kunci_jawaban"],
    "bobot": ["bobot", "poin", "score"],
    "kelas_tujuan": ["kelas_tujuan", "kelas", "kelas_soal"],
}


def _clean(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_kelas(value: str) -> Optional[str]:
    text = _clean(value).lower()
    if not text:
        return None
    mapping = {
        "olimpiade": "olimpiade",
        "tahfidz": "tahfidz",
        "tahfiz": "tahfidz",
        "multimedia": "multimedia",
        "mm": "multimedia",
        "internasional": "internasional",
        "international": "internasional",
        "reguler": "reguler",
        "regular": "reguler",
    }
    if text in mapping:
        return mapping[text]
    for kode, label in KELAS_CHOICES:
        if text == label.lower() or text == kode:
            return kode
    return None


def _map_header(headers: list[str]) -> dict:
    mapped = {}
    normalized = {_clean(h).lower().replace(" ", "_"): i for i, h in enumerate(headers)}
    for field, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                mapped[field] = normalized[alias]
                break
    return mapped


def buat_blanko_soal_xlsx(kelas_default: str = "olimpiade") -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Soal Tes"
    headers = [
        "kelas_tujuan",
        "pertanyaan",
        "opsi_a",
        "opsi_b",
        "opsi_c",
        "opsi_d",
        "jawaban_benar",
        "bobot",
    ]
    fill = PatternFill("solid", fgColor="FFF2CC")
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(1, col, h)
        cell.font = Font(bold=True)
        cell.fill = fill
    contoh = [
        kelas_default or "olimpiade",
        "Contoh: Berapakah hasil 2 + 2?",
        "3",
        "4",
        "5",
        "6",
        "B",
        1,
    ]
    for col, val in enumerate(contoh, start=1):
        ws.cell(2, col, val)
    # Contoh teks Arab (UTF-8) — Excel mendukung huruf Arab di kolom pertanyaan/opsi
    ws.cell(3, 1, kelas_default or "tahfidz")
    ws.cell(3, 2, "Contoh Arab: اقْرَأْ بِاسْمِ رَبِّكَ")
    ws.cell(3, 3, "الَّذِي")
    ws.cell(3, 4, "خَلَقَ")
    ws.cell(3, 5, "عَلَّمَ")
    ws.cell(3, 6, "الْقَلَمَ")
    ws.cell(3, 7, "B")
    ws.cell(3, 8, 1)

    ws2 = wb.create_sheet("Petunjuk")
    ws2["A1"] = "Isi kelas_tujuan: olimpiade / tahfidz / multimedia / internasional / reguler"
    ws2["A2"] = "jawaban_benar: A / B / C / D"
    ws2["A3"] = "Teks Arab didukung (simpan Excel UTF-8 / .xlsx biasa)."
    ws2["A4"] = "Soal BERGAMBAR: tambahkan/edit via menu Bank Soal (upload file atau tempel Snipping Tool / Ctrl+V)."
    ws2["A5"] = "Hapus baris contoh sebelum upload."
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def baca_soal_file(file_storage):
    filename = (file_storage.filename or "").lower()
    if filename.endswith(".xlsx"):
        wb = load_workbook(file_storage, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return [], "File kosong."
        headers = [_clean(h) for h in rows[0]]
        mapped = _map_header(headers)
        if "pertanyaan" not in mapped or "jawaban_benar" not in mapped:
            return [], "Kolom wajib: pertanyaan, opsi_a..d, jawaban_benar."
        records = []
        for row in rows[1:]:
            if not row or all(v is None or str(v).strip() == "" for v in row):
                continue
            item = {}
            for field, idx in mapped.items():
                item[field] = row[idx] if idx < len(row) else None
            records.append(item)
        return records, None
    if filename.endswith(".csv"):
        raw = file_storage.read()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return [], "File kosong."
        headers = [_clean(h) for h in rows[0]]
        mapped = _map_header(headers)
        if "pertanyaan" not in mapped:
            return [], "Kolom wajib belum lengkap."
        records = []
        for row in rows[1:]:
            if not row or all(str(v).strip() == "" for v in row):
                continue
            item = {}
            for field, idx in mapped.items():
                item[field] = row[idx] if idx < len(row) else None
            records.append(item)
        return records, None
    return [], "Format harus .xlsx atau .csv"


def impor_soal_tes(rows: list[dict], kelas_default: str = "") -> dict:
    sukses = 0
    dilewati = 0
    gagal = []
    default_kelas = _normalize_kelas(kelas_default) if kelas_default else None

    for idx, row in enumerate(rows, start=1):
        pertanyaan = _clean(row.get("pertanyaan"))
        if pertanyaan.lower().startswith("contoh:"):
            dilewati += 1
            continue
        opsi_a = _clean(row.get("opsi_a"))
        opsi_b = _clean(row.get("opsi_b"))
        opsi_c = _clean(row.get("opsi_c"))
        opsi_d = _clean(row.get("opsi_d"))
        jawaban = _clean(row.get("jawaban_benar")).upper()[:1]
        kelas = _normalize_kelas(row.get("kelas_tujuan")) or default_kelas
        try:
            bobot = int(float(_clean(row.get("bobot") or 1) or 1))
        except ValueError:
            bobot = 1

        if not pertanyaan or not all([opsi_a, opsi_b, opsi_c, opsi_d]):
            gagal.append(f"Baris {idx}: pertanyaan/opsi belum lengkap.")
            continue
        if jawaban not in ("A", "B", "C", "D"):
            gagal.append(f"Baris {idx}: jawaban_benar harus A/B/C/D.")
            continue
        if not kelas or kelas not in dict(KELAS_CHOICES):
            gagal.append(f"Baris {idx}: kelas_tujuan tidak valid.")
            continue

        db.session.add(
            SoalTes(
                kelas_tujuan=kelas,
                pertanyaan=pertanyaan,
                opsi_a=opsi_a,
                opsi_b=opsi_b,
                opsi_c=opsi_c,
                opsi_d=opsi_d,
                jawaban_benar=jawaban,
                bobot=bobot,
                is_active=True,
            )
        )
        sukses += 1

    if sukses:
        db.session.commit()
    return {"sukses": sukses, "dilewati": dilewati, "gagal": gagal}
