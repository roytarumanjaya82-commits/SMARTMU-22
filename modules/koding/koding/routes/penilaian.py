from io import BytesIO
from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from koding import db
from koding.auth_utils import guru_required
from koding.config import JENIS_UJIAN

bp = Blueprint("penilaian", __name__)


def _reset_percobaan_siswa(siswa_id, ujian_id):
    """Hapus nilai + seluruh percobaan siswa untuk satu ujian agar bisa dikerjakan ulang."""
    percs = db.query(
        "SELECT id FROM percobaan_ujian WHERE siswa_id=%s AND ujian_id=%s",
        (siswa_id, ujian_id),
    )
    for p in percs:
        db.execute("DELETE FROM jawaban_siswa WHERE percobaan_id=%s", (p["id"],))
    db.execute(
        "DELETE FROM percobaan_ujian WHERE siswa_id=%s AND ujian_id=%s",
        (siswa_id, ujian_id),
    )
    db.execute(
        "DELETE FROM nilai WHERE siswa_id=%s AND ujian_id=%s",
        (siswa_id, ujian_id),
    )


@bp.route("/")
@guru_required
def index():
    return render_template("penilaian/index.html", jenis_map=JENIS_UJIAN)


@bp.route("/rekap")
@guru_required
def rekap():
    jenis = request.args.get("jenis", "latihan")
    kelas_id = request.args.get("kelas_id", type=int)
    kelas_list = db.query("SELECT * FROM kelas ORDER BY nama_kelas")
    if not kelas_id and kelas_list:
        kelas_id = kelas_list[0]["id"]

    ujian_list = db.query(
        "SELECT id, judul FROM ujian WHERE jenis=%s AND aktif=1 ORDER BY id",
        (jenis,),
    )

    rows = []
    if kelas_id:
        siswa = db.query(
            "SELECT id, nis, nama_siswa FROM siswa WHERE kelas_id=%s ORDER BY nama_siswa",
            (kelas_id,),
        )
        nilai_map = {}
        if ujian_list:
            ids = [u["id"] for u in ujian_list]
            placeholders = ",".join(["%s"] * len(ids))
            nilai_rows = db.query(
                f"""
                SELECT siswa_id, ujian_id, skor
                FROM nilai
                WHERE ujian_id IN ({placeholders})
                """,
                tuple(ids),
            )
            for n in nilai_rows:
                nilai_map[(n["siswa_id"], n["ujian_id"])] = float(n["skor"])

        for s in siswa:
            skor_per_ujian = {u["id"]: nilai_map.get((s["id"], u["id"])) for u in ujian_list}
            nilai_ada = [v for v in skor_per_ujian.values() if v is not None]
            rata = round(sum(nilai_ada) / len(nilai_ada), 1) if nilai_ada else None
            rows.append(
                {
                    "siswa_id": s["id"],
                    "nis": s["nis"],
                    "nama_siswa": s["nama_siswa"],
                    "skor": skor_per_ujian,
                    "rata": rata,
                }
            )

    return render_template(
        "penilaian/rekap.html",
        jenis=jenis,
        jenis_map=JENIS_UJIAN,
        kelas_list=kelas_list,
        kelas_id=kelas_id,
        ujian_list=ujian_list,
        rows=rows,
    )


