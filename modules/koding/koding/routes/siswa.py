import random
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file,
    abort,
)
from koding import db
from koding.auth_utils import siswa_required
from koding.config import JENIS_UJIAN
from koding.tingkat_utils import resolve_tingkat
from koding.materi_upload import absolute_materi_path, ext_label

bp = Blueprint("siswa", __name__)


def _tingkat():
    # Murid hanya melihat materi/ujian sesuai tingkat kelasnya sendiri.
    return resolve_tingkat(session.get("tingkat"), None, "7")


def _semester(default="Ganjil"):
    semester = request.args.get("semester", default)
    return semester if semester in ("Ganjil", "Genap") else default


@bp.route("/")
@siswa_required
def dashboard():
    siswa_id = session["siswa_id"]
    tingkat = _tingkat()
    materi = db.query(
        """
        SELECT id, urutan, semester, tingkat, judul, ringkasan, file_tipe
        FROM materi WHERE aktif=1 AND tingkat=%s
        ORDER BY FIELD(semester,'Ganjil','Genap'), urutan
        """,
        (tingkat,),
    )
    ujian = db.query(
        """
        SELECT u.id, u.judul, u.jenis, u.durasi_menit, u.nilai_kkm, u.semester,
               n.skor AS skor_terakhir
        FROM ujian u
        LEFT JOIN nilai n ON n.ujian_id=u.id AND n.siswa_id=%s
        WHERE u.aktif=1 AND u.tingkat=%s
        ORDER BY FIELD(u.jenis,'latihan','ulangan_harian','sumatif','sts_ganjil','sts_genap','sas'), u.id
        """,
        (siswa_id, tingkat),
    )
    ringkas = db.query(
        """
        SELECT n.jenis, ROUND(AVG(n.skor),1) AS rata, COUNT(*) AS jumlah
        FROM nilai n
        JOIN ujian u ON u.id=n.ujian_id
        WHERE n.siswa_id=%s AND u.tingkat=%s
        GROUP BY n.jenis
        """,
        (siswa_id, tingkat),
    )
    return render_template(
        "siswa/dashboard.html",
        materi=materi,
        ujian=ujian,
        ringkas=ringkas,
        jenis_map=JENIS_UJIAN,
        tingkat=tingkat,
    )


@bp.route("/materi")
@siswa_required
def materi_list():
    semester = _semester("Ganjil")
    tingkat = _tingkat()
    data = db.query(
        """
        SELECT id, urutan, semester, tingkat, judul, ringkasan,
               file_nama, file_tipe, file_ukuran
        FROM materi WHERE aktif=1 AND semester=%s AND tingkat=%s
        ORDER BY urutan
        """,
        (semester, tingkat),
    )
    return render_template(
        "siswa/materi_list.html",
        data=data,
        semester=semester,
        tingkat=tingkat,
        ext_label=ext_label,
    )


@bp.route("/materi/<int:materi_id>")
@siswa_required
def materi_detail(materi_id):
    item = db.query(
        "SELECT * FROM materi WHERE id=%s AND aktif=1", (materi_id,), one=True
    )
    if not item:
        flash("Materi tidak ditemukan.", "danger")
        return redirect(url_for("siswa.materi_list"))
    if str(item.get("tingkat") or "7") != _tingkat():
        flash("Materi ini untuk tingkat kelas lain.", "warning")
        return redirect(url_for("siswa.materi_list"))
    semua = db.query(
        """
        SELECT id, urutan, judul, file_tipe FROM materi
        WHERE aktif=1 AND semester=%s AND tingkat=%s
        ORDER BY urutan
        """,
        (item.get("semester") or "Ganjil", item.get("tingkat") or "7"),
    )
    return render_template(
        "siswa/materi_detail.html",
        item=item,
        semua=semua,
        ext_label=ext_label,
    )


