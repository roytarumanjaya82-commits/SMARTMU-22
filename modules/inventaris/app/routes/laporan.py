from datetime import datetime
from io import BytesIO

from flask import Blueprint, abort, render_template, request, send_file
from flask_login import login_required, current_user
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from app import models
from config import (
    SCHOOL_ADDRESS,
    SCHOOL_KEPALA,
    SCHOOL_KOTA,
    SCHOOL_NAME,
    SCHOOL_NBM_KEPALA,
    SCHOOL_NPSN,
    SCHOOL_WEBSITE,
)

laporan_bp = Blueprint("laporan", __name__, url_prefix="/laporan")

BULAN = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


def _fmt_tanggal(nilai):
    if not nilai:
        return "-"
    try:
        saat = datetime.strptime(str(nilai)[:10], "%Y-%m-%d")
    except ValueError:
        return str(nilai)
    return f"{saat.day} {BULAN[saat.month]} {saat.year}"


def _tanggal_cetak(saat=None):
    saat = saat or datetime.now()
    return f"{saat.day} {BULAN[saat.month]} {saat.year}"


def _school_meta():
    return {
        "nama": SCHOOL_NAME,
        "npsn": SCHOOL_NPSN,
        "alamat": SCHOOL_ADDRESS,
        "website": SCHOOL_WEBSITE,
        "kepala": SCHOOL_KEPALA,
        "nbm_kepala": SCHOOL_NBM_KEPALA,
        "kota": SCHOOL_KOTA,
    }


def _report_stats(items):
    total_jenis = len(items)
    total_unit = sum(int(b.get("jumlah") or 0) for b in items)
    tersedia = sum(int(b.get("jumlah_tersedia") or 0) for b in items)
    by_kondisi = {}
    by_kategori = {}
    for b in items:
        kondisi = b.get("kondisi") or "Lainnya"
        by_kondisi[kondisi] = by_kondisi.get(kondisi, 0) + 1
        kat = b.get("kategori_nama") or "Tanpa Kategori"
        by_kategori[kat] = by_kategori.get(kat, 0) + 1
    return {
        "total_jenis": total_jenis,
        "total_unit": total_unit,
        "tersedia": tersedia,
        "dipinjam_unit": max(0, total_unit - tersedia),
        "by_kondisi": sorted(by_kondisi.items(), key=lambda x: (-x[1], x[0])),
        "by_kategori": sorted(by_kategori.items(), key=lambda x: (-x[1], x[0])),
    }


@laporan_bp.route("/")
@login_required
def index():
    return render_template("laporan/index.html")


@laporan_bp.route("/barang")
@login_required
def barang():
    q = request.args.get("q", "").strip()
    kategori_id = request.args.get("kategori_id") or None
    kondisi = request.args.get("kondisi") or None
    if kategori_id:
        kategori_id = int(kategori_id)

    items = models.list_barang(
        q=q or None,
        kategori_id=kategori_id,
        kondisi=kondisi,
    )
    stats = _report_stats(items)
    now = datetime.now()
    tanggal_cetak = _tanggal_cetak(now)

    return render_template(
        "laporan/barang.html",
        items=items,
        stats=stats,
        school=_school_meta(),
        petugas=current_user.nama_lengkap,
        tanggal_cetak=tanggal_cetak,
        waktu_cetak=now.strftime("%d/%m/%Y %H:%M"),
        q=q,
        kategori_id=kategori_id,
        kondisi=kondisi,
        kategori_list=models.list_kategori(),
        print_mode=request.args.get("print") == "1",
    )


@laporan_bp.route("/peminjaman")
@login_required
def peminjaman():
    status = request.args.get("status") or None
    dari = (request.args.get("dari") or "").strip() or None
    sampai = (request.args.get("sampai") or "").strip() or None
    items = models.list_peminjaman(status=status, dari=dari, sampai=sampai)
    masih = sum(1 for p in items if p.get("status") == "Dipinjam")
    kembali = sum(1 for p in items if p.get("status") == "Dikembalikan")
    unit = sum(int(p.get("jumlah") or 0) for p in items)
    now = datetime.now()
    return render_template(
        "laporan/peminjaman.html",
        items=items,
        school=_school_meta(),
        petugas=current_user.nama_lengkap,
        tanggal_cetak=_tanggal_cetak(now),
        waktu_cetak=now.strftime("%d/%m/%Y %H:%M"),
        fmt=_fmt_tanggal,
        status=status or "",
        dari=dari or "",
        sampai=sampai or "",
        stats={
            "transaksi": len(items),
            "masih": masih,
            "kembali": kembali,
            "unit": unit,
        },
        print_mode=request.args.get("print") == "1",
    )


def _terlambat(item):
    rencana = item.get("tanggal_kembali_rencana") or ""
    aktual = item.get("tanggal_kembali_aktual") or ""
    return bool(rencana and aktual and aktual > rencana)


