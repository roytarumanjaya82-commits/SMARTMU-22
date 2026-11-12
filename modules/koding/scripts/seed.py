"""Inisialisasi database, materi, soal, akun guru, dan contoh siswa."""
import json
import sys
from pathlib import Path

import pymysql
from openpyxl import Workbook
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from koding.config import Config  # noqa: E402
from koding.excel_siswa import buat_blanko_excel  # noqa: E402

MYSQL = {
    "host": Config.MYSQL_HOST,
    "port": Config.MYSQL_PORT,
    "user": Config.MYSQL_USER,
    "password": Config.MYSQL_PASSWORD,
    "charset": "utf8mb4",
}


MATERI = [
    {
        "urutan": 1,
        "judul": "Pengenalan Python",
        "ringkasan": "Sejarah singkat Python dan mengapa bahasa ini cocok untuk pemula.",
        "isi_html": """
        <h3>Apa itu Python?</h3>
        <p>Python adalah bahasa pemrograman tingkat tinggi yang dibuat oleh <strong>Guido van Rossum</strong>.
        Bahasa ini terkenal mudah dibaca karena sintaksnya mirip bahasa Inggris.</p>
        <h3>Mengapa belajar Python?</h3>
        <ul>
          <li>Cocok untuk pemula</li>
          <li>Banyak digunakan di data, web, otomasi, dan AI</li>
          <li>Komunitas besar dan dokumentasi lengkap</li>
        </ul>
        """,
        "contoh_kode": 'print("Halo, dunia Python!")',
    },
    {
        "urutan": 2,
        "judul": "Perintah Output: print()",
        "ringkasan": "Menampilkan teks atau nilai ke layar dengan fungsi print().",
        "isi_html": """
        <h3>Fungsi print()</h3>
        <p><code>print()</code> dipakai untuk menampilkan output ke layar.
        Teks (string) harus diapit tanda kutip.</p>
        <ul>
          <li>Benar: <code>print("Halo Informatika")</code></li>
          <li>Salah: <code>print(Halo Informatika)</code></li>
        </ul>
        """,
        "contoh_kode": 'print("Halo Informatika")\nprint(7 + 5)',
    },
    {
        "urutan": 3,
        "judul": "Variabel dan Aturan Nama",
        "ringkasan": "Variabel sebagai wadah data serta aturan penamaan yang sah di Python.",
        "isi_html": """
        <h3>Variabel</h3>
        <p>Variabel adalah wadah untuk menyimpan nilai data.</p>
        <h3>Aturan nama variabel</h3>
        <ul>
          <li>Boleh huruf, angka, dan underscore (_)</li>
          <li>Tidak boleh diawali angka (contoh salah: <code>2nama</code>)</li>
          <li>Tidak boleh memakai spasi</li>
          <li>Case-sensitive: <code>Nama</code> berbeda dengan <code>nama</code></li>
        </ul>
        """,
        "contoh_kode": 'nama_siswa = "Aisyah"\numur20 = 13\nprint(nama_siswa, umur20)',
    },
    {
        "urutan": 4,
        "judul": "Tipe Data Dasar",
        "ringkasan": "int, float, str, dan boolean serta cara mengenalinya.",
        "isi_html": """
        <h3>Tipe data penting</h3>
        <ul>
          <li><strong>int</strong> — bilangan bulat (85)</li>
          <li><strong>float</strong> — bilangan desimal (3.14)</li>
          <li><strong>str</strong> — teks ("Python")</li>
          <li><strong>bool</strong> — True / False</li>
        </ul>
        """,
        "contoh_kode": 'nilai = 85\npi = 3.14\nnama = "Roy"\nlulus = True\nprint(type(nilai), type(pi), type(nama), type(lulus))',
    },
    {
        "urutan": 5,
        "judul": "Operator Aritmatika",
        "ringkasan": "Operasi hitung +, -, *, /, //, %, dan **.",
        "isi_html": """
        <h3>Simbol aritmatika</h3>
        <ul>
          <li><code>+</code> tambah, <code>-</code> kurang, <code>*</code> kali</li>
          <li><code>/</code> bagi desimal, <code>//</code> bagi bulat (floor)</li>
          <li><code>%</code> sisa bagi (modulus)</li>
          <li><code>**</code> pangkat</li>
        </ul>
        """,
        "contoh_kode": "print(15 % 4)   # 3\nprint(17 // 3)  # 5\nprint(2 ** 3)   # 8",
    },
    {
        "urutan": 6,
        "judul": "Input Pengguna & Konversi Tipe",
        "ringkasan": "Menerima data dengan input() dan mengubahnya dengan int()/float().",
        "isi_html": """
        <h3>input()</h3>
        <p>Secara bawaan, <code>input()</code> selalu menghasilkan <strong>string</strong>.
        Jika ingin dihitung, konversi dulu dengan <code>int()</code> atau <code>float()</code>.</p>
        """,
        "contoh_kode": 'umur = int(input("Umur: "))\nprint("Tahun depan:", umur + 1)',
    },
    {
        "urutan": 7,
        "judul": "Komentar, Indentasi, dan Error",
        "ringkasan": "Menulis komentar, pentingnya indentasi, serta SyntaxError.",
        "isi_html": """
        <h3>Komentar</h3>
        <p>Gunakan tanda <code>#</code> untuk komentar satu baris.</p>
        <h3>Indentasi</h3>
        <p>Indentasi menentukan blok kode. Salah indentasi bisa menimbulkan error.</p>
        <h3>SyntaxError</h3>
        <p>Muncul jika tata bahasa/sintaks Python salah.</p>
        """,
        "contoh_kode": "# ini komentar\nnama = \"Python\"\nprint(nama)",
    },
    {
        "urutan": 8,
        "judul": "Percabangan if-elif-else",
        "ringkasan": "Pengambilan keputusan dengan if, elif, dan else.",
        "isi_html": """
        <h3>Struktur percabangan</h3>
        <p>Diawali kata kunci <code>if</code>. Gunakan operator perbandingan seperti
        <code>==</code>, <code>!=</code>, <code>&gt;</code>, <code>&lt;</code>, <code>&gt;=</code>, <code>&lt;=</code>.</p>
        """,
        "contoh_kode": 'nilai = 70\nif nilai >= 75:\n    print("Lulus")\nelse:\n    print("Remedial")',
    },
    {
        "urutan": 9,
        "judul": "Perulangan for dan while",
        "ringkasan": "Mengulang proses dengan for-range dan while.",
        "isi_html": """
        <h3>for</h3>
        <p>Cocok jika jumlah pengulangan sudah diketahui, biasanya bersama <code>range()</code>.</p>
        <h3>while</h3>
        <p>Mengulang selama kondisi masih True. Pastikan variabel pengontrol berubah agar tidak infinite loop.</p>
        """,
        "contoh_kode": "for i in range(3):\n    print(i)\n\nx = 1\nwhile x < 4:\n    print(x)\n    x = x + 1",
    },
    {
        "urutan": 10,
        "judul": "List dan Indexing",
        "ringkasan": "Menyimpan banyak data dalam list serta mengakses/mengubah elemen.",
        "isi_html": """
        <h3>List</h3>
        <p>Ditulis dengan kurung siku <code>[]</code>. Indeks dimulai dari <strong>0</strong>.</p>
        <ul>
          <li>Akses elemen: <code>buah[2]</code></li>
          <li>Ubah elemen: <code>angka[1] = 10</code></li>
          <li>Panjang data: <code>len(...)</code></li>
        </ul>
        """,
        "contoh_kode": 'buah = ["Apel", "Pisang", "Jeruk", "Mangga"]\nprint(buah[2])\nangka = [2, 4, 6]\nangka[1] = 10\nprint(angka)',
    },
]


