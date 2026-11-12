"""Seed kurikulum Kelas 9 (project-based) — Ganjil & Genap."""
import sys
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from koding.config import Config  # noqa: E402
from koding.kurikulum_kelas9 import MATERI_GANJIL, MATERI_GENAP  # noqa: E402

KKM = 77
TINGKAT = "9"


def Q(q, a, b, c, d, kunci, materi):
    return {
        "question": q,
        "options": {"A": a, "B": b, "C": c, "D": d},
        "answer": kunci,
        "materi": materi,
    }


SOAL_GANJIL = [
    Q("Kickoff project Kelas 9 terutama bertujuan...", "Langsung coding tanpa rencana", "Menentukan masalah, tujuan, dan fitur wajib", "Menghapus README", "Menonaktifkan validasi", "B", "Kickoff"),
    Q("MVP dalam project berarti...", "Semua fitur tanpa batas", "Fitur wajib paling penting agar project bisa dipakai", "Hanya dekorasi UI", "Database wajib cloud", "B", "Kickoff"),
    Q("Struktur folder project membantu...", "Menyembunyikan bug", "Organisasi berkas agar mudah dirawat", "Menghapus modul", "Mematikan JSON", "B", "Struktur"),
    Q("File models.py pada project biasanya berisi...", "Menu CLI saja", "Class/data model", "Password WiFi", "Gambar PNG", "B", "Struktur"),
    Q("Menu CLI project umumnya memakai...", "Infinite recursion tanpa base", "Loop utama + pemanggilan fungsi per pilihan", "Hanya print sekali", "Tanpa kondisi keluar", "B", "CLI"),
    Q("Pilihan 0 pada menu CLI biasanya untuk...", "Menambah data", "Keluar dari aplikasi", "Menghapus Python", "Membuat class", "B", "CLI"),
    Q("Modularisasi project memisahkan...", "Semua ke satu fungsi super", "Tanggung jawab antar file/modul", "Hanya komentar", "Hanya warna UI", "B", "Modul"),
    Q("main.py pada pola project sering berperan sebagai...", "Penyimpan JSON saja", "Pengatur alur/menu aplikasi", "Driver VGA", "File CSS", "B", "Modul"),
    Q("Service class dalam project dipakai untuk...", "Menyimpan password OS", "Mengelola operasi data (tambah, cari, rekap)", "Mengganti interpreter", "Mematikan assert", "B", "OOP"),
    Q("Keunggulan OOP pada project nyata...", "Data dan perilaku terkait tersusun rapi", "Wajib tanpa fungsi", "Tidak bisa dites", "Hanya untuk GUI", "A", "OOP"),
    Q("Persistensi JSON membuat data...", "Hilang tiap restart pasti", "Bisa dimuat lagi setelah program ditutup", "Menjadi gambar", "Tidak bisa di-debug", "B", "JSON"),
    Q("json.dumps pada project dipakai untuk...", "Membuka port 80", "Mengubah data Python menjadi teks JSON", "Menghapus class", "Sorting wajib", "B", "JSON"),
    Q("Validasi nilai 0–100 penting agar...", "Data rusak diterima", "Input tidak masuk akal ditolak", "Loop berhenti otomatis", "README terhapus", "B", "Validasi"),
    Q("try/except pada project terutama untuk...", "Mempercantik font", "Menangani error agar aplikasi tidak crash", "Mengganti KKM", "Menambah RAM", "B", "Validasi"),
    Q("assert pada testing mini memastikan...", "Kondisi penting benar saat uji", "UI selalu gelap", "File selalu kosong", "Route selalu 404", "A", "Testing"),
    Q("Kasus uji list kosong berguna untuk...", "Mengabaikan bug", "Memastikan fungsi aman saat tidak ada data", "Menghapus README", "Mematikan menu", "B", "Testing"),
    Q("README project minimal berisi...", "Hanya emoji", "Tujuan, cara menjalankan, dan fitur", "Password guru", "Source kernel", "B", "README"),
    Q("Deliverable showcase ganjil menekankan...", "Fitur tak terbatas tanpa demo", "MVP jalan + simpan data + README + demo", "Hanya screenshot palsu", "Tanpa menu", "B", "Showcase"),
    Q("Pemisahan storage.py bertujuan...", "Menyimpan detail baca/tulis terpisah dari menu", "Menghapus JSON", "Memaksa satu file", "Menonaktifkan class", "A", "Modul"),
    Q("Fitur wajib project sebaiknya...", "Ditulis setelah coding selesai saja", "Ditentukan di kickoff agar pengerjaan terarah", "Diabaikan", "Diganti dekorasi", "B", "Kickoff"),
    Q("Class NilaiService.rata() mengembalikan 0 jika data kosong agar...", "Error ZeroDivision tidak terjadi", "Nilai selalu 100", "JSON rusak", "Menu hilang", "A", "OOP"),
    Q("Mode append file berbeda dengan write karena...", "Append menambah di akhir, write menimpa", "Append menghapus disk", "Write hanya untuk gambar", "Keduanya identik selalu", "A", "JSON"),
    Q("Pesan error validasi yang baik bersifat...", "Kabur dan teknis saja", "Jelas bagi pengguna project", "Dalam bahasa mesin", "Tanpa teks", "B", "Validasi"),
    Q("Demo project 3–5 menit sebaiknya menampilkan...", "Semua kode baris demi baris", "Alur fitur utama yang berjalan", "Hanya struktur folder", "Log error saja", "B", "Showcase"),
    Q("Checklist showcase membantu...", "Memastikan kelengkapan sebelum presentasi", "Menghapus fitur wajib", "Menonaktifkan testing", "Menghindari README", "A", "Showcase"),
    Q("Project Kelas 9 disebut lanjutan Kelas 8 karena...", "Mengabaikan OOP/JSON", "Menerapkan bekal Kelas 8 ke produk utuh", "Hanya mengulang print hello", "Tanpa validasi", "B", "Kickoff"),
    Q("Field data project ditentukan agar...", "Tidak jelas apa yang disimpan", "Struktur record konsisten", "Wajib tanpa nama", "Hanya integer", "B", "Struktur"),
    Q("Loop menu tanpa opsi keluar berisiko...", "Infinite loop", "Otomatis selesai", "JSON terformat", "Class hilang", "A", "CLI"),
    Q("Pengujian sebelum demo termasuk...", "Best practice project", "Pemborosan waktu selalu", "Menghapus assert", "Menolak validasi", "A", "Testing"),
    Q("Dokumentasi membantu orang lain...", "Menjalankan dan memahami project", "Menghapus kode", "Mengganti OS", "Mematikan Python", "A", "README"),
    Q("MVP bukan berarti...", "Fitur wajib cukup untuk dipakai", "Semua ide harus masuk di versi pertama", "Ada tujuan jelas", "Bisa didemo", "B", "Kickoff"),
    Q("Penyimpanan data project paling sederhana di tahap awal sering memakai...", "JSON/file", "Superkomputer", "Assembly", "Tanpa data", "A", "JSON"),
    Q("Fungsi baca_nilai yang mengembalikan (None, pesan) menandakan...", "Validasi gagal", "Nilai sempurna", "File hilang wajib", "Class rusak", "A", "Validasi"),
    Q("all(checklist.values()) True artinya...", "Semua item checklist terpenuhi", "Semua gagal", "Tidak ada checklist", "Hanya satu True", "A", "Showcase"),
    Q("models.py dan storage.py dipisah agar...", "Perubahan penyimpanan tidak merusak model", "Lebih sulit dibaca", "Wajib satu class saja", "Tanpa fungsi", "A", "Modul"),
    Q("Project kickoff menulis pengguna target supaya...", "Fitur sesuai kebutuhan pemakai", "Kode lebih lambat", "JSON otomatis encrypt", "GUI wajib 3D", "A", "Kickoff"),
    Q("Testing mini fokus pada...", "Fungsi inti project", "Warna tombol saja", "Nama file acak", "Iklan", "A", "Testing"),
    Q("README yang baik mengurangi...", "Ketergantungan menjelaskan manual berulang", "Kemampuan coding", "Jumlah fitur", "KKM", "A", "README"),
    Q("Service class berbeda dari class data karena...", "Lebih fokus mengelola kumpulan operasi", "Tidak boleh punya method", "Wajib tanpa atribut", "Hanya untuk HTML", "A", "OOP"),
    Q("Hasil belajar utama semester ganjil Kelas 9 adalah...", "Project MVP yang terdokumentasi dan bisa didemo", "Hanya teori tanpa produk", "Hanya menghafal sintaks", "Tanpa validasi/simpan data", "A", "Showcase"),
]

