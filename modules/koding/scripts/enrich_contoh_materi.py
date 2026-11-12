"""Tambah minimal 3 contoh soal + penyelesaian ke setiap materi."""
import re
import sys
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from koding.config import Config  # noqa: E402

MARKER = "<!-- CONTOH-SOAL-MATERI -->"


def blok(nomor, soal, kode, penjelasan, output=None):
    out = ""
    if output is not None:
        out = f"<p><strong>Output:</strong> <code>{output}</code></p>"
    return f"""
    <div class="card" style="margin:0.75rem 0;padding:0.9rem 1rem">
      <p><strong>Contoh soal {nomor}.</strong> {soal}</p>
      <pre class="code-box">{kode}</pre>
      {out}
      <p><strong>Penyelesaian:</strong> {penjelasan}</p>
    </div>
    """


def bagian(contoh_list):
    isi = "\n".join(
        blok(i, c["soal"], c["kode"], c["penjelasan"], c.get("output"))
        for i, c in enumerate(contoh_list, start=1)
    )
    return f"""
    {MARKER}
    <h3>Contoh soal &amp; penyelesaian</h3>
    <p>Kerjakan di pikiran dulu, lalu bandingkan dengan penyelesaian di bawahnya. Minimal tiga contoh untuk materi ini.</p>
    {isi}
    """


