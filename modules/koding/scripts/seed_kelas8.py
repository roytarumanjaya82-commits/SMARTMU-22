"""Seed kurikulum Kelas 8 (Python lanjutan) — Ganjil & Genap."""
import sys
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from koding.config import Config  # noqa: E402
from koding.kurikulum_kelas8 import MATERI_GANJIL, MATERI_GENAP  # noqa: E402

KKM = 77

def Q(q, a, b, c, d, kunci, materi):
    return {
        "question": q,
        "options": {"A": a, "B": b, "C": c, "D": d},
        "answer": kunci,
        "materi": materi,
    }


SOAL_GANJIL = [
    Q("Set di Python terutama digunakan untuk menyimpan...", "Data berpasangan key-value", "Nilai unik tanpa duplikat", "Hanya string panjang", "File biner", "B", "Set"),
    Q("Hasil dari print({1, 2, 2, 3}) adalah...", "{1, 2, 2, 3}", "{1, 2, 3}", "[1, 2, 3]", "(1, 2, 3)", "B", "Set"),
    Q("Operasi irisan dua set memakai simbol...", "|", "&", "-", "+", "B", "Set"),
    Q("List comprehension [x*2 for x in range(3)] menghasilkan...", "[0, 2, 4]", "[1, 2, 3]", "[2, 4, 6]", "[0, 1, 2]", "A", "List Comp"),
    Q("Sintaks list comprehension yang benar adalah...", "[for x in data x]", "[x for x in data]", "(x for in data)", "{x: data}", "B", "List Comp"),
    Q("*args pada fungsi berguna untuk...", "Menghapus parameter", "Menerima banyak argumen posisi", "Membuat class", "Membuka file", "B", "Fungsi"),
    Q("lambda a, b: a-b adalah...", "Class baru", "Fungsi singkat tanpa nama", "Modul JSON", "Exception", "B", "Fungsi"),
    Q("Blok untuk menangkap error disebut...", "try", "except", "loop", "class", "B", "Exception"),
    Q("Error akibat pembagian dengan nol bertipe...", "ValueError", "TypeError", "ZeroDivisionError", "NameError", "C", "Exception"),
    Q("Mode open untuk menulis file (menimpa isi lama) adalah...", "r", "a", "w", "x+", "C", "File"),
    Q("Pola paling aman membuka file adalah...", "f = open(); f.close() manual saja", "with open(...) as f:", "selalu mode wb", "tanpa encoding", "B", "File"),
    Q("Manfaat memecah kode menjadi modul adalah...", "Program lebih sulit dibaca", "Kode lebih rapi dan bisa dipakai ulang", "Menghapus fungsi", "Menonaktifkan import", "B", "Modul"),
    Q("Class dalam OOP berfungsi sebagai...", "Hasil jadi object saja", "Cetakan/blueprint object", "Database MySQL", "Error handler wajib", "B", "OOP"),
    Q("Object adalah...", "Nama file .py", "Instance/hasil dari class", "Hanya dictionary", "Keyword Python", "B", "OOP"),
    Q("Parameter pertama method instance biasanya bernama...", "this", "self", "cls saja selalu", "init", "B", "OOP"),
    Q("Method __init__ dipanggil saat...", "Program ditutup", "Object baru dibuat", "File dihapus", "Import gagal", "B", "OOP"),
    Q("Perhatikan:\nclass Siswa:\n    def __init__(self, nama):\n        self.nama = nama\ns = Siswa(\"Budi\")\nprint(s.nama)\nOutputnya...", "Siswa", "Budi", "self", "Error", "B", "OOP"),
    Q("Atribut object adalah...", "Fungsi milik class", "Data/variabel milik object", "Nama modul", "Jenis exception", "B", "OOP"),
    Q("Hasil [n for n in range(5) if n % 2 == 1] adalah...", "[0, 2, 4]", "[1, 3]", "[1, 3, 5]", "[2, 4]", "B", "List Comp"),
    Q("except ValueError menangani error saat...", "Bagi nol", "Konversi tipe gagal (mis. int(\"a\"))", "File tidak ketemu saja", "Syntax salah", "B", "Exception"),
    Q("Mode \"a\" pada open berarti...", "Hapus file", "Append/tambah di akhir", "Baca biner", "Buat class", "B", "File"),
    Q("from math import sqrt artinya...", "Import seluruh modul os", "Import fungsi sqrt saja dari math", "Hapus math", "Buat set", "B", "Modul"),
    Q("Manakah nama class yang paling sesuai konvensi?", "nama_siswa", "NamaSiswa", "namaSiswa_class", "NAMA", "B", "OOP"),
    Q("Jika method tidak memakai self sebagai parameter pertama (instance method), biasanya...", "Tetap ideal", "Akan error saat dipanggil lewat object", "Otomatis jadi set", "Menjadi file", "B", "OOP"),
    Q("Tujuan finally dalam try-except adalah...", "Hanya jalan jika error", "Selalu dijalankan", "Mengganti return", "Membuat object", "B", "Exception"),
    Q("Set TIDAK mendukung...", "Keanggotaan unik", "Indexing seperti set[0] secara umum", "Operasi union", "Penambahan elemen", "B", "Set"),
    Q("kuadrat = list(map(lambda x: x*x, [1,2,3])) hasilnya...", "[1, 2, 3]", "[1, 4, 9]", "[2, 4, 6]", "Error", "B", "Fungsi"),
    Q("Menyimpan teks ke file memakai method...", "f.push()", "f.write()", "f.append_text()", "f.dump_only()", "B", "File"),
    Q("Class Produk dengan __init__(self, nama, harga) membutuhkan berapa argumen saat membuat object (selain self)?", "0", "1", "2", "3", "C", "OOP"),
    Q("Pemrograman berorientasi objek menekankan...", "Hanya satu variabel global", "Object yang punya data dan perilaku", "Tanpa fungsi", "Tanpa class", "B", "OOP"),
    Q("Hasil dari {1, 2} | {2, 3} adalah...", "{2}", "{1, 2, 3}", "{1, 3}", "[1, 2, 3]", "B", "Set"),
    Q("Blok try berisi...", "Hanya komentar", "Kode yang mungkin menimbulkan error", "Hanya import", "Hanya class", "B", "Exception"),
    Q("Docstring fungsi ditulis...", "Setelah return", "String di baris pertama tubuh fungsi", "Di file JSON saja", "Sebagai nama class", "B", "Best practice"),
    Q("self.nama = nama dalam __init__ artinya...", "Menghapus atribut", "Menyimpan parameter ke atribut object", "Membuat set", "Membuka file", "B", "OOP"),
    Q("Manakah yang termasuk keunggulan modularisasi?", "Semua kode wajib 1 file", "Perawatan dan kolaborasi lebih mudah", "Tidak bisa diuji", "Wajib tanpa fungsi", "B", "Modul"),
    Q("Perhatikan:\ntry:\n    print(int(\"12\"))\nexcept:\n    print(\"err\")\nOutput...", "err", "12", "Error tanpa output", "None", "B", "Exception"),
    Q("List comprehension lebih sering dipakai untuk...", "Membuat GUI", "Membangun list baru secara ringkas", "Koneksi MySQL", "Inheritance", "B", "List Comp"),
    Q("Object s1 dan s2 dari class yang sama...", "Pasti atributnya identik selalu", "Bisa punya nilai atribut berbeda", "Tidak boleh ada dua object", "Otomatis menjadi set", "B", "OOP"),
    Q("f.read() mengembalikan...", "List angka saja", "Isi file sebagai string (mode teks)", "Class", "Exception wajib", "B", "File"),
    Q("Fokus proyek mini OOP ganjil adalah...", "HTML saja", "Menerapkan class, atribut, method, dan __init__", "Hanya bubble sort", "Hanya tkinter", "B", "Proyek"),
]

