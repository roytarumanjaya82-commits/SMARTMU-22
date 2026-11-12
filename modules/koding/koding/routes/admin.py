from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    abort,
)
from koding import db
from koding.auth_utils import guru_required, hash_password
from koding.excel_siswa import buat_blanko_excel, baca_excel_siswa
from koding.config import JENIS_UJIAN, Config
from koding.tingkat_utils import TINGKAT_VALID, tingkat_dari_nama_kelas
from koding.pdf_login_siswa import buat_pdf_login_siswa
from koding.materi_upload import (
    validate_materi_file,
    save_materi_file,
    delete_materi_file,
    absolute_materi_path,
    ext_label,
)

PASSWORD_AWAL_SISWA = "123456"

bp = Blueprint("admin", __name__)


@bp.route("/")
@guru_required
def dashboard():
    stats = {
        "kelas": db.query("SELECT COUNT(*) AS n FROM kelas", one=True)["n"],
        "siswa": db.query("SELECT COUNT(*) AS n FROM siswa", one=True)["n"],
        "materi": db.query("SELECT COUNT(*) AS n FROM materi WHERE aktif=1", one=True)["n"],
        "ujian": db.query("SELECT COUNT(*) AS n FROM ujian WHERE aktif=1", one=True)["n"],
        "nilai": db.query("SELECT COUNT(*) AS n FROM nilai", one=True)["n"],
    }
    recent = db.query(
        """
        SELECT n.skor, n.jenis, n.dinilai_at, s.nama_siswa, u.judul, k.nama_kelas
        FROM nilai n
        JOIN siswa s ON s.id=n.siswa_id
        JOIN ujian u ON u.id=n.ujian_id
        JOIN kelas k ON k.id=s.kelas_id
        ORDER BY n.dinilai_at DESC LIMIT 8
        """
    )
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


@bp.route("/kelas", methods=["GET", "POST"])
@guru_required
def kelas():
    if request.method == "POST":
        nama = request.form.get("nama_kelas", "").strip()
        tahun = request.form.get("tahun_ajaran", "2026/2027").strip()
        semester = request.form.get("semester", "Ganjil")
        tingkat = request.form.get("tingkat") or tingkat_dari_nama_kelas(nama)
        if tingkat not in TINGKAT_VALID:
            tingkat = tingkat_dari_nama_kelas(nama)
        if not nama:
            flash("Nama kelas wajib diisi.", "danger")
        else:
            try:
                db.execute(
                    """
                    INSERT INTO kelas (nama_kelas, tingkat, tahun_ajaran, semester)
                    VALUES (%s,%s,%s,%s)
                    """,
                    (nama, tingkat, tahun, semester),
                )
                flash("Kelas berhasil ditambahkan.", "success")
            except Exception as e:
                flash(f"Gagal menambah kelas: {e}", "danger")
        return redirect(url_for("admin.kelas"))

    data = db.query(
        """
        SELECT k.*, COUNT(s.id) AS jumlah_siswa
        FROM kelas k
        LEFT JOIN siswa s ON s.kelas_id=k.id
        GROUP BY k.id
        ORDER BY k.nama_kelas
        """
    )
    return render_template("admin/kelas.html", data=data)


@bp.route("/kelas/<int:kelas_id>/hapus", methods=["POST"])
@guru_required
def hapus_kelas(kelas_id):
    db.execute("DELETE FROM kelas WHERE id=%s", (kelas_id,))
    flash("Kelas dihapus.", "info")
    return redirect(url_for("admin.kelas"))


@bp.route("/siswa")
@guru_required
def siswa():
    kelas_id = request.args.get("kelas_id", type=int)
    kelas_list = db.query("SELECT * FROM kelas ORDER BY nama_kelas")
    if not kelas_id and kelas_list:
        kelas_id = kelas_list[0]["id"]
    siswa_list = []
    if kelas_id:
        siswa_list = db.query(
            """
            SELECT s.*, u.username
            FROM siswa s
            LEFT JOIN users u ON u.id=s.user_id
            WHERE s.kelas_id=%s
            ORDER BY s.nama_siswa
            """,
            (kelas_id,),
        )
    return render_template(
        "admin/siswa.html",
        kelas_list=kelas_list,
        siswa_list=siswa_list,
        kelas_id=kelas_id,
    )