# Kunci = judul materi persis seperti di database
CONTOH = {
    "Pengenalan Python": [
        {
            "soal": "Tampilkan teks sambutan sekolah memakai print.",
            "kode": 'print("Selamat datang di SMP Muhammadiyah 22")',
            "output": "Selamat datang di SMP Muhammadiyah 22",
            "penjelasan": "String diapit tanda kutip, lalu dikirim ke <code>print()</code> agar muncul di layar.",
        },
        {
            "soal": "Tampilkan dua baris: nama mapel dan tahun pelajaran.",
            "kode": 'print("Mapel: Koding")\nprint("TP 2026/2027")',
            "output": "Mapel: Koding / TP 2026/2027 (dua baris)",
            "penjelasan": "Setiap <code>print</code> membuat baris baru. Cocok untuk menampilkan informasi berurutan.",
        },
        {
            "soal": "Hitung dan tampilkan hasil 7 + 5 tanpa variabel.",
            "kode": "print(7 + 5)",
            "output": "12",
            "penjelasan": "Angka tidak perlu kutip. Python menghitung ekspresi dulu, lalu menampilkan hasilnya.",
        },
    ],
    "Perintah Output: print()": [
        {
            "soal": "Cetak nama dan kelas dalam satu baris.",
            "kode": 'print("Aisyah", "kelas 7.5")',
            "output": "Aisyah kelas 7.5",
            "penjelasan": "Beberapa argumen pada <code>print</code> dipisah spasi secara bawaan.",
        },
        {
            "soal": "Cetak hasil perkalian 8 × 9.",
            "kode": "print(8 * 9)",
            "output": "72",
            "penjelasan": "Operator <code>*</code> dikerjakan sebelum dicetak.",
        },
        {
            "soal": "Cetak teks dan angka sekaligus.",
            "kode": 'print("Nilai KKM:", 77)',
            "output": "Nilai KKM: 77",
            "penjelasan": "String dan angka boleh digabung sebagai argumen terpisah pada <code>print</code>.",
        },
    ],
    "Variabel dan Aturan Nama": [
        {
            "soal": "Simpan nama siswa lalu tampilkan.",
            "kode": 'nama = "Rafi"\nprint(nama)',
            "output": "Rafi",
            "penjelasan": "Nilai disimpan di variabel <code>nama</code>, lalu dibaca saat di-<code>print</code>.",
        },
        {
            "soal": "Buat dua variabel umur dan tahun depan.",
            "kode": "umur = 13\ntahun_depan = umur + 1\nprint(tahun_depan)",
            "output": "14",
            "penjelasan": "Variabel boleh dipakai dalam ekspresi untuk menghasilkan nilai baru.",
        },
        {
            "soal": "Tunjukkan bahwa nama variabel case-sensitive.",
            "kode": 'Mapel = "Koding"\nmapel = "Informatika"\nprint(Mapel)\nprint(mapel)',
            "output": "Koding / Informatika",
            "penjelasan": "<code>Mapel</code> dan <code>mapel</code> dianggap berbeda oleh Python.",
        },
    ],
    "Tipe Data Dasar": [
        {
            "soal": "Buat variabel int, float, str, bool lalu cetak tipenya.",
            "kode": 'n = 90\nbb = 45.5\nnama = "Dewi"\nlulus = True\nprint(type(n), type(bb), type(nama), type(lulus))',
            "output": "&lt;class 'int'&gt; &lt;class 'float'&gt; &lt;class 'str'&gt; &lt;class 'bool'&gt;",
            "penjelasan": "<code>type()</code> memberitahu jenis data yang tersimpan.",
        },
        {
            "soal": "Gabungkan string nama dan kelas.",
            "kode": 'nama = "Budi"\nkelas = "7.5"\nprint(nama + " - " + kelas)',
            "output": "Budi - 7.5",
            "penjelasan": "Operator <code>+</code> pada string artinya penggabungan (concatenation).",
        },
        {
            "soal": "Ubah status lulus menjadi False lalu cetak.",
            "kode": "lulus = True\nlulus = False\nprint(lulus)",
            "output": "False",
            "penjelasan": "Nilai variabel boleh diganti. Boolean hanya <code>True</code> atau <code>False</code>.",
        },
    ],
    "Operator Aritmatika": [
        {
            "soal": "Hitung sisa bagi 20 dibagi 6.",
            "kode": "print(20 % 6)",
            "output": "2",
            "penjelasan": "<code>%</code> (modulus) menghasilkan sisa pembagian.",
        },
        {
            "soal": "Hitung pembagian bulat 17 // 5.",
            "kode": "print(17 // 5)",
            "output": "3",
            "penjelasan": "<code>//</code> membuang pecahan (floor division).",
        },
        {
            "soal": "Hitung 3 pangkat 4.",
            "kode": "print(3 ** 4)",
            "output": "81",
            "penjelasan": "<code>**</code> adalah operator pangkat: 3×3×3×3 = 81.",
        },
    ],
    "Input Pengguna & Konversi Tipe": [
        {
            "soal": "Ambil angka lalu tampilkan dua kalinya (simulasi tanpa input nyata).",
            "kode": 'angka = int("12")  # ganti dengan int(input("Angka: "))\nprint(angka * 2)',
            "output": "24",
            "penjelasan": "<code>input()</code> menghasilkan string, jadi perlu <code>int()</code> sebelum dihitung.",
        },
        {
            "soal": "Hitung luas persegi dari sisi yang diketik pengguna.",
            "kode": 'sisi = float("4.5")  # float(input("Sisi: "))\nprint("Luas:", sisi * sisi)',
            "output": "Luas: 20.25",
            "penjelasan": "Gunakan <code>float</code> jika sisi boleh desimal.",
        },
        {
            "soal": "Gabungkan sapaan dengan nama dari input.",
            "kode": 'nama = "Aina"  # input("Nama: ")\nprint("Halo,", nama)',
            "output": "Halo, Aina",
            "penjelasan": "Untuk teks, konversi tidak wajib karena <code>input</code> sudah string.",
        },
    ],
    "Komentar, Indentasi, dan Error": [
        {
            "soal": "Tulis komentar yang menjelaskan baris kode.",
            "kode": '# Menyimpan KKM mapel koding\nkkm = 77\nprint(kkm)',
            "output": "77",
            "penjelasan": "Teks setelah <code>#</code> diabaikan interpreter; berguna untuk catatan.",
        },
        {
            "soal": "Tunjukkan blok if dengan indentasi benar.",
            "kode": 'nilai = 80\nif nilai >= 77:\n    print("Tuntas")  # indentasi 4 spasi',
            "output": "Tuntas",
            "penjelasan": "Isi blok <code>if</code> harus menjorok; tanpa indentasi muncul IndentationError.",
        },
        {
            "soal": "Perbaiki ide SyntaxError pada string tanpa kutip penutup (versi benar).",
            "kode": 'print("Belajar Python")  # kutip harus berpasangan',
            "output": "Belajar Python",
            "penjelasan": "SyntaxError sering karena tanda kutip/kurung tidak lengkap.",
        },
    ],
    "Percabangan if-elif-else": [
        {
            "soal": "Tentukan tuntas/belum berdasarkan KKM 77.",
            "kode": 'nilai = 70\nif nilai >= 77:\n    print("Tuntas")\nelse:\n    print("Belum tuntas")',
            "output": "Belum tuntas",
            "penjelasan": "70 &lt; 77 sehingga cabang <code>else</code> yang dijalankan.",
        },
        {
            "soal": "Buat predikat A/B/C dari nilai.",
            "kode": 'nilai = 88\nif nilai >= 90:\n    print("A")\nelif nilai >= 80:\n    print("B")\nelse:\n    print("C")',
            "output": "B",
            "penjelasan": "<code>elif</code> dicek hanya jika <code>if</code> sebelumnya salah. 88 masuk rentang B.",
        },
        {
            "soal": "Cek bilangan genap atau ganjil.",
            "kode": "n = 15\nif n % 2 == 0:\n    print(\"Genap\")\nelse:\n    print(\"Ganjil\")",
            "output": "Ganjil",
            "penjelasan": "Sisa bagi 15%2 = 1, jadi ganjil.",
        },
    ],
    "Perulangan for dan while": [
        {
            "soal": "Cetak angka 1 sampai 5 dengan for.",
            "kode": "for i in range(1, 6):\n    print(i)",
            "output": "1 2 3 4 5 (masing-masing baris)",
            "penjelasan": "<code>range(1, 6)</code> menghasilkan 1..5 (batas akhir tidak ikut).",
        },
        {
            "soal": "Jumlahkan 1+2+3+4 dengan for.",
            "kode": "total = 0\nfor i in range(1, 5):\n    total = total + i\nprint(total)",
            "output": "10",
            "penjelasan": "Akumulator <code>total</code> ditambah tiap putaran loop.",
        },
        {
            "soal": "Hitung mundur 3,2,1 dengan while.",
            "kode": "n = 3\nwhile n > 0:\n    print(n)\n    n = n - 1",
            "output": "3 2 1",
            "penjelasan": "Variabel <code>n</code> dikurangi agar kondisi while akhirnya False.",
        },
    ],
    "List dan Indexing": [
        {
            "soal": "Ambil elemen ketiga dari list buah.",
            "kode": 'buah = ["Apel", "Pisang", "Jeruk", "Mangga"]\nprint(buah[2])',
            "output": "Jeruk",
            "penjelasan": "Indeks dimulai dari 0, jadi indeks 2 = elemen ketiga.",
        },
        {
            "soal": "Ubah nilai kedua pada list angka menjadi 10.",
            "kode": "angka = [2, 4, 6]\nangka[1] = 10\nprint(angka)",
            "output": "[2, 10, 6]",
            "penjelasan": "List bersifat mutable: elemen bisa diganti lewat indeks.",
        },
        {
            "soal": "Tampilkan panjang list siswa.",
            "kode": 'siswa = ["Aina", "Bimasena", "Danish"]\nprint(len(siswa))',
            "output": "3",
            "penjelasan": "<code>len()</code> menghitung banyak elemen list.",
        },
    ],
    "Review Kelas 7 & Set": [
        {
            "soal": "Buat set dari list yang punya duplikat.",
            "kode": "data = [1, 2, 2, 3, 3, 3]\nunik = set(data)\nprint(unik)",
            "output": "{1, 2, 3}",
            "penjelasan": "Set otomatis membuang duplikat.",
        },
        {
            "soal": "Cari irisan dua himpunan kelas.",
            "kode": 'a = {"Aina", "Budi", "Citra"}\nb = {"Budi", "Dewi"}\nprint(a & b)',
            "output": "{'Budi'}",
            "penjelasan": "Operator <code>&amp;</code> menghasilkan anggota yang ada di kedua set.",
        },
        {
            "soal": "Gabungkan dua set NIS.",
            "kode": "x = {101, 102}\ny = {102, 103}\nprint(x | y)",
            "output": "{101, 102, 103}",
            "penjelasan": "Operator <code>|</code> adalah gabungan (union).",
        },
    ],
    "List Comprehension": [
        {
            "soal": "Buat list kuadrat 1..5.",
            "kode": "kuadrat = [x * x for x in range(1, 6)]\nprint(kuadrat)",
            "output": "[1, 4, 9, 16, 25]",
            "penjelasan": "Ekspresi <code>x*x</code> dievaluasi untuk setiap x pada range.",
        },
        {
            "soal": "Ambil hanya bilangan genap 0..9.",
            "kode": "genap = [n for n in range(10) if n % 2 == 0]\nprint(genap)",
            "output": "[0, 2, 4, 6, 8]",
            "penjelasan": "Bagian <code>if</code> memfilter elemen sebelum dimasukkan ke list baru.",
        },
        {
            "soal": "Ubah semua nama menjadi huruf besar.",
            "kode": 'nama = ["ani", "budi"]\nbesar = [n.upper() for n in nama]\nprint(besar)',
            "output": "['ANI', 'BUDI']",
            "penjelasan": "Method string bisa dipakai di dalam comprehension.",
        },
    ],
    "Fungsi Lanjutan": [
        {
            "soal": "Jumlahkan banyak angka dengan *args.",
            "kode": "def jumlah(*angka):\n    return sum(angka)\nprint(jumlah(2, 4, 6, 8))",
            "output": "20",
            "penjelasan": "<code>*args</code> menampung argumen menjadi tuple lalu dijumlahkan.",
        },
        {
            "soal": "Buat sapaan dengan parameter default.",
            "kode": 'def sapa(nama, sapaan="Halo"):\n    return f"{sapaan}, {nama}!"\nprint(sapa("Rafi"))\nprint(sapa("Dewi", "Selamat pagi"))',
            "output": "Halo, Rafi! / Selamat pagi, Dewi!",
            "penjelasan": "Jika argumen kedua tidak diisi, nilai default dipakai.",
        },
        {
            "soal": "Gunakan lambda untuk mengalikan dua bilangan.",
            "kode": "kali = lambda a, b: a * b\nprint(kali(6, 7))",
            "output": "42",
            "penjelasan": "Lambda cocok untuk fungsi singkat satu ekspresi.",
        },
    ],
    "Exception Handling": [
        {
            "soal": "Tangani konversi string non-angka.",
            "kode": 'try:\n    n = int("abc")\nexcept ValueError:\n    print("Harus angka")',
            "output": "Harus angka",
            "penjelasan": "<code>int(\"abc\")</code> memicu ValueError yang ditangkap except.",
        },
        {
            "soal": "Tangani pembagian nol.",
            "kode": "try:\n    print(10 / 0)\nexcept ZeroDivisionError:\n    print(\"Tidak boleh nol\")",
            "output": "Tidak boleh nol",
            "penjelasan": "Tanpa except, program berhenti; dengan except, pesan ramah ditampilkan.",
        },
        {
            "soal": "Pakai finally setelah try berhasil.",
            "kode": 'try:\n    print(int("12"))\nexcept ValueError:\n    print("err")\nfinally:\n    print("selesai")',
            "output": "12 / selesai",
            "penjelasan": "<code>finally</code> selalu jalan, baik ada error maupun tidak.",
        },
    ],
    "File Handling Dasar": [
        {
            "soal": "Tulis dua baris ke file teks.",
            "kode": 'with open("catatan.txt", "w", encoding="utf-8") as f:\n    f.write("Baris 1\\n")\n    f.write("Baris 2\\n")\nprint("tersimpan")',
            "output": "tersimpan",
            "penjelasan": "Mode <code>w</code> membuat/menimpa file. <code>with</code> menutup file otomatis.",
        },
        {
            "soal": "Baca kembali isi file.",
            "kode": 'with open("catatan.txt", "r", encoding="utf-8") as f:\n    isi = f.read()\nprint(isi)',
            "output": "Baris 1 / Baris 2",
            "penjelasan": "<code>read()</code> mengembalikan seluruh teks sebagai string.",
        },
        {
            "soal": "Tambah catatan di akhir file (append).",
            "kode": 'with open("catatan.txt", "a", encoding="utf-8") as f:\n    f.write("Baris 3\\n")\nprint("ditambah")',
            "output": "ditambah",
            "penjelasan": "Mode <code>a</code> tidak menghapus isi lama; menulis di akhir.",
        },
    ],
    "Modul Sendiri": [
        {
            "soal": "Definisikan fungsi luas di modul hitung (disimulasikan).",
            "kode": "def luas_persegi(s):\n    return s * s\nprint(luas_persegi(6))",
            "output": "36",
            "penjelasan": "Fungsi ini biasanya disimpan di <code>hitung.py</code> lalu diimpor.",
        },
        {
            "soal": "Tambah fungsi keliling pada modul yang sama.",
            "kode": "def keliling_persegi(s):\n    return 4 * s\nprint(keliling_persegi(6))",
            "output": "24",
            "penjelasan": "Satu modul boleh berisi banyak fungsi terkait.",
        },
        {
            "soal": "Panggil dua fungsi modul berurutan.",
            "kode": "def luas_persegi(s):\n    return s * s\ndef keliling_persegi(s):\n    return 4 * s\ns = 5\nprint(luas_persegi(s), keliling_persegi(s))",
            "output": "25 20",
            "penjelasan": "Setelah diimpor, fungsi dipanggil seperti fungsi lokal.",
        },
    ],
    "OOP: Class dan Object": [
        {
            "soal": "Buat class kosong Siswa lalu dua object.",
            "kode": "class Siswa:\n    pass\na = Siswa()\nb = Siswa()\nprint(type(a), type(b))",
            "output": "&lt;class '__main__.Siswa'&gt; (dua kali)",
            "penjelasan": "Class adalah cetakan; <code>a</code> dan <code>b</code> object berbeda.",
        },
        {
            "soal": "Tambah method sapa pada class.",
            "kode": 'class Siswa:\n    def sapa(self):\n        print("Halo siswa!")\nSiswa().sapa()',
            "output": "Halo siswa!",
            "penjelasan": "Method dipanggil lewat object: <code>object.method()</code>.",
        },
        {
            "soal": "Panggil method dari dua object.",
            "kode": 'class Siswa:\n    def sapa(self):\n        print("Halo")\nSiswa().sapa()\nSiswa().sapa()',
            "output": "Halo / Halo",
            "penjelasan": "Setiap object memakai method yang sama dari class.",
        },
    ],
    "Atribut dan Method": [
        {
            "soal": "Isi atribut merk pada object Mobil.",
            "kode": 'class Mobil:\n    def bunyi(self):\n        print("Broom!")\nm = Mobil()\nm.merk = "Avanza"\nprint(m.merk)\nm.bunyi()',
            "output": "Avanza / Broom!",
            "penjelasan": "Atribut = data; method = perilaku.",
        },
        {
            "soal": "Tambah atribut tahun lalu cetak keduanya.",
            "kode": 'class Mobil:\n    pass\nm = Mobil()\nm.merk = "Brio"\nm.tahun = 2024\nprint(m.merk, m.tahun)',
            "output": "Brio 2024",
            "penjelasan": "Satu object boleh punya banyak atribut.",
        },
        {
            "soal": "Buat dua object dengan atribut berbeda.",
            "kode": 'class Buku:\n    pass\na = Buku(); a.judul = "Python"\nb = Buku(); b.judul = "Algoritma"\nprint(a.judul, b.judul)',
            "output": "Python Algoritma",
            "penjelasan": "Object sejenis bisa menyimpan nilai atribut yang berbeda.",
        },
    ],
    "Constructor __init__": [
        {
            "soal": "Buat Siswa dengan __init__ nama dan nilai.",
            "kode": 'class Siswa:\n    def __init__(self, nama, nilai):\n        self.nama = nama\n        self.nilai = nilai\ns = Siswa("Dewi", 85)\nprint(s.nama, s.nilai)',
            "output": "Dewi 85",
            "penjelasan": "<code>__init__</code> mengisi atribut saat object dibuat.",
        },
        {
            "soal": "Tambah method status berdasarkan KKM 77.",
            "kode": 'class Siswa:\n    def __init__(self, nama, nilai):\n        self.nama = nama\n        self.nilai = nilai\n    def status(self):\n        return "Tuntas" if self.nilai >= 77 else "Belum"\nprint(Siswa("Budi", 70).status())',
            "output": "Belum",
            "penjelasan": "Method memakai atribut <code>self.nilai</code> yang diisi di __init__.",
        },
        {
            "soal": "Buat dua siswa dan bandingkan statusnya.",
            "kode": 'class Siswa:\n    def __init__(self, nama, nilai):\n        self.nama = nama\n        self.nilai = nilai\n    def status(self):\n        return "Tuntas" if self.nilai >= 77 else "Belum"\na = Siswa("Aisyah", 90)\nb = Siswa("Rafi", 75)\nprint(a.status(), b.status())',
            "output": "Tuntas Belum",
            "penjelasan": "Setiap object punya nilai sendiri sehingga status bisa berbeda.",
        },
    ],
    "Proyek Mini OOP Ganjil": [
        {
            "soal": "Class Produk menghitung harga setelah diskon.",
            "kode": 'class Produk:\n    def __init__(self, nama, harga):\n        self.nama = nama\n        self.harga = harga\n    def diskon(self, persen):\n        return self.harga * (100 - persen) / 100\np = Produk("Pulpen", 5000)\nprint(p.diskon(10))',
            "output": "4500.0",
            "penjelasan": "Diskon 10% dari 5000 = 4500.",
        },
        {
            "soal": "Tambah method info untuk menampilkan nama dan harga.",
            "kode": 'class Produk:\n    def __init__(self, nama, harga):\n        self.nama = nama\n        self.harga = harga\n    def info(self):\n        return f"{self.nama}: Rp{self.harga}"\nprint(Produk("Buku", 15000).info())',
            "output": "Buku: Rp15000",
            "penjelasan": "Method membaca atribut object untuk menyusun teks.",
        },
        {
            "soal": "Hitung diskon 20% untuk produk lain.",
            "kode": 'class Produk:\n    def __init__(self, nama, harga):\n        self.nama = nama\n        self.harga = harga\n    def diskon(self, persen):\n        return self.harga * (100 - persen) / 100\nprint(Produk("Penggaris", 8000).diskon(20))',
            "output": "6400.0",
            "penjelasan": "Class yang sama dipakai ulang untuk object berbeda.",
        },
    ],
    "Inheritance (Pewarisan)": [
        {
            "soal": "Class Kucing mewarisi Hewan lalu override suara.",
            "kode": 'class Hewan:\n    def suara(self):\n        print("...")\nclass Kucing(Hewan):\n    def suara(self):\n        print("Meong")\nKucing().suara()',
            "output": "Meong",
            "penjelasan": "Method anak mengganti (override) method induk.",
        },
        {
            "soal": "Class Anjing juga mewarisi Hewan.",
            "kode": 'class Hewan:\n    def suara(self):\n        print("...")\nclass Anjing(Hewan):\n    def suara(self):\n        print("Guk")\nAnjing().suara()',
            "output": "Guk",
            "penjelasan": "Banyak class anak boleh mewarisi induk yang sama.",
        },
        {
            "soal": "Panggil method induk jika anak tidak override.",
            "kode": 'class Hewan:\n    def gerak(self):\n        print("bergerak")\nclass Burung(Hewan):\n    pass\nBurung().gerak()',
            "output": "bergerak",
            "penjelasan": "Jika tidak di-override, method induk tetap dipakai.",
        },
    ],
    "Encapsulation Dasar": [
        {
            "soal": "Setor uang ke rekening lewat method.",
            "kode": 'class Rekening:\n    def __init__(self, saldo):\n        self.__saldo = saldo\n    def lihat(self):\n        return self.__saldo\n    def setor(self, x):\n        if x > 0:\n            self.__saldo += x\nr = Rekening(1000)\nr.setor(500)\nprint(r.lihat())',
            "output": "1500",
            "penjelasan": "Saldo dilindungi; perubahan hanya lewat method setor.",
        },
        {
            "soal": "Tolak setoran negatif.",
            "kode": 'class Rekening:\n    def __init__(self, saldo):\n        self.__saldo = saldo\n    def lihat(self):\n        return self.__saldo\n    def setor(self, x):\n        if x > 0:\n            self.__saldo += x\n        else:\n            print("Setoran harus positif")\nr = Rekening(1000)\nr.setor(-50)\nprint(r.lihat())',
            "output": "Setoran harus positif / 1000",
            "penjelasan": "Validasi di method menjaga data tetap aman.",
        },
        {
            "soal": "Lihat saldo awal tanpa mengubahnya.",
            "kode": 'class Rekening:\n    def __init__(self, saldo):\n        self.__saldo = saldo\n    def lihat(self):\n        return self.__saldo\nprint(Rekening(2500).lihat())',
            "output": "2500",
            "penjelasan": "Getter <code>lihat()</code> membaca atribut privat.",
        },
    ],
    "JSON Sederhana": [
        {
            "soal": "Ubah dict menjadi string JSON.",
            "kode": 'import json\ndata = {"nama": "Rafi", "nilai": 88}\nprint(json.dumps(data))',
            "output": '{"nama": "Rafi", "nilai": 88}',
            "penjelasan": "<code>dumps</code> mengubah struktur Python menjadi teks JSON.",
        },
        {
            "soal": "Kembalikan string JSON menjadi dict.",
            "kode": 'import json\nteks = \'{"nama": "Aina", "nilai": 91}\'\ndata = json.loads(teks)\nprint(data["nama"], data["nilai"])',
            "output": "Aina 91",
            "penjelasan": "<code>loads</code> mem-parsing teks JSON ke dict/list Python.",
        },
        {
            "soal": "Simpan list mapel dalam JSON.",
            "kode": 'import json\ndata = {"mapel": ["Koding", "Matematika"]}\nprint(json.dumps(data, ensure_ascii=False))',
            "output": '{"mapel": ["Koding", "Matematika"]}',
            "penjelasan": "List di dalam dict ikut terserialisasi ke JSON.",
        },
    ],
    "Algoritma Searching": [
        {
            "soal": "Cari angka 9 dengan linear search.",
            "kode": "def linear_search(data, target):\n    for i, x in enumerate(data):\n        if x == target:\n            return i\n    return -1\nprint(linear_search([4, 7, 9, 2], 9))",
            "output": "2",
            "penjelasan": "9 ditemukan di indeks 2.",
        },
        {
            "soal": "Cari data yang tidak ada.",
            "kode": "def linear_search(data, target):\n    for i, x in enumerate(data):\n        if x == target:\n            return i\n    return -1\nprint(linear_search([4, 7, 9, 2], 5))",
            "output": "-1",
            "penjelasan": "Konvensi mengembalikan -1 jika target tidak ditemukan.",
        },
        {
            "soal": "Cari nama dalam list string.",
            "kode": 'def linear_search(data, target):\n    for i, x in enumerate(data):\n        if x == target:\n            return i\n    return -1\nprint(linear_search(["Aina", "Budi", "Citra"], "Budi"))',
            "output": "1",
            "penjelasan": "Algoritma sama untuk tipe data apa pun yang bisa dibandingkan.",
        },
    ],
    "Algoritma Sorting": [
        {
            "soal": "Urutkan [5,1,4,2] dengan bubble sort.",
            "kode": "def bubble_sort(data):\n    a = data[:]\n    n = len(a)\n    for i in range(n):\n        for j in range(0, n - i - 1):\n            if a[j] > a[j + 1]:\n                a[j], a[j + 1] = a[j + 1], a[j]\n    return a\nprint(bubble_sort([5, 1, 4, 2]))",
            "output": "[1, 2, 4, 5]",
            "penjelasan": "Pasangan bersebelahan ditukar berulang sampai terurut.",
        },
        {
            "soal": "Bandingkan dengan sorted bawaan.",
            "kode": "angka = [5, 1, 4, 2]\nprint(sorted(angka))\nprint(angka)",
            "output": "[1, 2, 4, 5] / [5, 1, 4, 2]",
            "penjelasan": "<code>sorted</code> mengembalikan list baru; list asli tidak berubah.",
        },
        {
            "soal": "Urutkan nama secara alfabet.",
            "kode": 'nama = ["Citra", "Aina", "Budi"]\nprint(sorted(nama))',
            "output": "['Aina', 'Budi', 'Citra']",
            "penjelasan": "String diurutkan leksikografis (kamus).",
        },
    ],
    "Rekursi Dasar": [
        {
            "soal": "Hitung faktorial 5 secara rekursif.",
            "kode": "def faktorial(n):\n    if n <= 1:\n        return 1\n    return n * faktorial(n - 1)\nprint(faktorial(5))",
            "output": "120",
            "penjelasan": "5×4×3×2×1. Base case n&lt;=1 menghentikan rekursi.",
        },
        {
            "soal": "Hitung mundur dengan rekursi.",
            "kode": 'def hitung_mundur(n):\n    if n <= 0:\n        print("selesai")\n        return\n    print(n)\n    hitung_mundur(n - 1)\nhitung_mundur(3)',
            "output": "3 2 1 selesai",
            "penjelasan": "Setiap panggilan mengurangi n menuju base case.",
        },
        {
            "soal": "Faktorial 1 harus 1.",
            "kode": "def faktorial(n):\n    if n <= 1:\n        return 1\n    return n * faktorial(n - 1)\nprint(faktorial(1))",
            "output": "1",
            "penjelasan": "Base case langsung mengembalikan 1 tanpa rekursi lanjut.",
        },
    ],
    "GUI Sederhana dengan Tkinter": [
        {
            "soal": "Siapkan jendela dengan judul.",
            "kode": 'import tkinter as tk\nroot = tk.Tk()\nroot.title("Koding 8")\nprint(root.title())\n# root.mainloop()  # jalankan di komputer lokal',
            "output": "Koding 8",
            "penjelasan": "<code>Tk()</code> membuat jendela; <code>title</code> mengatur judul.",
        },
        {
            "soal": "Tambah label teks.",
            "kode": 'import tkinter as tk\nroot = tk.Tk()\ntk.Label(root, text="Halo Kelas 8").pack()\nprint("label siap")\n# root.mainloop()',
            "output": "label siap",
            "penjelasan": "<code>pack()</code> menaruh widget di jendela.",
        },
        {
            "soal": "Tambah tombol tutup.",
            "kode": 'import tkinter as tk\nroot = tk.Tk()\ntk.Button(root, text="Tutup", command=root.destroy).pack()\nprint("tombol siap")\n# root.mainloop()',
            "output": "tombol siap",
            "penjelasan": "<code>command</code> menentukan fungsi saat tombol diklik.",
        },
    ],
    "Debugging & Testing Dasar": [
        {
            "soal": "Fungsi rata-rata dengan assert data tidak kosong.",
            "kode": 'def rata(data):\n    assert len(data) > 0, "Data kosong"\n    return sum(data) / len(data)\nprint(rata([80, 90, 70]))',
            "output": "80.0",
            "penjelasan": "Assert lolos karena list berisi tiga nilai.",
        },
        {
            "soal": "Tangkap AssertionError pada list kosong.",
            "kode": 'def rata(data):\n    assert len(data) > 0, "Data kosong"\n    return sum(data) / len(data)\ntry:\n    print(rata([]))\nexcept AssertionError as e:\n    print("Tertangkap:", e)',
            "output": "Tertangkap: Data kosong",
            "penjelasan": "Assert gagal memicu AssertionError yang bisa ditangkap.",
        },
        {
            "soal": "Debug dengan print nilai variabel.",
            "kode": 'nilai = [80, 90]\ntotal = sum(nilai)\nprint("DEBUG total=", total)\nprint("rata=", total / len(nilai))',
            "output": "DEBUG total= 170 / rata= 85.0",
            "penjelasan": "Print sementara membantu memastikan nilai di tiap langkah benar.",
        },
    ],
    "Best Practice & Dokumentasi": [
        {
            "soal": "Tulis fungsi luas segitiga dengan docstring.",
            "kode": "def luas_segitiga(alas, tinggi):\n    '''Menghitung luas segitiga.'''\n    return 0.5 * alas * tinggi\nprint(luas_segitiga(10, 4))\nprint(luas_segitiga.__doc__)",
            "output": "20.0 / Menghitung luas segitiga.",
            "penjelasan": "Docstring menjelaskan tujuan fungsi; bisa dibaca lewat __doc__.",
        },
        {
            "soal": "Pakai nama variabel yang bermakna.",
            "kode": 'jumlah_siswa = 32\nnilai_kkm = 77\nprint(jumlah_siswa, nilai_kkm)',
            "output": "32 77",
            "penjelasan": "Nama jelas lebih mudah dipahami daripada a, b, x1.",
        },
        {
            "soal": "Pisahkan hitung dan tampil ke dua fungsi.",
            "kode": 'def hitung_luas(s):\n    return s * s\ndef tampil_luas(s):\n    print("Luas:", hitung_luas(s))\ntampil_luas(5)',
            "output": "Luas: 25",
            "penjelasan": "Satu fungsi satu tugas membuat kode lebih rapi (best practice).",
        },
    ],
    "Proyek Akhir Kelas 8": [
        {
            "soal": "Tambah dua nilai siswa ke NilaiApp.",
            "kode": 'class NilaiApp:\n    def __init__(self):\n        self.data = {}\n    def tambah(self, nama, nilai):\n        self.data[nama] = nilai\napp = NilaiApp()\napp.tambah("Aisyah", 90)\napp.tambah("Budi", 78)\nprint(app.data)',
            "output": "{'Aisyah': 90, 'Budi': 78}",
            "penjelasan": "Dict di dalam class menyimpan pasangan nama–nilai.",
        },
        {
            "soal": "Hitung rata-rata nilai.",
            "kode": 'class NilaiApp:\n    def __init__(self):\n        self.data = {}\n    def tambah(self, nama, nilai):\n        self.data[nama] = nilai\n    def rata(self):\n        return sum(self.data.values()) / len(self.data) if self.data else 0\napp = NilaiApp()\napp.tambah("Aisyah", 90)\napp.tambah("Budi", 80)\nprint(app.rata())',
            "output": "85.0",
            "penjelasan": "Method rata memakai seluruh nilai yang tersimpan.",
        },
        {
            "soal": "Siapkan penyimpanan ke JSON (tanpa wajib menulis file).",
            "kode": 'import json\ndata = {"Aisyah": 90, "Budi": 78}\nteks = json.dumps(data, ensure_ascii=False, indent=2)\nprint(teks)',
            "output": "JSON terformat berisi dua siswa",
            "penjelasan": "Pada proyek akhir, teks ini biasanya ditulis ke file dengan json.dump.",
        },
    ],
    # ----- Kelas 9 (project-based) -----
    "Project Kickoff: Ide & Kebutuhan": [
        {
            "soal": "Tulis brief project: masalah, tujuan, dan 3 fitur MVP.",
            "kode": 'project = {\n  "masalah": "Nilai siswa tercecer di kertas",\n  "tujuan": "Aplikasi pencatat nilai sederhana",\n  "mvp": ["tambah nilai", "lihat daftar", "hitung rata"]\n}\nprint(project["tujuan"])\nprint(len(project["mvp"]), "fitur wajib")',
            "output": "Aplikasi pencatat nilai sederhana / 3 fitur wajib",
            "penjelasan": "Kickoff merangkum masalah, tujuan, dan daftar fitur wajib sebelum coding.",
        },
        {
            "soal": "Tandai fitur wajib vs opsional.",
            "kode": 'fitur = [("tambah", True), ("laporan PDF", False), ("cari", True)]\nwajib = [n for n, w in fitur if w]\nprint(wajib)',
            "output": "['tambah', 'cari']",
            "penjelasan": "MVP hanya mengambil fitur yang wajib agar project tetap terarah.",
        },
        {
            "soal": "Cetak checklist kickoff yang sudah diisi.",
            "kode": 'cek = {"ide": True, "pengguna": True, "mvp": True, "risiko": False}\nprint("siap:", all(cek.values()))\nprint([k for k, v in cek.items() if not v])',
            "output": "siap: False / ['risiko']",
            "penjelasan": "Checklist memastikan elemen kickoff lengkap sebelum masuk desain.",
        },
    ],
    "Desain Data & Struktur Folder Project": [
        {
            "soal": "Susun record siswa sebagai dict.",
            "kode": 'siswa = {"nis": "2909001", "nama": "Kirana", "nilai": 88}\nprint(siswa["nama"], siswa["nilai"])',
            "output": "Kirana 88",
            "penjelasan": "Field data ditentukan dulu agar struktur record konsisten di seluruh project.",
        },
        {
            "soal": "Cetak peta folder project sederhana.",
            "kode": 'folder = ["main.py", "models.py", "storage.py", "data/", "README.md"]\nfor f in folder:\n    print("-", f)',
            "output": "- main.py ... - README.md",
            "penjelasan": "Struktur folder membantu memisahkan alur, model, dan penyimpanan.",
        },
        {
            "soal": "Buat list of dict sebagai koleksi data awal.",
            "kode": 'data = [\n  {"nama": "Kirana", "nilai": 88},\n  {"nama": "Dimas", "nilai": 75},\n]\nprint(len(data), "record")\nprint(data[0]["nama"])',
            "output": "2 record / Kirana",
            "penjelasan": "List of dict adalah bentuk data yang sering dipakai di project Kelas 9.",
        },
    ],
    "Project CLI: Menu Aplikasi": [
        {
            "soal": "Buat loop menu dengan pilihan keluar 0.",
            "kode": 'pilihan = "1"\nwhile pilihan != "0":\n    print("1. Lihat  0. Keluar")\n    pilihan = "0"  # simulasi input keluar\nprint("selesai")',
            "output": "1. Lihat  0. Keluar / selesai",
            "penjelasan": "Menu CLI memakai loop sampai pengguna memilih keluar.",
        },
        {
            "soal": "Panggil fungsi sesuai pilihan menu.",
            "kode": 'def lihat():\n    print("daftar kosong")\ndef jalankan(p):\n    if p == "1":\n        lihat()\n    elif p == "0":\n        print("keluar")\njalankan("1")\njalankan("0")',
            "output": "daftar kosong / keluar",
            "penjelasan": "Setiap pilihan menu memicu fungsi terkait.",
        },
        {
            "soal": "Tolak pilihan menu yang tidak dikenal.",
            "kode": 'p = "9"\nif p not in ("0", "1", "2"):\n    print("pilihan tidak valid")\nelse:\n    print("ok")',
            "output": "pilihan tidak valid",
            "penjelasan": "Validasi pilihan mencegah menu masuk cabang yang salah.",
        },
    ],
    "Modularisasi Project": [
        {
            "soal": "Pisahkan fungsi hitung ke modul logika (disimulasikan).",
            "kode": '# seolah di logic.py\ndef rata(nilai):\n    return sum(nilai) / len(nilai) if nilai else 0\n# main memakai fungsi itu\nprint(rata([80, 90]))',
            "output": "85.0",
            "penjelasan": "Modularisasi memisahkan tanggung jawab agar file tidak membengkak.",
        },
        {
            "soal": "Simulasikan import nama fungsi dari modul.",
            "kode": 'def simpan(data):\n    return f"tersimpan:{len(data)}"\nstorage_simpan = simpan  # seperti from storage import simpan\nprint(storage_simpan([1, 2, 3]))',
            "output": "tersimpan:3",
            "penjelasan": "main.py biasanya hanya mengatur alur dan memanggil modul lain.",
        },
        {
            "soal": "Tunjukkan pemisahan models vs storage.",
            "kode": 'class Siswa:\n    def __init__(self, nama):\n        self.nama = nama\ndef ke_dict(s):\n    return {"nama": s.nama}\ns = Siswa("Salma")\nprint(ke_dict(s))',
            "output": "{'nama': 'Salma'}",
            "penjelasan": "Model menyimpan bentuk data; storage fokus baca/tulis.",
        },
    ],
    "OOP di Project Nyata": [
        {
            "soal": "Buat service class untuk menambah nilai.",
            "kode": 'class NilaiService:\n    def __init__(self):\n        self.data = []\n    def tambah(self, nama, nilai):\n        self.data.append({"nama": nama, "nilai": nilai})\nsvc = NilaiService()\nsvc.tambah("Kirana", 90)\nprint(svc.data)',
            "output": "[{'nama': 'Kirana', 'nilai': 90}]",
            "penjelasan": "Service class mengelola operasi data project.",
        },
        {
            "soal": "Hitung rata-rata lewat method service.",
            "kode": 'class NilaiService:\n    def __init__(self, data):\n        self.data = data\n    def rata(self):\n        if not self.data:\n            return 0\n        return sum(x["nilai"] for x in self.data) / len(self.data)\nsvc = NilaiService([{"nilai": 80}, {"nilai": 100}])\nprint(svc.rata())',
            "output": "90.0",
            "penjelasan": "Method rata menjaga logika perhitungan tetap di satu tempat.",
        },
        {
            "soal": "Cari data berdasarkan nama.",
            "kode": 'class NilaiService:\n    def __init__(self, data):\n        self.data = data\n    def cari(self, nama):\n        for d in self.data:\n            if d["nama"] == nama:\n                return d\n        return None\nsvc = NilaiService([{"nama": "Dimas", "nilai": 77}])\nprint(svc.cari("Dimas"))',
            "output": "{'nama': 'Dimas', 'nilai': 77}",
            "penjelasan": "Pencarian adalah operasi umum pada service project.",
        },
    ],
    "Persistensi Project dengan JSON": [
        {
            "soal": "Ubah list dict menjadi teks JSON.",
            "kode": 'import json\ndata = [{"nama": "Kirana", "nilai": 88}]\nteks = json.dumps(data, ensure_ascii=False)\nprint(teks)',
            "output": '[{"nama": "Kirana", "nilai": 88}]',
            "penjelasan": "json.dumps mengubah data Python menjadi teks siap disimpan.",
        },
        {
            "soal": "Muat kembali data dari string JSON.",
            "kode": 'import json\nteks = \'[{"nama": "Dimas", "nilai": 80}]\'\ndata = json.loads(teks)\nprint(data[0]["nama"])',
            "output": "Dimas",
            "penjelasan": "json.loads mengembalikan struktur Python dari teks JSON.",
        },
        {
            "soal": "Siapkan payload simpan project (tanpa wajib tulis file).",
            "kode": 'import json\npayload = {"versi": 1, "data": [{"nama": "Salma", "nilai": 92}]}\nprint(json.dumps(payload, indent=2))',
            "output": "JSON terformat berisi versi dan data",
            "penjelasan": "Project biasanya membungkus data dengan metadata seperti versi.",
        },
    ],
    "Validasi & Exception pada Project": [
        {
            "soal": "Validasi nilai harus 0–100.",
            "kode": 'def valid_nilai(n):\n    if not isinstance(n, (int, float)):\n        return False, "bukan angka"\n    if n < 0 or n > 100:\n        return False, "di luar rentang"\n    return True, "ok"\nprint(valid_nilai(105))\nprint(valid_nilai(90))',
            "output": "(False, 'di luar rentang') / (True, 'ok')",
            "penjelasan": "Validasi menolak input yang tidak masuk akal sebelum disimpan.",
        },
        {
            "soal": "Tangani konversi input gagal dengan try/except.",
            "kode": 'teks = "abc"\ntry:\n    nilai = int(teks)\nexcept ValueError:\n    nilai = None\n    print("input harus angka")\nprint(nilai)',
            "output": "input harus angka / None",
            "penjelasan": "try/except menjaga aplikasi tetap berjalan saat input salah.",
        },
        {
            "soal": "Tolak nama kosong.",
            "kode": 'nama = "   "\nif not nama.strip():\n    print("nama wajib diisi")\nelse:\n    print("ok")',
            "output": "nama wajib diisi",
            "penjelasan": "Pesan validasi harus jelas bagi pengguna project.",
        },
    ],
    "Testing Mini untuk Project": [
        {
            "soal": "Uji fungsi rata pada list kosong.",
            "kode": 'def rata(nilai):\n    return sum(nilai) / len(nilai) if nilai else 0\nassert rata([]) == 0\nassert rata([80, 100]) == 90\nprint("lulus")',
            "output": "lulus",
            "penjelasan": "assert memastikan perilaku penting benar sebelum demo.",
        },
        {
            "soal": "Uji pencarian yang tidak ketemu.",
            "kode": 'def cari(data, nama):\n    for d in data:\n        if d["nama"] == nama:\n            return d\n    return None\nassert cari([], "X") is None\nprint("ok")',
            "output": "ok",
            "penjelasan": "Kasus kosong/tidak ketemu sering menjadi sumber bug.",
        },
        {
            "soal": "Uji validasi nilai batas.",
            "kode": 'def ok(n):\n    return 0 <= n <= 100\nassert ok(0) and ok(100) and not ok(-1)\nprint("batas aman")',
            "output": "batas aman",
            "penjelasan": "Testing mini fokus pada fungsi inti project.",
        },
    ],
    "Dokumentasi Project & README": [
        {
            "soal": "Susun bagian README sebagai dict lalu cetak.",
            "kode": 'readme = {\n  "tujuan": "Pencatat nilai kelas",\n  "jalankan": "python main.py",\n  "fitur": ["tambah", "lihat", "rata"],\n}\nprint("#", readme["tujuan"])\nprint("Cara:", readme["jalankan"])',
            "output": "# Pencatat nilai kelas / Cara: python main.py",
            "penjelasan": "README minimal berisi tujuan, cara menjalankan, dan fitur.",
        },
        {
            "soal": "Cetak daftar fitur untuk dokumentasi.",
            "kode": 'fitur = ["CLI menu", "JSON save", "validasi"]\nfor i, f in enumerate(fitur, 1):\n    print(f"{i}. {f}")',
            "output": "1. CLI menu / 2. JSON save / 3. validasi",
            "penjelasan": "Dokumentasi membantu orang lain memahami project tanpa penjelasan lisan berulang.",
        },
        {
            "soal": "Tulis contoh penggunaan singkat.",
            "kode": 'contoh = [\n  "1) pilih Tambah",\n  "2) isi nama & nilai",\n  "3) pilih Lihat",\n]\nprint("\\n".join(contoh))',
            "output": "1) pilih Tambah ... 3) pilih Lihat",
            "penjelasan": "Contoh penggunaan mempercepat orang lain mencoba project.",
        },
    ],
    "Showcase Project Ganjil": [
        {
            "soal": "Hitung kelengkapan checklist showcase.",
            "kode": 'cek = {"mvp": True, "simpan": True, "readme": True, "demo": False}\nskor = sum(cek.values()) / len(cek)\nprint(round(skor * 100), "%")',
            "output": "75 %",
            "penjelasan": "Checklist memastikan deliverable ganjil lengkap sebelum presentasi.",
        },
        {
            "soal": "Susun urutan demo 3 menit.",
            "kode": 'demo = ["buka menu", "tambah data", "tampilkan rata", "buka README"]\nfor langkah in demo:\n    print("-", langkah)',
            "output": "- buka menu ... - buka README",
            "penjelasan": "Demo singkat menampilkan alur fitur utama yang berjalan.",
        },
        {
            "soal": "Tandai project siap showcase.",
            "kode": 'wajib = {"mvp": True, "json": True, "readme": True}\nprint("siap" if all(wajib.values()) else "belum")',
            "output": "siap",
            "penjelasan": "Showcase ganjil menekankan MVP jalan + data tersimpan + dokumentasi.",
        },
    ],
    "Project Web: Pengantar Flask Mini": [
        {
            "soal": "Simulasikan route beranda mengembalikan teks.",
            "kode": 'def index():\n    return "Beranda Project Kelas 9"\nprint(index())',
            "output": "Beranda Project Kelas 9",
            "penjelasan": "Pada Flask, fungsi route mengembalikan respons halaman.",
        },
        {
            "soal": "Petakan path ke nama halaman.",
            "kode": 'routes = {"/": "beranda", "/nilai": "daftar nilai"}\nprint(routes["/"])\nprint(routes.get("/laporan", "404"))',
            "output": "beranda / 404",
            "penjelasan": "Setiap path web mengarah ke halaman/fungsi tertentu.",
        },
        {
            "soal": "Tunjukkan data yang dikirim ke template.",
            "kode": 'konteks = {"judul": "Nilai", "jumlah": 3}\nprint(f"{konteks[\'judul\']}: {konteks[\'jumlah\']} data")',
            "output": "Nilai: 3 data",
            "penjelasan": "Route menyiapkan data; template menampilkannya.",
        },
    ],
    "Project Web: Route & Template": [
        {
            "soal": "Buat daftar navigasi dari dict route.",
            "kode": 'halaman = {"/": "Beranda", "/siswa": "Siswa", "/laporan": "Laporan"}\nfor path, judul in halaman.items():\n    print(path, "->", judul)',
            "output": "/ -> Beranda ... /laporan -> Laporan",
            "penjelasan": "Banyak halaman berarti banyak route yang terhubung di navigasi.",
        },
        {
            "soal": "Render teks template sederhana dengan replace.",
            "kode": 'tpl = "Halo, {{ nama }}"\nhtml = tpl.replace("{{ nama }}", "Kirana")\nprint(html)',
            "output": "Halo, Kirana",
            "penjelasan": "Template menggabungkan kerangka HTML dengan data dinamis.",
        },
        {
            "soal": "Siapkan konteks daftar siswa untuk halaman.",
            "kode": 'siswa = ["Kirana", "Dimas"]\nprint("<ul>")\nfor s in siswa:\n    print(f"  <li>{s}</li>")\nprint("</ul>")',
            "output": "daftar <li> siswa",
            "penjelasan": "Loop di template (atau simulasi) menampilkan banyak data.",
        },
    ],
    "Project Data: Model & Penyimpanan": [
        {
            "soal": "Pisahkan model record dan repo list.",
            "kode": 'def buat_siswa(nama, nilai):\n    return {"nama": nama, "nilai": nilai}\nclass Repo:\n    def __init__(self):\n        self._data = []\n    def add(self, item):\n        self._data.append(item)\n    def all(self):\n        return list(self._data)\nr = Repo()\nr.add(buat_siswa("Salma", 91))\nprint(r.all())',
            "output": "[{'nama': 'Salma', 'nilai': 91}]",
            "penjelasan": "Lapisan repo memisahkan detail penyimpanan dari tampilan/route.",
        },
        {
            "soal": "Ambil semua data dari repo.",
            "kode": 'repo = [{"nama": "A"}, {"nama": "B"}]\nprint(len(repo), "item")',
            "output": "2 item",
            "penjelasan": "Read (all) memastikan data Create benar-benar tersimpan.",
        },
        {
            "soal": "Simulasikan simpan ke memori lalu muat lagi.",
            "kode": 'db = []\ndef simpan(item):\n    db.append(item)\ndef muat():\n    return list(db)\nsimpan({"nama": "Dimas"})\nprint(muat())',
            "output": "[{'nama': 'Dimas'}]",
            "penjelasan": "Pola simpan/muat sama baik di memori maupun file JSON.",
        },
    ],
    "Project CRUD Dasar": [
        {
            "soal": "Create: tambah record baru.",
            "kode": 'data = []\ndata.append({"id": 1, "nama": "Kirana", "nilai": 88})\nprint(data)',
            "output": "[{'id': 1, 'nama': 'Kirana', 'nilai': 88}]",
            "penjelasan": "Create menambah data baru ke koleksi.",
        },
        {
            "soal": "Update: ubah nilai siswa yang sudah ada.",
            "kode": 'data = [{"id": 1, "nama": "Kirana", "nilai": 70}]\nfor d in data:\n    if d["id"] == 1:\n        d["nilai"] = 90\nprint(data[0]["nilai"])',
            "output": "90",
            "penjelasan": "Update mengubah field record yang sudah ada.",
        },
        {
            "soal": "Delete: hapus record terpilih.",
            "kode": 'data = [{"id": 1}, {"id": 2}]\ndata = [d for d in data if d["id"] != 1]\nprint(data)',
            "output": "[{'id': 2}]",
            "penjelasan": "Delete menghapus data yang dipilih tanpa merusak sisanya.",
        },
    ],
    "Project Form & Validasi Web": [
        {
            "soal": "Validasi form: nama tidak boleh kosong.",
            "kode": 'form = {"nama": "", "nilai": "80"}\nerror = []\nif not form["nama"].strip():\n    error.append("nama wajib")\nprint(error or ["ok"])',
            "output": "['nama wajib']",
            "penjelasan": "Validasi form menolak input kosong sebelum disimpan.",
        },
        {
            "soal": "Validasi nilai form harus angka 0–100.",
            "kode": 'teks = "120"\ntry:\n    n = int(teks)\n    ok = 0 <= n <= 100\nexcept ValueError:\n    ok = False\nprint("valid" if ok else "tolak")',
            "output": "tolak",
            "penjelasan": "Nilai di luar rentang atau non-angka ditolak.",
        },
        {
            "soal": "Kumpulkan pesan error yang ramah.",
            "kode": 'err = ["Nama wajib diisi", "Nilai harus 0-100"]\nprint("; ".join(err))',
            "output": "Nama wajib diisi; Nilai harus 0-100",
            "penjelasan": "Pesan jelas membantu pengguna memperbaiki input.",
        },
    ],
    "Project Laporan & Filter Data": [
        {
            "soal": "Hitung rata-rata dan jumlah tuntas (KKM 77).",
            "kode": 'nilai = [90, 70, 80, 60]\nrata = sum(nilai) / len(nilai)\ntuntas = len([n for n in nilai if n >= 77])\nprint(rata, tuntas)',
            "output": "75.0 2",
            "penjelasan": "Laporan menampilkan ringkasan seperti rata-rata dan jumlah tuntas.",
        },
        {
            "soal": "Filter siswa tuntas.",
            "kode": 'data = [{"nama": "A", "nilai": 90}, {"nama": "B", "nilai": 70}]\ntuntas = [d for d in data if d["nilai"] >= 77]\nprint([d["nama"] for d in tuntas])',
            "output": "['A']",
            "penjelasan": "Filter membantu melihat subset data sesuai kriteria.",
        },
        {
            "soal": "Buat ringkasan laporan sebagai dict.",
            "kode": 'nilai = [88, 76, 92]\nlaporan = {\n  "jumlah": len(nilai),\n  "rata": round(sum(nilai)/len(nilai), 1),\n  "tuntas": sum(1 for n in nilai if n >= 77),\n}\nprint(laporan)',
            "output": "{'jumlah': 3, 'rata': 85.3, 'tuntas': 2}",
            "penjelasan": "Ringkasan siap dikirim ke template/halaman laporan.",
        },
    ],
    "Project Session & Hak Akses Sederhana": [
        {
            "soal": "Cek apakah session boleh mengelola data.",
            "kode": 'def boleh_kelola(session):\n    return session.get("role") == "guru"\nprint(boleh_kelola({"role": "guru"}))\nprint(boleh_kelola({"role": "siswa"}))',
            "output": "True / False",
            "penjelasan": "Hak akses membatasi menu kelola sesuai peran.",
        },
        {
            "soal": "Simulasikan set role saat login.",
            "kode": 'session = {}\nsession["role"] = "siswa"\nsession["nama"] = "Kirana"\nprint(session)',
            "output": "{'role': 'siswa', 'nama': 'Kirana'}",
            "penjelasan": "Session menyimpan identitas/peran selama pengguna memakai aplikasi.",
        },
        {
            "soal": "Tolak aksi hapus jika bukan guru.",
            "kode": 'role = "siswa"\nif role != "guru":\n    print("akses ditolak")\nelse:\n    print("hapus diizinkan")',
            "output": "akses ditolak",
            "penjelasan": "Pembatasan peran melindungi operasi sensitif.",
        },
    ],
    "Project API JSON Mini": [
        {
            "soal": "Bentuk payload API status ok.",
            "kode": 'import json\npayload = {"status": "ok", "jumlah": 2, "data": [{"nama": "A"}]}\nprint(json.dumps(payload))',
            "output": 'JSON berisi status, jumlah, data',
            "penjelasan": "API JSON mengembalikan data terstruktur, bukan halaman HTML.",
        },
        {
            "soal": "Endpoint ringkas hanya mengirim ringkasan.",
            "kode": 'import json\nnilai = [80, 90, 70]\nringkas = {"rata": sum(nilai)/len(nilai), "max": max(nilai)}\nprint(json.dumps(ringkas))',
            "output": '{"rata": 80.0, "max": 90}',
            "penjelasan": "Payload yang baik punya status/ringkas data yang jelas.",
        },
        {
            "soal": "Tandai error pada respons API.",
            "kode": 'import json\nprint(json.dumps({"status": "error", "pesan": "nilai tidak valid"}))',
            "output": '{"status": "error", "pesan": "nilai tidak valid"}',
            "penjelasan": "API juga perlu menyampaikan kegagalan secara terstruktur.",
        },
    ],
    "Project Hardening & Debugging": [
        {
            "soal": "Catat jenis error ke log sederhana.",
            "kode": 'LOG = []\ntry:\n    int("x")\nexcept ValueError as e:\n    LOG.append(type(e).__name__)\nprint(LOG)',
            "output": "['ValueError']",
            "penjelasan": "Logging membantu melacak jenis kesalahan saat hardening.",
        },
        {
            "soal": "Perbaiki pembagian kosong dengan guard.",
            "kode": 'nilai = []\nrata = sum(nilai) / len(nilai) if nilai else 0\nprint(rata)',
            "output": "0",
            "penjelasan": "Hardening menutup celah bug pada kasus ekstrem.",
        },
        {
            "soal": "Prioritaskan bug fitur utama.",
            "kode": 'bug = [("crash simpan", "utama"), ("typo README", "kecil")]\nutama = [b for b, p in bug if p == "utama"]\nprint(utama)',
            "output": "['crash simpan']",
            "penjelasan": "Menjelang capstone, perbaiki dulu yang merusak fitur utama.",
        },
    ],
    "Capstone Project Akhir Kelas 9": [
        {
            "soal": "Hitung skor rubrik kelengkapan.",
            "kode": 'rubrik = {"berjalan": True, "crud": True, "simpan": True, "laporan": False, "readme": True}\nskor = sum(rubrik.values()) / len(rubrik) * 100\nprint(int(skor))',
            "output": "80",
            "penjelasan": "Rubrik menilai project terpadu dari beberapa kriteria.",
        },
        {
            "soal": "Checklist deliverable capstone.",
            "kode": 'wajib = ["validasi", "simpan", "laporan", "readme"]\nselesai = {"validasi", "simpan", "readme"}\nprint([x for x in wajib if x not in selesai])',
            "output": "['laporan']",
            "penjelasan": "Capstone harus memakai validasi + simpan + laporan + dokumentasi.",
        },
        {
            "soal": "Tandai project siap dinilai.",
            "kode": 'siap = all([True, True, True, True])  # demo, CRUD, data, README\nprint("siap dinilai" if siap else "belum")',
            "output": "siap dinilai",
            "penjelasan": "Hasil genap Kelas 9: project web/data terpadu siap demo dan dinilai rubrik.",
        },
    ],
    # ----- Jalur Game OOP Kelas 7–9 -----
    "Game OOP: Objek dalam Dunia Game": [
        {
            "soal": "Buat objek player sebagai dict.",
            "kode": 'player = {"nama": "Hero", "hp": 100, "skor": 0, "x": 0}\nprint(player["nama"], player["hp"])',
            "output": "Hero 100",
            "penjelasan": "Dict menyatukan data penting player dalam satu objek.",
        },
        {
            "soal": "Buat objek musuh dan bandingkan nama.",
            "kode": 'p = {"nama": "Hero"}\nm = {"nama": "Slime"}\nprint(p["nama"], "vs", m["nama"])',
            "output": "Hero vs Slime",
            "penjelasan": "Setiap entitas game punya objek data sendiri.",
        },
        {
            "soal": "Tambah field senjata pada player.",
            "kode": 'player = {"nama": "Hero", "hp": 100}\nplayer["senjata"] = "pedang"\nprint(player)',
            "output": "{'nama': 'Hero', 'hp': 100, 'senjata': 'pedang'}",
            "penjelasan": "Field objek bisa ditambah sesuai kebutuhan game.",
        },
    ],
    "Game OOP: Player, Skor, dan Fungsi": [
        {
            "soal": "Fungsi menambah skor player.",
            "kode": 'def tambah_skor(p, poin):\n    p["skor"] += poin\np = {"skor": 0}\ntambah_skor(p, 15)\nprint(p["skor"])',
            "output": "15",
            "penjelasan": "Fungsi mengubah data objek — pola perilaku sebelum class.",
        },
        {
            "soal": "Kurangi HP tanpa negatif.",
            "kode": 'def kena(p, dmg):\n    p["hp"] = max(0, p["hp"] - dmg)\np = {"hp": 10}\nkena(p, 25)\nprint(p["hp"])',
            "output": "0",
            "penjelasan": "max(0, ...) menjaga HP tidak negatif.",
        },
        {
            "soal": "Cetak status ringkas player.",
            "kode": 'def status(p):\n    print(p["nama"], "HP", p["hp"], "skor", p["skor"])\nstatus({"nama": "Hero", "hp": 80, "skor": 12})',
            "output": "Hero HP 80 skor 12",
            "penjelasan": "Fungsi status membantu membaca kondisi objek tiap giliran.",
        },
    ],
    "Game OOP: Loop Game Sederhana": [
        {
            "soal": "Simulasikan 3 putaran tambah skor.",
            "kode": 'p = {"skor": 0}\nfor i in range(3):\n    p["skor"] += 10\nprint(p["skor"])',
            "output": "30",
            "penjelasan": "Loop mengulang update data sampai syarat terpenuhi.",
        },
        {
            "soal": "Berhenti saat HP habis.",
            "kode": 'p = {"hp": 15}\nwhile p["hp"] > 0:\n    p["hp"] -= 5\nprint("mati", p["hp"])',
            "output": "mati 0",
            "penjelasan": "Kondisi loop menentukan kapan game berakhir.",
        },
        {
            "soal": "Menang jika skor mencapai target.",
            "kode": 'p = {"skor": 0}\nwhile p["skor"] < 20:\n    p["skor"] += 5\nprint("menang", p["skor"])',
            "output": "menang 20",
            "penjelasan": "Target skor adalah salah satu syarat menang pada game loop.",
        },
    ],
    "Game OOP: Nyawa, Item, dan Benturan Sederhana": [
        {
            "soal": "Cek benturan posisi sama.",
            "kode": 'def dekat(a, b):\n    return a["x"] == b["x"]\nprint(dekat({"x": 3}, {"x": 3}))\nprint(dekat({"x": 1}, {"x": 4}))',
            "output": "True / False",
            "penjelasan": "Benturan teks/1D cukup membandingkan posisi.",
        },
        {
            "soal": "Ambil potion jika bertabrakan.",
            "kode": 'p = {"hp": 50, "x": 2}\nitem = {"heal": 20, "x": 2, "aktif": True}\nif item["aktif"] and p["x"] == item["x"]:\n    p["hp"] += item["heal"]\n    item["aktif"] = False\nprint(p["hp"], item["aktif"])',
            "output": "70 False",
            "penjelasan": "Setelah diambil, item dinonaktifkan agar tidak double heal.",
        },
        {
            "soal": "Tabrak musuh mengurangi HP.",
            "kode": 'p = {"hp": 40, "x": 5}\nm = {"dmg": 10, "x": 5}\nif p["x"] == m["x"]:\n    p["hp"] -= m["dmg"]\nprint(p["hp"])',
            "output": "30",
            "penjelasan": "Aturan benturan menentukan efek saat dua objek bertemu.",
        },
    ],
    "Game OOP: Mini Game Teks Kelas 7": [
        {
            "soal": "Serang musuh dan tambah skor.",
            "kode": 'p = {"hp": 40, "skor": 0}\nm = {"hp": 20}\nm["hp"] -= 12\np["skor"] += 12\nprint(m["hp"], p["skor"])',
            "output": "8 12",
            "penjelasan": "Aksi serang mengubah objek musuh dan skor player.",
        },
        {
            "soal": "Tentukan menang atau kalah.",
            "kode": 'p_hp, m_hp = 5, 0\nhasil = "menang" if m_hp <= 0 and p_hp > 0 else "kalah"\nprint(hasil)',
            "output": "menang",
            "penjelasan": "Proyek mini harus punya kondisi selesai yang jelas.",
        },
        {
            "soal": "Satu putaran balasan musuh.",
            "kode": 'p = {"hp": 30}\nm_hidup = True\nif m_hidup:\n    p["hp"] -= 7\nprint(p["hp"])',
            "output": "23",
            "penjelasan": "Giliran musuh menjaga battle tetap seimbang.",
        },
    ],
    "Game OOP: Class Player untuk Game": [
        {
            "soal": "Buat dua object Player.",
            "kode": 'class Player:\n    def __init__(self, nama, hp=100):\n        self.nama = nama\n        self.hp = hp\na = Player("Hero")\nb = Player("Ninja", 80)\nprint(a.nama, a.hp, b.nama, b.hp)',
            "output": "Hero 100 Ninja 80",
            "penjelasan": "Satu class menghasilkan banyak object dengan data sendiri.",
        },
        {
            "soal": "Inisialisasi skor default 0.",
            "kode": 'class Player:\n    def __init__(self, nama):\n        self.nama = nama\n        self.skor = 0\np = Player("Hero")\nprint(p.skor)',
            "output": "0",
            "penjelasan": "__init__ mengisi atribut awal object game.",
        },
        {
            "soal": "Cetak identitas player.",
            "kode": 'class Player:\n    def __init__(self, nama, hp):\n        self.nama, self.hp = nama, hp\n    def info(self):\n        return f"{self.nama}({self.hp})"\nprint(Player("Hero", 90).info())',
            "output": "Hero(90)",
            "penjelasan": "Method info membaca atribut object.",
        },
    ],
    "Game OOP: Method Gerak, Serang, dan Heal": [
        {
            "soal": "Gerakkan player ke kanan.",
            "kode": 'class Player:\n    def __init__(self):\n        self.x = 0\n    def gerak(self, dx):\n        self.x += dx\np = Player()\np.gerak(3)\nprint(p.x)',
            "output": "3",
            "penjelasan": "Method gerak mengubah atribut posisi object.",
        },
        {
            "soal": "Serang mengurangi HP target.",
            "kode": 'class P:\n    def __init__(self, hp):\n        self.hp = hp\n        self.skor = 0\n    def serang(self, t, dmg=10):\n        t.hp = max(0, t.hp - dmg)\n        self.skor += dmg\na, b = P(100), P(30)\na.serang(b, 12)\nprint(b.hp, a.skor)',
            "output": "18 12",
            "penjelasan": "Method serang memengaruhi object lain dan skor penyerang.",
        },
        {
            "soal": "Heal tidak melebihi 100.",
            "kode": 'class P:\n    def __init__(self, hp):\n        self.hp = hp\n    def heal(self, n):\n        self.hp = min(100, self.hp + n)\np = P(95)\np.heal(20)\nprint(p.hp)',
            "output": "100",
            "penjelasan": "Batas maksimal menjaga aturan game tetap wajar.",
        },
    ],
    "Game OOP: Inheritance Player dan Enemy": [
        {
            "soal": "Entity dasar punya hidup().",
            "kode": 'class Entity:\n    def __init__(self, nama, hp):\n        self.nama, self.hp = nama, hp\n    def hidup(self):\n        return self.hp > 0\nprint(Entity("A", 1).hidup(), Entity("B", 0).hidup())',
            "output": "True False",
            "penjelasan": "Class dasar memuat perilaku bersama semua entitas.",
        },
        {
            "soal": "Player mewarisi Entity dan punya skor.",
            "kode": 'class Entity:\n    def __init__(self, nama, hp):\n        self.nama, self.hp = nama, hp\nclass Player(Entity):\n    def __init__(self, nama):\n        super().__init__(nama, 100)\n        self.skor = 0\np = Player("Hero")\nprint(p.nama, p.hp, p.skor)',
            "output": "Hero 100 0",
            "penjelasan": "super().__init__ mengisi bagian class induk.",
        },
        {
            "soal": "Enemy override serang.",
            "kode": 'class Enemy:\n    def serang(self, target):\n        target.hp = max(0, target.hp - 8)\nclass P:\n    def __init__(self):\n        self.hp = 20\np = P()\nEnemy().serang(p)\nprint(p.hp)',
            "output": "12",
            "penjelasan": "Override memberi perilaku khusus pada turunan.",
        },
    ],
    "Game OOP: Game Loop dengan Banyak Object": [
        {
            "soal": "Kurangi HP semua musuh dalam list.",
            "kode": 'class E:\n    def __init__(self, hp):\n        self.hp = hp\nmusuh = [E(20), E(15)]\nfor m in musuh:\n    m.hp -= 10\nprint([m.hp for m in musuh])',
            "output": "[10, 5]",
            "penjelasan": "Loop mengupdate banyak object tiap putaran.",
        },
        {
            "soal": "Saring musuh yang masih hidup.",
            "kode": 'class E:\n    def __init__(self, hp):\n        self.hp = hp\nmusuh = [E(0), E(8), E(0)]\nhidup = [m for m in musuh if m.hp > 0]\nprint(len(hidup))',
            "output": "1",
            "penjelasan": "Filter membersihkan entity yang sudah kalah.",
        },
        {
            "soal": "Hitung total HP musuh tersisa.",
            "kode": 'musuh_hp = [12, 0, 7]\nprint(sum(h for h in musuh_hp if h > 0))',
            "output": "19",
            "penjelasan": "Agregasi membantu menampilkan status wave musuh.",
        },
    ],
    "Game OOP: Mini Game Arena Kelas 8": [
        {
            "soal": "Satu giliran hero menyerang orc.",
            "kode": 'class E:\n    def __init__(self, hp):\n        self.hp = hp\nhero, orc = E(50), E(35)\norc.hp = max(0, orc.hp - 12)\nprint(orc.hp)',
            "output": "23",
            "penjelasan": "Arena memakai method/aksi berulang sampai selesai.",
        },
        {
            "soal": "Tentukan pemenang arena.",
            "kode": 'p_hp, e_hp = 10, 0\nprint("Menang" if p_hp > 0 and e_hp <= 0 else "Kalah")',
            "output": "Menang",
            "penjelasan": "Kondisi akhir wajib ada pada proyek arena.",
        },
        {
            "soal": "Akumulasi skor dari damage.",
            "kode": 'skor = 0\nfor dmg in (12, 12, 12):\n    skor += dmg\nprint(skor)',
            "output": "36",
            "penjelasan": "Skor akhir biasanya dari total damage atau objektif lain.",
        },
    ],
    "Game Project: Desain Entity & Scene": [
        {
            "soal": "Ganti scene aktif pada Game.",
            "kode": 'class Scene:\n    def __init__(self, nama):\n        self.nama = nama\nclass Game:\n    def __init__(self):\n        self.scene = Scene("menu")\n    def ganti(self, nama):\n        self.scene = Scene(nama)\ng = Game()\ng.ganti("play")\nprint(g.scene.nama)',
            "output": "play",
            "penjelasan": "Game mengatur scene yang sedang aktif.",
        },
        {
            "soal": "Daftar class rencana project.",
            "kode": 'rencana = ["Entity", "Player", "Enemy", "Scene", "Game"]\nprint(len(rencana), "class")\nprint(rencana[0], "→", rencana[-1])',
            "output": "5 class / Entity → Game",
            "penjelasan": "Desain dulu memetakan class sebelum coding panjang.",
        },
        {
            "soal": "Scene.update mengembalikan nama state.",
            "kode": 'class Scene:\n    def __init__(self, nama):\n        self.nama = nama\n    def update(self):\n        return self.nama\nprint(Scene("menu").update())',
            "output": "menu",
            "penjelasan": "Tiap scene punya perilaku update sendiri.",
        },
    ],
    "Game Project: State Machine (Menu–Play–Game Over)": [
        {
            "soal": "Start mengubah state ke play.",
            "kode": 'class Game:\n    def __init__(self):\n        self.state = "menu"\n    def update(self, aksi):\n        if self.state == "menu" and aksi == "start":\n            self.state = "play"\ng = Game()\ng.update("start")\nprint(g.state)',
            "output": "play",
            "penjelasan": "Transisi state menjaga alur game teratur.",
        },
        {
            "soal": "Poin hanya bertambah saat play.",
            "kode": 'state, skor = "menu", 0\nif state == "play":\n    skor += 1\nprint(skor)\nstate = "play"\nif state == "play":\n    skor += 1\nprint(skor)',
            "output": "0 / 1",
            "penjelasan": "State mencegah aksi play berjalan di menu.",
        },
        {
            "soal": "Mati mengarah ke gameover.",
            "kode": 'state = "play"\nif state == "play":\n    state = "gameover"\nprint(state)',
            "output": "gameover",
            "penjelasan": "Game over adalah state terpisah dari play.",
        },
    ],
    "Game Project: Multi-Entity & Collision": [
        {
            "soal": "Ambil koin saat posisi sama.",
            "kode": 'class Ent:\n    def __init__(self, x):\n        self.x = x\np, koin = Ent(2), Ent(2)\nskor = 1 if p.x == koin.x else 0\nprint(skor)',
            "output": "1",
            "penjelasan": "Collision memicu interaksi antar entity.",
        },
        {
            "soal": "Sisakan item yang tidak tertabrak.",
            "kode": 'px = 3\nitems = [1, 3, 5]\nsisa = [x for x in items if x != px]\nprint(sisa)',
            "output": "[1, 5]",
            "penjelasan": "Entity yang diambil dihapus dari dunia game.",
        },
        {
            "soal": "Hitung tabrakan dalam satu tick.",
            "kode": 'player_x = 4\nmusuh_x = [2, 4, 4]\nhit = sum(1 for x in musuh_x if x == player_x)\nprint(hit)',
            "output": "2",
            "penjelasan": "Satu tick bisa memeriksa banyak entity sekaligus.",
        },
    ],
    "Game Project: Highscore & Save JSON": [
        {
            "soal": "Update highscore jika skor lebih tinggi.",
            "kode": 'import json\ndata = {"highscore": 10}\nskor = 25\nif skor > data["highscore"]:\n    data["highscore"] = skor\nprint(json.dumps(data))',
            "output": '{"highscore": 25}',
            "penjelasan": "Rekor baru harus disimpan ke struktur data/JSON.",
        },
        {
            "soal": "Muat highscore dari teks JSON.",
            "kode": 'import json\ndata = json.loads(\'{"highscore": 42}\')\nprint(data["highscore"])',
            "output": "42",
            "penjelasan": "Saat mulai, project memuat rekor sebelumnya.",
        },
        {
            "soal": "Skor lebih rendah tidak menimpa rekor.",
            "kode": 'hs, skor = 50, 30\nif skor > hs:\n    hs = skor\nprint(hs)',
            "output": "50",
            "penjelasan": "Highscore hanya berubah jika benar-benar lebih tinggi.",
        },
    ],
    "Game Project: Capstone Game OOP Kelas 9": [
        {
            "soal": "Simulasikan main lalu simpan HS.",
            "kode": 'class Game:\n    def __init__(self):\n        self.skor = 0\n        self.highscore = 0\n    def main(self):\n        self.skor = 18\n        if self.skor > self.highscore:\n            self.highscore = self.skor\ng = Game()\ng.main()\nprint(g.highscore)',
            "output": "18",
            "penjelasan": "Capstone menggabungkan play dan persistensi rekor.",
        },
        {
            "soal": "Cek kelengkapan rubrik capstone game.",
            "kode": 'wajib = ["entity", "state", "collision", "save", "readme"]\npunya = {"entity", "state", "save", "readme"}\nprint([x for x in wajib if x not in punya])',
            "output": "['collision']",
            "penjelasan": "Checklist memastikan deliverable capstone lengkap.",
        },
        {
            "soal": "Tandai siap showcase.",
            "kode": 'cek = {"berjalan": True, "oop": True, "save": True, "demo": True}\nprint("siap" if all(cek.values()) else "belum")',
            "output": "siap",
            "penjelasan": "Game OOP 7–9 selesai jika project berjalan dan siap demo.",
        },
    ],
}