@laporan_bp.route("/pengembalian")
@login_required
def pengembalian():
    dari = (request.args.get("dari") or "").strip() or None
    sampai = (request.args.get("sampai") or "").strip() or None
    items = models.list_peminjaman(
        status="Dikembalikan",
        dari=dari,
        sampai=sampai,
        kolom_tanggal="tanggal_kembali_aktual",
    )
    items.sort(key=lambda p: (p.get("tanggal_kembali_aktual") or "", p["id"]), reverse=True)
    unit = sum(int(p.get("jumlah") or 0) for p in items)
    telat = sum(1 for p in items if _terlambat(p))
    now = datetime.now()
    return render_template(
        "laporan/pengembalian.html",
        items=items,
        school=_school_meta(),
        petugas=current_user.nama_lengkap,
        tanggal_cetak=_tanggal_cetak(now),
        waktu_cetak=now.strftime("%d/%m/%Y %H:%M"),
        fmt=_fmt_tanggal,
        terlambat=_terlambat,
        dari=dari or "",
        sampai=sampai or "",
        stats={
            "transaksi": len(items),
            "unit": unit,
            "tepat": len(items) - telat,
            "telat": telat,
        },
        print_mode=request.args.get("print") == "1",
    )


@laporan_bp.route("/pengembalian/<int:peminjaman_id>/tanda-terima")
@login_required
def tanda_terima_kembali(peminjaman_id):
    item = models.get_peminjaman(peminjaman_id)
    if not item or item.get("status") != "Dikembalikan":
        abort(404)
    now = datetime.now()
    tahun = str(item.get("tanggal_kembali_aktual") or now.year)[:4]
    return render_template(
        "laporan/tanda_terima_kembali.html",
        item=item,
        school=_school_meta(),
        petugas=current_user.nama_lengkap,
        tanggal_cetak=_tanggal_cetak(now),
        waktu_cetak=now.strftime("%d/%m/%Y %H:%M"),
        fmt=_fmt_tanggal,
        nomor=f"TTK-INV/{int(item['id']):04d}/{tahun}",
        terlambat=_terlambat(item),
        print_mode=request.args.get("print") == "1",
    )


@laporan_bp.route("/peminjaman/<int:peminjaman_id>/tanda-terima")
@login_required
def tanda_terima(peminjaman_id):
    item = models.get_peminjaman(peminjaman_id)
    if not item:
        abort(404)
    now = datetime.now()
    tahun = str(item.get("tanggal_pinjam") or now.year)[:4]
    return render_template(
        "laporan/tanda_terima.html",
        item=item,
        school=_school_meta(),
        petugas=current_user.nama_lengkap,
        tanggal_cetak=_tanggal_cetak(now),
        waktu_cetak=now.strftime("%d/%m/%Y %H:%M"),
        fmt=_fmt_tanggal,
        nomor=f"TT-INV/{int(item['id']):04d}/{tahun}",
        print_mode=request.args.get("print") == "1",
    )


@laporan_bp.route("/export-excel")
@login_required
def export_excel():
    wb = Workbook()

    ws = wb.active
    ws.title = "Barang"
    headers = [
        "Kode", "Nama", "Kategori", "Lokasi", "Jumlah", "Tersedia",
        "Satuan", "Kondisi", "Sumber", "Tahun", "Harga", "Keterangan",
    ]
    ws.append(headers)
    header_fill = PatternFill("solid", fgColor="1B5E4A")
    header_font = Font(color="FFFFFF", bold=True)
    for col, _ in enumerate(headers, 1):
        cell = ws.cell(1, col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for b in models.list_barang():
        ws.append([
            b["kode"],
            b["nama"],
            b.get("kategori_nama") or "",
            b.get("lokasi_nama") or "",
            b["jumlah"],
            b["jumlah_tersedia"],
            b["satuan"],
            b["kondisi"],
            b.get("sumber") or "",
            b.get("tahun_perolehan") or "",
            b.get("harga_perolehan") or 0,
            b.get("keterangan") or "",
        ])

    ws2 = wb.create_sheet("Peminjaman")
    headers2 = [
        "Kode Barang", "Nama Barang", "Peminjam", "Kelas/Unit", "Jumlah",
        "Tgl Pinjam", "Rencana Kembali", "Tgl Kembali", "Status", "Petugas",
    ]
    ws2.append(headers2)
    for col, _ in enumerate(headers2, 1):
        cell = ws2.cell(1, col)
        cell.fill = header_fill
        cell.font = header_font

    for p in models.list_peminjaman():
        ws2.append([
            p.get("barang_kode"),
            p.get("barang_nama"),
            p["peminjam"],
            p.get("kelas_unit") or "",
            p["jumlah"],
            p["tanggal_pinjam"],
            p.get("tanggal_kembali_rencana") or "",
            p.get("tanggal_kembali_aktual") or "",
            p["status"],
            p.get("petugas") or "",
        ])

    for sheet in (ws, ws2):
        for column in sheet.columns:
            max_len = 0
            col_letter = column[0].column_letter
            for cell in column:
                max_len = max(max_len, len(str(cell.value or "")))
            sheet.column_dimensions[col_letter].width = min(max_len + 2, 40)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="laporan_inventaris_smpm22.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
