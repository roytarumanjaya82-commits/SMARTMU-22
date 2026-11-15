import csv
import io
import re
import unicodedata
from datetime import datetime
from typing import Any, Optional

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

from tpk.extensions import db
from tpk.models import KELAS_CHOICES, Murid, User
from tpk.utils import (
    DEFAULT_PASSWORD_MURID,
    buat_username_dari_nama,
    get_tahun_ajaran,
    normalisasi_gelombang,
    pastikan_akun_ortu,
    tambah_gelombang_ke_daftar,
)

# Template resmi blanko murid
BLANKO_HEADERS = [
    "nomor",
    "nisn",
    "nama",
    "jenis_kelamin",
    "asal_sekolah",
    "gelombang",
    "tempat_tanggal_lahir",
    "alamat",
    "nama_orang_tua_wali",
    "no_hp_orang_tua_wali",
    "alamat_orang_tua_wali",
    "minat_ke_kelas",
]

BLANKO_HEADERS_LABEL = [
    "Nomor",
    "NISN",
    "Nama",
    "Jenis Kelamin",
    "Asal Sekolah",
    "Gelombang",
    "Tempat Tanggal Lahir",
    "Alamat",
    "Nama Orang Tua/Wali",
    "No HP Orang Tua/Wali",
    "Alamat Orang Tua/Wali",
    "Minat ke Kelas",
]

CONTOH_BARIS = [
    1,
    "0123456789",
    "Ahmad Fauzi",
    "L",
    "SD Muhammadiyah Contoh",
    "1",
    "Jakarta, 15-05-2012",
    "Jl. Contoh No. 1 Pamulang",
    "Bapak Ahmad",
    "081298765432",
    "Jl. Contoh No. 1 Pamulang",
    "tahfidz",
]

# Kolom wajib diisi
REQUIRED_FIELDS = ("nomor", "nama_lengkap", "jenis_kelamin", "asal_sekolah", "gelombang")

HEADER_ALIASES = {
    "nomor": ["nomor", "no", "no_urut", "nomer", "urut"],
    "nisn": ["nisn", "no_nisn", "nomor_nisn"],
    "nama_lengkap": [
        "nama",
        "nama_lengkap",
        "nama_siswa",
        "nama_murid",
        "nama_peserta",
    ],
    "jenis_kelamin": ["jenis_kelamin", "jk", "kelamin", "gender"],
    "asal_sekolah": [
        "asal_sekolah",
        "sekolah_asal",
        "sekolah",
        "sd_asal",
        "nama_sekolah",
    ],
    "gelombang": [
        "gelombang",
        "gelombang_pendaftaran",
        "batch",
        "wave",
        "periode_gelombang",
    ],
    "tempat_tanggal_lahir": [
        "tempat_tanggal_lahir",
        "tempat_tgl_lahir",
        "ttl",
        "tempat_dan_tanggal_lahir",
        "tempat_tanggal_lahir_ttl",
    ],
    "tempat_lahir": ["tempat_lahir", "tmp_lahir"],
    "tanggal_lahir": ["tanggal_lahir", "tgl_lahir", "dob"],
    "alamat_ortu": [
        "alamat_orang_tua_wali",
        "alamat_orang_tua",
        "alamat_ortu",
        "alamat_wali",
        "alamat_ortu_wali",
    ],
    "alamat": ["alamat", "alamat_lengkap", "alamat_siswa", "alamat_murid"],
    "nama_ortu": [
        "nama_orang_tua_wali",
        "nama_orang_tua",
        "nama_ortu",
        "nama_wali",
        "orang_tua_wali",
        "wali",
    ],
    "no_hp_ortu": [
        "no_hp_orang_tua_wali",
        "no_hp_orang_tua",
        "no_hp_ortu",
        "hp_ortu",
        "telepon_ortu",
        "no_hp_wali",
        "wa_ortu",
    ],
    "pilihan_kelas_1": [
        "minat_ke_kelas",
        "minat_kelas",
        "minat",
        "pilihan_kelas",
        "pilihan_kelas_1",
        "kelas",
        "program",
    ],
}

KELAS_VALID = set(dict(KELAS_CHOICES).keys())
KELAS_ALIAS = {
    "olimpiade": "olimpiade",
    "tahfidz": "tahfidz",
    "multimedia": "multimedia",
    "internasional": "internasional",
    "reguler": "reguler",
    "olympic": "olimpiade",
    "olympiade": "olimpiade",
    "tahfiz": "tahfidz",
    "tahfizh": "tahfidz",
    "tahfid": "tahfidz",
    "mm": "multimedia",
    "international": "internasional",
}