SOAL_GENAP = [
    Q("Flask pada Kelas 9 dipakai untuk...", "Project web mini dengan Python", "Mengganti MySQL", "Menghapus OOP", "Mematikan JSON", "A", "Flask"),
    Q("Route / pada Flask biasanya menampilkan...", "Beranda project", "File BIOS", "Password root", "Driver printer", "A", "Flask"),
    Q("Banyak halaman project web berarti...", "Banyak route", "Satu print saja", "Tanpa template", "Tanpa data", "A", "Route"),
    Q("Template HTML pada project web berfungsi...", "Menampilkan data dari Python ke halaman", "Mengompilasi C++", "Menghapus session", "Menyimpan OS", "A", "Route"),
    Q("Lapisan Repo/storage memisahkan...", "Detail penyimpanan dari route/tampilan", "Semua ke satu file wajib", "Validasi dari bumi", "KKM dari rapor", "A", "Data"),
    Q("CRUD kepanjangan yang benar...", "Create Read Update Delete", "Copy Run Undo Draw", "Class Route User Data", "Cache RAM USB Disk", "A", "CRUD"),
    Q("Create pada CRUD berarti...", "Menambah data baru", "Menghapus semua", "Hanya membaca", "Logout", "A", "CRUD"),
    Q("Update berbeda dengan Create karena...", "Mengubah data yang sudah ada", "Selalu membuat id baru tanpa cek", "Menghapus database", "Menutup server", "A", "CRUD"),
    Q("Validasi form web menolak...", "Input kosong/tidak valid sebelum disimpan", "Semua input selalu", "Hanya angka genap", "README", "A", "Form"),
    Q("Pesan validasi yang baik...", "Mudah dipahami pengguna", "Selalu dalam hex", "Kosong", "Acak", "A", "Form"),
    Q("Laporan project biasanya menampilkan...", "Rata-rata, jumlah tuntas, ringkasan", "Hanya warna latar", "Password", "Source kernel", "A", "Laporan"),
    Q("Filter data membantu...", "Menemukan subset data sesuai kriteria", "Menghapus Python", "Mematikan CRUD", "Menyembunyikan README", "A", "Laporan"),
    Q("Session peran guru/siswa berguna untuk...", "Membatasi menu sesuai hak akses", "Mempercepat CPU 1000x", "Menghapus validasi", "Mengganti JSON jadi gambar", "A", "Akses"),
    Q("API JSON mini mengembalikan...", "Data terstruktur agar bisa dibaca aplikasi lain", "File exe", "Sinyal radio", "Password WiFi", "A", "API"),
    Q("json.dumps pada endpoint API menghasilkan...", "String JSON", "Object Tkinter", "Query SQL wajib", "Bitmap", "A", "API"),
    Q("Hardening project menjelang akhir berarti...", "Memperkuat penanganan error dan perbaikan bug", "Menghapus testing", "Menambah fitur tanpa uji", "Menonaktifkan README", "A", "Hardening"),
    Q("Capstone Kelas 9 menekankan...", "Project terpadu sesuai rubrik", "Hanya satu print hello", "Tanpa dokumentasi", "Tanpa data", "A", "Capstone"),
    Q("Rubrik capstone umumnya menilai...", "Berjalan, CRUD, simpan, laporan, README", "Hanya font", "Hanya warna", "Hanya nama file", "A", "Capstone"),
    Q("Delete pada CRUD harus...", "Menghapus data yang dipilih dengan aman", "Menghapus seluruh disk", "Menghapus Python", "Menghapus siswa dari sekolah fisik", "A", "CRUD"),
    Q("Repo.add lalu Repo.all menggambarkan...", "Create dan Read", "Hanya Delete", "Hanya CSS", "Hanya login OS", "A", "Data"),
    Q("Project web Kelas 9 adalah lanjutan CLI karena...", "Fitur data/validasi tetap, antarmuka naik ke web", "Semua konsep Kelas 8 dibuang", "Tidak perlu route", "Tidak perlu laporan", "A", "Flask"),
    Q("Dictionary halaman route -> judul membantu...", "Merancang navigasi project", "Menghapus template", "Mematikan Flask", "Menyembunyikan bug", "A", "Route"),
    Q("Validasi nilai non-angka harus...", "Mengembalikan pesan error", "Disimpan apa adanya", "Diubah jadi 100 diam-diam", "Crash tanpa pesan", "A", "Form"),
    Q("list comprehension untuk filter tuntas memakai...", "Syarat nilai >= KKM", "Hapus semua data", "Sort turun wajib", "JSON encrypt", "A", "Laporan"),
    Q("role pada session sebaiknya dicek sebelum...", "Membuka menu kelola", "Menutup laptop", "Install OS", "Cetak ASCII art", "A", "Akses"),
    Q("Payload API yang baik punya...", "Status/ringkas data jelas", "Password root", "File virus", "Random bytes saja", "A", "API"),
    Q("LOG_ERROR pada hardening membantu...", "Melacak jenis kesalahan", "Menghapus log disk", "Mematikan exception", "Menyembunyikan bug permanen", "A", "Hardening"),
    Q("Skor kelengkapan rubrik dihitung dari...", "Proporsi kriteria yang terpenuhi", "Panjang nama file", "Jumlah komentar saja", "Warna tombol", "A", "Capstone"),
    Q("Update nama siswa pada list dict membutuhkan...", "Menemukan record lalu mengubah field", "Membuat OS baru", "Menghapus Flask", "Menonaktifkan JSON", "A", "CRUD"),
    Q("Pemisahan route dan storage memudahkan...", "Ganti cara simpan tanpa ubah semua tampilan", "Menghapus semua route", "Menghindari validasi", "Menolak laporan", "A", "Data"),
    Q("Form kosong nama harus...", "Ditolak validasi", "Disimpan sebagai None tanpa pesan", "Diisi otomatis password", "Menutup server", "A", "Form"),
    Q("Jumlah tuntas dari list nilai memakai...", "Filter nilai >= 77 lalu len", "Hanya max(nilai)", "Hanya min(nilai)", "Random", "A", "Laporan"),
    Q("boleh_kelola(session) False untuk siswa artinya...", "Siswa tidak boleh menu kelola", "Siswa admin super", "Session rusak wajib", "JSON hilang", "A", "Akses"),
    Q("Endpoint JSON berbeda dari halaman HTML karena...", "Mengutamakan data terstruktur, bukan tampilan", "Tidak bisa memakai Python", "Wajib GUI Tkinter", "Wajib tanpa status", "A", "API"),
    Q("Menjelang capstone, prioritas bug adalah...", "Yang merusak fitur utama", "Yang hanya salah ketik README opsional", "Warna footer", "Nama variabel panjang", "A", "Hardening"),
    Q("Project terpadu Kelas 9 sebaiknya...", "Memakai validasi + simpan + laporan", "Hanya satu tombol kosong", "Tanpa README", "Tanpa uji", "A", "Capstone"),
    Q("Create tanpa Read membuat project...", "Sulit dipastikan data masuk", "Lebih sempurna", "Otomatis berlaporan", "Tanpa bug", "A", "CRUD"),
    Q("Flask mini di sekolah dijalankan biasanya di...", "Lokal/server latihan", "Satellite", "BIOS chip", "Printer saja", "A", "Flask"),
    Q("Template menerima data dari route agar...", "Halaman menampilkan informasi dinamis", "HTML tidak bisa ada", "Python berhenti", "JSON terhapus", "A", "Route"),
    Q("Hasil belajar genap Kelas 9 adalah...", "Project web/data terpadu siap demo dan dinilai rubrik", "Hanya teori Flask tanpa produk", "Hanya CLI tanpa kemajuan", "Tanpa dokumentasi", "A", "Capstone"),
]