@bp.route("/siswa/blanko")
@guru_required
def blanko_siswa():
    kelas_id = request.args.get("kelas_id", type=int)
    nama = "7.5"
    if kelas_id:
        k = db.query("SELECT nama_kelas FROM kelas WHERE id=%s", (kelas_id,), one=True)
        if k:
            nama = k["nama_kelas"]
    bio = buat_blanko_excel(nama)
    return send_file(
        bio,
        as_attachment=True,
        download_name=f"blanko_siswa_{nama.replace(' ', '_')}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/siswa/impor", methods=["POST"])
@guru_required
def impor_siswa():
    kelas_id = request.form.get("kelas_id", type=int)
    file = request.files.get("file_excel")
    if not kelas_id or not file or not file.filename:
        flash("Pilih kelas dan file Excel.", "danger")
        return redirect(url_for("admin.siswa", kelas_id=kelas_id))

    try:
        rows = baca_excel_siswa(file)
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("admin.siswa", kelas_id=kelas_id))

    sukses, gagal = 0, 0
    for row in rows:
        try:
            existing_user = db.query(
                "SELECT id FROM users WHERE username=%s", (row["username"],), one=True
            )
            if existing_user:
                user_id = existing_user["id"]
            else:
                user_id, _ = db.execute(
                    """
                    INSERT INTO users (username, password_hash, nama_lengkap, role)
                    VALUES (%s,%s,%s,'siswa')
                    """,
                    (row["username"], hash_password(row["password"]), row["nama_siswa"]),
                )

            existing_siswa = db.query(
                "SELECT id FROM siswa WHERE kelas_id=%s AND nis=%s",
                (kelas_id, row["nis"]),
                one=True,
            )
            if existing_siswa:
                db.execute(
                    """
                    UPDATE siswa SET nama_siswa=%s, jenis_kelamin=%s, user_id=%s
                    WHERE id=%s
                    """,
                    (row["nama_siswa"], row["jenis_kelamin"], user_id, existing_siswa["id"]),
                )
            else:
                db.execute(
                    """
                    INSERT INTO siswa (user_id, kelas_id, nis, nama_siswa, jenis_kelamin)
                    VALUES (%s,%s,%s,%s,%s)
                    """,
                    (
                        user_id,
                        kelas_id,
                        row["nis"],
                        row["nama_siswa"],
                        row["jenis_kelamin"],
                    ),
                )
            sukses += 1
        except Exception:
            gagal += 1

    flash(f"Impor selesai. Berhasil: {sukses}, gagal: {gagal}.", "success" if sukses else "danger")
    return redirect(url_for("admin.siswa", kelas_id=kelas_id))


@bp.route("/siswa/<int:siswa_id>/hapus", methods=["POST"])
@guru_required
def hapus_siswa(siswa_id):
    s = db.query("SELECT user_id, kelas_id FROM siswa WHERE id=%s", (siswa_id,), one=True)
    if s:
        db.execute("DELETE FROM siswa WHERE id=%s", (siswa_id,))
        if s["user_id"]:
            masih = db.query(
                "SELECT id FROM siswa WHERE user_id=%s", (s["user_id"],), one=True
            )
            if not masih:
                db.execute(
                    "DELETE FROM users WHERE id=%s AND role='siswa'", (s["user_id"],)
                )
        flash("Siswa dihapus.", "info")
        return redirect(url_for("admin.siswa", kelas_id=s["kelas_id"]))
    return redirect(url_for("admin.siswa"))


