"""Tambah materi, latihan, ulangan, dan sumatif Semester Genap (tanpa menghapus data Ganjil)."""
import sys
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from koding.config import Config  # noqa: E402

MATERI_GENAP = [
    {
        "urutan": 1,
        "judul": "Percabangan Bersarang (Nested if)",
        "ringkasan": "Menggabungkan beberapa if untuk keputusan bertingkat.",
        "isi_html": """
        <h3>Apa itu nested if?</h3>
        <p>Nested if adalah percabangan di dalam percabangan. Dipakai saat keputusan
        membutuhkan lebih dari satu syarat berurutan.</p>
        <h3>Contoh kasus</h3>
        <ul>
          <li>Cek apakah nilai valid (0–100), lalu tentukan predikat</li>
          <li>Cek login: username benar dulu, baru cek password</li>
        </ul>
        <p>Gunakan indentasi yang rapi agar blok <code>if</code> tidak membingungkan.</p>
        """,
        "contoh_kode": 'nilai = 82\nif nilai >= 0 and nilai <= 100:\n    if nilai >= 77:\n        print("Tuntas")\n    else:\n        print("Belum tuntas")\nelse:\n    print("Nilai tidak valid")',
    },
    {
        "urutan": 2,
        "judul": "Perulangan Bersarang & Pola",
        "ringkasan": "for di dalam for untuk membuat pola dan tabel sederhana.",
        "isi_html": """
        <h3>Nested loop</h3>
        <p>Perulangan bersarang memakai loop di dalam loop. Cocok untuk membuat pola bintang,
        tabel perkalian, atau mengunjungi setiap baris dan kolom.</p>
        <h3>Tips</h3>
        <ul>
          <li>Loop luar mengatur baris</li>
          <li>Loop dalam mengatur kolom/isi baris</li>
          <li>Gunakan <code>end=""</code> pada <code>print</code> agar tetap di baris yang sama</li>
        </ul>
        """,
        "contoh_kode": 'for i in range(1, 4):\n    for j in range(i):\n        print("*", end="")\n    print()',
    },
    {
        "urutan": 3,
        "judul": "Method List Lanjutan",
        "ringkasan": "append, insert, remove, pop, sort, dan reverse pada list.",
        "isi_html": """
        <h3>Method penting pada list</h3>
        <ul>
          <li><code>append(x)</code> — menambah di akhir</li>
          <li><code>insert(i, x)</code> — menambah di indeks i</li>
          <li><code>remove(x)</code> — menghapus nilai x pertama</li>
          <li><code>pop()</code> — menghapus & mengembalikan elemen terakhir</li>
          <li><code>sort()</code> — mengurutkan</li>
          <li><code>reverse()</code> — membalik urutan</li>
        </ul>
        """,
        "contoh_kode": 'angka = [3, 1, 2]\nangka.append(4)\nangka.sort()\nprint(angka)  # [1, 2, 3, 4]\nangka.pop()\nprint(angka)  # [1, 2, 3]',
    },
    {
        "urutan": 4,
        "judul": "Manipulasi String Lanjutan",
        "ringkasan": "Indexing, slicing, upper/lower, replace, split, dan join.",
        "isi_html": """
        <h3>String bisa diolah</h3>
        <ul>
          <li>Indexing: <code>teks[0]</code></li>
          <li>Slicing: <code>teks[0:3]</code></li>
          <li><code>upper()</code> / <code>lower()</code></li>
          <li><code>replace("a", "i")</code></li>
          <li><code>split()</code> memecah string menjadi list</li>
          <li><code>"-".join(list)</code> menggabungkan list menjadi string</li>
        </ul>
        <p>String bersifat immutable: method string menghasilkan string baru.</p>
        """,
        "contoh_kode": 'teks = "Koding Python"\nprint(teks.lower())\nprint(teks[0:6])\nprint(teks.replace("Python", "7.5"))\nkata = teks.split()\nprint(kata)',
    },
    {
        "urutan": 5,
        "judul": "Tuple",
        "ringkasan": "Struktur data mirip list tetapi bersifat tetap (immutable).",
        "isi_html": """
        <h3>Apa itu tuple?</h3>
        <p>Tuple ditulis dengan kurung biasa <code>()</code>. Isinya tidak bisa diubah setelah dibuat.</p>
        <h3>Kapan dipakai?</h3>
        <ul>
          <li>Data yang tidak boleh berubah (misal koordinat)</li>
          <li>Pengembalian beberapa nilai sekaligus</li>
        </ul>
        <p>Indexing tetap dimulai dari 0, sama seperti list dan string.</p>
        """,
        "contoh_kode": 'koordinat = (10, 20)\nprint(koordinat[0])\n# koordinat[0] = 5  # Error, tuple tidak bisa diubah\nnama, umur = ("Aisyah", 13)\nprint(nama, umur)',
    },
    {
        "urutan": 6,
        "judul": "Dictionary Dasar",
        "ringkasan": "Menyimpan data berpasangan kunci (key) dan nilai (value).",
        "isi_html": """
        <h3>Dictionary</h3>
        <p>Ditulis dengan kurung kurawal <code>{}</code>. Setiap elemen berupa <code>key: value</code>.</p>
        <ul>
          <li>Akses: <code>siswa["nama"]</code></li>
          <li>Tambah/ubah: <code>siswa["nilai"] = 90</code></li>
          <li>Method: <code>keys()</code>, <code>values()</code>, <code>items()</code></li>
        </ul>
        """,
        "contoh_kode": 'siswa = {"nama": "Budi", "nis": "2507503", "nilai": 88}\nprint(siswa["nama"])\nsiswa["nilai"] = 91\nprint(siswa)',
    },
    {
        "urutan": 7,
        "judul": "Fungsi (Function)",
        "ringkasan": "Membuat blok kode yang bisa dipanggil ulang dengan def.",
        "isi_html": """
        <h3>Mengapa perlu fungsi?</h3>
        <p>Fungsi membuat program lebih rapi, tidak berulang, dan mudah diperbaiki.</p>
        <h3>Struktur dasar</h3>
        <pre>def nama_fungsi(parameter):\n    # proses\n    return hasil</pre>
        <ul>
          <li><code>def</code> untuk mendefinisikan</li>
          <li>Parameter menerima input</li>
          <li><code>return</code> mengembalikan hasil</li>
        </ul>
        """,
        "contoh_kode": 'def luas_persegi(sisi):\n    return sisi * sisi\n\nhasil = luas_persegi(5)\nprint(hasil)  # 25',
    },
    {
        "urutan": 8,
        "judul": "Parameter, Return, dan Default Value",
        "ringkasan": "Fungsi dengan banyak parameter, nilai balik, dan parameter bawaan.",
        "isi_html": """
        <h3>Variasi fungsi</h3>
        <ul>
          <li>Tanpa parameter: <code>def sapa():</code></li>
          <li>Dengan parameter: <code>def sapa(nama):</code></li>
          <li>Default value: <code>def sapa(nama="Siswa"):</code></li>
          <li>Return lebih dari satu nilai (sebagai tuple)</li>
        </ul>
        """,
        "contoh_kode": 'def sapa(nama="Siswa"):\n    return f"Halo, {nama}!"\n\nprint(sapa())\nprint(sapa("Rafi"))\n\ndef hitung(a, b):\n    return a + b, a * b\n\ntambah, kali = hitung(3, 4)\nprint(tambah, kali)',
    },
    {
        "urutan": 9,
        "judul": "Modul math dan random",
        "ringkasan": "Memakai library bawaan Python untuk matematika dan bilangan acak.",
        "isi_html": """
        <h3>import modul</h3>
        <p>Modul adalah kumpulan fungsi siap pakai. Impor dulu sebelum digunakan.</p>
        <ul>
          <li><code>math.sqrt()</code>, <code>math.pi</code>, <code>math.ceil()</code></li>
          <li><code>random.randint(a, b)</code>, <code>random.choice(list)</code></li>
        </ul>
        """,
        "contoh_kode": 'import math\nimport random\n\nprint(math.sqrt(16))\nprint(math.pi)\nprint(random.randint(1, 6))\nprint(random.choice(["A", "B", "C"]))',
    },
    {
        "urutan": 10,
        "judul": "Proyek Mini & Problem Solving",
        "ringkasan": "Menggabungkan materi genap untuk membuat program sederhana.",
        "isi_html": """
        <h3>Langkah problem solving</h3>
        <ol>
          <li>Pahami masalah</li>
          <li>Tentukan input–proses–output</li>
          <li>Pilih struktur data & algoritma</li>
          <li>Tulis fungsi yang jelas</li>
          <li>Uji dengan beberapa contoh</li>
        </ol>
        <p>Contoh proyek: nilai siswa, tebak angka, kasir sederhana, atau daftar belanja.</p>
        """,
        "contoh_kode": 'def status_kkm(nilai, kkm=77):\n    if nilai >= kkm:\n        return "Tuntas"\n    return "Belum tuntas"\n\ndata = {"Aisyah": 90, "Budi": 70, "Rafi": 77}\nfor nama, nilai in data.items():\n    print(nama, nilai, status_kkm(nilai))',
    },
]