def connect():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )


def ensure_schema(cur):
    for tabel in ("materi", "ujian", "kelas"):
        cur.execute(f"SHOW COLUMNS FROM {tabel} LIKE 'tingkat'")
        if not cur.fetchone():
            cur.execute(
                f"ALTER TABLE {tabel} ADD COLUMN tingkat ENUM('7','8','9') NOT NULL DEFAULT '7'"
            )
        else:
            cur.execute(
                f"ALTER TABLE {tabel} MODIFY tingkat ENUM('7','8','9') NOT NULL DEFAULT '7'"
            )
    cur.execute("UPDATE kelas SET tingkat='9' WHERE nama_kelas LIKE '9%' OR nama_kelas LIKE 'IX%'")
    cur.execute("UPDATE kelas SET tingkat='8' WHERE nama_kelas LIKE '8%' OR nama_kelas LIKE 'VIII%'")
    cur.execute("UPDATE kelas SET tingkat='7' WHERE nama_kelas LIKE '7%' OR nama_kelas LIKE 'VII%'")


def insert_materi(cur, items, semester):
    ids = []
    for m in items:
        cur.execute(
            """
            INSERT INTO materi (tingkat, urutan, semester, judul, ringkasan, isi_html, contoh_kode, aktif)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """,
            (TINGKAT, m["urutan"], semester, m["judul"], m["ringkasan"], m["isi_html"], m["contoh_kode"]),
        )
        ids.append(cur.lastrowid)
    return ids