@bp.route("/siswa/cetak-pdf")
@guru_required
def cetak_pdf_siswa():
    """Cetak PDF daftar + kartu login siswa terdaftar per kelas."""
    kelas_id = request.args.get("kelas_id", type=int)
    reset_pw = request.args.get("reset", type=int) == 1
    if not kelas_id:
        flash("Pilih kelas terlebih dahulu.", "danger")
        return redirect(url_for("admin.siswa"))

    kelas = db.query("SELECT * FROM kelas WHERE id=%s", (kelas_id,), one=True)
    if not kelas:
        flash("Kelas tidak ditemukan.", "danger")
        return redirect(url_for("admin.siswa"))

    siswa_list = db.query(
        """
        SELECT s.nis, s.nama_siswa, s.jenis_kelamin, s.user_id, u.username
        FROM siswa s
        LEFT JOIN users u ON u.id=s.user_id
        WHERE s.kelas_id=%s
        ORDER BY s.nama_siswa
        """,
        (kelas_id,),
    )
    if not siswa_list:
        flash("Belum ada siswa terdaftar di kelas ini.", "warning")
        return redirect(url_for("admin.siswa", kelas_id=kelas_id))

    if reset_pw:
        pw_hash = hash_password(PASSWORD_AWAL_SISWA)
        for s in siswa_list:
            if s.get("user_id"):
                db.execute(
                    "UPDATE users SET password_hash=%s WHERE id=%s AND role='siswa'",
                    (pw_hash, s["user_id"]),
                )

    rows = []
    for s in siswa_list:
        rows.append(
            {
                "nis": s.get("nis"),
                "nama_siswa": s.get("nama_siswa"),
                "username": s.get("username") or s.get("nis"),
                "password": PASSWORD_AWAL_SISWA,
            }
        )

    login_url = (Config.APP_BASE_URL or "").strip()
    if login_url:
        login_url = login_url.rstrip("/") + url_for("auth.login")
    else:
        login_url = request.url_root.rstrip("/") + url_for("auth.login")

    bio = buat_pdf_login_siswa(
        kelas["nama_kelas"],
        rows,
        login_url=login_url,
        password_default=PASSWORD_AWAL_SISWA,
    )
    safe_kelas = str(kelas["nama_kelas"]).replace(" ", "_")
    return send_file(
        bio,
        as_attachment=True,
        download_name=f"login_siswa_{safe_kelas}.pdf",
        mimetype="application/pdf",
    )


@bp.route("/materi", methods=["GET", "POST"])
@guru_required
def materi():
    if request.method == "POST":
        judul = request.form.get("judul", "").strip()
        ringkasan = request.form.get("ringkasan", "").strip()
        tingkat = request.form.get("tingkat", "7")
        semester = request.form.get("semester", "Ganjil")
        urutan = request.form.get("urutan", type=int) or 1
        isi_html = request.form.get("isi_html", "").strip()
        file_storage = request.files.get("berkas")

        if tingkat not in TINGKAT_VALID:
            tingkat = "7"
        if semester not in ("Ganjil", "Genap"):
            semester = "Ganjil"
        if not judul:
            flash("Judul materi wajib diisi.", "danger")
            return redirect(url_for("admin.materi", tingkat=tingkat, semester=semester))

        meta, err = validate_materi_file(file_storage)
        if err:
            flash(err, "danger")
            return redirect(url_for("admin.materi", tingkat=tingkat, semester=semester))

        rel_path = save_materi_file(file_storage, tingkat, meta)
        if not isi_html:
            isi_html = (
                f"<p>Materi unggahan ({ext_label(meta['tipe'])}). "
                "Unduh berkas untuk mempelajari isi lengkapnya.</p>"
            )
        try:
            db.execute(
                """
                INSERT INTO materi
                  (tingkat, urutan, semester, judul, ringkasan, isi_html,
                   file_nama, file_path, file_tipe, file_ukuran, aktif)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)
                """,
                (
                    tingkat,
                    urutan,
                    semester,
                    judul,
                    ringkasan or None,
                    isi_html,
                    meta["original"],
                    rel_path,
                    meta["tipe"],
                    meta["ukuran"],
                ),
            )
            flash(
                f"Materi kelas {tingkat} ({ext_label(meta['tipe'])}) berhasil diunggah.",
                "success",
            )
        except Exception as e:
            delete_materi_file(rel_path)
            flash(f"Gagal menyimpan materi: {e}", "danger")
        return redirect(url_for("admin.materi", tingkat=tingkat, semester=semester))

    semester = request.args.get("semester", "Semua")
    tingkat = request.args.get("tingkat", "Semua")
    sql = "SELECT * FROM materi WHERE 1=1"
    args = []
    if semester in ("Ganjil", "Genap"):
        sql += " AND semester=%s"
        args.append(semester)
    else:
        semester = "Semua"
    if tingkat in TINGKAT_VALID:
        sql += " AND tingkat=%s"
        args.append(tingkat)
    else:
        tingkat = "Semua"
    sql += " ORDER BY tingkat, FIELD(semester,'Ganjil','Genap'), urutan, id"
    data = db.query(sql, tuple(args) if args else None)
    return render_template(
        "admin/materi.html",
        data=data,
        semester=semester,
        tingkat=tingkat,
        ext_label=ext_label,
    )