@bp.route("/materi/<int:materi_id>/unduh")
@siswa_required
def materi_unduh(materi_id):
    item = db.query(
        "SELECT * FROM materi WHERE id=%s AND aktif=1", (materi_id,), one=True
    )
    if not item or not item.get("file_path"):
        abort(404)
    if str(item.get("tingkat") or "7") != _tingkat():
        abort(404)
    path = absolute_materi_path(item["file_path"])
    if not path.is_file():
        flash("Berkas materi tidak ditemukan.", "danger")
        return redirect(url_for("siswa.materi_detail", materi_id=materi_id))
    return send_file(
        path,
        as_attachment=True,
        download_name=item.get("file_nama") or path.name,
    )


def _daftar_ujian(siswa_id, semester, tingkat, jenis_filter_sql, jenis_args=()):
    return db.query(
        f"""
        SELECT u.*, n.skor, n.percobaan_id AS hasil_id,
               (
                 SELECT p.id FROM percobaan_ujian p
                 WHERE p.ujian_id=u.id AND p.siswa_id=%s AND p.status='berlangsung'
                 ORDER BY p.id DESC LIMIT 1
               ) AS berlangsung_id
        FROM ujian u
        LEFT JOIN nilai n ON n.ujian_id=u.id AND n.siswa_id=%s
        WHERE u.aktif=1 AND u.semester=%s AND u.tingkat=%s
          AND {jenis_filter_sql}
        ORDER BY u.id
        """,
        (siswa_id, siswa_id, semester, tingkat) + tuple(jenis_args),
    )


@bp.route("/latihan")
@siswa_required
def latihan():
    semester = _semester("Ganjil")
    tingkat = _tingkat()
    data = _daftar_ujian(
        session["siswa_id"], semester, tingkat, "u.jenis='latihan'"
    )
    return render_template(
        "siswa/ujian_list.html",
        data=data,
        judul="Latihan Interaktif",
        jenis="latihan",
        semester=semester,
        tingkat=tingkat,
    )


@bp.route("/ulangan-harian")
@siswa_required
def ulangan_harian():
    semester = _semester("Ganjil")
    tingkat = _tingkat()
    data = _daftar_ujian(
        session["siswa_id"], semester, tingkat, "u.jenis='ulangan_harian'"
    )
    return render_template(
        "siswa/ujian_list.html",
        data=data,
        judul="Ulangan Harian",
        jenis="ulangan_harian",
        semester=semester,
        tingkat=tingkat,
    )


@bp.route("/asesmen")
@siswa_required
def asesmen():
    semester = _semester("Ganjil")
    tingkat = _tingkat()
    data = _daftar_ujian(
        session["siswa_id"],
        semester,
        tingkat,
        "u.jenis IN ('sumatif','sts_ganjil','sts_genap','sas')",
    )
    # urutkan jenis asesmen
    order = {"sumatif": 0, "sts_ganjil": 1, "sts_genap": 2, "sas": 3}
    data = sorted(data, key=lambda x: (order.get(x["jenis"], 9), x["id"]))
    return render_template(
        "siswa/ujian_list.html",
        data=data,
        judul="Asesmen Sumatif",
        jenis="asesmen",
        semester=semester,
        tingkat=tingkat,
    )


