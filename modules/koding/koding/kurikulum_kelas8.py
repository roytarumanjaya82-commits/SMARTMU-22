"""Kurikulum Kelas 8: Python lanjutan dari fondasi Kelas 7, penjelasan lebih detail."""

MATERI_GANJIL = [
    {
        "urutan": 1,
        "judul": "Review Kelas 7 & Set",
        "ringkasan": "Mengulang list, dict, fungsi, lalu mengenal set sebagai himpunan nilai unik.",
        "isi_html": """
        <h3>Mengapa perlu review Kelas 7?</h3>
        <p>Di Kelas 7 kamu sudah belajar variabel, percabangan, perulangan, <strong>list</strong>,
        <strong>dictionary</strong>, dan <strong>fungsi</strong>. Kelas 8 memakai semua itu sebagai fondasi,
        lalu menambah struktur data dan teknik yang lebih kuat.</p>
        <h3>Ringkas fondasi yang harus hafal</h3>
        <ul>
          <li><code>list</code> — berurutan, boleh duplikat, diubah: <code>[1, 2, 3]</code></li>
          <li><code>dict</code> — pasangan kunci–nilai: <code>{"nama": "Aisyah"}</code></li>
          <li><code>def nama(...):</code> — membuat fungsi agar kode tidak diulang</li>
        </ul>
        <h3>Apa itu set?</h3>
        <p><strong>Set</strong> (himpunan) menyimpan nilai <em>unik</em>. Duplikat otomatis hilang.
        Penulisan: <code>{1, 2, 3}</code> atau <code>set([1, 2, 2, 3])</code>.</p>
        <h3>Operasi penting</h3>
        <ul>
          <li><code>|</code> atau <code>.union()</code> — gabungan</li>
          <li><code>&amp;</code> atau <code>.intersection()</code> — irisan</li>
          <li><code>-</code> — selisih</li>
          <li><code>.add()</code> / <code>.discard()</code> — tambah / buang elemen</li>
        </ul>
        <h3>Kapan memakai set?</h3>
        <p>Saat kamu butuh daftar tanpa duplikat, misalnya NIS unik, atau membandingkan dua kelompok anggota.</p>
        <p><em>Catatan:</em> set tidak berurutan seperti list, jadi indexing <code>s[0]</code> tidak dipakai.</p>
        """,
        "contoh_kode": 'angka = {1, 2, 2, 3}\nprint(angka)  # {1, 2, 3}\na = {1, 2, 3}\nb = {3, 4}\nprint("gabungan:", a | b)\nprint("irisan:", a & b)\nprint("selisih:", a - b)',
    },
    {
        "urutan": 2,
        "judul": "List Comprehension",
        "ringkasan": "Membuat list baru dengan sintaks ringkas dari Kelas 7 yang memakai loop.",
        "isi_html": """
        <h3>Dari loop Kelas 7 ke bentuk ringkas</h3>
        <p>Di Kelas 7, membuat list baru biasanya memakai <code>for</code> dan <code>append</code>.
        List comprehension menulis pola yang sama dalam satu baris yang lebih jelas.</p>
        <pre>hasil = [ekspresi for item in iterable if syarat]</pre>
        <h3>Langkah membaca comprehension</h3>
        <ol>
          <li>Lihat <code>for item in iterable</code> — dari mana datanya</li>
          <li>Lihat <code>if syarat</code> (opsional) — filter</li>
          <li>Lihat ekspresi di depan — nilai yang dimasukkan ke list baru</li>
        </ol>
        <h3>Contoh setara dengan loop</h3>
        <p>Loop klasik:</p>
        <pre>kuadrat = []
for x in range(1, 6):
    kuadrat.append(x * x)</pre>
        <p>Comprehension:</p>
        <pre>kuadrat = [x * x for x in range(1, 6)]</pre>
        <h3>Tips</h3>
        <ul>
          <li>Pakai comprehension untuk transformasi sederhana</li>
          <li>Jika logikanya rumit (banyak if bersarang), loop biasa lebih mudah dibaca</li>
        </ul>
        """,
        "contoh_kode": 'kuadrat = [x*x for x in range(1, 6)]\nprint(kuadrat)\ngenap = [n for n in range(10) if n % 2 == 0]\nprint(genap)\nnama = ["ani", "budi"]\nbesar = [n.upper() for n in nama]\nprint(besar)',
    },
    {
        "urutan": 3,
        "judul": "Fungsi Lanjutan",
        "ringkasan": "Parameter default, *args, dan lambda — pengembangan dari fungsi Kelas 7.",
        "isi_html": """
        <h3>Fungsi Kelas 7 vs Kelas 8</h3>
        <p>Kelas 7: fungsi dengan parameter tetap. Kelas 8: fungsi lebih fleksibel agar bisa
        menerima banyak argumen atau nilai bawaan.</p>
        <h3>Parameter default</h3>
        <p>Jika pemanggil tidak mengisi argumen, nilai bawaan dipakai.</p>
        <pre>def sapa(nama, sapaan="Halo"):
    print(sapaan, nama)</pre>
        <h3>*args</h3>
        <p><code>*args</code> menampung banyak argumen posisi menjadi tuple. Cocok untuk jumlah, rata-rata, dll.</p>
        <h3>lambda</h3>
        <p>Fungsi singkat satu ekspresi, sering dipakai bersama <code>map</code>, <code>filter</code>, atau <code>sorted</code>.</p>
        <pre>kali = lambda a, b: a * b</pre>
        <h3>Latihan berpikir</h3>
        <p>Jika sebuah fungsi kadang dipanggil dengan 2 angka, kadang 5 angka, manakah yang lebih cocok:
        banyak parameter opsional, atau <code>*args</code>?</p>
        """,
        "contoh_kode": 'def jumlah(*angka):\n    return sum(angka)\nprint(jumlah(1, 2, 3, 4))\n\ndef sapa(nama, sapaan="Halo"):\n    return f"{sapaan}, {nama}!"\nprint(sapa("Rafi"))\nprint(sapa("Dewi", "Selamat pagi"))\n\nkali = lambda a, b: a * b\nprint(kali(3, 5))',
    },
    {
        "urutan": 4,
        "judul": "Exception Handling",
        "ringkasan": "Menangani error agar program tidak langsung berhenti.",
        "isi_html": """
        <h3>Mengapa perlu menangani error?</h3>
        <p>Input pengguna sering tidak sesuai harapan: huruf saat diminta angka, atau pembagian nol.
        Tanpa penanganan, program berhenti. Dengan <code>try/except</code>, kamu bisa memberi pesan ramah.</p>
        <h3>Struktur</h3>
        <ul>
          <li><code>try</code> — kode yang berisiko error</li>
          <li><code>except JenisError</code> — penanganan khusus</li>
          <li><code>else</code> — jalan jika tidak ada error (opsional)</li>
          <li><code>finally</code> — selalu dijalankan (opsional), misalnya menutup file</li>
        </ul>
        <h3>Error yang sering muncul</h3>
        <ul>
          <li><code>ValueError</code> — konversi gagal, mis. <code>int("abc")</code></li>
          <li><code>ZeroDivisionError</code> — bagi nol</li>
          <li><code>TypeError</code> — operasi tipe tidak cocok</li>
          <li><code>KeyError</code> / <code>IndexError</code> — kunci/indeks tidak ada</li>
        </ul>
        <h3>Praktik baik</h3>
        <p>Tangkap error yang spesifik. Hindari <code>except:</code> kosong tanpa pesan, karena menyembunyikan bug.</p>
        """,
        "contoh_kode": 'try:\n    n = int("0")\n    print(10 / n)\nexcept ValueError:\n    print("Harus angka")\nexcept ZeroDivisionError:\n    print("Tidak boleh nol")\nfinally:\n    print("Blok selesai")',
    },
    {
        "urutan": 5,
        "judul": "File Handling Dasar",
        "ringkasan": "Membaca dan menulis file teks dengan aman memakai with open.",
        "isi_html": """
        <h3>Program yang mengingat data</h3>
        <p>Variabel hilang saat program ditutup. File membuat data bertahan: catatan, daftar nilai, log.</p>
        <h3>Mode penting</h3>
        <ul>
          <li><code>r</code> — baca (file harus ada)</li>
          <li><code>w</code> — tulis baru (menimpa isi lama)</li>
          <li><code>a</code> — append, menambah di akhir</li>
        </ul>
        <h3>Pola wajib: with</h3>
        <pre>with open("catatan.txt", "w", encoding="utf-8") as f:
    f.write("teks")</pre>
        <p><code>with</code> memastikan file tertutup meski terjadi error — terkait materi exception.</p>
        <h3>Encoding</h3>
        <p>Untuk teks Indonesia, pakai <code>encoding="utf-8"</code> agar huruf tidak rusak.</p>
        """,
        "contoh_kode": 'with open("catatan.txt", "w", encoding="utf-8") as f:\n    f.write("Belajar Python Kelas 8\\n")\n    f.write("File handling dasar\\n")\n\nwith open("catatan.txt", "r", encoding="utf-8") as f:\n    print(f.read())',
    },
    {
        "urutan": 6,
        "judul": "Modul Sendiri",
        "ringkasan": "Memecah program menjadi file .py yang diimpor ulang.",
        "isi_html": """
        <h3>Kenapa memisah modul?</h3>
        <p>Satu file panjang sulit dibaca. Modul memisahkan tanggung jawab: hitung di <code>hitung.py</code>,
        tampilan di <code>utama.py</code>.</p>
        <h3>Cara memakai</h3>
        <ul>
          <li><code>import hitung</code> lalu <code>hitung.luas_persegi(6)</code></li>
          <li><code>from hitung import luas_persegi</code> lalu panggil langsung</li>
        </ul>
        <h3>Hubungan dengan Kelas 7</h3>
        <p>Fungsi yang dulu kamu tulis berulang di satu file, sekarang dikumpulkan di modul lalu diimpor.</p>
        <h3>Tips</h3>
        <ul>
          <li>Nama file modul: huruf kecil, tanpa spasi</li>
          <li>Jangan menamai file sama dengan modul bawaan (<code>math.py</code>, <code>random.py</code>)</li>
        </ul>
        """,
        "contoh_kode": '# bayangkan file hitung.py berisi:\ndef luas_persegi(s):\n    return s * s\n\ndef keliling_persegi(s):\n    return 4 * s\n\n# di file utama:\n# import hitung\n# print(hitung.luas_persegi(6))\nprint(luas_persegi(6) if False else 36)  # contoh hasil',
    },
    {
        "urutan": 7,
        "judul": "OOP: Class dan Object",
        "ringkasan": "Beralih dari data terpisah ke object yang punya data dan perilaku.",
        "isi_html": """
        <h3>Masalah gaya prosedural</h3>
        <p>Di Kelas 7, data siswa sering tersebar: list nama, list nilai, fungsi terpisah.
        OOP menggabungkan <strong>data</strong> dan <strong>perilaku</strong> dalam satu object.</p>
        <h3>Istilah</h3>
        <ul>
          <li><strong>Class</strong> — cetakan / blueprint</li>
          <li><strong>Object (instance)</strong> — hasil cetakan, contoh nyata</li>
        </ul>
        <p>Class <code>Siswa</code> bisa menghasilkan object Aisyah, Budi, Rafi — masing-masing punya data sendiri.</p>
        <h3>Sintaks dasar</h3>
        <pre>class Siswa:
    def sapa(self):
        print("Halo siswa!")

s1 = Siswa()
s1.sapa()</pre>
        <h3>self</h3>
        <p><code>self</code> merujuk ke object yang sedang dipakai. Wajib menjadi parameter pertama method instance.</p>
        """,
        "contoh_kode": 'class Siswa:\n    def sapa(self):\n        print("Halo siswa!")\n\ns1 = Siswa()\ns2 = Siswa()\ns1.sapa()\ns2.sapa()',
    },
    {
        "urutan": 8,
        "judul": "Atribut dan Method",
        "ringkasan": "Membedakan data object (atribut) dan perilaku (method).",
        "isi_html": """
        <h3>Atribut = data</h3>
        <p>Contoh: <code>nama</code>, <code>nilai</code>, <code>merk</code>. Disimpan di object, biasanya lewat <code>self.nama</code>.</p>
        <h3>Method = perilaku</h3>
        <p>Fungsi di dalam class. Contoh: <code>sapa()</code>, <code>status()</code>, <code>diskon()</code>.</p>
        <h3>Mengisi atribut</h3>
        <p>Bisa diisi setelah object dibuat, tetapi praktik baik memakai <code>__init__</code> (materi berikutnya)
        agar setiap object lahir dengan data lengkap.</p>
        <h3>Latihan konsep</h3>
        <p>Untuk class <code>Buku</code>, sebutkan 2 atribut dan 1 method yang masuk akal.</p>
        """,
        "contoh_kode": 'class Mobil:\n    def bunyi(self):\n        print("Broom!")\n\nm = Mobil()\nm.merk = "Avanza"\nm.tahun = 2024\nprint(m.merk, m.tahun)\nm.bunyi()',
    },
    {
        "urutan": 9,
        "judul": "Constructor __init__",
        "ringkasan": "Mengisi atribut otomatis saat object dibuat.",
        "isi_html": """
        <h3>Apa itu constructor?</h3>
        <p><code>__init__</code> dipanggil otomatis saat kamu menulis <code>Siswa("Dewi", 85)</code>.
        Tempat terbaik untuk menyimpan parameter ke atribut object.</p>
        <pre>class Siswa:
    def __init__(self, nama, nilai):
        self.nama = nama
        self.nilai = nilai</pre>
        <h3>Alur</h3>
        <ol>
          <li>Python membuat object kosong</li>
          <li><code>__init__</code> mengisi atribut</li>
          <li>Object siap dipakai</li>
        </ol>
        <h3>Hubungan dengan KKM sekolah</h3>
        <p>Method <code>status()</code> bisa memakai atribut <code>nilai</code> dan membandingkannya dengan KKM 77.</p>
        """,
        "contoh_kode": 'class Siswa:\n    def __init__(self, nama, nilai):\n        self.nama = nama\n        self.nilai = nilai\n    def status(self):\n        return "Tuntas" if self.nilai >= 77 else "Belum"\n\ns = Siswa("Dewi", 85)\nprint(s.nama, s.nilai, s.status())\nprint(Siswa("Budi", 70).status())',
    },
    {
        "urutan": 10,
        "judul": "Proyek Mini OOP Ganjil",
        "ringkasan": "Menggabungkan class, atribut, method, dan __init__ pada kasus nyata.",
        "isi_html": """
        <h3>Tujuan proyek</h3>
        <p>Membuktikan kamu mampu merancang class sederhana untuk masalah sehari-hari di sekolah/toko.</p>
        <h3>Ide proyek</h3>
        <ul>
          <li><strong>Produk &amp; diskon</strong> — atribut nama/harga, method hitung diskon</li>
          <li><strong>Nilai siswa</strong> — atribut nama/nilai, method predikat &amp; tuntas</li>
          <li><strong>Peminjaman buku</strong> — status dipinjam/tersedia</li>
        </ul>
        <h3>Checklist sebelum mengumpulkan</h3>
        <ol>
          <li>Ada class dengan <code>__init__</code></li>
          <li>Minimal 2 atribut bermakna</li>
          <li>Minimal 2 method (selain <code>__init__</code>)</li>
          <li>Ada contoh pembuatan object dan pemanggilan method</li>
          <li>Nama class/atribut jelas (bukan <code>a</code>, <code>b</code>)</li>
        </ol>
        """,
        "contoh_kode": 'class Produk:\n    def __init__(self, nama, harga):\n        self.nama = nama\n        self.harga = harga\n    def diskon(self, persen):\n        return self.harga * (100 - persen) / 100\n    def info(self):\n        return f"{self.nama}: Rp{self.harga}"\n\np = Produk("Pulpen", 5000)\nprint(p.info())\nprint("Harga setelah diskon 10%:", p.diskon(10))',
    },
]