def insert_ujian(cur, judul, deskripsi, jenis, semester, materi_id, soal_items, durasi, jumlah, pembahasan=1):
    cur.execute(
        "SELECT id FROM ujian WHERE tingkat=%s AND judul=%s AND semester=%s",
        (TINGKAT, judul, semester),
    )
    old = cur.fetchone()
    if old:
        cur.execute("DELETE FROM soal WHERE ujian_id=%s", (old["id"],))
        cur.execute("DELETE FROM ujian WHERE id=%s", (old["id"],))
    cur.execute(
        """
        INSERT INTO ujian
        (judul, deskripsi, jenis, semester, tingkat, materi_id, durasi_menit, jumlah_soal, nilai_kkm, acak_soal, tampil_pembahasan, aktif)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s,0)
        """,
        (judul, deskripsi, jenis, semester, TINGKAT, materi_id, durasi, jumlah, KKM, pembahasan),
    )
    uid = cur.lastrowid
    for i, q in enumerate(soal_items, start=1):
        cur.execute(
            """
            INSERT INTO soal
            (ujian_id, nomor, pertanyaan, opsi_a, opsi_b, opsi_c, opsi_d, kunci_jawaban, pembahasan, bobot, aktif)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1,0)
            """,
            (
                uid,
                i,
                q["question"],
                q["options"]["A"],
                q["options"]["B"],
                q["options"]["C"],
                q["options"]["D"],
                q["answer"],
                f"Materi terkait: {q.get('materi') or '-'}",
            ),
        )
    return uid