@bp.route("/ujian/<int:ujian_id>/mulai", methods=["POST"])
@siswa_required
def mulai_ujian(ujian_id):
    ujian = db.query("SELECT * FROM ujian WHERE id=%s AND aktif=1", (ujian_id,), one=True)
    if not ujian:
        flash("Ujian tidak tersedia.", "danger")
        return redirect(url_for("siswa.dashboard"))
    if str(ujian.get("tingkat") or "7") != _tingkat():
        flash("Kegiatan ini untuk tingkat kelas lain.", "warning")
        return redirect(url_for("siswa.dashboard"))

    siswa_id = session["siswa_id"]
    aktif = db.query(
        """
        SELECT id FROM percobaan_ujian
        WHERE ujian_id=%s AND siswa_id=%s AND status='berlangsung'
        ORDER BY id DESC LIMIT 1
        """,
        (ujian_id, siswa_id),
        one=True,
    )
    if aktif:
        return redirect(url_for("siswa.kerjakan", percobaan_id=aktif["id"]))

    # Sudah pernah selesai: siswa tidak boleh mengulang (hanya guru yang bisa reset)
    nilai = db.query(
        "SELECT id, percobaan_id FROM nilai WHERE siswa_id=%s AND ujian_id=%s",
        (siswa_id, ujian_id),
        one=True,
    )
    selesai = db.query(
        """
        SELECT id FROM percobaan_ujian
        WHERE siswa_id=%s AND ujian_id=%s AND status='selesai'
        ORDER BY id DESC LIMIT 1
        """,
        (siswa_id, ujian_id),
        one=True,
    )
    if nilai or selesai:
        flash(
            "Anda sudah mengerjakan kegiatan ini. Pengulangan hanya bisa diizinkan oleh guru (reset).",
            "warning",
        )
        hasil_id = (nilai or {}).get("percobaan_id") or (selesai or {}).get("id")
        if hasil_id:
            return redirect(url_for("siswa.hasil", percobaan_id=hasil_id))
        return redirect(url_for("siswa.dashboard"))

    perc_id, _ = db.execute(
        """
        INSERT INTO percobaan_ujian (ujian_id, siswa_id, mulai_at, status)
        VALUES (%s,%s,%s,'berlangsung')
        """,
        (ujian_id, siswa_id, datetime.now()),
    )
    return redirect(url_for("siswa.kerjakan", percobaan_id=perc_id))


