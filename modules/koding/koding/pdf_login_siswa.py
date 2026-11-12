"""Cetak PDF kartu login siswa terdaftar per kelas."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

LOGO_PATH = Path(__file__).resolve().parent / "static" / "img" / "logo-smpm22.png"
TEAL = colors.HexColor("#0F766E")
INK = colors.HexColor("#0F172A")
MUTED = colors.HexColor("#475569")
LINE = colors.HexColor("#CBD5E1")
CARD_BG = colors.HexColor("#F8FAFC")


def buat_pdf_login_siswa(
    nama_kelas: str,
    siswa_list: list[dict],
    *,
    login_url: str = "",
    password_default: str = "123456",
    sekolah: str = "SMP Muhammadiyah 22 Setiabudi Pamulang",
) -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.4 * cm,
        rightMargin=1.4 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
        title=f"Kartu Login Siswa - Kelas {nama_kelas}",
        author="Koding 7.5",
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleID",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=TEAL,
        alignment=TA_CENTER,
        spaceAfter=2,
        leading=20,
    )
    subtitle = ParagraphStyle(
        "SubID",
        parent=styles["Normal"],
        fontSize=10,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=13,
    )
    body = ParagraphStyle(
        "BodyID",
        parent=styles["Normal"],
        fontSize=9.5,
        textColor=INK,
        alignment=TA_LEFT,
        leading=13,
        spaceAfter=4,
    )
    card_title = ParagraphStyle(
        "CardTitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=TEAL,
        fontName="Helvetica-Bold",
        leading=12,
        alignment=TA_CENTER,
    )
    card_line = ParagraphStyle(
        "CardLine",
        parent=styles["Normal"],
        fontSize=9,
        textColor=INK,
        leading=12,
    )
    small = ParagraphStyle(
        "SmallID",
        parent=styles["Normal"],
        fontSize=8,
        textColor=MUTED,
        alignment=TA_CENTER,
        leading=11,
    )

    story = []

    header_bits = []
    if LOGO_PATH.exists():
        header_bits.append(Image(str(LOGO_PATH), width=1.6 * cm, height=1.6 * cm))
    header_bits.append(
        [
            Paragraph("Koding 7.5 — Kartu Login Siswa", title),
            Paragraph(sekolah, subtitle),
            Paragraph(f"Kelas <b>{nama_kelas}</b> · Total siswa: <b>{len(siswa_list)}</b>", subtitle),
        ]
    )
    if len(header_bits) == 2:
        head = Table(
            [[header_bits[0], header_bits[1]]],
            colWidths=[2.0 * cm, 15.5 * cm],
        )
        head.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(head)
    else:
        story.extend(header_bits[0])

    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.2, color=TEAL, spaceAfter=8))

    petunjuk = [
        "Gunakan data di bawah untuk masuk ke aplikasi pembelajaran Koding.",
        "Username biasanya sama dengan NIS. Password awal: <b>123456</b> "
        "(kecuali diubah saat impor Excel).",
    ]
    if login_url:
        petunjuk.append(f"Alamat login: <b>{login_url}</b>")
    for p in petunjuk:
        story.append(Paragraph(f"• {p}", body))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Daftar akun login</b>", body))
    story.append(Spacer(1, 4))

    table_data = [
        [
            Paragraph("<b>No</b>", small),
            Paragraph("<b>NIS</b>", small),
            Paragraph("<b>Nama Siswa</b>", small),
            Paragraph("<b>Username</b>", small),
            Paragraph("<b>Password</b>", small),
        ]
    ]
    for i, s in enumerate(siswa_list, start=1):
        username = s.get("username") or s.get("nis") or "-"
        password = s.get("password") or password_default
        table_data.append(
            [
                Paragraph(str(i), small),
                Paragraph(str(s.get("nis") or "-"), small),
                Paragraph(str(s.get("nama_siswa") or "-"), small),
                Paragraph(f"<b>{username}</b>", small),
                Paragraph(f"<b>{password}</b>", small),
            ]
        )

    col_w = [1.0 * cm, 2.6 * cm, 7.2 * cm, 3.6 * cm, 2.8 * cm]
    tbl = Table(table_data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (4, 1), (4, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CARD_BG]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(tbl)

    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Kartu potong (bagi ke siswa)</b>", body))
    story.append(
        Paragraph(
            "Potong tiap kotak. Setiap siswa menerima satu kartu login.",
            small,
        )
    )
    story.append(Spacer(1, 6))

    def _kartu(s):
        username = s.get("username") or s.get("nis") or "-"
        password = s.get("password") or password_default
        lines = [
            Paragraph("Koding 7.5 · Kartu Login", card_title),
            Paragraph(f"Kelas: <b>{nama_kelas}</b>", card_line),
            Paragraph(f"Nama: <b>{s.get('nama_siswa') or '-'}</b>", card_line),
            Paragraph(f"NIS: {s.get('nis') or '-'}", card_line),
            Paragraph(f"Username: <b>{username}</b>", card_line),
            Paragraph(f"Password: <b>{password}</b>", card_line),
        ]
        if login_url:
            lines.append(Paragraph(f"Login: {login_url}", small))
        return lines

    card_w = 8.6 * cm
    pair_rows = []
    for i in range(0, len(siswa_list), 2):
        left = _kartu(siswa_list[i])
        right = _kartu(siswa_list[i + 1]) if i + 1 < len(siswa_list) else [Paragraph("", card_line)]
        pair_rows.append([left, right])

    if pair_rows:
        card_grid = Table(pair_rows, colWidths=[card_w, card_w])
        card_grid.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("BOX", (0, 0), (0, -1), 0.8, TEAL),
                    ("BOX", (1, 0), (1, -1), 0.8, TEAL),
                    ("LINEBELOW", (0, 0), (-1, -2), 0.6, LINE),
                    ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(card_grid)

    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "Dokumen ini berisi kredensial login. Simpan dan bagikan hanya kepada siswa yang bersangkutan.",
            small,
        )
    )

    doc.build(story)
    buf.seek(0)
    return buf