def connect(db=None):
    cfg = dict(MYSQL)
    if db:
        cfg["database"] = db
    return pymysql.connect(**cfg, autocommit=True)


def run_schema():
    schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
    conn = connect()
    try:
        with conn.cursor() as cur:
            for stmt in schema.split(";"):
                s = stmt.strip()
                if s:
                    cur.execute(s)
        print("Schema OK")
    finally:
        conn.close()


def seed():
    questions = json.loads((ROOT / "_questions.json").read_text(encoding="utf-8"))
    conn = connect(Config.MYSQL_DB)
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM jawaban_siswa")
            cur.execute("DELETE FROM nilai")
            cur.execute("DELETE FROM percobaan_ujian")
            cur.execute("DELETE FROM soal")
            cur.execute("DELETE FROM ujian")
            cur.execute("DELETE FROM materi")
            cur.execute("DELETE FROM siswa")
            cur.execute("DELETE FROM kelas")
            cur.execute("DELETE FROM users")

            cur.execute(
                """
                INSERT INTO users (username, password_hash, nama_lengkap, role)
                VALUES (%s,%s,%s,'guru')
                """,
                ("guru", generate_password_hash("guru123"), "Roy Tarumanjaya, S.Kom"),
            )

            cur.execute(
                """
                INSERT INTO kelas (nama_kelas, tingkat, tahun_ajaran, semester)
                VALUES ('7.5', '7', '2026/2027', 'Ganjil')
                """
            )
            kelas_id = cur.lastrowid

            contoh_siswa = [
                ("2507501", "Ahmad Fauzan", "L"),
                ("2507502", "Siti Aisyah", "P"),
                ("2507503", "Budi Santoso", "L"),
                ("2507504", "Dewi Lestari", "P"),
                ("2507505", "Rafi Pratama", "L"),
            ]
            for nis, nama, jk in contoh_siswa:
                cur.execute(
                    """
                    INSERT INTO users (username, password_hash, nama_lengkap, role)
                    VALUES (%s,%s,%s,'siswa')
                    """,
                    (nis, generate_password_hash("123456"), nama),
                )
                uid = cur.lastrowid
                cur.execute(
                    """
                    INSERT INTO siswa (user_id, kelas_id, nis, nama_siswa, jenis_kelamin)
                    VALUES (%s,%s,%s,%s,%s)
                    """,
                    (uid, kelas_id, nis, nama, jk),
                )

            materi_ids = []
            for m in MATERI:
                cur.execute(
                    """
                    INSERT INTO materi (tingkat, urutan, semester, judul, ringkasan, isi_html, contoh_kode)
                    VALUES ('7', %s,'Ganjil',%s,%s,%s,%s)
                    """,
                    (m["urutan"], m["judul"], m["ringkasan"], m["isi_html"], m["contoh_kode"]),
                )
                materi_ids.append(cur.lastrowid)

            def insert_ujian(judul, deskripsi, jenis, materi_id, soal_items, durasi, jumlah, pembahasan=1, semester="Ganjil"):
                cur.execute(
                    """
                    INSERT INTO ujian
                    (judul, deskripsi, jenis, semester, tingkat, materi_id, durasi_menit, jumlah_soal, nilai_kkm, acak_soal, tampil_pembahasan, aktif)
                    VALUES (%s,%s,%s,%s,'7',%s,%s,%s,77,1,%s,0)
                    """,
                    (judul, deskripsi, jenis, semester, materi_id, durasi, jumlah, pembahasan),
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
                            q["options"].get("A", "-"),
                            q["options"].get("B", "-"),
                            q["options"].get("C", "-"),
                            q["options"].get("D", "-"),
                            q["answer"],
                            f"Materi terkait: {q.get('materi') or '-'}",
                        ),
                    )
                return uid

            # Latihan per materi (chunk questions)
            chunks = [
                (0, questions[0:4], "Latihan 1: Pengenalan & Output"),
                (2, questions[3:8], "Latihan 2: Variabel & Tipe Data"),
                (4, questions[8:14], "Latihan 3: Operator & Input"),
                (7, questions[14:22], "Latihan 4: Percabangan & Dasar Lanjutan"),
                (8, questions[22:30], "Latihan 5: Perulangan & List"),
                (9, questions[30:40], "Latihan 6: Logika & Manipulasi Data"),
            ]
            for materi_idx, qs, judul in chunks:
                insert_ujian(
                    judul,
                    "Latihan interaktif dengan pembahasan langsung setelah selesai.",
                    "latihan",
                    materi_ids[materi_idx],
                    qs,
                    20,
                    len(qs),
                    1,
                )

            insert_ujian(
                "Ulangan Harian 1 - Dasar Python",
                "Ulangan harian materi pengenalan hingga tipe data.",
                "ulangan_harian",
                materi_ids[0],
                questions[0:10],
                30,
                10,
                1,
            )
            insert_ujian(
                "Ulangan Harian 2 - Operator, Input, Percabangan",
                "Ulangan harian materi operator sampai if-else.",
                "ulangan_harian",
                materi_ids[4],
                questions[9:20],
                30,
                10,
                1,
            )
            insert_ujian(
                "Ulangan Harian 3 - Perulangan & List",
                "Ulangan harian materi for/while dan list.",
                "ulangan_harian",
                materi_ids[8],
                questions[20:30],
                30,
                10,
                1,
            )

            insert_ujian(
                "Sumatif Materi Dasar Koding",
                "Penilaian sumatif setelah rangkaian latihan.",
                "sumatif",
                None,
                questions[0:20],
                40,
                20,
                0,
            )
            insert_ujian(
                "STS Ganjil Koding 7.5",
                "Sumatif Tengah Semester Ganjil.",
                "sts_ganjil",
                None,
                questions[0:25],
                60,
                25,
                0,
            )
            insert_ujian(
                "STS Genap Koding 7.5",
                "Sumatif Tengah Semester Genap (dilengkapi penuh lewat scripts/seed_genap.py).",
                "sts_genap",
                None,
                questions[15:40],
                60,
                25,
                0,
                semester="Genap",
            )
            insert_ujian(
                "SAS Koding 7.5",
                "Sumatif Akhir Semester — seluruh materi.",
                "sas",
                None,
                questions,
                90,
                40,
                0,
            )

        print("Seed data OK")
        print("Guru  : guru / guru123")
        print("Siswa : NIS contoh 2507501 / 123456")
    finally:
        conn.close()

    # blanko contoh
    Config.BLANKO_FOLDER.mkdir(parents=True, exist_ok=True)
    bio = buat_blanko_excel("7.5")
    out = Config.BLANKO_FOLDER / "blanko_siswa_7.5.xlsx"
    out.write_bytes(bio.read())
    print("Blanko Excel:", out)


if __name__ == "__main__":
    run_schema()
    seed()