# Bank soal semester genap (40 soal)
SOAL_GENAP = [
    {
        "q": "Nested if artinya...",
        "a": "Perulangan di dalam fungsi",
        "b": "Percabangan di dalam percabangan",
        "c": "List di dalam dictionary",
        "d": "Komentar di dalam string",
        "kunci": "B",
        "materi": "Nested if",
    },
    {
        "q": "Perhatikan kode:\nnilai = 80\nif nilai >= 0:\n    if nilai >= 77:\n        print(\"Tuntas\")\nOutput yang muncul adalah...",
        "a": "Tuntas",
        "b": "Belum tuntas",
        "c": "Error",
        "d": "Tidak ada output",
        "kunci": "A",
        "materi": "Nested if",
    },
    {
        "q": "Loop bersarang (nested loop) paling cocok untuk...",
        "a": "Membuat satu variabel saja",
        "b": "Membuat pola baris dan kolom",
        "c": "Menghapus file",
        "d": "Mengganti nama modul",
        "kunci": "B",
        "materi": "Nested loop",
    },
    {
        "q": "Hasil dari kode berikut:\nfor i in range(2):\n    for j in range(2):\n        print(i, j)\nJumlah baris output adalah...",
        "a": "2",
        "b": "3",
        "c": "4",
        "d": "5",
        "kunci": "C",
        "materi": "Nested loop",
    },
    {
        "q": "Method list untuk menambah elemen di akhir adalah...",
        "a": "insert()",
        "b": "append()",
        "c": "add()",
        "d": "push()",
        "kunci": "B",
        "materi": "Method List",
    },
    {
        "q": "Perhatikan kode:\ndata = [2, 4]\ndata.insert(1, 3)\nprint(data)\nHasilnya adalah...",
        "a": "[1, 2, 3, 4]",
        "b": "[2, 3, 4]",
        "c": "[3, 2, 4]",
        "d": "[2, 4, 3]",
        "kunci": "B",
        "materi": "Method List",
    },
    {
        "q": "Method yang menghapus dan mengembalikan elemen terakhir list adalah...",
        "a": "remove()",
        "b": "delete()",
        "c": "pop()",
        "d": "clear()",
        "kunci": "C",
        "materi": "Method List",
    },
    {
        "q": "Hasil print(\"Python\"[0:3]) adalah...",
        "a": "Pyt",
        "b": "yth",
        "c": "Pyth",
        "d": "hon",
        "kunci": "A",
        "materi": "String",
    },
    {
        "q": "Method string untuk mengubah semua huruf menjadi kapital adalah...",
        "a": "capitalize()",
        "b": "upper()",
        "c": "lower()",
        "d": "title()",
        "kunci": "B",
        "materi": "String",
    },
    {
        "q": "Hasil dari \"a-b-c\".split(\"-\") adalah...",
        "a": "\"abc\"",
        "b": "[\"a\", \"b\", \"c\"]",
        "c": "(\"a\", \"b\", \"c\")",
        "d": "{\"a\", \"b\", \"c\"}",
        "kunci": "B",
        "materi": "String",
    },
    {
        "q": "Tuple pada Python ditulis dengan...",
        "a": "Kurung siku []",
        "b": "Kurung kurawal {}",
        "c": "Kurung biasa ()",
        "d": "Tanda petik \"\"",
        "kunci": "C",
        "materi": "Tuple",
    },
    {
        "q": "Sifat utama tuple adalah...",
        "a": "Mutable (bisa diubah)",
        "b": "Immutable (tidak bisa diubah)",
        "c": "Selalu berisi angka",
        "d": "Tidak bisa diindeks",
        "kunci": "B",
        "materi": "Tuple",
    },
    {
        "q": "Perhatikan:\nt = (1, 2, 3)\nprint(t[1])\nOutputnya adalah...",
        "a": "1",
        "b": "2",
        "c": "3",
        "d": "(1, 2)",
        "kunci": "B",
        "materi": "Tuple",
    },
    {
        "q": "Dictionary menyimpan data dalam bentuk...",
        "a": "index: nilai saja",
        "b": "key: value",
        "c": "baris dan kolom Excel",
        "d": "hanya list bersarang",
        "kunci": "B",
        "materi": "Dictionary",
    },
    {
        "q": "Cara mengakses nilai nama dari siswa = {\"nama\": \"Dewi\", \"nilai\": 90} adalah...",
        "a": "siswa[0]",
        "b": "siswa.nama",
        "c": "siswa[\"nama\"]",
        "d": "siswa(nama)",
        "kunci": "C",
        "materi": "Dictionary",
    },
    {
        "q": "Perhatikan:\nd = {\"a\": 1, \"b\": 2}\nd[\"b\"] = 5\nprint(d)\nHasilnya...",
        "a": "{\"a\": 1, \"b\": 2}",
        "b": "{\"a\": 1, \"b\": 5}",
        "c": "{\"b\": 5}",
        "d": "Error",
        "kunci": "B",
        "materi": "Dictionary",
    },
    {
        "q": "Kata kunci untuk membuat fungsi di Python adalah...",
        "a": "func",
        "b": "function",
        "c": "def",
        "d": "define",
        "kunci": "C",
        "materi": "Fungsi",
    },
    {
        "q": "Apa fungsi utama return dalam sebuah fungsi?",
        "a": "Menampilkan teks ke layar saja",
        "b": "Mengembalikan nilai hasil fungsi",
        "c": "Menghapus variabel",
        "d": "Mengulang proses otomatis",
        "kunci": "B",
        "materi": "Fungsi",
    },
    {
        "q": "Perhatikan:\ndef kali(x, y):\n    return x * y\nprint(kali(3, 4))\nOutputnya adalah...",
        "a": "7",
        "b": "12",
        "c": "34",
        "d": "x * y",
        "kunci": "B",
        "materi": "Fungsi",
    },
    {
        "q": "Parameter default pada fungsi berguna untuk...",
        "a": "Menghapus fungsi",
        "b": "Memberi nilai bawaan jika argumen tidak dikirim",
        "c": "Mengubah tipe data otomatis",
        "d": "Menonaktifkan return",
        "kunci": "B",
        "materi": "Fungsi",
    },
    {
        "q": "Perintah untuk memakai modul matematika adalah...",
        "a": "include math",
        "b": "using math",
        "c": "import math",
        "d": "require math",
        "kunci": "C",
        "materi": "Modul",
    },
    {
        "q": "Hasil math.sqrt(49) adalah...",
        "a": "7.0",
        "b": "49",
        "c": "24.5",
        "d": "9.0",
        "kunci": "A",
        "materi": "Modul",
    },
    {
        "q": "Fungsi random.randint(1, 3) akan menghasilkan...",
        "a": "Selalu angka 1",
        "b": "Angka acak 1, 2, atau 3",
        "c": "Angka acak 0 sampai 3",
        "d": "List [1, 2, 3]",
        "kunci": "B",
        "materi": "Modul",
    },
    {
        "q": "Manakah yang benar tentang string di Python?",
        "a": "String bisa diubah elemennya seperti list",
        "b": "String bersifat immutable",
        "c": "String tidak bisa di-slicing",
        "d": "String hanya boleh huruf kecil",
        "kunci": "B",
        "materi": "String",
    },
    {
        "q": "Hasil dari \"-\".join([\"7\", \"5\"]) adalah...",
        "a": "[\"7\", \"-\", \"5\"]",
        "b": "7-5",
        "c": "75",
        "d": "Error",
        "kunci": "B",
        "materi": "String",
    },
    {
        "q": "Untuk mengurutkan list naik dipakai method...",
        "a": "order()",
        "b": "sort()",
        "c": "arrange()",
        "d": "sorted_list()",
        "kunci": "B",
        "materi": "Method List",
    },
    {
        "q": "Perhatikan:\nangka = [1, 2, 3]\nangka.remove(2)\nprint(angka)\nHasilnya...",
        "a": "[1, 3]",
        "b": "[2]",
        "c": "[1, 2]",
        "d": "[1, 2, 3, 2]",
        "kunci": "A",
        "materi": "Method List",
    },
    {
        "q": "Manakah akses dictionary yang SALAH?",
        "a": "data[\"nis\"]",
        "b": "data.get(\"nis\")",
        "c": "data.nis",
        "d": "data[\"nama\"]",
        "kunci": "C",
        "materi": "Dictionary",
    },
    {
        "q": "Jika fungsi tidak memakai return, nilai kembaliannya adalah...",
        "a": "0",
        "b": "False",
        "c": "None",
        "d": "Empty string",
        "kunci": "C",
        "materi": "Fungsi",
    },
    {
        "q": "Urutan langkah problem solving yang tepat adalah...",
        "a": "Kode dulu, baru pahami masalah",
        "b": "Pahami masalah → rancang → kode → uji",
        "c": "Uji → kode → hapus modul",
        "d": "Import → print → selesai",
        "kunci": "B",
        "materi": "Problem Solving",
    },
    {
        "q": "Perhatikan:\ndef status(n, kkm=77):\n    return \"Tuntas\" if n >= kkm else \"Belum\"\nprint(status(77))\nOutputnya...",
        "a": "Belum",
        "b": "Tuntas",
        "c": "77",
        "d": "Error",
        "kunci": "B",
        "materi": "Problem Solving",
    },
    {
        "q": "Untuk mengambil semua kunci dictionary dipakai...",
        "a": "data.values()",
        "b": "data.keys()",
        "c": "data.items() saja tanpa kunci",
        "d": "data.index()",
        "kunci": "B",
        "materi": "Dictionary",
    },
    {
        "q": "Hasil dari kode:\nfor i in range(1, 4):\n    print(\"*\" * i)\nBaris terakhir menampilkan...",
        "a": "*",
        "b": "**",
        "c": "***",
        "d": "****",
        "kunci": "C",
        "materi": "Nested loop",
    },
    {
        "q": "Unpacking tuple nama, kota = (\"Rafi\", \"Pamulang\") membuat variabel kota berisi...",
        "a": "Rafi",
        "b": "Pamulang",
        "c": "(\"Rafi\", \"Pamulang\")",
        "d": "Error",
        "kunci": "B",
        "materi": "Tuple",
    },
    {
        "q": "Modul yang tepat untuk membuat angka dadu acak 1–6 adalah...",
        "a": "math",
        "b": "os",
        "c": "random",
        "d": "sys",
        "kunci": "C",
        "materi": "Modul",
    },
    {
        "q": "Perhatikan:\ndef luas(p, l=4):\n    return p * l\nprint(luas(5))\nHasilnya...",
        "a": "9",
        "b": "20",
        "c": "5",
        "d": "Error karena l kosong",
        "kunci": "B",
        "materi": "Fungsi",
    },
    {
        "q": "Method string replace(\"a\", \"i\") pada \"makan\" menghasilkan...",
        "a": "mikin",
        "b": "mikan",
        "c": "makin",
        "d": "makan",
        "kunci": "A",
        "materi": "String",
    },
    {
        "q": "Struktur data yang tepat untuk biodata siswa (nama, nis, kelas) adalah...",
        "a": "Hanya integer",
        "b": "Dictionary",
        "c": "Boolean saja",
        "d": "Range",
        "kunci": "B",
        "materi": "Dictionary",
    },
    {
        "q": "Dalam nested if, blok dalam hanya dijalankan jika...",
        "a": "Selalu, tanpa syarat",
        "b": "Syarat if luar terpenuhi",
        "c": "Ada error di if luar",
        "d": "Loop sudah selesai",
        "kunci": "B",
        "materi": "Nested if",
    },
    {
        "q": "Tujuan utama memecah program menjadi fungsi adalah...",
        "a": "Agar file Python menjadi lebih besar",
        "b": "Agar kode lebih rapi dan bisa dipakai ulang",
        "c": "Agar tidak bisa diuji",
        "d": "Agar tuple menjadi list",
        "kunci": "B",
        "materi": "Problem Solving",
    },
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


def ensure_columns(cur):
    cur.execute("SHOW COLUMNS FROM materi LIKE 'semester'")
    if not cur.fetchone():
        cur.execute(
            "ALTER TABLE materi ADD COLUMN semester ENUM('Ganjil','Genap') NOT NULL DEFAULT 'Ganjil' AFTER urutan"
        )
    cur.execute("SHOW COLUMNS FROM ujian LIKE 'semester'")
    if not cur.fetchone():
        cur.execute(
            "ALTER TABLE ujian ADD COLUMN semester ENUM('Ganjil','Genap') NOT NULL DEFAULT 'Ganjil' AFTER jenis"
        )
    # pastikan data lama bertanda Ganjil
    cur.execute("UPDATE materi SET semester='Ganjil' WHERE semester IS NULL OR semester=''")
    cur.execute(
        """
        UPDATE ujian SET semester='Ganjil'
        WHERE jenis IN ('latihan','ulangan_harian','sumatif','sts_ganjil','sas')
          AND judul NOT LIKE '%Genap%'
        """
    )


def to_soal_item(item):
    return {
        "question": item["q"],
        "options": {"A": item["a"], "B": item["b"], "C": item["c"], "D": item["d"]},
        "answer": item["kunci"],
        "materi": item["materi"],
    }


def insert_ujian(cur, judul, deskripsi, jenis, materi_id, soal_items, durasi, jumlah, pembahasan=1):
    # hapus ujian genap lama dengan judul sama (agar bisa dijalankan ulang)
    cur.execute("SELECT id FROM ujian WHERE judul=%s AND semester='Genap'", (judul,))
    old = cur.fetchone()
    if old:
        cur.execute("DELETE FROM soal WHERE ujian_id=%s", (old["id"],))
        cur.execute("DELETE FROM ujian WHERE id=%s", (old["id"],))

    cur.execute(
        """
        INSERT INTO ujian
        (judul, deskripsi, jenis, semester, tingkat, materi_id, durasi_menit, jumlah_soal, nilai_kkm, acak_soal, tampil_pembahasan, aktif)
        VALUES (%s,%s,%s,'Genap','7',%s,%s,%s,77,1,%s,0)
        """,
        (judul, deskripsi, jenis, materi_id, durasi, jumlah, pembahasan),
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


def main():
    soal = [to_soal_item(x) for x in SOAL_GENAP]
    conn = connect()
    try:
        with conn.cursor() as cur:
            ensure_columns(cur)

            # bersihkan materi genap lama
            cur.execute("SELECT id FROM materi WHERE semester='Genap'")
            old_ids = [r["id"] for r in cur.fetchall()]
            if old_ids:
                cur.execute(
                    "UPDATE ujian SET materi_id=NULL WHERE materi_id IN (%s)"
                    % ",".join(["%s"] * len(old_ids)),
                    old_ids,
                )
                cur.execute("DELETE FROM materi WHERE semester='Genap'")

            materi_ids = []
            for m in MATERI_GENAP:
                cur.execute(
                    """
                    INSERT INTO materi (tingkat, urutan, semester, judul, ringkasan, isi_html, contoh_kode)
                    VALUES ('7', %s,'Genap',%s,%s,%s,%s)
                    """,
                    (m["urutan"], m["judul"], m["ringkasan"], m["isi_html"], m["contoh_kode"]),
                )
                materi_ids.append(cur.lastrowid)

            chunks = [
                (0, soal[0:6], "Latihan Genap 1: Nested if & Loop"),
                (2, soal[4:10], "Latihan Genap 2: List & String"),
                (4, soal[10:16], "Latihan Genap 3: Tuple & Dictionary"),
                (6, soal[16:24], "Latihan Genap 4: Fungsi & Modul"),
                (9, soal[24:32], "Latihan Genap 5: String, List, Dict Lanjutan"),
                (9, soal[32:40], "Latihan Genap 6: Problem Solving"),
            ]
            for materi_idx, qs, judul in chunks:
                insert_ujian(
                    cur,
                    judul,
                    "Latihan interaktif semester genap dengan pembahasan.",
                    "latihan",
                    materi_ids[materi_idx],
                    qs,
                    20,
                    len(qs),
                    1,
                )

            insert_ujian(
                cur,
                "UH Genap 1 - Nested, List, String",
                "Ulangan harian semester genap bagian 1.",
                "ulangan_harian",
                materi_ids[0],
                soal[0:12],
                30,
                12,
                1,
            )
            insert_ujian(
                cur,
                "UH Genap 2 - Tuple, Dict, Fungsi",
                "Ulangan harian semester genap bagian 2.",
                "ulangan_harian",
                materi_ids[4],
                soal[10:22],
                30,
                12,
                1,
            )
            insert_ujian(
                cur,
                "UH Genap 3 - Modul & Problem Solving",
                "Ulangan harian semester genap bagian 3.",
                "ulangan_harian",
                materi_ids[8],
                soal[20:32],
                30,
                12,
                1,
            )
            insert_ujian(
                cur,
                "Sumatif Genap Koding 7.5",
                "Penilaian sumatif materi semester genap.",
                "sumatif",
                None,
                soal[0:20],
                40,
                20,
                0,
            )

            # ganti STS Genap dengan bank soal genap
            cur.execute("SELECT id FROM ujian WHERE jenis='sts_genap'")
            for row in cur.fetchall():
                cur.execute("DELETE FROM soal WHERE ujian_id=%s", (row["id"],))
                cur.execute("DELETE FROM ujian WHERE id=%s", (row["id"],))
            insert_ujian(
                cur,
                "STS Genap Koding 7.5",
                "Sumatif Tengah Semester Genap.",
                "sts_genap",
                None,
                soal[0:25],
                60,
                25,
                0,
            )

            # SAS Genap khusus (seluruh materi genap)
            insert_ujian(
                cur,
                "SAS Genap Koding 7.5",
                "Sumatif Akhir Semester Genap — seluruh materi genap.",
                "sas",
                None,
                soal,
                90,
                40,
                0,
            )
            cur.execute("UPDATE ujian SET semester='Genap' WHERE judul LIKE '%Genap%'")

        print("Semester Genap siap.")
        print("- 10 materi genap")
        print("- 6 latihan, 3 UH, 1 sumatif, STS Genap, SAS Genap")
        print("- KKM 77")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