@bp.route("/export")
@guru_required
def export_excel():
    jenis = request.args.get("jenis", "latihan")
    kelas_id = request.args.get("kelas_id", type=int)
    if not kelas_id:
        return "Kelas belum dipilih", 400

    kelas = db.query("SELECT * FROM kelas WHERE id=%s", (kelas_id,), one=True)
    ujian_list = db.query(
        "SELECT id, judul FROM ujian WHERE jenis=%s AND aktif=1 ORDER BY id",
        (jenis,),
    )
    siswa = db.query(
        "SELECT id, nis, nama_siswa FROM siswa WHERE kelas_id=%s ORDER BY nama_siswa",
        (kelas_id,),
    )

    nilai_map = {}
    if ujian_list:
        ids = [u["id"] for u in ujian_list]
        placeholders = ",".join(["%s"] * len(ids))
        nilai_rows = db.query(
            f"SELECT siswa_id, ujian_id, skor FROM nilai WHERE ujian_id IN ({placeholders})",
            tuple(ids),
        )
        for n in nilai_rows:
            nilai_map[(n["siswa_id"], n["ujian_id"])] = float(n["skor"])

    wb = Workbook()
    ws = wb.active
    ws.title = "Rekap Nilai"
    header_fill = PatternFill("solid", fgColor="0F766E")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    ws["A1"] = f"REKAP PENILAIAN - {JENIS_UJIAN.get(jenis, jenis).upper()}"
    ws["A2"] = f"Kelas: {kelas['nama_kelas']} | Tahun: {kelas['tahun_ajaran']} | Semester: {kelas['semester']}"
    ws.merge_cells("A1:H1")
    ws.merge_cells("A2:H2")
    ws["A1"].font = Font(bold=True, size=14, color="0F766E")

    headers = ["No", "NIS", "Nama Siswa"] + [u["judul"] for u in ujian_list] + ["Rata-rata"]
    for c, h in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=c, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(wrap_text=True, horizontal="center")
        cell.border = thin

    for i, s in enumerate(siswa, start=1):
        values = [i, s["nis"], s["nama_siswa"]]
        skor_list = []
        for u in ujian_list:
            skor = nilai_map.get((s["id"], u["id"]))
            values.append(skor if skor is not None else "-")
            if skor is not None:
                skor_list.append(skor)
        values.append(round(sum(skor_list) / len(skor_list), 1) if skor_list else "-")
        for c, v in enumerate(values, start=1):
            cell = ws.cell(row=4 + i, column=c, value=v)
            cell.border = thin

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 28
    for idx in range(4, len(headers) + 1):
        ws.column_dimensions[chr(64 + idx) if idx <= 26 else "A"].width = 18

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    nama = f"rekap_{jenis}_{kelas['nama_kelas'].replace(' ', '_')}.xlsx"
    return send_file(
        bio,
        as_attachment=True,
        download_name=nama,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/reset")
@guru_required
def reset():
    jenis = request.args.get("jenis", "latihan")
    kelas_id = request.args.get("kelas_id", type=int)
    ujian_id = request.args.get("ujian_id", type=int)
    kelas_list = db.query("SELECT * FROM kelas ORDER BY nama_kelas")
    if not kelas_id and kelas_list:
        kelas_id = kelas_list[0]["id"]

    ujian_list = db.query(
        """
        SELECT id, judul, tingkat, semester
        FROM ujian WHERE jenis=%s AND aktif=1
        ORDER BY tingkat, semester, id
        """,
        (jenis,),
    )
    if not ujian_id and ujian_list:
        ujian_id = ujian_list[0]["id"]

    rows = []
    if kelas_id and ujian_id:
        rows = db.query(
            """
            SELECT s.id AS siswa_id, s.nis, s.nama_siswa, n.skor, n.dinilai_at,
                   (
                     SELECT p.status FROM percobaan_ujian p
                     WHERE p.siswa_id=s.id AND p.ujian_id=%s
                     ORDER BY p.id DESC LIMIT 1
                   ) AS status_terakhir
            FROM siswa s
            LEFT JOIN nilai n ON n.siswa_id=s.id AND n.ujian_id=%s
            WHERE s.kelas_id=%s
            ORDER BY s.nama_siswa
            """,
            (ujian_id, ujian_id, kelas_id),
        )

    return render_template(
        "penilaian/reset.html",
        jenis=jenis,
        jenis_map=JENIS_UJIAN,
        kelas_list=kelas_list,
        kelas_id=kelas_id,
        ujian_list=ujian_list,
        ujian_id=ujian_id,
        rows=rows,
    )


@bp.route("/reset/siswa", methods=["POST"])
@guru_required
def reset_siswa():
    siswa_id = request.form.get("siswa_id", type=int)
    ujian_id = request.form.get("ujian_id", type=int)
    jenis = request.form.get("jenis", "latihan")
    kelas_id = request.form.get("kelas_id", type=int)
    if not siswa_id or not ujian_id:
        flash("Data reset tidak lengkap.", "danger")
        return redirect(url_for("penilaian.reset"))

    _reset_percobaan_siswa(siswa_id, ujian_id)
    flash("Percobaan siswa berhasil direset. Siswa dapat mengerjakan ulang.", "success")
    return redirect(
        url_for("penilaian.reset", jenis=jenis, kelas_id=kelas_id, ujian_id=ujian_id)
    )


@bp.route("/reset/kelas", methods=["POST"])
@guru_required
def reset_kelas():
    ujian_id = request.form.get("ujian_id", type=int)
    kelas_id = request.form.get("kelas_id", type=int)
    jenis = request.form.get("jenis", "latihan")
    if not ujian_id or not kelas_id:
        flash("Data reset tidak lengkap.", "danger")
        return redirect(url_for("penilaian.reset"))

    siswa = db.query("SELECT id FROM siswa WHERE kelas_id=%s", (kelas_id,))
    for s in siswa:
        _reset_percobaan_siswa(s["id"], ujian_id)
    flash(
        f"Reset selesai untuk {len(siswa)} siswa pada ujian terpilih.",
        "success",
    )
    return redirect(
        url_for("penilaian.reset", jenis=jenis, kelas_id=kelas_id, ujian_id=ujian_id)
    )