@bp.route("/materi/<int:materi_id>")
@guru_required
def materi_detail(materi_id):
    item = db.query("SELECT * FROM materi WHERE id=%s", (materi_id,), one=True)
    if not item:
        flash("Materi tidak ditemukan.", "danger")
        return redirect(url_for("admin.materi"))
    return render_template(
        "admin/materi_detail.html", item=item, ext_label=ext_label
    )


@bp.route("/materi/<int:materi_id>/upload", methods=["POST"])
@guru_required
def materi_upload_berkas(materi_id):
    item = db.query("SELECT * FROM materi WHERE id=%s", (materi_id,), one=True)
    if not item:
        flash("Materi tidak ditemukan.", "danger")
        return redirect(url_for("admin.materi"))

    file_storage = request.files.get("berkas")
    meta, err = validate_materi_file(file_storage)
    if err:
        flash(err, "danger")
        return redirect(url_for("admin.materi_detail", materi_id=materi_id))

    rel_path = save_materi_file(file_storage, item["tingkat"], meta)
    old_path = item.get("file_path")
    try:
        db.execute(
            """
            UPDATE materi
            SET file_nama=%s, file_path=%s, file_tipe=%s, file_ukuran=%s
            WHERE id=%s
            """,
            (
                meta["original"],
                rel_path,
                meta["tipe"],
                meta["ukuran"],
                materi_id,
            ),
        )
        delete_materi_file(old_path)
        flash(f"Berkas {ext_label(meta['tipe'])} berhasil dilampirkan.", "success")
    except Exception as e:
        delete_materi_file(rel_path)
        flash(f"Gagal menyimpan berkas: {e}", "danger")
    return redirect(url_for("admin.materi_detail", materi_id=materi_id))


@bp.route("/materi/<int:materi_id>/unduh")
@guru_required
def materi_unduh(materi_id):
    item = db.query("SELECT * FROM materi WHERE id=%s", (materi_id,), one=True)
    if not item or not item.get("file_path"):
        abort(404)
    path = absolute_materi_path(item["file_path"])
    if not path.is_file():
        flash("Berkas tidak ditemukan di server.", "danger")
        return redirect(url_for("admin.materi_detail", materi_id=materi_id))
    return send_file(
        path,
        as_attachment=True,
        download_name=item.get("file_nama") or path.name,
    )


@bp.route("/materi/<int:materi_id>/hapus-berkas", methods=["POST"])
@guru_required
def materi_hapus_berkas(materi_id):
    item = db.query("SELECT * FROM materi WHERE id=%s", (materi_id,), one=True)
    if not item:
        flash("Materi tidak ditemukan.", "danger")
        return redirect(url_for("admin.materi"))
    delete_materi_file(item.get("file_path"))
    db.execute(
        """
        UPDATE materi
        SET file_nama=NULL, file_path=NULL, file_tipe=NULL, file_ukuran=NULL
        WHERE id=%s
        """,
        (materi_id,),
    )
    flash("Berkas materi dihapus.", "info")
    return redirect(url_for("admin.materi_detail", materi_id=materi_id))


