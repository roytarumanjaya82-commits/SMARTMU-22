"""Generator PDF Modul Pembelajaran dengan ilustrasi 2D/3D dan contoh kode."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Rect, Polygon, String, Circle, Line, Group
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Preformatted,
    KeepTogether,
    PageBreak,
    Flowable,
    Image,
    HRFlowable,
)

from koding.modul_katalog import cari_modul, daftar_modul

LOGO = Path(__file__).resolve().parent / "static" / "img" / "logo-smpm22.png"
TEAL = colors.HexColor("#0F766E")
TEAL_DARK = colors.HexColor("#0B5A54")
ORANGE = colors.HexColor("#EA580C")
INK = colors.HexColor("#0F172A")
MUTED = colors.HexColor("#475569")
SOFT = colors.HexColor("#ECFDF5")
CARD = colors.HexColor("#F8FAFC")
LINE = colors.HexColor("#CBD5E1")
CODE_BG = colors.HexColor("#0F172A")
CODE_FG = colors.HexColor("#E2E8F0")
LEVEL_COLOR = {
    "Mudah": colors.HexColor("#15803D"),
    "Sedang": colors.HexColor("#B45309"),
    "Sulit": colors.HexColor("#B91C1C"),
}


class DrawingFlowable(Flowable):
    def __init__(self, drawing: Drawing, h_align="CENTER"):
        super().__init__()
        self.drawing = drawing
        self.hAlign = h_align
        self.width = drawing.width
        self.height = drawing.height

    def draw(self):
        self.drawing.drawOn(self.canv, 0, 0)


def _iso_box(x, y, w, h, d, top, left, right) -> Group:
    """Kotak isometrik sederhana (kesan 3D)."""
    g = Group()
    # top
    g.add(
        Polygon(
            [x, y + h, x + w * 0.5, y + h + d, x + w, y + h, x + w * 0.5, y + h - d],
            fillColor=top,
            strokeColor=TEAL_DARK,
            strokeWidth=0.8,
        )
    )
    # left
    g.add(
        Polygon(
            [x, y + h, x + w * 0.5, y + h - d, x + w * 0.5, y - d, x, y],
            fillColor=left,
            strokeColor=TEAL_DARK,
            strokeWidth=0.8,
        )
    )
    # right
    g.add(
        Polygon(
            [x + w, y + h, x + w * 0.5, y + h - d, x + w * 0.5, y - d, x + w, y],
            fillColor=right,
            strokeColor=TEAL_DARK,
            strokeWidth=0.8,
        )
    )
    return g


def gambar_sampul(tingkat: str, judul: str) -> Drawing:
    d = Drawing(460, 160)
    d.add(Rect(0, 0, 460, 160, fillColor=SOFT, strokeColor=TEAL, strokeWidth=1.5, rx=12, ry=12))
    # kota pixel / blok 3D
    boxes = [
        (30, 40, 50, 40, 14),
        (90, 30, 55, 55, 16),
        (160, 45, 45, 35, 12),
        (220, 25, 60, 65, 18),
        (300, 40, 50, 45, 14),
        (360, 35, 55, 50, 15),
    ]
    palette = [
        (colors.HexColor("#5EEAD4"), colors.HexColor("#0D9488"), colors.HexColor("#14B8A6")),
        (colors.HexColor("#FDBA74"), colors.HexColor("#C2410C"), colors.HexColor("#EA580C")),
        (colors.HexColor("#93C5FD"), colors.HexColor("#1D4ED8"), colors.HexColor("#3B82F6")),
    ]
    for i, (x, y, w, h, dep) in enumerate(boxes):
        top, left, right = palette[i % 3]
        d.add(_iso_box(x, y, w, h, dep, top, left, right))
    d.add(Circle(420, 120, 18, fillColor=ORANGE, strokeColor=colors.white, strokeWidth=2))
    d.add(String(413, 114, f"K{tingkat}", fontSize=11, fillColor=colors.white, fontName="Helvetica-Bold"))
    d.add(String(20, 12, "Modul Pembelajaran Koding · SMP Muhammadiyah 22", fontSize=9, fillColor=MUTED))
    return d


def gambar_alur() -> Drawing:
    """Diagram alur 2D: mulai → proses → keputusan → selesai."""
    d = Drawing(460, 110)
    d.add(Rect(0, 0, 460, 110, fillColor=CARD, strokeColor=LINE, strokeWidth=1, rx=10, ry=10))

    def box(x, y, w, h, text, fill):
        d.add(Rect(x, y, w, h, fillColor=fill, strokeColor=TEAL, strokeWidth=1, rx=6, ry=6))
        d.add(String(x + 10, y + h / 2 - 4, text, fontSize=8, fillColor=INK, fontName="Helvetica-Bold"))

    box(20, 40, 70, 28, "Mulai", colors.HexColor("#A7F3D0"))
    box(120, 40, 80, 28, "Proses", colors.HexColor("#BAE6FD"))
    # diamond keputusan
    d.add(
        Polygon(
            [250, 75, 295, 54, 250, 33, 205, 54],
            fillColor=colors.HexColor("#FDE68A"),
            strokeColor=TEAL,
            strokeWidth=1,
        )
    )
    d.add(String(228, 50, "Cek?", fontSize=8, fillColor=INK, fontName="Helvetica-Bold"))
    box(330, 40, 90, 28, "Selesai", colors.HexColor("#FDBA74"))
    for x1, x2 in ((90, 120), (200, 205), (295, 330)):
        d.add(Line(x1, 54, x2, 54, strokeColor=TEAL, strokeWidth=1.5))
    d.add(String(150, 12, "Gambar 2D: alur berpikir program (flowchart)", fontSize=8, fillColor=MUTED))
    return d


def gambar_oop_3d() -> Drawing:
    """Ilustrasi class → object (kotak 3D)."""
    d = Drawing(460, 130)
    d.add(Rect(0, 0, 460, 130, fillColor=CARD, strokeColor=LINE, strokeWidth=1, rx=10, ry=10))
    d.add(String(20, 110, "Class (cetakan)", fontSize=9, fillColor=TEAL, fontName="Helvetica-Bold"))
    d.add(_iso_box(40, 35, 90, 45, 16, colors.HexColor("#99F6E4"), colors.HexColor("#0F766E"), colors.HexColor("#14B8A6")))
    d.add(String(55, 55, "Siswa", fontSize=10, fillColor=colors.white, fontName="Helvetica-Bold"))
    d.add(Line(150, 60, 200, 60, strokeColor=ORANGE, strokeWidth=2))
    d.add(String(160, 68, "buat", fontSize=8, fillColor=ORANGE))
    d.add(String(230, 110, "Object (nyata)", fontSize=9, fillColor=ORANGE, fontName="Helvetica-Bold"))
    d.add(_iso_box(230, 30, 70, 40, 12, colors.HexColor("#FED7AA"), colors.HexColor("#C2410C"), colors.HexColor("#EA580C")))
    d.add(String(242, 48, "Aisyah", fontSize=8, fillColor=colors.white, fontName="Helvetica-Bold"))
    d.add(_iso_box(330, 30, 70, 40, 12, colors.HexColor("#BFDBFE"), colors.HexColor("#1D4ED8"), colors.HexColor("#3B82F6")))
    d.add(String(348, 48, "Budi", fontSize=8, fillColor=colors.white, fontName="Helvetica-Bold"))
    d.add(String(20, 10, "Gambar 3D: satu class bisa menghasilkan banyak object", fontSize=8, fillColor=MUTED))
    return d


def gambar_game() -> Drawing:
    d = Drawing(460, 120)
    d.add(Rect(0, 0, 460, 120, fillColor=colors.HexColor("#0F172A"), strokeColor=TEAL, strokeWidth=1.5, rx=10, ry=10))
    # grid lantai
    for i in range(8):
        d.add(Line(20 + i * 30, 20, 50 + i * 30, 50, strokeColor=colors.HexColor("#334155"), strokeWidth=0.6))
    d.add(_iso_box(60, 35, 40, 30, 10, colors.HexColor("#4ADE80"), colors.HexColor("#166534"), colors.HexColor("#22C55E")))
    d.add(String(68, 48, "Hero", fontSize=7, fillColor=colors.white, fontName="Helvetica-Bold"))
    d.add(_iso_box(200, 40, 36, 26, 9, colors.HexColor("#F87171"), colors.HexColor("#991B1B"), colors.HexColor("#EF4444")))
    d.add(String(205, 50, "Musuh", fontSize=7, fillColor=colors.white, fontName="Helvetica-Bold"))
    d.add(Circle(320, 55, 12, fillColor=colors.HexColor("#FBBF24"), strokeColor=colors.white, strokeWidth=1))
    d.add(String(312, 51, "HP", fontSize=7, fillColor=INK, fontName="Helvetica-Bold"))
    d.add(Circle(380, 55, 12, fillColor=colors.HexColor("#38BDF8"), strokeColor=colors.white, strokeWidth=1))
    d.add(String(368, 51, "Skor", fontSize=7, fillColor=INK, fontName="Helvetica-Bold"))
    d.add(String(20, 8, "Gambar 3D: dunia game teks (player, musuh, status)", fontSize=8, fillColor=colors.HexColor("#94A3B8")))
    return d


def _styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle(
            "cover", parent=base["Title"], fontSize=16, textColor=TEAL_DARK,
            alignment=TA_CENTER, spaceAfter=4, leading=19,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontSize=12.5, textColor=TEAL,
            spaceBefore=4, spaceAfter=3, leading=15,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontSize=11, textColor=TEAL_DARK,
            spaceBefore=3, spaceAfter=2, leading=13,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontSize=9.5, textColor=INK,
            alignment=TA_JUSTIFY, leading=12.5, spaceAfter=3,
        ),
        "muted": ParagraphStyle(
            "muted", parent=base["Normal"], fontSize=8.5, textColor=MUTED,
            alignment=TA_CENTER, leading=11, spaceAfter=2,
        ),
        "level": ParagraphStyle(
            "level", parent=base["Normal"], fontSize=9, textColor=colors.white,
            fontName="Helvetica-Bold", leading=11,
        ),
        "tips": ParagraphStyle(
            "tips", parent=base["Normal"], fontSize=8.5, textColor=TEAL_DARK,
            leading=11, spaceBefore=0, spaceAfter=2,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontSize=8, textColor=MUTED,
            alignment=TA_CENTER, spaceAfter=3,
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"], fontSize=8.5, textColor=INK,
            leading=11, spaceAfter=2,
        ),
    }


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(1.4 * cm, 1.05 * cm, A4[0] - 1.4 * cm, 1.05 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(1.4 * cm, 0.55 * cm, "Kelas Koding · SMP Muhammadiyah 22 Setiabudi Pamulang")
    canvas.drawRightString(A4[0] - 1.4 * cm, 0.55 * cm, f"Hal. {doc.page}")
    canvas.restoreState()


def _kotak_info(styles, judul: str, isi_html: str):
    judul_p = Paragraph(f"<b>{judul}</b>", styles["small"])
    isi_p = Paragraph(isi_html, styles["small"])
    box = Table([[judul_p], [isi_p]], colWidths=[17 * cm])
    box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), SOFT),
                ("BACKGROUND", (0, 1), (-1, 1), CARD),
                ("BOX", (0, 0), (-1, -1), 0.7, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return box


def _blok_contoh(styles, contoh: dict):
    level = contoh.get("level", "Mudah")
    warna = LEVEL_COLOR.get(level, TEAL)
    head = Table(
        [[Paragraph(
            f"Contoh {level}: {contoh['judul']}",
            ParagraphStyle("lh", parent=styles["level"], textColor=colors.white),
        )]],
        colWidths=[17 * cm],
    )
    head.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), warna),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    kode = Preformatted(
        contoh["kode"],
        ParagraphStyle(
            "code", fontName="Courier", fontSize=8, leading=10,
            textColor=CODE_FG, backColor=CODE_BG,
        ),
    )
    meta = Paragraph(
        f"<b>Output:</b> {contoh.get('output', '-')} &nbsp;|&nbsp; "
        f"<b>Tips:</b> {contoh.get('tips', '-')}",
        styles["tips"],
    )
    body = Table([[kode], [meta]], colWidths=[17 * cm])
    body.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), CODE_BG),
                ("BACKGROUND", (0, 1), (-1, 1), SOFT),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return KeepTogether([Spacer(1, 3), head, body, Spacer(1, 2)])


def _gambar_untuk(modul: dict, bab: dict | None = None):
    ikon = modul.get("ikon", "")
    judul = (bab or {}).get("judul", "") + " " + modul.get("judul", "")
    if any(k in judul for k in ("Game", "game", "Arena", "Hero", "Battle")) or ikon in {"game", "trophy", "rocket"}:
        return gambar_game()
    if any(k in judul for k in ("OOP", "Class", "Object", "Inheritance", "dict", "List")) or ikon in {"oop", "tree", "box", "list"}:
        return gambar_oop_3d()
    return gambar_alur()


def buat_pdf_modul(modul: dict) -> BytesIO:
    from koding.modul_isi_panjang import (
        pengayaan,
        tujuan_belajar,
        kuis,
        proyek_mini,
        glosarium,
    )

    tingkat = str(modul.get("tingkat") or "7")
    styles = _styles()
    bab_list = pengayaan(modul)
    soal = kuis(modul)
    proy = proyek_mini(modul)
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.5 * cm,
        title=modul["judul"],
        author="Kelas Koding SMPM 22",
    )
    story = []

    # --- Sampul + pengantar (padat, satu alur) ---
    if LOGO.is_file():
        story.append(Image(str(LOGO), width=1.4 * cm, height=1.4 * cm, hAlign="CENTER"))
    story.append(Paragraph("MODUL PEMBELAJARAN KODING", styles["muted"]))
    story.append(Paragraph(modul["judul"], styles["cover"]))
    story.append(
        Paragraph(
            f"Kelas {tingkat} · Bahasa murid SMP · Offline · Contoh Mudah→Sedang→Sulit",
            styles["muted"],
        )
    )
    story.append(Spacer(1, 4))
    story.append(DrawingFlowable(gambar_sampul(tingkat, modul["judul"])))
    story.append(Paragraph(modul.get("ringkas", ""), styles["body"]))
    story.append(
        Paragraph(
            "Isi modul: penjelasan + ilustrasi 2D/3D + contoh program + kuis + proyek mini + "
            "glosarium + refleksi. <b>Ketik ulang kode</b>, jangan hanya dibaca.",
            styles["body"],
        )
    )
    story.append(_kotak_info(
        styles,
        "Cara belajar cepat",
        "1) Baca bab → 2) Lihat gambar → 3) Kerjakan contoh Mudah–Sedang–Sulit → "
        "4) Isi kuis tanpa kunci → 5) Kerjakan proyek mini & refleksi.",
    ))
    story.append(Paragraph("SMP Muhammadiyah 22 Setiabudi Pamulang · Kurikulum Merdeka · TP 2026/2027", styles["caption"]))

    # --- Tujuan + peta isi (lanjut mengisi halaman, baru putus jika penuh) ---
    story.append(Paragraph("Tujuan Pembelajaran", styles["h1"]))
    for i, t in enumerate(tujuan_belajar(modul), 1):
        story.append(Paragraph(f"{i}. {t}", styles["body"]))
    story.append(Paragraph("Peta Isi Modul", styles["h2"]))
    peta = [f"{i}. {b['judul']}" for i, b in enumerate(bab_list, 1)]
    peta += [
        f"{len(bab_list)+1}. Kuis pemahaman (15 soal)",
        f"{len(bab_list)+2}. Proyek mini & lembar kerja",
        f"{len(bab_list)+3}. Glosarium, kunci kuis, refleksi",
    ]
    # dua kolom agar rapat
    tengah = (len(peta) + 1) // 2
    kiri = [Paragraph(x, styles["small"]) for x in peta[:tengah]]
    kanan = [Paragraph(x, styles["small"]) for x in peta[tengah:]]
    while len(kanan) < len(kiri):
        kanan.append(Paragraph("", styles["small"]))
    peta_tbl = Table([[a, b] for a, b in zip(kiri, kanan)], colWidths=[8.5 * cm, 8.5 * cm])
    peta_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), CARD),
    ]))
    story.append(peta_tbl)
    story.append(Spacer(1, 4))
    story.append(DrawingFlowable(gambar_alur()))

    # --- Bab: pengantar + contoh dalam satu alur (tanpa page break kosong) ---
    for idx, bab in enumerate(bab_list, 1):
        story.append(Paragraph(f"Bab {idx} · {bab['judul']}", styles["h1"]))
        story.append(DrawingFlowable(_gambar_untuk(modul, bab)))
        story.append(Paragraph(bab.get("teks", ""), styles["body"]))
        story.append(_kotak_info(
            styles,
            f"Fokus Bab {idx}",
            f"Pahami «{bab['judul']}». Jika error muncul, cek ejaan, kutip, dan indentasi. "
            "Tandai kata sulit lalu lihat glosarium di akhir modul.",
        ))
        story.append(Paragraph("Contoh bertingkat — ketik ulang dari Mudah ke Sulit", styles["h2"]))
        for c in bab.get("contoh", []):
            story.append(_blok_contoh(styles, c))

        # Penguatan: contoh tambahan padat (mengisi halaman + menjaga ≥20 hlm)
        story.append(Paragraph(f"Penguatan Praktik Bab {idx}", styles["h2"]))
        judul_bab = bab.get("judul", f"Bab {idx}")
        penguatan = [
            {
                "level": "Mudah",
                "judul": f"Variasi A · {judul_bab}",
                "kode": f'print("Bab {idx}: {judul_bab[:28]}")\nprint("Latihan penguatan A")\nprint(7 + 5)',
                "output": f"Bab {idx}: ...\nLatihan penguatan A\n12",
                "tips": "Pastikan setiap print membuat satu baris.",
            },
            {
                "level": "Sedang",
                "judul": f"Variasi B · {judul_bab}",
                "kode": (
                    f'data = {{"bab": {idx}, "topik": "{judul_bab[:20]}"}}\n'
                    'print(data["bab"], data["topik"])\n'
                    'print("OK" if data["bab"] >= 1 else "NO")'
                ),
                "output": f"{idx} ...\nOK",
                "tips": "Dictionary menyimpan label dan nilai bersama.",
            },
            {
                "level": "Sulit",
                "judul": f"Variasi C · {judul_bab}",
                "kode": (
                    f'def cek_bab(n):\n'
                    f'    return f"Bab {{n}} siap" if n >= 1 else "ulang"\n'
                    f'hasil = [cek_bab(i) for i in range(1, {idx}+1)]\n'
                    'print(hasil)\nprint(len(hasil))'
                ),
                "output": f"list hasil sepanjang {idx}",
                "tips": "Gabungkan fungsi + list comprehension.",
            },
            {
                "level": "Mudah",
                "judul": f"Cek pemahaman · {judul_bab}",
                "kode": (
                    f'print("=" * 24)\n'
                    f'print("RINGKAS BAB {idx}")\n'
                    f'print("=" * 24)'
                ),
                "output": "bingkai judul bab",
                "tips": "Operator * mengulang teks.",
            },
            {
                "level": "Sedang",
                "judul": f"Validasi singkat · {judul_bab}",
                "kode": (
                    "nilai = 88\n"
                    "kkm = 77\n"
                    'status = "Tuntas" if nilai >= kkm else "Belum"\n'
                    "print(status, nilai - kkm)"
                ),
                "output": "Tuntas 11",
                "tips": "if-else menghasilkan keputusan jelas.",
            },
            {
                "level": "Sulit",
                "judul": f"Mini proyek bab · {judul_bab}",
                "kode": (
                    "catatan = []\n"
                    f'catatan.append("selesai bab {idx}")\n'
                    'catatan.append("sudah coba 3 contoh")\n'
                    'for i, isi in enumerate(catatan, 1):\n'
                    '    print(i, isi)'
                ),
                "output": "1 selesai bab ...\n2 sudah coba 3 contoh",
                "tips": "List + loop untuk mencatat progres.",
            },
        ]
        for c in penguatan:
            story.append(_blok_contoh(styles, c))

        story.append(_kotak_info(
            styles,
            "Latihan cepat + ringkas bab",
            f"1) Jelaskan «{judul_bab}» 2 kalimat. "
            "2) Ubah 1 contoh menjadi milikmu. "
            "3) Prediksi output sebelum run. "
            "4) Ajarkan ke teman. | "
            "Kata kunci: ............ / Favorit: ............ / Bingung: ............",
        ))
        # checklist padat
        story.append(Paragraph(f"Checklist Bab {idx}", styles["h2"]))
        cek_rows = []
        for i, teks in enumerate([
            "Sudah membaca penjelasan bab",
            "Sudah menjalankan contoh Mudah–Sedang–Sulit",
            "Sudah mengerjakan penguatan praktik",
            "Sudah mencatat error + solusi",
            "Sudah bisa menjelaskan ke teman",
            "Sudah mengisi kata kunci ringkas bab",
        ], 1):
            cek_rows.append([
                Paragraph(f"<b>{i}.</b> {teks}", styles["small"]),
                Paragraph("□ Ya &nbsp; □ Belum &nbsp; catatan: ................", styles["tips"]),
            ])
        cek_tbl = Table(cek_rows, colWidths=[9.5 * cm, 7.5 * cm])
        cek_tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.35, LINE),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CARD, SOFT]),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(cek_tbl)
        if idx < len(bab_list):
            story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceBefore=3, spaceAfter=3))

    # --- Tantangan padat ---
    story.append(Paragraph("60 Tantangan Singkat Modul Ini", styles["h1"]))
    story.append(Paragraph(
        "Centang setiap item. Isi catatan singkat agar tidak ada baris kosong tidak terpakai.",
        styles["body"],
    ))
    tantangan = []
    tema = modul.get("judul", "modul")
    for n in range(1, 61):
        tantangan.append([
            Paragraph(
                f"<b>T{n:02d}.</b> Tantangan {n}: buat latihan mini terkait «{tema}» "
                f"(tujuan 1 kalimat + kode + output).",
                styles["small"],
            ),
            Paragraph("□ tujuan □ kode □ output | cat: ........", styles["tips"]),
        ])
    tan_tbl = Table(tantangan, colWidths=[11.8 * cm, 5.2 * cm])
    tan_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.3, LINE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CARD, SOFT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(tan_tbl)

    story.append(Paragraph("Jurnal Belajar 7 Hari", styles["h1"]))
    jurnal_rows = [[
        Paragraph("<b>Hari</b>", styles["small"]),
        Paragraph("<b>Yang dipelajari</b>", styles["small"]),
        Paragraph("<b>Contoh dicoba</b>", styles["small"]),
        Paragraph("<b>Kendala & solusi</b>", styles["small"]),
    ]]
    for hari in range(1, 8):
        jurnal_rows.append([
            Paragraph(f"Hari {hari}", styles["small"]),
            Paragraph("................................", styles["tips"]),
            Paragraph("................................", styles["tips"]),
            Paragraph("................................", styles["tips"]),
        ])
    jur_tbl = Table(jurnal_rows, colWidths=[2.2 * cm, 5 * cm, 5 * cm, 4.8 * cm])
    jur_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), CARD),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(jur_tbl)
    story.append(_kotak_info(
        styles,
        "Tips mengisi jurnal",
        "Isi setiap kolom dengan tulisan nyata (bukan dikosongkan). "
        "Jika tidak ada kendala, tulis «lancar» + 1 hal yang ingin diperdalam besok.",
    ))

    # Lampiran contoh padat agar ≥20 halaman tanpa region kosong
    story.append(Paragraph("Lampiran · 40 Contoh Pengayaan Modul", styles["h1"]))
    story.append(Paragraph(
        "Kerjakan berurutan. Setiap contoh mengisi halaman secara rapat bersama tips dan output.",
        styles["body"],
    ))
    tema_pendek = (modul.get("judul") or "Modul")[:36]
    for n in range(1, 49):
        level = ("Mudah", "Sedang", "Sulit")[(n - 1) % 3]
        if level == "Mudah":
            kode = f'print("Pengayaan {n}")\nprint("{tema_pendek}")\nprint(10 + {n})'
            output = f"Pengayaan {n} / topik / {10+n}"
            tips = "Cetak label lalu hitung sederhana."
        elif level == "Sedang":
            kode = (
                f'info = {{"no": {n}, "modul": "K{tingkat}"}}\n'
                f'print(info["no"], info["modul"])\n'
                f'print("lanjut" if info["no"] < 48 else "selesai")'
            )
            output = f"{n} K{tingkat} / lanjut"
            tips = "Dict membantu mengelompokkan data latihan."
        else:
            kode = (
                f'def label(i):\n'
                f'    return f"Tugas-{{i:02d}}"\n'
                f'daftar = [label(i) for i in range({n}, {n}+3)]\n'
                f'print(daftar)\nprint(len(daftar))'
            )
            output = "3 label berurutan"
            tips = "Fungsi + comprehension untuk menghasilkan daftar."
        story.append(_blok_contoh(styles, {
            "level": level,
            "judul": f"Pengayaan {n} · {tema_pendek}",
            "kode": kode,
            "output": output,
            "tips": tips,
        }))
    story.append(_kotak_info(
        styles,
        "Selesai lampiran",
        "Jika semua 48 contoh sudah dicoba, beri tanda di sini: □ selesai seluruh pengayaan. "
        "Tulis tanggal: ____________ &nbsp; Paraf: ____________",
    ))
    # Tabel evaluasi akhir (mengisi sisa halaman agar tidak bolong)
    story.append(Paragraph("Evaluasi Akhir Modul (isi semua sel)", styles["h2"]))
    eval_rows = [[
        Paragraph("<b>Aspek</b>", styles["small"]),
        Paragraph("<b>Nilai diri (1-5)</b>", styles["small"]),
        Paragraph("<b>Bukti / catatan</b>", styles["small"]),
    ]]
    for aspek in [
        "Memahami penjelasan bab",
        "Menjalankan contoh Mudah",
        "Menjalankan contoh Sedang",
        "Menjalankan contoh Sulit",
        "Mengisi kuis mandiri",
        "Menyelesaikan proyek mini",
        "Menjelaskan ke teman",
        "Siap materi berikutnya",
    ]:
        eval_rows.append([
            Paragraph(aspek, styles["small"]),
            Paragraph("1  2  3  4  5", styles["tips"]),
            Paragraph("................................", styles["tips"]),
        ])
    eval_tbl = Table(eval_rows, colWidths=[6.5 * cm, 4 * cm, 6.5 * cm])
    eval_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CARD, SOFT]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(eval_tbl)

    # --- Kuis padat ---
    story.append(Paragraph("Kuis Pemahaman (kerjakan dulu, kunci di belakang)", styles["h1"]))
    story.append(Paragraph(
        "Tulis jawaban singkat di kolom kanan. Jangan membuka kunci sebelum selesai mencoba.",
        styles["body"],
    ))
    kuis_rows = []
    for s in soal:
        kuis_rows.append([
            Paragraph(f"<b>{s['n']}.</b> {s['q']}", styles["small"]),
            Paragraph("Jawaban: ........................", styles["tips"]),
        ])
    kuis_tbl = Table(kuis_rows, colWidths=[11.2 * cm, 5.8 * cm])
    kuis_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), CARD),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CARD, SOFT]),
    ]))
    story.append(kuis_tbl)

    # --- Proyek + lembar kerja padat ---
    story.append(Paragraph(proy["judul"], styles["h1"]))
    story.append(DrawingFlowable(
        gambar_game() if ("Game" in modul["judul"] or modul.get("ikon") == "game") else gambar_oop_3d()
    ))
    story.append(Paragraph(proy["brief"], styles["body"]))
    syarat_txt = "<br/>".join(f"{i}. {s}" for i, s in enumerate(proy["syarat"], 1))
    rubrik_txt = " · ".join(f"{n} ({b})" for n, b in proy["rubrik"])
    story.append(_kotak_info(styles, "Syarat wajib", syarat_txt))
    story.append(_kotak_info(styles, "Rubrik", rubrik_txt))

    story.append(Paragraph("Lembar Kerja Proyek Mini", styles["h2"]))
    identitas = Table(
        [[
            Paragraph("Nama: ........................", styles["small"]),
            Paragraph("Kelas: ............", styles["small"]),
            Paragraph("Tanggal: ............", styles["small"]),
        ]],
        colWidths=[7 * cm, 5 * cm, 5 * cm],
    )
    identitas.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(identitas)
    story.append(Paragraph("Judul program: .........................................................................", styles["small"]))
    story.append(Paragraph("Tujuan: .................................................................................", styles["small"]))
    # area kode sebagai kotak bergaris (lebih rapi dari banyak underscore longgar)
    garis = [[Paragraph(f"{i+1:>2} |", styles["tips"]), Paragraph("." * 70, styles["tips"])] for i in range(10)]
    area_kode = Table(garis, colWidths=[1.2 * cm, 15.8 * cm])
    area_kode.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, TEAL),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE),
        ("BACKGROUND", (0, 0), (0, -1), SOFT),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(Paragraph("Cuplikan kode", styles["h2"]))
    story.append(area_kode)
    story.append(Paragraph("Output:", styles["h2"]))
    out_box = Table(
        [[Paragraph("." * 85, styles["tips"])] for _ in range(3)],
        colWidths=[17 * cm],
    )
    out_box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), CARD),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(out_box)

    # --- Glosarium 2 kolom ---
    story.append(Paragraph("Glosarium Koding", styles["h1"]))
    gloss = glosarium(modul)
    g_rows = []
    for i in range(0, len(gloss), 2):
        kiri = gloss[i]
        kanan = gloss[i + 1] if i + 1 < len(gloss) else ("", "")
        g_rows.append([
            Paragraph(f"<b>{kiri[0]}</b> — {kiri[1]}", styles["small"]),
            Paragraph(f"<b>{kanan[0]}</b> — {kanan[1]}" if kanan[0] else "", styles["small"]),
        ])
    g_tbl = Table(g_rows, colWidths=[8.5 * cm, 8.5 * cm])
    g_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CARD, SOFT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(g_tbl)

    # --- Kunci kuis padat ---
    story.append(Paragraph("Kunci Kuis (buka setelah mencoba)", styles["h1"]))
    kunci_rows = []
    for i in range(0, len(soal), 2):
        a = soal[i]
        b = soal[i + 1] if i + 1 < len(soal) else None
        kunci_rows.append([
            Paragraph(f"<b>{a['n']}.</b> {a['a']}", styles["small"]),
            Paragraph(f"<b>{b['n']}.</b> {b['a']}" if b else "", styles["small"]),
        ])
    kunci_tbl = Table(kunci_rows, colWidths=[8.5 * cm, 8.5 * cm])
    kunci_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(kunci_tbl)

    # --- Refleksi + sertifikat padat ---
    story.append(Paragraph("Refleksi & Tantangan Akhir", styles["h1"]))
    refleksi = [
        "1. Hal paling berkesan: .....................................................................",
        "2. Bagian yang masih sulit: ................................................................",
        "3. Contoh yang berhasil dimodifikasi: ......................................................",
        "4. Pertanyaan untuk guru: ..................................................................",
        "5. Target minggu depan: ....................................................................",
    ]
    for r in refleksi:
        story.append(Paragraph(r, styles["small"]))
    story.append(Spacer(1, 4))
    story.append(_kotak_info(
        styles,
        "Sertifikat Partisipasi",
        f"Dinyatakan bahwa <b>________________________</b> telah mempelajari «{modul['judul']}» "
        f"Kelas {tingkat} dan mengerjakan latihan modul.<br/>"
        "Tanda tangan murid: _____________ &nbsp;&nbsp; Guru: _____________",
    ))
    story.append(Spacer(1, 4))
    story.append(DrawingFlowable(gambar_sampul(tingkat, "Modul selesai — lanjut praktik!")))
    story.append(Paragraph(
        "Semangat belajar koding. Satu langkah kecil setiap hari lebih baik daripada menunda.",
        styles["muted"],
    ))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buf.seek(0)
    return buf


def path_cache_modul(kode: str, folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{kode}.pdf"


def pastikan_pdf(kode: str, folder: Path, *, paksa: bool = False) -> Path | None:
    modul = cari_modul(kode)
    if not modul:
        return None
    path = path_cache_modul(kode, folder)
    if path.is_file() and not paksa:
        return path
    bio = buat_pdf_modul(modul)
    path.write_bytes(bio.read())
    return path


def generate_semua(folder: Path, tingkat: str | None = None) -> list[Path]:
    hasil = []
    items = daftar_modul(tingkat) if tingkat else []
    if not tingkat:
        from koding.modul_katalog import semua_modul

        items = semua_modul()
    for m in items:
        p = pastikan_pdf(m["kode"], folder, paksa=True)
        if p:
            hasil.append(p)
    return hasil