def potong_lama(html: str) -> str:
    if MARKER in html:
        return html.split(MARKER, 1)[0].rstrip()
    # potong heading lama jika pernah ditambah manual
    return re.split(r"<h3>\s*Contoh soal\s*&amp;\s*penyelesaian\s*</h3>", html, maxsplit=1)[0].rstrip()


def contoh_kode_gabungan(items):
    bagian_kode = []
    for i, c in enumerate(items, start=1):
        bagian_kode.append(f"# Contoh {i}\n{c['kode']}")
    return "\n\n".join(bagian_kode)


def main():
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, judul, isi_html, contoh_kode FROM materi WHERE aktif=1 ORDER BY id"
            )
            rows = cur.fetchall()
            ok = 0
            kurang = []
            for row in rows:
                judul = row["judul"]
                contoh = CONTOH.get(judul)
                if not contoh or len(contoh) < 3:
                    kurang.append(judul)
                    continue
                dasar = potong_lama(row["isi_html"] or "")
                baru = dasar + "\n" + bagian(contoh)
                kode = contoh_kode_gabungan(contoh)
                cur.execute(
                    "UPDATE materi SET isi_html=%s, contoh_kode=%s WHERE id=%s",
                    (baru, kode, row["id"]),
                )
                ok += 1
                print(f"OK [{row['id']}] {judul} (+{len(contoh)} contoh)")
            if kurang:
                print("BELUM ADA BANK CONTOH:")
                for j in kurang:
                    print(" -", j)
            print(f"Selesai: {ok} materi diperbarui.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