MATERI_GENAP = [
    {
        "urutan": 1,
        "judul": "Inheritance (Pewarisan)",
        "ringkasan": "Class anak mewarisi sifat class induk lalu menambah fitur baru.",
        "isi_html": """
        <h3>Ide utama</h3>
        <p>Inheritance menghindari menyalin kode class yang mirip. Class anak memakai method/atribut induk,
        lalu boleh menambah atau mengganti (override) perilakunya.</p>
        <h3>Sintaks</h3>
        <pre>class Anak(Induk):
    ...</pre>
        <h3>Override</h3>
        <p>Jika class anak menulis ulang method dengan nama sama, pemanggilan lewat object anak memakai versi anak.</p>
        <h3>Contoh sekolah</h3>
        <p>Class <code>Pengguna</code> punya login. Class <code>Siswa</code> dan <code>Guru</code> mewarisinya,
        lalu menambah menu yang berbeda.</p>
        """,
        "contoh_kode": 'class Hewan:\n    def suara(self):\n        print("...")\n\nclass Kucing(Hewan):\n    def suara(self):\n        print("Meong")\n\nclass Anjing(Hewan):\n    def suara(self):\n        print("Guk")\n\nKucing().suara()\nAnjing().suara()',
    },
    {
        "urutan": 2,
        "judul": "Encapsulation Dasar",
        "ringkasan": "Melindungi data object agar perubahan lebih aman dan terkontrol.",
        "isi_html": """
        <h3>Masalah data terbuka</h3>
        <p>Jika saldo rekening bisa diubah bebas dari luar (<code>r.saldo = -999</code>), data mudah rusak.
        Encapsulation membatasi cara mengubah data.</p>
        <h3>Konvensi Python</h3>
        <ul>
          <li><code>_nama</code> — internal (jangan diutak-atik sembarangan)</li>
          <li><code>__nama</code> — name mangling, lebih ketat</li>
        </ul>
        <h3>Getter / setter</h3>
        <p>Method <code>lihat()</code> / <code>setor()</code> mengontrol baca-tulis. Setoran negatif bisa ditolak.</p>
        """,
        "contoh_kode": 'class Rekening:\n    def __init__(self, saldo):\n        self.__saldo = saldo\n    def lihat(self):\n        return self.__saldo\n    def setor(self, x):\n        if x > 0:\n            self.__saldo += x\n        else:\n            print("Setoran harus positif")\n\nr = Rekening(1000)\nr.setor(500)\nr.setor(-10)\nprint(r.lihat())',
    },
    {
        "urutan": 3,
        "judul": "JSON Sederhana",
        "ringkasan": "Menyimpan dict/list ke format JSON agar data mudah dibaca ulang.",
        "isi_html": """
        <h3>Apa itu JSON?</h3>
        <p>Format teks untuk data terstruktur, mirip dict/list Python. Banyak dipakai API dan penyimpanan konfigurasi.</p>
        <h3>Modul json</h3>
        <ul>
          <li><code>json.dumps(data)</code> — Python → string JSON</li>
          <li><code>json.loads(teks)</code> — string JSON → Python</li>
          <li><code>json.dump</code> / <code>json.load</code> — langsung ke/dari file</li>
        </ul>
        <h3>Hubungan materi sebelumnya</h3>
        <p>Gabungkan dengan file handling: simpan nilai siswa ke <code>nilai.json</code>, lalu baca lagi saat program dibuka.</p>
        """,
        "contoh_kode": 'import json\ndata = {"nama": "Rafi", "nilai": 88, "mapel": ["Koding", "Matematika"]}\nteks = json.dumps(data, ensure_ascii=False)\nprint(teks)\nbalik = json.loads(teks)\nprint(balik["nama"], balik["nilai"])',
    },
    {
        "urutan": 4,
        "judul": "Algoritma Searching",
        "ringkasan": "Mencari data: linear search dan pengenalan binary search.",
        "isi_html": """
        <h3>Searching</h3>
        <p>Mencari apakah suatu nilai ada di kumpulan data, dan di indeks berapa.</p>
        <h3>Linear search</h3>
        <p>Cek satu per satu dari awal. Mudah dipahami, cocok data kecil. Perkiraan langkah: O(n).</p>
        <h3>Binary search</h3>
        <p>Data <strong>harus terurut</strong>. Tiap langkah membuang setengah data. Lebih cepat untuk data besar.</p>
        <h3>Kaitan Kelas 7</h3>
        <p>Kamu sudah memakai loop untuk memeriksa list. Sekarang pola itu diberi nama algoritma dan dianalisis.</p>
        """,
        "contoh_kode": 'def linear_search(data, target):\n    for i, x in enumerate(data):\n        if x == target:\n            return i\n    return -1\n\ndata = [4, 7, 9, 2]\nprint(linear_search(data, 9))\nprint(linear_search(data, 5))',
    },
    {
        "urutan": 5,
        "judul": "Algoritma Sorting",
        "ringkasan": "Mengurutkan data: bubble sort, selection sort, dan sorted() bawaan.",
        "isi_html": """
        <h3>Mengapa mengurutkan?</h3>
        <p>Data terurut memudahkan pencarian, peringkat nilai, dan laporan.</p>
        <h3>Yang perlu dipahami</h3>
        <ul>
          <li><strong>Bubble sort</strong> — tukar pasangan bersebelahan berulang</li>
          <li><strong>Selection sort</strong> — pilih elemen ekstrem, tempatkan di posisi yang benar</li>
          <li><code>sorted(data)</code> — bawaan Python, mengembalikan list baru</li>
          <li><code>data.sort()</code> — mengurutkan list asli (in-place)</li>
        </ul>
        <h3>Pesan pembelajaran</h3>
        <p>Di dunia nyata sering memakai <code>sorted</code>, tetapi menulis bubble/selection melatih cara berpikir langkah demi langkah.</p>
        """,
        "contoh_kode": 'def bubble_sort(data):\n    a = data[:]\n    n = len(a)\n    for i in range(n):\n        for j in range(0, n - i - 1):\n            if a[j] > a[j + 1]:\n                a[j], a[j + 1] = a[j + 1], a[j]\n    return a\n\nangka = [5, 1, 4, 2]\nprint(bubble_sort(angka))\nprint(sorted(angka))\nprint(angka)  # asli tidak berubah karena bubble memakai salinan',
    },
    {
        "urutan": 6,
        "judul": "Rekursi Dasar",
        "ringkasan": "Fungsi yang memanggil dirinya sendiri dengan base case yang jelas.",
        "isi_html": """
        <h3>Rekursi</h3>
        <p>Fungsi memanggil dirinya untuk menyelesaikan versi masalah yang lebih kecil.</p>
        <h3>Dua bagian wajib</h3>
        <ul>
          <li><strong>Base case</strong> — kondisi berhenti</li>
          <li><strong>Recursive case</strong> — memanggil diri dengan input lebih kecil</li>
        </ul>
        <h3>Contoh</h3>
        <p>Faktorial: <code>n! = n × (n-1)!</code>, dengan <code>1! = 1</code>.</p>
        <h3>Peringatan</h3>
        <p>Tanpa base case → <code>RecursionError</code>. Untuk n besar, versi loop kadang lebih aman/cepat.</p>
        """,
        "contoh_kode": 'def faktorial(n):\n    if n <= 1:\n        return 1\n    return n * faktorial(n - 1)\n\nprint(faktorial(5))  # 120\n\ndef hitung_mundur(n):\n    if n <= 0:\n        print("selesai")\n        return\n    print(n)\n    hitung_mundur(n - 1)\n\nhitung_mundur(3)',
    },
    {
        "urutan": 7,
        "judul": "GUI Sederhana dengan Tkinter",
        "ringkasan": "Membuat jendela interaktif: label, tombol, dan event loop.",
        "isi_html": """
        <h3>Dari console ke jendela</h3>
        <p>Selama ini input/output lewat teks. Tkinter (bawaan Python) membuat antarmuka grafis sederhana.</p>
        <h3>Komponen dasar</h3>
        <ul>
          <li><code>Tk()</code> — jendela utama</li>
          <li><code>Label</code> — teks</li>
          <li><code>Button</code> — tombol dengan <code>command</code></li>
          <li><code>Entry</code> — kotak input</li>
          <li><code>mainloop()</code> — menunggu aksi pengguna</li>
        </ul>
        <h3>Catatan</h3>
        <p>Di lingkungan server web, GUI desktop tidak ditampilkan ke browser. Materi ini untuk latihan di komputer lokal siswa/guru.</p>
        """,
        "contoh_kode": 'import tkinter as tk\nroot = tk.Tk()\nroot.title("Koding 8")\ntk.Label(root, text="Halo Kelas 8").pack(padx=12, pady=8)\ntk.Button(root, text="Tutup", command=root.destroy).pack(pady=8)\n# root.mainloop()  # aktifkan saat dijalankan di komputer lokal',
    },
    {
        "urutan": 8,
        "judul": "Debugging & Testing Dasar",
        "ringkasan": "Menemukan bug dengan traceback, print, dan assert.",
        "isi_html": """
        <h3>Bug itu normal</h3>
        <p>Programmer menghabiskan banyak waktu memperbaiki kesalahan. Yang penting: punya cara sistematis.</p>
        <h3>Langkah debugging</h3>
        <ol>
          <li>Baca pesan error / traceback dari bawah ke atas</li>
          <li>Cetak nilai variabel di titik mencurigakan</li>
          <li>Uji dengan input sederhana yang hasilnya sudah kamu ketahui</li>
          <li>Perbaiki, lalu uji lagi</li>
        </ol>
        <h3>assert</h3>
        <p><code>assert kondisi, "pesan"</code> memaksa program berhenti jika kondisi salah — berguna saat menulis tes kecil.</p>
        """,
        "contoh_kode": 'def rata(data):\n    assert len(data) > 0, "Data kosong"\n    return sum(data) / len(data)\n\nprint(rata([80, 90, 70]))\ntry:\n    print(rata([]))\nexcept AssertionError as e:\n    print("Tertangkap:", e)',
    },
    {
        "urutan": 9,
        "judul": "Best Practice & Dokumentasi",
        "ringkasan": "Menulis kode yang rapi, mudah dibaca, dan terdokumentasi.",
        "isi_html": """
        <h3>Kode dibaca manusia</h3>
        <p>Komputer menerima kode jelek sekalipun. Teman dan kamu sendiri di masa depan membutuhkan kode yang jelas.</p>
        <h3>Praktik baik</h3>
        <ul>
          <li>Nama variabel/fungsi menjelaskan makna</li>
          <li>Satu fungsi = satu tugas (jangan terlalu panjang)</li>
          <li>Docstring menjelaskan tujuan</li>
          <li>DRY — Don't Repeat Yourself</li>
          <li>Konsisten dalam gaya penulisan</li>
        </ul>
        <h3>Docstring</h3>
        <pre>def luas_segitiga(alas, tinggi):
    '''Menghitung luas segitiga.'''
    return 0.5 * alas * tinggi</pre>
        """,
        "contoh_kode": "def luas_segitiga(alas, tinggi):\n    '''Menghitung luas segitiga.'''\n    return 0.5 * alas * tinggi\n\nprint(luas_segitiga.__doc__)\nprint(luas_segitiga(10, 4))",
    },
    {
        "urutan": 10,
        "judul": "Proyek Akhir Kelas 8",
        "ringkasan": "Menggabungkan OOP, JSON/file, dan logika/algoritma sederhana.",
        "isi_html": """
        <h3>Proyek terpadu</h3>
        <p>Ini puncak Kelas 8: bukan materi baru, melainkan menyatukan yang sudah dipelajari.</p>
        <h3>Contoh aplikasi nilai</h3>
        <ul>
          <li>Class menyimpan data nilai</li>
          <li>Method tambah, rata-rata, cari nama</li>
          <li>Simpan/muat lewat JSON</li>
          <li>Tangani error input</li>
        </ul>
        <h3>Rubrik singkat</h3>
        <ol>
          <li>OOP dipakai dengan benar</li>
          <li>Ada penyimpanan data (file/JSON)</li>
          <li>Ada proses/logika (cari, urut, atau rekap)</li>
          <li>Ada penanganan error dasar</li>
          <li>Kode rapi + docstring singkat</li>
        </ol>
        """,
        "contoh_kode": 'import json\n\nclass NilaiApp:\n    def __init__(self):\n        self.data = {}\n    def tambah(self, nama, nilai):\n        self.data[nama] = nilai\n    def rata(self):\n        return sum(self.data.values()) / len(self.data) if self.data else 0\n    def simpan(self, path):\n        with open(path, "w", encoding="utf-8") as f:\n            json.dump(self.data, f, ensure_ascii=False, indent=2)\n\napp = NilaiApp()\napp.tambah("Aisyah", 90)\napp.tambah("Budi", 78)\nprint("Rata-rata:", app.rata())\nprint(app.data)',
    },
]
