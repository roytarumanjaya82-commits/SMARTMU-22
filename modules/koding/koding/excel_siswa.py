from io import BytesIO
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side


HEADERS = ["No", "NIS", "Nama Siswa", "Jenis Kelamin (L/P)", "Username (opsional)", "Password (opsional)"]


def buat_blanko_excel(nama_kelas="7.5"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Daftar Siswa"

    header_fill = PatternFill("solid", fgColor="0F766E")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    ws["A1"] = "BLANKO IMPOR DAFTAR SISWA"
    ws["A2"] = f"Kelas: {nama_kelas}"
    ws["A3"] = "Petunjuk: isi mulai baris 6. Kolom Username/Password boleh dikosongkan (otomatis NIS / 123456)."
    ws.merge_cells("A1:F1")
    ws.merge_cells("A2:F2")
    ws.merge_cells("A3:F3")
    ws["A1"].font = Font(bold=True, size=14, color="0F766E")

    for col, title in enumerate(HEADERS, start=1):
        cell = ws.cell(row=5, column=col, value=title)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
        cell.border = thin

    contoh = [
        (1, "2507001", "Ahmad Fauzan", "L", "", ""),
        (2, "2507002", "Siti Aisyah", "P", "", ""),
        (3, "2507003", "Budi Santoso", "L", "", ""),
    ]
    for r, row in enumerate(contoh, start=6):
        for c, val in enumerate(row, start=1):
            cell = ws.cell(row=r, column=c, value=val)
            cell.border = thin

    widths = [6, 14, 28, 20, 22, 20]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + i)].width = w

    petunjuk = wb.create_sheet("Petunjuk")
    petunjuk["A1"] = "Cara mengisi blanko"
    petunjuk["A1"].font = Font(bold=True, size=13)
    lines = [
        "1. Simpan file ini, lalu isi data siswa pada sheet Daftar Siswa.",
        "2. Kolom wajib: NIS, Nama Siswa, Jenis Kelamin (L atau P).",
        "3. Jika Username kosong, sistem memakai NIS sebagai username login.",
        "4. Jika Password kosong, password awal menjadi 123456.",
        "5. Siswa dapat login dari HP/laptop/tablet dengan username & password tersebut.",
        "6. Upload file di menu Admin > Siswa > Impor Excel.",
    ]
    for i, line in enumerate(lines, start=3):
        petunjuk[f"A{i}"] = line
    petunjuk.column_dimensions["A"].width = 90

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    return bio


def baca_excel_siswa(file_storage):
    wb = load_workbook(file_storage, data_only=True)
    ws = wb.active
    rows = []
    for idx, row in enumerate(ws.iter_rows(min_row=6, values_only=True), start=6):
        if not row or all(v is None or str(v).strip() == "" for v in row):
            continue
        nis = str(row[1]).strip() if row[1] is not None else ""
        nama = str(row[2]).strip() if row[2] is not None else ""
        jk = str(row[3]).strip().upper() if row[3] is not None else ""
        username = str(row[4]).strip() if len(row) > 4 and row[4] else ""
        password = str(row[5]).strip() if len(row) > 5 and row[5] else ""
        if not nis or not nama:
            raise ValueError(f"Baris {idx}: NIS dan Nama wajib diisi.")
        if jk and jk not in ("L", "P"):
            raise ValueError(f"Baris {idx}: Jenis Kelamin harus L atau P.")
        rows.append(
            {
                "nis": nis,
                "nama_siswa": nama,
                "jenis_kelamin": jk or None,
                "username": username or nis,
                "password": password or "123456",
            }
        )
    if not rows:
        raise ValueError("Tidak ada data siswa yang terbaca dari file Excel.")
    return rows
