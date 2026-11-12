"""Isi panjang tambahan per modul agar PDF mencapai minimal ~20 halaman."""

from __future__ import annotations


def _c(level, judul, kode, output, tips):
    return {"level": level, "judul": judul, "kode": kode, "output": output, "tips": tips}


def _bab(judul, teks, contoh):
    return {"judul": judul, "teks": teks, "contoh": contoh}


def pengayaan(modul: dict) -> list[dict]:
    """Gabungkan bab katalog + bab tambahan sesuai kode modul."""
    dasar = list(modul.get("bab") or [])
    ekstra = EKSTRA.get(modul["kode"], [])
    return dasar + ekstra


def tujuan_belajar(modul: dict) -> list[str]:
    tingkat = modul.get("tingkat", "7")
    return [
        f"Memahami konsep inti «{modul['judul']}» dengan bahasa sederhana murid SMP.",
        "Menjalankan contoh program bertingkat: Mudah, Sedang, dan Sulit.",
        "Menjelaskan kembali isi modul kepada teman dengan kata sendiri.",
        "Mengerjakan latihan mandiri dan proyek mini di akhir modul.",
        f"Siap memakai bekal ini untuk materi berikutnya di Kelas {tingkat}.",
    ]


def kuis(modul: dict) -> list[dict]:
    """15 soal pilihan singkat terkait modul (tanpa kunci di list ini dipakai terpisah)."""
    j = modul["judul"]
    return [
        {"n": i + 1, "q": q, "a": a}
        for i, (q, a) in enumerate(
            [
                (f"Modul «{j}» paling cocok dipelajari dengan cara…", "Membaca lalu mengetik ulang contoh"),
                ("Urutan belajar contoh yang disarankan…", "Mudah → Sedang → Sulit"),
                ("Indentasi di Python penting karena…", "Menandai blok perintah"),
                ("print() dipakai untuk…", "Menampilkan hasil ke layar"),
                ("Variabel berguna untuk…", "Menyimpan data agar bisa dipakai lagi"),
                ("if dipakai ketika…", "Program harus memilih berdasarkan syarat"),
                ("for/while berguna untuk…", "Mengulang perintah"),
                ("List cocok untuk…", "Menyimpan banyak nilai berurutan"),
                ("Dictionary menyimpan data sebagai…", "Pasangan kunci dan nilai"),
                ("def membuat…", "Fungsi yang bisa dipanggil ulang"),
                ("Class dalam OOP adalah…", "Cetakan untuk membuat object"),
                ("Method adalah…", "Perilaku/fungsi milik object"),
                ("JSON sering dipakai untuk…", "Menyimpan data terstruktur"),
                ("Game loop artinya…", "Mengulang alur game sampai selesai"),
                ("Setelah selesai modul, sebaiknya…", "Mengerjakan refleksi dan proyek mini"),
            ]
        )
    ]


def proyek_mini(modul: dict) -> dict:
    return {
        "judul": f"Proyek Mini · {modul['judul']}",
        "brief": (
            "Buat program pendek (15–40 baris) yang memakai ide utama modul ini. "
            "Tulis nama file, tujuan program, dan cuplikan output di buku catatan atau README singkat."
        ),
        "syarat": [
            "Program bisa dijalankan tanpa error.",
            "Ada minimal satu print atau output yang jelas.",
            "Pakai konsep utama modul (jangan hanya copy contoh tanpa diubah).",
            "Ganti angka/nama menjadi data milikmu (sekolah/kelas/teman).",
            "Siap menjelaskan ke guru dalam 1 menit.",
        ],
        "rubrik": [
            ("Berjalan", "40%"),
            ("Sesuai konsep modul", "30%"),
            ("Ada sentuhan ide sendiri", "20%"),
            ("Keterampilan menjelaskan", "10%"),
        ],
    }


def glosarium(modul: dict) -> list[tuple[str, str]]:
    return [
        ("Python", "Bahasa pemrograman yang ramah untuk pemula."),
        ("Program", "Kumpulan perintah yang dijalankan komputer."),
        ("Syntax", "Aturan penulisan kode yang harus dipatuhi."),
        ("Bug", "Kesalahan dalam program."),
        ("Debug", "Proses mencari dan memperbaiki bug."),
        ("Variabel", "Tempat menyimpan data dengan nama."),
        ("Tipe data", "Jenis nilai, misalnya teks atau angka."),
        ("String", "Teks, biasanya diapit tanda kutip."),
        ("Integer", "Bilangan bulat."),
        ("Float", "Bilangan desimal."),
        ("Boolean", "Nilai benar/salah (True/False)."),
        ("Operator", "Simbol hitung atau pembanding (+, -, ==, dan sebagainya)."),
        ("Percabangan", "Pemilihan alur dengan if/elif/else."),
        ("Perulangan", "Mengulang perintah dengan for/while."),
        ("List", "Kumpulan data berurutan."),
        ("Dictionary", "Kumpulan pasangan kunci–nilai."),
        ("Fungsi", "Blok perintah yang bisa dipanggil ulang."),
        ("Parameter", "Data masuk ke fungsi."),
        ("Return", "Nilai yang dikembalikan fungsi."),
        ("Class", "Cetakan object dalam OOP."),
        ("Object", "Hasil dari class; punya data dan perilaku."),
        ("Method", "Fungsi yang menempel pada object."),
        ("Inheritance", "Pewarisan sifat class induk ke class anak."),
        ("JSON", "Format teks untuk menyimpan data terstruktur."),
        ("Modul (file)", "File Python yang berisi fungsi/class untuk diimpor."),
        ("Exception", "Kesalahan saat program berjalan; bisa ditangani try/except."),
        ("Algorithm", "Langkah-langkah logis menyelesaikan masalah."),
        ("Game loop", "Siklus ulang tampil–input–update pada game."),
        ("CRUD", "Create, Read, Update, Delete."),
        ("MVP", "Fitur wajib paling penting agar project bisa dipakai."),
    ]