@bp.route("/materi/<int:materi_id>/hapus", methods=["POST"])
@guru_required
def materi_hapus(materi_id):
    item = db.query("SELECT * FROM materi WHERE id=%s", (materi_id,), one=True)
    if not item:
        flash("Materi tidak ditemukan.", "danger")
        return redirect(url_for("admin.materi"))
    delete_materi_file(item.get("file_path"))
    db.execute("DELETE FROM materi WHERE id=%s", (materi_id,))
    flash("Materi dihapus.", "info")
    return redirect(
        url_for(
            "admin.materi",
            tingkat=item.get("tingkat"),
            semester=item.get("semester"),
        )
    )


@bp.route("/ujian")
@guru_required
def ujian():
    jenis = request.args.get("jenis")
    tingkat = request.args.get("tingkat", "Semua")
    where = ["1=1"]
    args = []
    if jenis:
        where.append("u.jenis=%s")
        args.append(jenis)
    if tingkat in TINGKAT_VALID:
        where.append("u.tingkat=%s")
        args.append(tingkat)
    else:
        tingkat = "Semua"
    data = db.query(
        f"""
        SELECT u.*, m.judul AS materi_judul,
               (SELECT COUNT(*) FROM soal s WHERE s.ujian_id=u.id) AS total_soal
        FROM ujian u
        LEFT JOIN materi m ON m.id=u.materi_id
        WHERE {' AND '.join(where)}
        ORDER BY u.tingkat, FIELD(u.jenis,'latihan','ulangan_harian','sumatif','sts_ganjil','sts_genap','sas'), u.id
        """,
        tuple(args) if args else None,
    )
    return render_template(
        "admin/ujian.html",
        data=data,
        jenis=jenis,
        tingkat=tingkat,
        jenis_map=JENIS_UJIAN,
    )


@bp.route("/ujian/<int:ujian_id>")
@guru_required
def ujian_detail(ujian_id):
    item = db.query(
        """
        SELECT u.*, m.judul AS materi_judul
        FROM ujian u LEFT JOIN materi m ON m.id=u.materi_id
        WHERE u.id=%s
        """,
        (ujian_id,),
        one=True,
    )
    if not item:
        flash("Ujian tidak ditemukan.", "danger")
        return redirect(url_for("admin.ujian"))
    soal = db.query("SELECT * FROM soal WHERE ujian_id=%s ORDER BY nomor, id", (ujian_id,))
    return render_template("admin/ujian_detail.html", item=item, soal=soal, jenis_map=JENIS_UJIAN)


@bp.route("/ujian/<int:ujian_id>/toggle-aktif", methods=["POST"])
@guru_required
def ujian_toggle_aktif(ujian_id):
    item = db.query("SELECT id, aktif, judul FROM ujian WHERE id=%s", (ujian_id,), one=True)
    if not item:
        flash("Ujian tidak ditemukan.", "danger")
        return redirect(url_for("admin.ujian"))
    new_aktif = 0 if item["aktif"] else 1
    db.execute("UPDATE ujian SET aktif=%s WHERE id=%s", (new_aktif, ujian_id))
    status = "diaktifkan" if new_aktif else "dinonaktifkan"
    flash(f"Ujian «{item['judul']}» {status}.", "success")
    nxt = request.form.get("next") or request.args.get("next")
    if nxt == "detail":
        return redirect(url_for("admin.ujian_detail", ujian_id=ujian_id))
    return redirect(
        url_for(
            "admin.ujian",
            jenis=request.form.get("jenis") or None,
            tingkat=request.form.get("tingkat") or None,
        )
    )