@bp.route("/kerjakan/<int:percobaan_id>", methods=["GET", "POST"])
@siswa_required
def kerjakan(percobaan_id):
    perc = db.query(
        """
        SELECT p.*, u.judul, u.jenis, u.durasi_menit, u.tampil_pembahasan,
               u.acak_soal, u.jumlah_soal, u.nilai_kkm
        FROM percobaan_ujian p
        JOIN ujian u ON u.id=p.ujian_id
        WHERE p.id=%s AND p.siswa_id=%s
        """,
        (percobaan_id, session["siswa_id"]),
        one=True,
    )
    if not perc:
        flash("Percobaan tidak ditemukan.", "danger")
        return redirect(url_for("siswa.dashboard"))
    if perc["status"] == "selesai":
        return redirect(url_for("siswa.hasil", percobaan_id=percobaan_id))

    soal = db.query(
        """
        SELECT id, nomor, pertanyaan, opsi_a, opsi_b, opsi_c, opsi_d
        FROM soal
        WHERE ujian_id=%s
        ORDER BY nomor, id
        """,
        (perc["ujian_id"],),
    )
    if perc["acak_soal"]:
        random.Random(percobaan_id).shuffle(soal)
    if perc["jumlah_soal"] and len(soal) > perc["jumlah_soal"]:
        soal = soal[: perc["jumlah_soal"]]

    if request.method == "POST":
        benar = 0
        total = len(soal) or 1
        for s in soal:
            jawaban = request.form.get(f"soal_{s['id']}")
            kunci = db.query(
                "SELECT kunci_jawaban FROM soal WHERE id=%s", (s["id"],), one=True
            )["kunci_jawaban"]
            is_benar = 1 if jawaban and jawaban == kunci else 0
            if is_benar:
                benar += 1
            existing = db.query(
                "SELECT id FROM jawaban_siswa WHERE percobaan_id=%s AND soal_id=%s",
                (percobaan_id, s["id"]),
                one=True,
            )
            if existing:
                db.execute(
                    "UPDATE jawaban_siswa SET jawaban=%s, benar=%s WHERE id=%s",
                    (jawaban, is_benar, existing["id"]),
                )
            else:
                db.execute(
                    """
                    INSERT INTO jawaban_siswa (percobaan_id, soal_id, jawaban, benar)
                    VALUES (%s,%s,%s,%s)
                    """,
                    (percobaan_id, s["id"], jawaban, is_benar),
                )

        skor = round((benar / total) * 100, 2)
        db.execute(
            """
            UPDATE percobaan_ujian
            SET selesai_at=%s, skor=%s, status='selesai'
            WHERE id=%s
            """,
            (datetime.now(), skor, percobaan_id),
        )

        existing_nilai = db.query(
            "SELECT id FROM nilai WHERE siswa_id=%s AND ujian_id=%s",
            (session["siswa_id"], perc["ujian_id"]),
            one=True,
        )
        if existing_nilai:
            # Tidak menimpa nilai lama dari pengulangan ilegal
            db.execute(
                """
                UPDATE nilai SET skor=%s, percobaan_id=%s, dinilai_at=%s
                WHERE id=%s
                """,
                (skor, percobaan_id, datetime.now(), existing_nilai["id"]),
            )
        else:
            db.execute(
                """
                INSERT INTO nilai (siswa_id, ujian_id, jenis, skor, percobaan_id)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (session["siswa_id"], perc["ujian_id"], perc["jenis"], skor, percobaan_id),
            )

        flash(f"Ujian selesai. Skor Anda: {skor}", "success")
        return redirect(url_for("siswa.hasil", percobaan_id=percobaan_id))

    return render_template("siswa/kerjakan.html", perc=perc, soal=soal, jenis_map=JENIS_UJIAN)


@bp.route("/hasil/<int:percobaan_id>")
@siswa_required
def hasil(percobaan_id):
    perc = db.query(
        """
        SELECT p.*, u.judul, u.jenis, u.tampil_pembahasan, u.nilai_kkm
        FROM percobaan_ujian p
        JOIN ujian u ON u.id=p.ujian_id
        WHERE p.id=%s AND p.siswa_id=%s
        """,
        (percobaan_id, session["siswa_id"]),
        one=True,
    )
    if not perc:
        flash("Hasil tidak ditemukan.", "danger")
        return redirect(url_for("siswa.dashboard"))

    detail = db.query(
        """
        SELECT s.nomor, s.pertanyaan, s.opsi_a, s.opsi_b, s.opsi_c, s.opsi_d,
               s.kunci_jawaban, s.pembahasan, j.jawaban, j.benar
        FROM jawaban_siswa j
        JOIN soal s ON s.id=j.soal_id
        WHERE j.percobaan_id=%s
        ORDER BY s.nomor, s.id
        """,
        (percobaan_id,),
    )
    return render_template(
        "siswa/hasil.html", perc=perc, detail=detail, jenis_map=JENIS_UJIAN
    )


@bp.route("/nilaisaya")
@siswa_required
def nilai_saya():
    tingkat = _tingkat()
    data = db.query(
        """
        SELECT n.*, u.judul
        FROM nilai n JOIN ujian u ON u.id=n.ujian_id
        WHERE n.siswa_id=%s AND u.tingkat=%s
        ORDER BY FIELD(n.jenis,'latihan','ulangan_harian','sumatif','sts_ganjil','sts_genap','sas'), n.dinilai_at DESC
        """,
        (session["siswa_id"], tingkat),
    )
    return render_template(
        "siswa/nilai.html", data=data, jenis_map=JENIS_UJIAN, tingkat=tingkat
    )


def _folder_modul():
    from koding.config import Config

    folder = Config.BLANKO_FOLDER / "modul"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


@bp.route("/modul")
@siswa_required
def modul_list():
    from koding.modul_katalog import daftar_modul

    tingkat = _tingkat()
    modul = daftar_modul(tingkat)
    return render_template(
        "siswa/modul_list.html",
        modul=modul,
        tingkat=tingkat,
    )


@bp.route("/modul/<kode>/unduh")
@siswa_required
def modul_unduh(kode):
    from koding.modul_katalog import cari_modul
    from koding.modul_pdf import pastikan_pdf

    item = cari_modul(kode)
    if not item:
        abort(404)
    if str(item.get("tingkat")) != _tingkat():
        flash("Modul ini untuk kelas lain.", "warning")
        return redirect(url_for("siswa.modul_list"))
    path = pastikan_pdf(kode, _folder_modul())
    if not path or not path.is_file():
        flash("Gagal menyiapkan PDF modul.", "danger")
        return redirect(url_for("siswa.modul_list"))
    return send_file(
        path,
        as_attachment=True,
        download_name=f"{item['kode']}_{item['judul'][:40].replace(' ', '_')}.pdf",
        mimetype="application/pdf",
    )