# Bab ekstra per kode modul (bahasa murid SMP + contoh bertingkat)
EKSTRA: dict[str, list] = {
    "k7-m01": [
        _bab(
            "Menjalankan Python di sekolah",
            "Di lab atau HP, kamu bisa memakai editor online atau aplikasi yang disediakan guru. "
            "Yang penting: ketik perintah dengan teliti, lalu jalankan. Jika muncul tulisan merah (error), "
            "baca pesannya — biasanya ada salah ketik atau kurang tanda kutip. Jangan takut error; itu guru terbaik.",
            [
                _c("Mudah", "Tiga baris sapaan", 'print("Selamat pagi")\nprint("Selamat siang")\nprint("Selamat belajar")', "tiga baris sapaan", "Satu print = satu baris."),
                _c("Sedang", "Pakai sep=", 'print("Koding", "SMP", "22", sep="-")', "Koding-SMP-22", "sep mengatur pemisah."),
                _c("Sulit", "Pola bintang", 'print("*")\nprint("**")\nprint("***")\nprint("****")', "segitiga bintang", "Bisa juga dengan loop nanti."),
            ],
        ),
        _bab(
            "Kesalahan umum pemula",
            "Salah ketik nama perintah (pring bukan print), lupa kutip, atau huruf besar/kecil berbeda "
            "akan membuat program gagal. Python membedakan Print dan print. Biasakan membaca error dari baris paling bawah.",
            [
                _c("Mudah", "Perbaiki kutip", 'print("Halo")  # benar', "Halo", "Kutip pembuka dan penutup harus pasangan."),
                _c("Sedang", "Gabung tanpa error", 'print("Nilai =", 90)', "Nilai = 90", "Campur teks dan angka di print."),
                _c("Sulit", "Pesan error dibaca", 'teks = "angka"\n# int(teks) akan error ValueError\nprint("Cek dulu sebelum konversi")', "Cek dulu sebelum konversi", "Jangan langsung paksa ubah tipe."),
            ],
        ),
        _bab(
            "Latihan kreativitas teks",
            "Kamu bisa membuat poster ASCII sederhana hanya dengan print. Ini melatih ketelitian dan rasa seni kode.",
            [
                _c("Mudah", "Garis pemisah", 'print("-" * 30)', "------------------------------", "* mengulang karakter."),
                _c("Sedang", "Bingkai judul", 'print("+" + "-" * 18 + "+")\nprint("| BELAJAR PYTHON  |")\nprint("+" + "-" * 18 + "+")', "kotak judul", "Gabungkan string."),
                _c("Sulit", "Jadwal singkat", 'hari = ["Sen", "Sel", "Rab"]\nfor h in hari:\n    print(h, "- Koding")', "Sen - Koding ...", "Persiapan ke materi loop."),
            ],
        ),
        _bab(
            "Hubungan dengan kehidupan sekolah",
            "print dipakai untuk menampilkan nilai, pengumuman kelas, atau hasil kuis. Semakin rapi outputmu, "
            "semakin mudah orang lain memahami programmu.",
            [
                _c("Mudah", "Pengumuman", 'print("[PENGUMUMAN] Bawa buku koding")', "[PENGUMUMAN] Bawa buku koding", "Tanda kurung siku sebagai label."),
                _c("Sedang", "Rapor mini", 'print("Mapel: Koding")\nprint("Nilai:", 88)\nprint("Predikat: Baik")', "tiga baris rapor", "Susun informasi berurutan."),
                _c("Sulit", "Template absensi", 'nama = "Aisyah"\nstatus = "Hadir"\nprint(f"{nama:10} | {status}")', "Aisyah     | Hadir", "f-string merapikan tampilan."),
            ],
        ),
    ],
    "k7-m02": [
        _bab(
            "Aturan nama variabel",
            "Nama variabel boleh huruf, angka, dan garis bawah, tetapi tidak boleh diawali angka. "
            "Pilih nama yang bermakna: nilai_uts lebih jelas daripada x.",
            [
                _c("Mudah", "Nama yang baik", 'nilai_uts = 85\nprint(nilai_uts)', "85", "Pakai snake_case."),
                _c("Sedang", "Tukar nilai", 'a, b = 7, 8\na, b = b, a\nprint(a, b)', "8 7", "Python bisa tukar elegan."),
                _c("Sulit", "Hitung sisa bagi", 'jumlah = 20\nprint(jumlah % 3)', "2", "% = sisa pembagian."),
            ],
        ),
        _bab(
            "Tipe data di sekitar kita",
            "Nama siswa = string, umur = int, tinggi = float, lulus = bool. Mengetahui tipe membantu memilih operasi yang tepat.",
            [
                _c("Mudah", "Cek tipe", 'print(type(10))\nprint(type("10"))', "<class 'int'> / <class 'str'>", "Kutip mengubah angka jadi teks."),
                _c("Sedang", "Float uang jajan", 'jajan = 15.5\nprint(jajan * 2)', "31.0", "Desimal memakai titik."),
                _c("Sulit", "Bool dari perbandingan", 'tuntas = 80 >= 77\nprint(tuntas, type(tuntas))', "True <class 'bool'>", "Hasil perbandingan = boolean."),
            ],
        ),
        _bab(
            "Operator pembanding & logika",
            "Selain hitung, ada == != > < >= <=, serta and/or/not untuk menggabungkan syarat.",
            [
                _c("Mudah", "Bandingkan nilai", 'print(90 > 77)', "True", "Hasilnya True/False."),
                _c("Sedang", "Syarat ganda", 'nilai = 85\nprint(nilai >= 77 and nilai <= 100)', "True", "and = kedua syarat benar."),
                _c("Sulit", "Rentang aman", 'n = 105\nvalid = 0 <= n <= 100\nprint(valid)', "False", "Python mengizinkan rantai perbandingan."),
            ],
        ),
        _bab(
            "Kalkulator nilai kelas",
            "Gabungkan variabel dan operator untuk menghitung total, rata-rata, dan selisih terhadap KKM.",
            [
                _c("Mudah", "Total", 'print(80 + 90 + 70)', "240", "Jumlahkan dulu."),
                _c("Sedang", "Selisih KKM", 'nilai, kkm = 70, 77\nprint(kkm - nilai)', "7", "Butuh 7 poin lagi."),
                _c("Sulit", "Rata + pembulatan", 'rata = (88 + 76 + 92) / 3\nprint(round(rata, 1))', "85.3", "round membulatkan desimal."),
            ],
        ),
    ],
    "k7-m03": [
        _bab(
            "if bertingkat (elif)",
            "Kadang pilihan lebih dari dua: sangat baik, baik, cukup, kurang. Gunakan if-elif-else.",
            [
                _c("Mudah", "Dua cabang", 'x = 10\nif x > 0:\n    print("positif")', "positif", "Blok if harus menjorok."),
                _c("Sedang", "Predikat", 'n = 82\nif n >= 90:\n    print("A")\nelif n >= 77:\n    print("B")\nelse:\n    print("C")', "B", "Urutan syarat penting."),
                _c("Sulit", "Validasi dulu", 'n = -5\nif n < 0 or n > 100:\n    print("nilai tidak valid")\nelif n >= 77:\n    print("tuntas")\nelse:\n    print("belum")', "nilai tidak valid", "Validasi sebelum penilaian."),
            ],
        ),
        _bab(
            "for vs while",
            "for cocok jika sudah tahu berapa kali ulang. while cocok jika berhenti berdasarkan kondisi.",
            [
                _c("Mudah", "for range", 'for i in range(3):\n    print("hi", i)', "hi 0..2", "range mulai dari 0."),
                _c("Sedang", "while turun", 'n = 3\nwhile n > 0:\n    print(n)\n    n -= 1', "3 2 1", "Ubah variabel kondisi."),
                _c("Sulit", "Jumlah 1..N", 'N = 5\ntotal = 0\nfor i in range(1, N+1):\n    total += i\nprint(total)', "15", "Akumulator total."),
            ],
        ),
        _bab(
            "break dan continue",
            "break menghentikan loop. continue melewatkan sisa putaran lalu lanjut berikutnya.",
            [
                _c("Mudah", "break", 'for i in range(10):\n    if i == 3:\n        break\n    print(i)', "0 1 2", "Berhenti saat i==3."),
                _c("Sedang", "continue", 'for i in range(5):\n    if i % 2 == 0:\n        continue\n    print(i)', "1 3", "Lewati genap."),
                _c("Sulit", "Cari lalu berhenti", 'data = [70, 80, 90]\nfor n in data:\n    if n >= 85:\n        print("ketemu", n)\n        break', "ketemu 90", "Pola searching sederhana."),
            ],
        ),
        _bab(
            "Pola bintang & tabel kecil",
            "Loop bersarang (nested) membuat pola. Mulai dari pola sederhana agar tidak bingung.",
            [
                _c("Mudah", "5 bintang", 'print("*" * 5)', "*****", "Tanpa nested dulu."),
                _c("Sedang", "Segitiga", 'for i in range(1, 5):\n    print("*" * i)', "* ** *** ****", "i mengatur jumlah."),
                _c("Sulit", "Tabel perkalian 2", 'for i in range(1, 6):\n    print(f"2 x {i} = {2*i}")', "2 x 1 = 2 ...", "f-string untuk tabel."),
            ],
        ),
    ],
    "k7-m04": [
        _bab(
            "Operasi list penting",
            "append menambah, indexing mengambil, slicing memotong, len menghitung panjang.",
            [
                _c("Mudah", "append", 'a = [1, 2]\na.append(3)\nprint(a)', "[1, 2, 3]", "Menambah di akhir."),
                _c("Sedang", "slicing", 'a = [10, 20, 30, 40]\nprint(a[1:3])', "[20, 30]", "Dari index 1 sampai sebelum 3."),
                _c("Sulit", "Rata list", 'nilai = [80, 90, 70]\nprint(sum(nilai)/len(nilai))', "80.0", "sum dan len pasangan kuat."),
            ],
        ),
        _bab(
            "Dictionary lebih dalam",
            "Kamu bisa mengubah nilai, menambah kunci baru, atau mengulang semua pasangan kunci–nilai.",
            [
                _c("Mudah", "Ubah nilai", 's = {"nama": "Budi", "nilai": 80}\ns["nilai"] = 90\nprint(s)', "{'nama': 'Budi', 'nilai': 90}", "Assign ulang kunci."),
                _c("Sedang", "Loop items", 's = {"a": 1, "b": 2}\nfor k, v in s.items():\n    print(k, v)', "a 1 / b 2", "items() = pasangan."),
                _c("Sulit", "List of dict", 'data = [{"nama": "A", "n": 80}, {"nama": "B", "n": 90}]\nprint(data[1]["nama"])', "B", "Pola data siswa nyata."),
            ],
        ),
        _bab(
            "Fungsi dengan beberapa parameter",
            "Fungsi bisa menerima lebih dari satu masukan dan mengembalikan hasil untuk dipakai lagi.",
            [
                _c("Mudah", "Tambah", 'def tambah(a, b):\n    return a + b\nprint(tambah(2, 3))', "5", "return wajib jika butuh hasil."),
                _c("Sedang", "Default KKM", 'def tuntas(n, kkm=77):\n    return n >= kkm\nprint(tuntas(80), tuntas(70))', "True False", "Default memudahkan pemanggilan."),
                _c("Sulit", "Fungsi + list", 'def rata(nilai):\n    return sum(nilai)/len(nilai) if nilai else 0\nprint(rata([70, 80, 90]))', "80.0", "Jaga list kosong."),
            ],
        ),
        _bab(
            "Merapikan program dengan fungsi",
            "Pisahkan input, proses, dan output ke fungsi berbeda agar mudah diuji dan dibaca teman.",
            [
                _c("Mudah", "Fungsi sapa", 'def sapa(n):\n    print("Halo", n)\nsapa("Rafi")', "Halo Rafi", "Fungsi tanpa return."),
                _c("Sedang", "Pisah hitung & cetak", 'def hitung(a,b):\n    return a*b\ndef cetak(x):\n    print("Hasil:", x)\ncetak(hitung(4,5))', "Hasil: 20", "Satu fungsi satu tugas."),
                _c("Sulit", "Pipeline mini", 'def bersih(n):\n    return max(0, min(100, n))\ndef status(n):\n    return "OK" if bersih(n) >= 77 else "NO"\nprint(status(120), status(50))', "OK NO", "Validasi + keputusan."),
            ],
        ),
    ],
    "k7-m05": [
        _bab(
            "Merancang object game dengan dict",
            "Tentukan field wajib: nama, hp, skor, posisi. Semakin konsisten field-nya, semakin mudah dikembangkan.",
            [
                _c("Mudah", "Template player", 'p = {"nama": "Hero", "hp": 100, "skor": 0, "x": 0}\nprint(p.keys())', "dict_keys([...])", "keys melihat field."),
                _c("Sedang", "Gerak kanan", 'p = {"x": 0}\np["x"] += 1\nprint(p["x"])', "1", "Update posisi."),
                _c("Sulit", "Batas peta", 'p = {"x": 9}\np["x"] = min(10, p["x"] + 2)\nprint(p["x"])', "10", "Cegah keluar peta."),
            ],
        ),
        _bab(
            "Item dan benturan",
            "Item juga object. Benturan dicek dari posisi. Setelah diambil, nonaktifkan item agar tidak double.",
            [
                _c("Mudah", "Cek sama posisi", 'print({"x": 2}["x"] == {"x": 2}["x"])', "True", "Dasar collision."),
                _c("Sedang", "Ambil koin", 'p = {"x": 3, "skor": 0}\nkoin = {"x": 3, "aktif": True}\nif koin["aktif"] and p["x"] == koin["x"]:\n    p["skor"] += 1\n    koin["aktif"] = False\nprint(p, koin["aktif"])', "skor 1, aktif False", "Flag aktif penting."),
                _c("Sulit", "Damage musuh", 'p = {"hp": 50, "x": 1}\nm = {"x": 1, "dmg": 8}\nif p["x"] == m["x"]:\n    p["hp"] = max(0, p["hp"] - m["dmg"])\nprint(p["hp"])', "42", "max mencegah HP negatif."),
            ],
        ),
        _bab(
            "Menyusun game loop yang aman",
            "Selalu sediakan syarat berhenti. Loop tanpa akhir membuat program hang.",
            [
                _c("Mudah", "Loop 3 giliran", 'for giliran in range(3):\n    print("Giliran", giliran+1)', "Giliran 1..3", "for lebih aman untuk pemula."),
                _c("Sedang", "Stop saat skor", 'skor = 0\nwhile skor < 15:\n    skor += 5\nprint(skor)', "15", "Syarat jelas."),
                _c("Sulit", "Menu keluar", 'pilihan = "1"\nwhile pilihan != "0":\n    print("main...")\n    pilihan = "0"\nprint("selesai")', "main... selesai", "0 sebagai keluar."),
            ],
        ),
        _bab(
            "Menuju Kelas 8: dari dict ke class",
            "Dict + fungsi sudah cukup untuk game mini. Di Kelas 8, data dan perilaku digabung dalam class agar lebih rapi.",
            [
                _c("Mudah", "Fungsi status", 'def status(p):\n    return f"{p[\'nama\']} HP:{p[\'hp\"]}"\nprint(status({"nama":"Hero","hp":80}))', "Hero HP:80", "Fungsi membaca dict."),
                _c("Sedang", "Heal", 'def heal(p, n):\n    p["hp"] = min(100, p["hp"]+n)\np={"hp":90}; heal(p,20); print(p["hp"])', "100", "Batas maksimal 100."),
                _c("Sulit", "Skeleton class masa depan", 'class Player:\n    def __init__(self, nama):\n        self.nama = nama\n        self.hp = 100\nprint(Player("Hero").nama)', "Hero", "Pratinjau OOP Kelas 8."),
            ],
        ),
    ],
}