SOAL_GENAP = [
    Q("Inheritance memungkinkan class anak...", "Menghapus Python", "Mewarisi anggota class induk", "Mengganti MySQL", "Menutup file otomatis", "B", "Inheritance"),
    Q("Sintaks pewarisan yang benar...", "class Anak inherits Induk", "class Anak(Induk):", "class Anak -> Induk", "class Anak extends Induk:", "B", "Inheritance"),
    Q("Method overriding berarti...", "Menghapus class induk", "Class anak mendefinisikan ulang method induk", "Mengubah JSON jadi set", "Membuka GUI", "B", "Inheritance"),
    Q("Encapsulation bertujuan...", "Menyembunyikan/melindungi detail data", "Menghapus semua method", "Memaksa tanpa class", "Menonaktifkan import", "A", "Encapsulation"),
    Q("Atribut __saldo menandakan...", "Variabel global wajib", "Atribut internal/privat secara konvensi", "Nama modul", "Jenis sorting", "B", "Encapsulation"),
    Q("Modul Python untuk JSON adalah...", "os", "json", "tkinter", "math", "B", "JSON"),
    Q("json.dumps(dict) menghasilkan...", "File gambar", "String JSON", "Object class", "Set kosong", "B", "JSON"),
    Q("json.loads(teks) mengubah string JSON menjadi...", "Class", "Struktur data Python (mis. dict/list)", "File exe", "Exception saja", "B", "JSON"),
    Q("Linear search bekerja dengan...", "Membagi data jadi dua selalu", "Memeriksa elemen satu per satu", "Hanya pada string", "Tanpa perulangan", "B", "Searching"),
    Q("Syarat binary search yang penting...", "Data acak tanpa urutan", "Data sudah terurut", "Data harus set", "Data harus class", "B", "Searching"),
    Q("Bubble sort mengurutkan dengan...", "Tukar pasangan bersebelahan berulang", "Hanya satu perbandingan", "Recursion wajib", "JSON dump", "A", "Sorting"),
    Q("Fungsi bawaan untuk mengurutkan dan mengembalikan list baru adalah...", "order()", "sorted()", "arrange()", "rank()", "B", "Sorting"),
    Q("Rekursi membutuhkan...", "GUI", "Base case", "MySQL", "HTML", "B", "Rekursi"),
    Q("faktorial(5) secara rekursif menghasilkan...", "15", "120", "25", "5", "B", "Rekursi"),
    Q("Library GUI bawaan Python yang dibahas adalah...", "Django", "Tkinter", "Flask saja", "Pandas", "B", "Tkinter"),
    Q("Widget Tkinter untuk tombol adalah...", "tk.Label", "tk.Button", "tk.Frame saja wajib", "tk.JSON", "B", "Tkinter"),
    Q("assert dipakai untuk...", "Membuat window", "Memastikan kondisi benar saat pengujian", "Import modul", "Sorting otomatis", "B", "Testing"),
    Q("Langkah awal debugging yang baik...", "Abaikan traceback", "Baca pesan error dan cek nilai variabel", "Hapus semua fungsi", "Matikan komputer", "B", "Debugging"),
    Q("Docstring bermanfaat untuk...", "Dokumentasi singkat fungsi/class", "Mengganti interpreter", "Membuat set", "Mematikan exception", "A", "Best practice"),
    Q("Prinsip DRY berarti...", "Do Repeat Yourself", "Don't Repeat Yourself", "Data Random YAML", "Debug Run Yearly", "B", "Best practice"),
    Q("Class Kucing(Hewan) artinya...", "Hewan mewarisi Kucing", "Kucing mewarisi Hewan", "Tidak ada hubungan", "Keduanya modul JSON", "B", "Inheritance"),
    Q("Method getter sering dipakai untuk...", "Menghapus class", "Mengambil nilai atribut terlindungi", "Membuka port", "Membuat bubble sort", "B", "Encapsulation"),
    Q("Menyimpan dict ke file JSON biasanya memakai...", "json.dump", "math.sqrt", "random.choice", "tk.Label", "A", "JSON"),
    Q("Jika linear_search tidak menemukan data, konvensi contoh mengembalikan...", "0", "-1", "True", "\"ok\"", "B", "Searching"),
    Q("Selection sort berfokus pada...", "Memilih elemen ekstrem lalu menempatkannya", "Hanya recursion", "Hanya GUI", "Hanya JSON", "A", "Sorting"),
    Q("Tanpa base case, fungsi rekursif dapat...", "Lebih cepat pasti", "Terjadi infinite recursion / RecursionError", "Menjadi class", "Menjadi set", "B", "Rekursi"),
    Q("root.mainloop() pada Tkinter berfungsi untuk...", "Menutup Python instan", "Menjalankan event loop GUI", "Mengurutkan list", "Parse JSON", "B", "Tkinter"),
    Q("Pengujian dengan beberapa kasus input termasuk...", "Inheritance wajib", "Testing dasar", "Bubble saja", "Mode file wb", "B", "Testing"),
    Q("Nama fungsi yang jelas membantu...", "Obfuscation", "Keterbacaan dan perawatan kode", "Memperbanyak bug", "Menyembunyikan docstring", "B", "Best practice"),
    Q("Proyek akhir kelas 8 idealnya menggabungkan...", "Hanya print hello", "OOP + data (JSON/file) + logika/algoritma", "Hanya CSS", "Hanya SQL injection", "B", "Proyek"),
    Q("Override suara() pada class anak membuat...", "Method induk hilang dari dunia", "Pemanggilan lewat object anak memakai versi anak", "JSON rusak", "Sorting berhenti", "B", "Inheritance"),
    Q("self.__saldo tidak dimaksudkan diakses langsung dari luar agar...", "Lebih lambat", "Kontrol perubahan data lebih aman", "GUI hilang", "Set kosong", "B", "Encapsulation"),
    Q("Format data JSON mirip dengan...", "Dict/list Python", "Hanya tuple immutable wajib", "Bytecode", "Gambar PNG", "A", "JSON"),
    Q("Kompleksitas linear search secara kasar...", "O(1) selalu", "O(n)", "O(n log n) wajib", "O(0)", "B", "Searching"),
    Q("a.sort() berbeda dengan sorted(a) karena...", "a.sort() mengembalikan list baru, sorted mengubah asli", "a.sort() mengubah list asli (in-place), sorted mengembalikan list baru", "Keduanya error", "Keduanya hanya untuk set", "B", "Sorting"),
    Q("Fibonacci rekursif sederhana cocok untuk belajar, tetapi...", "Selalu paling cepat untuk n besar", "Bisa lambat tanpa optimasi", "Tidak butuh base case", "Wajib Tkinter", "B", "Rekursi"),
    Q("tk.Label dipakai untuk...", "Tombol", "Menampilkan teks/label", "Sorting", "Binary search", "B", "Tkinter"),
    Q("Pesan AssertionError muncul jika...", "assert berhasil", "Kondisi assert bernilai False", "File terbuka", "Import sukses", "B", "Testing"),
    Q("Fungsi kecil yang fokus satu tugas termasuk...", "Spaghetti code", "Best practice desain fungsi", "Encapsulation gagal", "Tanpa nama", "B", "Best practice"),
    Q("Contoh integrasi proyek: class nilai + json.dump dipakai untuk...", "Menyimpan data nilai ke file", "Menghapus interpreter", "Membuat bubble otomatis di CPU", "Menutup sekolah", "A", "Proyek"),
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
    for tabel, after in (
        ("materi", "AFTER id"),
        ("ujian", "AFTER semester"),
        ("kelas", "AFTER nama_kelas"),
    ):
        cur.execute(f"SHOW COLUMNS FROM {tabel} LIKE 'tingkat'")
        if not cur.fetchone():
            cur.execute(
                f"ALTER TABLE {tabel} ADD COLUMN tingkat ENUM('7','8','9') "
                f"NOT NULL DEFAULT '7' {after}"
            )
        else:
            cur.execute(
                f"ALTER TABLE {tabel} MODIFY tingkat ENUM('7','8','9') NOT NULL DEFAULT '7'"
            )

    cur.execute("UPDATE materi SET tingkat='7' WHERE tingkat IS NULL OR tingkat=''")
    cur.execute("UPDATE ujian SET tingkat='7' WHERE tingkat IS NULL OR tingkat=''")
    cur.execute(
        """
        UPDATE kelas SET tingkat='9' WHERE nama_kelas LIKE '9%' OR nama_kelas LIKE 'IX%'
        """
    )
    cur.execute(
        """
        UPDATE kelas SET tingkat='8' WHERE nama_kelas LIKE '8%' OR nama_kelas LIKE 'VIII%'
        """
    )
    cur.execute(
        """
        UPDATE kelas SET tingkat='7' WHERE tingkat IS NULL OR tingkat='' OR nama_kelas LIKE '7%'
        """
    )


def insert_materi(cur, items, semester):
    ids = []
    for m in items:
        cur.execute(
            """
            INSERT INTO materi (tingkat, urutan, semester, judul, ringkasan, isi_html, contoh_kode)
            VALUES ('8', %s, %s, %s, %s, %s, %s)
            """,
            (m["urutan"], semester, m["judul"], m["ringkasan"], m["isi_html"], m["contoh_kode"]),
        )
        ids.append(cur.lastrowid)
    return ids


def insert_ujian(cur, judul, deskripsi, jenis, semester, materi_id, soal_items, durasi, jumlah, pembahasan=1):
    cur.execute(
        "SELECT id FROM ujian WHERE tingkat='8' AND judul=%s AND semester=%s",
        (judul, semester),
    )
    old = cur.fetchone()
    if old:
        cur.execute("DELETE FROM soal WHERE ujian_id=%s", (old["id"],))
        cur.execute("DELETE FROM ujian WHERE id=%s", (old["id"],))

    cur.execute(
        """
        INSERT INTO ujian
        (judul, deskripsi, jenis, semester, tingkat, materi_id, durasi_menit, jumlah_soal, nilai_kkm, acak_soal, tampil_pembahasan, aktif)
        VALUES (%s,%s,%s,%s,'8',%s,%s,%s,%s,1,%s,0)
        """,
        (judul, deskripsi, jenis, semester, materi_id, durasi, jumlah, KKM, pembahasan),
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
    prefix = f"K8 {semester}"

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
            f"Latihan interaktif kelas 8 semester {semester.lower()}.",
            "latihan",
            semester,
            ids[idx],
            qs,
            25,
            len(qs),
            1,
        )

    insert_ujian(cur, f"UH {prefix} 1", "Ulangan harian 1 kelas 8.", "ulangan_harian", semester, ids[0], soal[0:12], 30, 12, 1)
    insert_ujian(cur, f"UH {prefix} 2", "Ulangan harian 2 kelas 8.", "ulangan_harian", semester, ids[3], soal[10:22], 30, 12, 1)
    insert_ujian(cur, f"UH {prefix} 3", "Ulangan harian 3 kelas 8.", "ulangan_harian", semester, ids[6], soal[20:32], 30, 12, 1)
    insert_ujian(cur, f"Sumatif {prefix}", "Sumatif materi kelas 8.", "sumatif", semester, None, soal[0:20], 45, 20, 0)

    jenis_sts = "sts_ganjil" if semester == "Ganjil" else "sts_genap"
    insert_ujian(cur, f"STS {prefix}", f"Sumatif Tengah Semester {semester} kelas 8.", jenis_sts, semester, None, soal[0:25], 60, 25, 0)
    insert_ujian(cur, f"SAS {prefix}", f"Sumatif Akhir Semester {semester} kelas 8.", "sas", semester, None, soal, 90, 40, 0)


def ensure_kelas8(cur):
    cur.execute("SELECT id FROM kelas WHERE nama_kelas IN ('8.5', '8.1') ORDER BY nama_kelas DESC LIMIT 1")
    row = cur.fetchone()
    if not row:
        cur.execute(
            """
            INSERT INTO kelas (nama_kelas, tingkat, tahun_ajaran, semester)
            VALUES ('8.5', '8', '2026/2027', 'Ganjil')
            """
        )
        kelas_id = cur.lastrowid
    else:
        kelas_id = row["id"]
        cur.execute("UPDATE kelas SET tingkat='8' WHERE id=%s", (kelas_id,))
    cur.execute("UPDATE kelas SET tingkat='8' WHERE nama_kelas LIKE '8%' OR nama_kelas LIKE 'VIII%'")

    contoh = [
        ("2808001", "Naufal Akbar", "L"),
        ("2808002", "Putri Maharani", "P"),
        ("2808003", "Farhan Rizki", "L"),
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

            # hapus kurikulum kelas 8 lama
            cur.execute("SELECT id FROM materi WHERE tingkat='8'")
            old_m = [r["id"] for r in cur.fetchall()]
            cur.execute("SELECT id FROM ujian WHERE tingkat='8'")
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
            kelas_id = ensure_kelas8(cur)

        print("Kurikulum Kelas 8 siap.")
        print("- 10 materi Ganjil + 10 materi Genap (Python lanjutan)")
        print("- Latihan, UH, Sumatif, STS, SAS per semester")
        print("- KKM 77")
        print("- Kelas contoh: 8.5 (atau 8.1)")
        print("- Login siswa contoh: 2808001 / 123456")
        print(f"- kelas_id={kelas_id}")
    finally:
        conn.close()
    # Perbanyak contoh soal + penyelesaian pada setiap materi
    sys.path.insert(0, str(ROOT / "scripts"))
    from enrich_contoh_materi import main as isi_contoh

    isi_contoh()


if __name__ == "__main__":
    main()