def _normalize_key(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().strip()
    text = text.replace("/", " ")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", "_", text)
    return text.strip("_")


def _map_header(raw_header: Any) -> Optional[str]:
    key = _normalize_key(raw_header)
    if not key:
        return None

    # Exact match dulu (lebih spesifik menang)
    best_field = None
    best_len = -1
    for field, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            if key == alias and len(alias) > best_len:
                best_field = field
                best_len = len(alias)
    if best_field:
        return best_field

    # Partial: alias terkandung di key, pilih yang terpanjang
    for field, aliases in HEADER_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            if alias in key and len(alias) > best_len:
                best_field = field
                best_len = len(alias)
    return best_field


def _normalize_kelas(value: Any):
    raw = str(value or "").strip().lower()
    if not raw:
        return None
    raw = re.sub(r"[^\w\s]", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    compact = raw.replace(" ", "_")
    if compact in KELAS_ALIAS:
        return KELAS_ALIAS[compact]
    if raw in KELAS_ALIAS:
        return KELAS_ALIAS[raw]
    for kode, label in KELAS_CHOICES:
        if kode in compact or label.lower() in raw:
            return kode
    return compact if compact in KELAS_VALID else None


def _normalize_jk(value: Any):
    raw = str(value or "").strip().lower()
    if not raw:
        return None
    if raw in ("l", "laki", "laki-laki", "laki laki", "pria", "male", "m"):
        return "L"
    if raw in ("p", "perempuan", "wanita", "female", "f"):
        return "P"
    return raw.upper() if raw.upper() in ("L", "P") else None


def _parse_date(value: Any):
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d %m %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    # contoh: 15 Mei 2012
    bulan = {
        "januari": 1,
        "februari": 2,
        "maret": 3,
        "april": 4,
        "mei": 5,
        "juni": 6,
        "juli": 7,
        "agustus": 8,
        "september": 9,
        "oktober": 10,
        "november": 11,
        "desember": 12,
    }
    m = re.match(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", text)
    if m:
        bln = bulan.get(m.group(2).lower())
        if bln:
            try:
                return datetime(int(m.group(3)), bln, int(m.group(1))).date()
            except ValueError:
                return None
    return None


def _parse_ttl(value: Any):
    """Pisahkan 'Tempat, tanggal' menjadi tempat_lahir & tanggal_lahir."""
    if value is None or value == "":
        return None, None
    if isinstance(value, datetime):
        return None, value.date()
    text = str(value).strip()
    if "," in text:
        tempat, tgl = [p.strip() for p in text.split(",", 1)]
        return tempat or None, _parse_date(tgl)
    # hanya tanggal
    tgl = _parse_date(text)
    if tgl:
        return None, tgl
    return text, None


def _clean(value: Any):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_nisn(value: Any):
    text = _clean(value)
    if text is None:
        return None
    if re.fullmatch(r"\d+\.0+", text):
        text = text.split(".")[0]
    text = re.sub(r"[^\dA-Za-z]", "", text)
    return text or None


def _clean_nomor(value: Any):
    text = _clean(value)
    if text is None:
        return None
    if re.fullmatch(r"\d+\.0+", text):
        text = text.split(".")[0]
    return text


def _buat_nisn_otomatis(nomor: str) -> str:
    digit = re.sub(r"\D", "", str(nomor)) or "0"
    kandidat = f"9{digit.zfill(9)}"[:20]
    n = 1
    while Murid.query.filter_by(nisn=kandidat).first():
        kandidat = f"9{digit.zfill(7)}{n}"[:20]
        n += 1
    return kandidat


def buat_blanko_xlsx() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Blanko Murid"

    header_fill = PatternFill("solid", fgColor="1F6B3A")
    header_font = Font(color="FFFFFF", bold=True)
    wajib_fill = PatternFill("solid", fgColor="FFF4E5")

    ws.append(BLANKO_HEADERS_LABEL)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(wrap_text=True, vertical="center")

    # Tandai kolom wajib: Nomor(1), Nama(3), Jenis Kelamin(4), Asal Sekolah(5), Gelombang(6)
    for col_idx in (1, 3, 4, 5, 6):
        ws.cell(row=1, column=col_idx).fill = PatternFill("solid", fgColor="C9A227")
        ws.cell(row=1, column=col_idx).font = Font(color="1A2E1C", bold=True)

    ws.append(CONTOH_BARIS)
    for col_idx in (1, 3, 4, 5, 6):
        ws.cell(row=2, column=col_idx).fill = wajib_fill

    from openpyxl.utils import get_column_letter

    widths = [10, 14, 28, 14, 28, 12, 26, 30, 24, 20, 30, 16]
    for i, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    petunjuk = wb.create_sheet("Petunjuk")
    petunjuk.append(["Kolom", "Wajib?", "Keterangan"])
    petunjuk.append(["Nomor", "YA", "Nomor urut murid"])
    petunjuk.append(["NISN", "Tidak", "Boleh dikosongkan"])
    petunjuk.append(["Nama", "YA", "Nama lengkap murid"])
    petunjuk.append(["Jenis Kelamin", "YA", "L / P atau Laki-laki / Perempuan"])
    petunjuk.append(["Asal Sekolah", "YA", "Nama sekolah asal"])
    petunjuk.append(["Gelombang", "YA", "Contoh: 1 / 2 / 3 atau Gelombang 1"])
    petunjuk.append(["Tempat Tanggal Lahir", "Tidak", "Contoh: Jakarta, 15-05-2012"])
    petunjuk.append(["Alamat", "Tidak", "Alamat murid"])
    petunjuk.append(["Nama Orang Tua/Wali", "Tidak", ""])
    petunjuk.append(["No HP Orang Tua/Wali", "Tidak", ""])
    petunjuk.append(["Alamat Orang Tua/Wali", "Tidak", ""])
    petunjuk.append(
        [
            "Minat ke Kelas",
            "Tidak",
            "olimpiade / tahfidz / multimedia / internasional / reguler (kosong = reguler)",
        ]
    )
    petunjuk.append([])
    petunjuk.append(
        [
            "Akun login",
            "",
            f"Username otomatis dari nama. Password = {DEFAULT_PASSWORD_MURID}",
        ]
    )
    petunjuk.append(
        [
            "Catatan",
            "",
            "Hapus baris contoh sebelum upload data asli. Kolom kuning/wajib harus diisi.",
        ]
    )

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def _find_header_row(rows: list) -> int:
    best_idx = 0
    best_score = -1
    for i, row in enumerate(rows[:20]):
        mapped = [_map_header(cell) for cell in row]
        score = sum(1 for m in mapped if m)
        if "nama_lengkap" in mapped:
            score += 4
        if "nomor" in mapped:
            score += 2
        if "jenis_kelamin" in mapped:
            score += 2
        if "asal_sekolah" in mapped:
            score += 2
        if "gelombang" in mapped:
            score += 2
        if score > best_score:
            best_score = score
            best_idx = i
    return best_idx


def _rows_to_records(raw_rows: list) -> tuple[list[dict], Optional[str]]:
    if not raw_rows:
        return [], "File kosong."

    header_idx = _find_header_row(raw_rows)
    header_cells = list(raw_rows[header_idx])
    field_map = {}
    used_fields = set()
    for i, cell in enumerate(header_cells):
        field = _map_header(cell)
        if field and field not in used_fields:
            field_map[i] = field
            used_fields.add(field)

    missing = []
    if "nama_lengkap" not in used_fields:
        missing.append("Nama")
    if "nomor" not in used_fields:
        missing.append("Nomor")
    if "jenis_kelamin" not in used_fields:
        missing.append("Jenis Kelamin")
    if "asal_sekolah" not in used_fields:
        missing.append("Asal Sekolah")
    if "gelombang" not in used_fields:
        missing.append("Gelombang")
    if missing:
        return [], (
            "Kolom wajib tidak ditemukan: "
            + ", ".join(missing)
            + ". Unduh blanko terbaru atau pastikan header kolom tersebut ada."
        )

    data = []
    for row in raw_rows[header_idx + 1 :]:
        if not any(cell not in (None, "") for cell in row):
            continue
        item = {}
        for i, field in field_map.items():
            item[field] = row[i] if i < len(row) else None
        nama = str(item.get("nama_lengkap") or "").strip().lower()
        if nama in ("nama", "nama lengkap", "nama siswa", "nama murid"):
            continue
        data.append(item)

    if not data:
        return [], "Tidak ada baris data murid yang bisa dibaca."
    return data, None


def _rows_from_xlsx(file_storage):
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


def _rows_from_csv(file_storage):
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


def baca_blanko(file_storage):
    filename = (file_storage.filename or "").lower()
    if filename.endswith(".xlsx"):
        return _rows_from_xlsx(file_storage)
    if filename.endswith(".csv"):
        return _rows_from_csv(file_storage)
    return [], "Format tidak didukung. Gunakan .xlsx atau .csv"


def impor_blanko_murid(rows: list[dict]) -> dict:
    sukses = 0
    dilewati = 0
    diperbarui = 0
    gagal = []
    gelombang_terpakai = set()

    for idx, row in enumerate(rows, start=1):
        nomor = _clean_nomor(row.get("nomor"))
        nama = _clean(row.get("nama_lengkap"))
        jk = _normalize_jk(row.get("jenis_kelamin"))
        asal = _clean(row.get("asal_sekolah"))
        gelombang = normalisasi_gelombang(row.get("gelombang"))
        nisn = _clean_nisn(row.get("nisn"))
        tahun_ajaran = get_tahun_ajaran()

        # Wajib: nomor, nama, jenis kelamin, asal sekolah, gelombang
        if not nomor or not nama or not jk or not asal or not gelombang:
            kurang = []
            if not nomor:
                kurang.append("Nomor")
            if not nama:
                kurang.append("Nama")
            if not jk:
                kurang.append("Jenis Kelamin")
            if not asal:
                kurang.append("Asal Sekolah")
            if not gelombang:
                kurang.append("Gelombang")
            gagal.append(f"Baris {idx}: kolom wajib belum lengkap ({', '.join(kurang)}).")
            continue

        # Lewati contoh template
        if nama == "Ahmad Fauzi" and str(nomor) == "1":
            dilewati += 1
            continue

        if "tempat_tanggal_lahir" in row and row.get("tempat_tanggal_lahir") not in (None, ""):
            tempat, tanggal = _parse_ttl(row.get("tempat_tanggal_lahir"))
        else:
            tempat = _clean(row.get("tempat_lahir"))
            tanggal = _parse_date(row.get("tanggal_lahir"))

        minat_raw = row.get("pilihan_kelas_1")
        pilihan1 = _normalize_kelas(minat_raw) if minat_raw not in (None, "") else "reguler"
        if minat_raw not in (None, "") and not pilihan1:
            gagal.append(f"Baris {idx} ({nama}): minat ke kelas tidak dikenali.")
            continue
        if not pilihan1:
            pilihan1 = "reguler"

        alamat = _clean(row.get("alamat"))
        nama_ortu = _clean(row.get("nama_ortu"))
        no_hp_ortu = _clean(row.get("no_hp_ortu"))
        alamat_ortu = _clean(row.get("alamat_ortu"))

        if not nisn:
            nisn = _buat_nisn_otomatis(nomor)

        existing = Murid.query.filter_by(nisn=nisn).first()
        # Jika NISN kosong diganti otomatis, coba cocokkan juga lewat nomor+nama? skip for now

        if existing:
            try:
                existing.user.nama_lengkap = nama
                existing.jenis_kelamin = jk
                existing.asal_sekolah = asal
                existing.gelombang = gelombang
                existing.tahun_ajaran = tahun_ajaran
                existing.nomor_urut = str(nomor)
                existing.tempat_lahir = tempat or existing.tempat_lahir
                if tanggal:
                    existing.tanggal_lahir = tanggal
                if alamat:
                    existing.alamat = alamat
                if nama_ortu:
                    existing.nama_ortu = nama_ortu
                if no_hp_ortu:
                    existing.no_hp_ortu = no_hp_ortu
                if alamat_ortu:
                    existing.alamat_ortu = alamat_ortu
                if minat_raw not in (None, ""):
                    existing.pilihan_kelas_1 = pilihan1
                pastikan_akun_ortu(existing, commit=False)
                db.session.commit()
                diperbarui += 1
                gelombang_terpakai.add(gelombang)
            except Exception as exc:  # noqa: BLE001
                db.session.rollback()
                gagal.append(f"Baris {idx} ({nama}): gagal diperbarui ({exc}).")
            continue

        username = buat_username_dari_nama(nama)
        try:
            user = User(
                username=username,
                nama_lengkap=nama,
                role="murid",
            )
            user.set_password(DEFAULT_PASSWORD_MURID)
            db.session.add(user)
            db.session.flush()

            murid = Murid(
                user_id=user.id,
                nisn=nisn,
                nomor_urut=str(nomor),
                tahun_ajaran=tahun_ajaran,
                gelombang=gelombang,
                tempat_lahir=tempat,
                tanggal_lahir=tanggal,
                jenis_kelamin=jk,
                alamat=alamat,
                nama_ortu=nama_ortu,
                no_hp_ortu=no_hp_ortu,
                alamat_ortu=alamat_ortu,
                asal_sekolah=asal,
                pilihan_kelas_1=pilihan1,
                status="terdaftar",
            )
            db.session.add(murid)
            db.session.flush()
            pastikan_akun_ortu(murid, commit=False)
            db.session.commit()
            sukses += 1
            gelombang_terpakai.add(gelombang)
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            gagal.append(f"Baris {idx} ({nama}): gagal disimpan ({exc}).")

    # Upload gelombang baru hanya menambah daftar, tidak menghapus gelombang lama
    if gelombang_terpakai:
        tambah_gelombang_ke_daftar(*sorted(gelombang_terpakai))

    return {
        "sukses": sukses,
        "diperbarui": diperbarui,
        "dilewati": dilewati,
        "gagal": gagal,
        "gelombang": sorted(gelombang_terpakai),
    }