def seed_semester(cur, semester, materi_list, soal):
    ids = insert_materi(cur, materi_list, semester)
    prefix = f"K9 {semester}"
    chunks = [
        (0, soal[0:8], f"Latihan {prefix} 1"),
        (2, soal[6:14], f"Latihan {prefix} 2"),
        (4, soal[12:20], f"Latihan {prefix} 3"),
        (6, soal[18:28], f"Latihan {prefix} 4"),
        (8, soal[24:32], f"Latihan {prefix} 5"),
        (9, soal[32:40], f"Latihan {prefix} 6"),
    ]
    for idx, qs, judul in chunks:
        insert_ujian(
            cur,
            judul,
            f"Latihan project kelas 9 semester {semester.lower()}.",
            "latihan",
            semester,
            ids[idx],
            qs,
            25,
            len(qs),
            1,
        )
    insert_ujian(cur, f"UH {prefix} 1", "Ulangan harian 1 kelas 9.", "ulangan_harian", semester, ids[0], soal[0:12], 30, 12, 1)
    insert_ujian(cur, f"UH {prefix} 2", "Ulangan harian 2 kelas 9.", "ulangan_harian", semester, ids[3], soal[10:22], 30, 12, 1)
    insert_ujian(cur, f"UH {prefix} 3", "Ulangan harian 3 kelas 9.", "ulangan_harian", semester, ids[6], soal[20:32], 30, 12, 1)
    insert_ujian(cur, f"Sumatif {prefix}", "Sumatif project kelas 9.", "sumatif", semester, None, soal[0:20], 45, 20, 0)
    jenis_sts = "sts_ganjil" if semester == "Ganjil" else "sts_genap"
    insert_ujian(cur, f"STS {prefix}", f"Sumatif Tengah Semester {semester} kelas 9.", jenis_sts, semester, None, soal[0:25], 60, 25, 0)
    insert_ujian(cur, f"SAS {prefix}", f"Sumatif Akhir Semester {semester} kelas 9.", "sas", semester, None, soal, 90, 40, 0)