# Generate similar ekstra for k8 and k9 by templating if missing keys - fill remaining codes
def _isi_k8():
    return {
        "k8-m01": [
            _bab("Set operasi himpunan", "Gabungan, irisan, selisih membantu mengelola data unik seperti NIS.", [
                _c("Mudah", "add/discard", 's={1,2}; s.add(3); s.discard(1); print(s)', "{2,3}", "discard aman jika tidak ada."),
                _c("Sedang", "union", 'print({1,2}|{2,3})', "{1,2,3}", "Operator |"),
                _c("Sulit", "NIS unik", 'nis=["a","b","a"]; print(list(set(nis)))', "unik", "set hilangkan duplikat."),
            ]),
            _bab("Comprehension dengan if", "Filter dan transformasi dalam satu baris yang masih bisa dibaca.", [
                _c("Mudah", "genap", 'print([n for n in range(6) if n%2==0])', "[0,2,4]", "Filter if."),
                _c("Sedang", "upper nama", 'print([n.upper() for n in ["a","b"]])', "['A','B']", "Transformasi."),
                _c("Sulit", "dict comp", 'nilai=[80,90]; print({i:n for i,n in enumerate(nilai)})', "{0:80,1:90}", "Comprehension dict."),
            ]),
            _bab("Kapan pakai list/set/dict", "Pilih struktur data sesuai kebutuhan agar program efisien dan jelas.", [
                _c("Mudah", "urut? list", 'print([3,1,2])', "[3,1,2]", "List menjaga urutan."),
                _c("Sedang", "cari cepat unik", 'print(2 in {1,2,3})', "True", "Set bagus untuk keanggotaan."),
                _c("Sulit", "mapping", 'print({"7.5":32}.get("7.5"))', "32", "Dict untuk pasangan."),
            ]),
            _bab("Latihan gabungan Kelas 7+8", "Campur list comprehension dan fungsi kecil.", [
                _c("Mudah", "kuadrat", 'print([x*x for x in range(1,4)])', "[1,4,9]", "Dasar."),
                _c("Sedang", "fungsi+comp", 'def f(a): return [n for n in a if n>=77]\nprint(f([70,80,90]))', "[80,90]", "Bungkus filter."),
                _c("Sulit", "rata tuntas", 't=[n for n in [60,80,90] if n>=77]\nprint(sum(t)/len(t))', "85.0", "Filter lalu rata."),
            ]),
        ],
        "k8-m02": [
            _bab("*args sederhana", "Fungsi bisa menerima banyak argumen.", [
                _c("Mudah", "jumlah", 'def jumlah(*a): return sum(a)\nprint(jumlah(1,2,3))', "6", "*a jadi tuple."),
                _c("Sedang", "rata args", 'def rata(*a): return sum(a)/len(a)\nprint(rata(80,100))', "90.0", "Panjang dinamis."),
                _c("Sulit", "campur", 'def info(nama, *n): print(nama, n)\ninfo("A",80,90)', "A (80, 90)", "Posisi dulu, lalu *args."),
            ]),
            _bab("try/except/else/finally", "Tangani error dengan rapi dan selalu tutup sumber daya jika perlu.", [
                _c("Mudah", "ValueError", 'try:\n int("x")\nexcept ValueError:\n print("salah")', "salah", "Tangkap spesifik."),
                _c("Sedang", "else", 'try:\n n=int("5")\nexcept ValueError:\n n=0\nelse:\n print("ok", n)', "ok 5", "else jika sukses."),
                _c("Sulit", "banyak except", 'try:\n print([1][5])\nexcept IndexError:\n print("index")\nexcept Exception:\n print("lain")', "index", "Urut dari spesifik."),
            ]),
            _bab("Membaca dan menulis teks", "Latihan pola write/read tanpa wajib akses file nyata di semua lingkungan.", [
                _c("Mudah", "join baris", 'print("\\n".join(["a","b"]))', "a\\nb", "Siap ditulis file."),
                _c("Sedang", "parse CSV mini", 'baris="Aisyah,90"; n,v=baris.split(","); print(n,int(v))', "Aisyah 90", "split."),
                _c("Sulit", "rekap dari baris", 'data=["A,80","B,90"]; print(sum(int(x.split(",")[1]) for x in data))', "170", "Parser sederhana."),
            ]),
            _bab("Modul math & random", "Pakai pustaka bawaan untuk hitung dan acak.", [
                _c("Mudah", "sqrt", 'import math; print(math.sqrt(16))', "4.0", "import math."),
                _c("Sedang", "randint", 'import random; print(1 <= random.randint(1,6) <= 6)', "True", "Daduku."),
                _c("Sulit", "pilih siswa", 'import random; print(random.choice(["A","B","C"]))', "salah satu", "choice."),
            ]),
        ],
        "k8-m03": [
            _bab("Atribut vs method", "Atribut menyimpan; method bekerja.", [
                _c("Mudah", "set atribut", 'class A:\n pass\na=A(); a.x=1; print(a.x)', "1", "Atribut dinamis."),
                _c("Sedang", "method ubah", 'class P:\n def __init__(self):\n  self.hp=10\n def dmg(self,n):\n  self.hp-=n\np=P(); p.dmg(3); print(p.hp)', "7", "self.hp."),
                _c("Sulit", "__str__", 'class S:\n def __init__(self,n):\n  self.n=n\n def __str__(self):\n  return f"Siswa({self.n})"\nprint(S("A"))', "Siswa(A)", "Cetak object rapi."),
            ]),
            _bab("Banyak object", "Setiap object independen.", [
                _c("Mudah", "dua siswa", 'class S:\n def __init__(self,n):\n  self.n=n\nprint(S("A").n, S("B").n)', "A B", "Instans berbeda."),
                _c("Sedang", "list object", 'class S:\n def __init__(self,n):\n  self.n=n\ndata=[S("A"),S("B")]\nprint([s.n for s in data])', "['A','B']", "Koleksi object."),
                _c("Sulit", "cari object", 'class S:\n def __init__(self,n,v):\n  self.n=v; self.nama=n\ndata=[S("A",80),S("B",90)]\nprint(next(s.nama for s in data if s.n>=85))', "B", "Pencarian."),
            ]),
            _bab("Proyek mini OOP nilai", "Gabungkan __init__, method status, dan kumpulan object.", [
                _c("Mudah", "status", 'class S:\n def __init__(self,v):\n  self.v=v\n def ok(self):\n  return self.v>=77\nprint(S(80).ok())', "True", "Method boolean."),
                _c("Sedang", "rata kelas", 'class S:\n def __init__(self,v):\n  self.v=v\nkel=[S(80),S(90)]\nprint(sum(s.v for s in kel)/len(kel))', "85.0", "Agregasi."),
                _c("Sulit", "Naikkan nilai", 'class S:\n def __init__(self,v):\n  self.v=v\n def bonus(self,b):\n  self.v=min(100,self.v+b)\ns=S(95); s.bonus(10); print(s.v)', "100", "Batas 100."),
            ]),
            _bab("Kesalahan OOP pemula", "Lupa self, lupa panggil __init__, mencampur data antar object.", [
                _c("Mudah", "self wajib", 'class A:\n def hi(self):\n  print("hi")\nA().hi()', "hi", "Parameter self."),
                _c("Sedang", "init parameter", 'class S:\n def __init__(self,n):\n  self.n=n\nprint(S("A").n)', "A", "Isi saat dibuat."),
                _c("Sulit", "jangan share list salah", 'class A:\n def __init__(self):\n  self.data=[]\na=A(); b=A(); a.data.append(1); print(b.data)', "[]", "List per instance."),
            ]),
        ],
        "k8-m04": [
            _bab("super() dan override", "Panggil induk lalu spesialisasi anak.", [
                _c("Mudah", "super init", 'class A:\n def __init__(self,n):\n  self.n=n\nclass B(A):\n def __init__(self,n):\n  super().__init__(n)\nprint(B("x").n)', "x", "super()."),
                _c("Sedang", "override", 'class A:\n def info(self):\n  return "A"\nclass B(A):\n def info(self):\n  return "B"\nprint(B().info())', "B", "Anak mengganti."),
                _c("Sulit", "perluas", 'class A:\n def info(self):\n  return "dasar"\nclass B(A):\n def info(self):\n  return super().info()+"+"\nprint(B().info())', "dasar+", "Gabung induk."),
            ]),
            _bab("JSON untuk save game/nilai", "Latihan membentuk dan membaca struktur save.", [
                _c("Mudah", "dumps", 'import json; print(json.dumps({"hp":10}))', '{"hp": 10}', "Ke teks."),
                _c("Sedang", "loads", 'import json; print(json.loads(\'{"hp":10}\')["hp"])', "10", "Ke dict."),
                _c("Sulit", "update save", 'import json; s={"hs":5}; s["hs"]=max(s["hs"],9); print(json.dumps(s))', '{"hs": 9}', "Highscore."),
            ]),
            _bab("Sorting & searching praktis", "Pakai sorted dan loop untuk kasus sekolah.", [
                _c("Mudah", "sorted", 'print(sorted([3,1,2]))', "[1,2,3]", "Menaik."),
                _c("Sedang", "sorted key", 'data=[{"n":"B","v":80},{"n":"A","v":90}]; print(sorted(data,key=lambda x:x["v"], reverse=True)[0]["n"])', "A", "Key fungsi."),
                _c("Sulit", "binary search ide", 'a=[1,3,5,7]; print(5 in a)', "True", "Keanggotaan list kecil."),
            ]),
            _bab("Rekursi pengenalan", "Fungsi memanggil dirinya; wajib ada basis.", [
                _c("Mudah", "basis", 'def f(n):\n if n<=0: return 0\n return 1\nprint(f(0))', "0", "Base case."),
                _c("Sedang", "hitung mundur", 'def cd(n):\n if n==0: return\n print(n); cd(n-1)\ncd(3)', "3 2 1", "Rekursi cetak."),
                _c("Sulit", "faktorial kecil", 'def fact(n):\n return 1 if n<=1 else n*fact(n-1)\nprint(fact(5))', "120", "Klasik."),
            ]),
        ],
        "k8-m05": [
            _bab("Entity dasar game", "HP, hidup(), dan nama pada class dasar.", [
                _c("Mudah", "hidup", 'class E:\n def __init__(self,hp):\n  self.hp=hp\n def hidup(self):\n  return self.hp>0\nprint(E(1).hidup())', "True", "Method status."),
                _c("Sedang", "damage", 'class E:\n def __init__(self,hp):\n  self.hp=hp\n def kena(self,d):\n  self.hp=max(0,self.hp-d)\ne=E(10); e.kena(3); print(e.hp)', "7", "max 0."),
                _c("Sulit", "Player skor", 'class P:\n def __init__(self):\n  self.skor=0\n def plus(self,n):\n  self.skor+=n\np=P(); p.plus(5); print(p.skor)', "5", "Skor terpisah HP."),
            ]),
            _bab("List musuh dan filter", "Kelola wave musuh.", [
                _c("Mudah", "buat 2 musuh", 'class E:\n def __init__(self,n):\n  self.n=n\nprint([E("a").n, E("b").n])', "['a','b']", "List instance."),
                _c("Sedang", "filter hidup", 'class E:\n def __init__(self,hp):\n  self.hp=hp\nms=[E(0),E(5)]; print(len([m for m in ms if m.hp>0]))', "1", "Comprehension."),
                _c("Sulit", "total HP", 'ms=[3,0,7]; print(sum(h for h in ms if h>0))', "10", "Agregasi."),
            ]),
            _bab("Giliran hero vs musuh", "Simulasikan turn-based singkat.", [
                _c("Mudah", "satu pukulan", 'e=20; e-=8; print(e)', "12", "Simpel."),
                _c("Sedang", "balasan", 'p,e=30,20\ne-=10\nif e>0: p-=6\nprint(p,e)', "24 10", "Syarat balasan."),
                _c("Sulit", "loop battle", 'p,e=40,30\nwhile p>0 and e>0:\n e-=12\n if e>0: p-=7\nprint("Menang" if p>0 else "Kalah")', "Menang", "Arena."),
            ]),
            _bab("Checklist showcase arena", "Siapkan demo singkat untuk guru.", [
                _c("Mudah", "cek class", 'cek={"player":True,"enemy":True}; print(all(cek.values()))', "True", "Checklist."),
                _c("Sedang", "skor demo", 'skor=36; print("siap" if skor>0 else "belum")', "siap", "Ada skor."),
                _c("Sulit", "rubrik", 'r={"oop":1,"loop":1,"selesai":1,"readme":0}; print(sum(r.values())/len(r))', "0.75", "Proporsi."),
            ]),
        ],
    }