def ensure_kelas9(cur):
    cur.execute("SELECT id FROM kelas WHERE nama_kelas IN ('9.5', '9.1', '9.3') ORDER BY nama_kelas DESC LIMIT 1")
    row = cur.fetchone()
    if not row:
        cur.execute(
            """
            INSERT INTO kelas (nama_kelas, tingkat, tahun_ajaran, semester)
            VALUES ('9.5', '9', '2026/2027', 'Ganjil')
            """
        )
        kelas_id = cur.lastrowid
    else:
        kelas_id = row["id"]
        cur.execute("UPDATE kelas SET tingkat='9' WHERE id=%s", (kelas_id,))
    cur.execute("UPDATE kelas SET tingkat='9' WHERE nama_kelas LIKE '9%' OR nama_kelas LIKE 'IX%'")
    contoh = [
        ("2909001", "Kirana Putri", "P"),
        ("2909002", "Dimas Arya", "L"),
        ("2909003", "Salma Aurelia", "P"),
    ]
    for nis, nama, jk in contoh:
        cur.execute("SELECT id FROM users WHERE username=%s", (nis,))
        u = cur.fetchone()
        if u:
            uid = u["id"]
        else:
            cur.execute(
                """
                INSERT INTO users (username, password_hash, nama_lengkap, role)
                VALUES (%s,%s,%s,'siswa')
                """,
                (nis, generate_password_hash("123456"), nama),
            )
            uid = cur.lastrowid
        cur.execute("SELECT id FROM siswa WHERE kelas_id=%s AND nis=%s", (kelas_id, nis))
        if not cur.fetchone():
            cur.execute(
                """
                INSERT INTO siswa (user_id, kelas_id, nis, nama_siswa, jenis_kelamin)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (uid, kelas_id, nis, nama, jk),
            )
    return kelas_id


def main():
    conn = connect()
    try:
        with conn.cursor() as cur:
            ensure_schema(cur)
            cur.execute("SELECT id FROM materi WHERE tingkat=%s", (TINGKAT,))
            old_m = [r["id"] for r in cur.fetchall()]
            cur.execute("SELECT id FROM ujian WHERE tingkat=%s", (TINGKAT,))
            old_u = [r["id"] for r in cur.fetchall()]
            for uid in old_u:
                cur.execute("DELETE FROM soal WHERE ujian_id=%s", (uid,))
            if old_u:
                cur.execute(
                    "DELETE FROM ujian WHERE id IN (%s)" % ",".join(["%s"] * len(old_u)),
                    old_u,
                )
            if old_m:
                cur.execute(
                    "DELETE FROM materi WHERE id IN (%s)" % ",".join(["%s"] * len(old_m)),
                    old_m,
                )
            seed_semester(cur, "Ganjil", MATERI_GANJIL, SOAL_GANJIL)
            seed_semester(cur, "Genap", MATERI_GENAP, SOAL_GENAP)
            kelas_id = ensure_kelas9(cur)
        print("Kurikulum Kelas 9 (project-based) siap.")
        print("- 10 materi Ganjil + 10 materi Genap")
        print("- Latihan, UH, Sumatif, STS, SAS per semester (default nonaktif)")
        print("- Login siswa contoh: 2909001 / 123456")
        print(f"- kelas_id={kelas_id}")
    finally:
        conn.close()
    sys.path.insert(0, str(ROOT / "scripts"))
    from enrich_contoh_materi import main as isi_contoh

    isi_contoh()


if __name__ == "__main__":
    main()