def _isi_k9():
    return {
        "k9-m01": [
            _bab("Menulis user story singkat", "Cerita pengguna membantu fitur tidak melenceng.", [
                _c("Mudah", "format", 'print("Sebagai guru, saya ingin rekap nilai cepat")', "teks user story", "Bahasa manusia."),
                _c("Sedang", "daftar story", 'stories=["tambah nilai","lihat rata"]; print(len(stories))', "2", "Hitung kebutuhan."),
                _c("Sulit", "prioritas", 'fitur=[("tambah",1),("pdf",3)]; print(sorted(fitur,key=lambda x:x[1])[0][0])', "tambah", "Angka prioritas."),
            ]),
            _bab("MVP vs nice-to-have", "Bedakan wajib dan tambahan.", [
                _c("Mudah", "tandai", 'print(("laporan PDF", False)[1])', "False", "Opsional."),
                _c("Sedang", "filter wajib", 'f=[("a",True),("b",False)]; print([n for n,w in f if w])', "['a']", "MVP list."),
                _c("Sulit", "progres mvp", 'wajib=["a","b","c"]; done={"a","c"}; print(len(done)/len(wajib))', "0.666...", "Progress."),
            ]),
            _bab("Kontrak data record", "Samakan field agar storage tidak kacau.", [
                _c("Mudah", "record", 'r={"nis":"1","nama":"A","nilai":80}; print(r["nis"])', "1", "Field tetap."),
                _c("Sedang", "valid kunci", 'wajib={"nis","nama","nilai"}; r={"nis":"1","nama":"A","nilai":80}; print(wajib<=r.keys())', "True", "Subset kunci."),
                _c("Sulit", "normalisasi", 'r={"Nama":"A","NILAI":"80"}; print({"nama":r["Nama"],"nilai":int(r["NILAI"])})', "rapi", "Seragamkan."),
            ]),
            _bab("Dokumentasi kickoff 1 halaman", "Ringkas masalah, pengguna, MVP, risiko.", [
                _c("Mudah", "judul", 'print("# Kickoff RekapNilai9")', "markdown judul", "Mulai docs."),
                _c("Sedang", "risiko", 'risiko=["input kosong"]; print("- "+risiko[0])', "- input kosong", "Catat risiko."),
                _c("Sulit", "template", 'doc={"masalah":"...","mvp":["a"]}; print(list(doc))', "kunci doc", "Struktur dokumen."),
            ]),
        ],
        "k9-m02": [
            _bab("Loop menu yang kuat", "Validasi input dan pisahkan handler.", [
                _c("Mudah", "dispatch", 'def lihat(): print("lihat")\n{"1":lihat}["1"]()', "lihat", "Dict fungsi."),
                _c("Sedang", "default", 'cmd={"1":lambda:print("ok")}; cmd.get("9", lambda:print("salah"))()', "salah", "get default."),
                _c("Sulit", "loop aman", 'for _ in range(2):\n print("menu")\n break', "menu", "Cegah infinite saat latihan."),
            ]),
            _bab("Pemisahan storage", "Isolasi baca/tulis dari UI.", [
                _c("Mudah", "repo list", 'db=[]; db.append(1); print(db)', "[1]", "Fake DB."),
                _c("Sedang", "save load", 'data=[1,2]; teks=str(data); print(eval(teks) if False else data)', "[1,2]", "Ide persist."),
                _c("Sulit", "json payload", 'import json; print(json.dumps({"data":[1]}))', '{"data": [1]}', "Standar."),
            ]),
            _bab("Validasi sebelum simpan", "Tolak data rusak lebih awal.", [
                _c("Mudah", "nama kosong", 'nama="  "; print(not nama.strip())', "True", "strip."),
                _c("Sedang", "nilai range", 'n=120; print(0<=n<=100)', "False", "Rentang."),
                _c("Sulit", "fungsi valid", 'def valid(n):\n try: x=int(n); return 0<=x<=100\n except: return False\nprint(valid("80"), valid("x"))', "True False", "try."),
            ]),
            _bab("Testing mini assert", "Kunci regresi sebelum demo.", [
                _c("Mudah", "assert dasar", 'assert 1+1==2; print("ok")', "ok", "assert."),
                _c("Sedang", "fungsi", 'def rata(a): return sum(a)/len(a)\nassert rata([80,100])==90; print("lulus")', "lulus", "Uji fungsi."),
                _c("Sulit", "kasus kosong", 'def rata(a): return sum(a)/len(a) if a else 0\nassert rata([])==0; print("aman")', "aman", "Edge case."),
            ]),
        ],
        "k9-m03": [
            _bab("Peta route", "Rancang navigasi sebelum coding.", [
                _c("Mudah", "dict route", 'print({"/":"home","/nilai":"list"})', "peta", "Path->halaman."),
                _c("Sedang", "404", 'r={"/":"home"}; print(r.get("/x","404"))', "404", "get."),
                _c("Sulit", "konteks", 'ctx={"judul":"Nilai","n":3}; print(ctx["judul"]+":"+str(ctx["n"]))', "Nilai:3", "Template data."),
            ]),
            _bab("CRUD lengkap singkat", "Latihan empat operasi.", [
                _c("Mudah", "create", 'd=[]; d.append({"id":1}); print(d)', "create", "append."),
                _c("Sedang", "update", 'd=[{"id":1,"n":1}]; d[0]["n"]=2; print(d)', "update", "ubah field."),
                _c("Sulit", "delete", 'd=[{"id":1},{"id":2}]; d=[x for x in d if x["id"]!=1]; print(d)', "[{'id':2}]", "filter."),
            ]),
            _bab("Form validation messages", "Pesan error harus manusiawi.", [
                _c("Mudah", "pesan", 'print("Nama wajib diisi")', "teks", "Jelas."),
                _c("Sedang", "kumpul error", 'err=["nama","nilai"]; print("; ".join(err))', "nama; nilai", "join."),
                _c("Sulit", "pipeline", 'form={"nama":"","nilai":"a"}; e=[];\nif not form["nama"]: e.append("nama")\ntry: int(form["nilai"])\nexcept: e.append("nilai")\nprint(e)', "['nama','nilai']", "Multi error."),
            ]),
            _bab("Laporan filter", "Ringkas angka untuk guru.", [
                _c("Mudah", "count", 'print(len([90,70,80]))', "3", "jumlah."),
                _c("Sedang", "tuntas", 'print(sum(1 for n in [90,70,80] if n>=77))', "2", "filter count."),
                _c("Sulit", "ringkas", 'n=[88,76,92]; print({"rata":round(sum(n)/len(n),1),"tuntas":sum(1 for x in n if x>=77)})', "dict laporan", "payload."),
            ]),
        ],
        "k9-m04": [
            _bab("State transitions", "Gambar tabel transisi state.", [
                _c("Mudah", "start", 's="menu"; s="play" if s=="menu" else s; print(s)', "play", "transisi."),
                _c("Sedang", "gameover", 's="play"; s="gameover"; print(s)', "gameover", "akhir."),
                _c("Sulit", "abaikan input salah state", 's,skor="menu",0\nif s=="play": skor+=1\nprint(skor)', "0", "Guard."),
            ]),
            _bab("Multi entity update", "Tick: gerak → tabrak → bersih.", [
                _c("Mudah", "gerak", 'x=0; x+=1; print(x)', "1", "update."),
                _c("Sedang", "tabrak", 'print(2==2)', "True", "cek."),
                _c("Sulit", "bersih", 'items=[1,2,2]; px=2; print([i for i in items if i!=px])', "[1]", "hapus."),
            ]),
            _bab("Highscore file mindset", "Muat → bandingkan → simpan.", [
                _c("Mudah", "banding", 'print(max(10,25))', "25", "max."),
                _c("Sedang", "update dict", 'd={"hs":10}; d["hs"]=max(d["hs"],25); print(d)', "{'hs':25}", "update."),
                _c("Sulit", "json", 'import json; print(json.dumps({"hs":25}))', '{"hs": 25}', "persist."),
            ]),
            _bab("Playtest notes", "Catat bug sebelum showcase.", [
                _c("Mudah", "log", 'print("BUG: HP negatif")', "catatan", "tulis."),
                _c("Sedang", "prioritas", 'bugs=[("crash",1),("typo",3)]; print(sorted(bugs,key=lambda x:x[1])[0][0])', "crash", "utamakan."),
                _c("Sulit", "done", 'todo=["collision","save"]; done=["save"]; print([t for t in todo if t not in done])', "['collision']", "sisa."),
            ]),
        ],
        "k9-m05": [
            _bab("Arsitektur capstone", "Game/App + Entity + Storage + Docs.", [
                _c("Mudah", "komponen", 'print(["Game","Entity","Storage","README"])', "list", "arsitektur."),
                _c("Sedang", "dependency", 'ok={"entity":True,"storage":True}; print(all(ok.values()))', "True", "siap."),
                _c("Sulit", "skeleton", 'class App:\n def __init__(self):\n  self.state="menu"\nprint(App().state)', "menu", "awal."),
            ]),
            _bab("Rubrik penilaian diri", "Nilai projectmu sebelum dikumpul.", [
                _c("Mudah", "cek", 'print({"berjalan":True})', "dict", "awal."),
                _c("Sedang", "skor", 'r=[1,1,1,0]; print(sum(r)/len(r)*100)', "75.0", "%."),
                _c("Sulit", "gap", 'w={"a","b","c","d"}; p={"a","b","d"}; print(w-p)', "{'c'}", "kurang."),
            ]),
            _bab("Demo script 3 menit", "Urutan demo yang meyakinkan.", [
                _c("Mudah", "langkah", 'print(["buka","fitur","save","readme"])', "urutan", "demo."),
                _c("Sedang", "timer", 'steps=4; print(f"{180//steps}s per langkah")', "45s per langkah", "bagi waktu."),
                _c("Sulit", "checklist demo", 'c={"jalan":1,"crud":1,"save":1}; print(all(c.values()))', "True", "go."),
            ]),
            _bab("After action review", "Refleksi setelah showcase.", [
                _c("Mudah", "apa yang jalan", 'print("Yang sukses: ...")', "teks", "catat."),
                _c("Sedang", "perbaiki", 'print(["uji lebih awal","pecah fungsi"])', "aksi", "next."),
                _c("Sulit", "target next", 'target={"flask":True,"game":True}; print(len(target))', "2", "lanjut belajar."),
            ]),
        ],
    }


EKSTRA.update(_isi_k8())
EKSTRA.update(_isi_k9())
