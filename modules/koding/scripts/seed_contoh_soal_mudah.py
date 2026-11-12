"""
Tambah contoh soal mudah (10 soal + pembahasan) untuk SETIAP materi kelas 7 & 8.
Menambah latihan terhubung ke materi; tidak menghapus soal lama.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from koding.config import Config  # noqa: E402


def Q(q, a, b, c, d, kunci, pembahasan):
    return {
        "pertanyaan": q,
        "opsi_a": a,
        "opsi_b": b,
        "opsi_c": c,
        "opsi_d": d,
        "kunci": kunci,
        "pembahasan": pembahasan,
    }


def soal_untuk(judul: str, tingkat: str, semester: str) -> list[dict]:
    j = judul.lower()
    bank: list[dict] = []

    # ----- Kelas 7 Ganjil -----
    if "pengenalan python" in j:
        bank = [
            Q("Siapa pencipta bahasa Python?", "Bill Gates", "Guido van Rossum", "Elon Musk", "Mark Zuckerberg", "B", "Python dibuat Guido van Rossum."),
            Q("Python cocok untuk pemula karena...", "Sintaksnya sulit", "Sintaksnya mudah dibaca", "Tidak punya print", "Tidak dipakai industri", "B", "Sintaks Python mirip bahasa sehari-hari."),
            Q("Manakah yang termasuk keunggulan Python?", "Hanya untuk game", "Banyak dipakai data, web, AI", "Tidak punya komunitas", "Tidak bisa matematika", "B", "Python dipakai luas di banyak bidang."),
            Q("Perintah pertama yang biasanya dicoba pemula adalah...", "delete()", "print(\"Halo\")", "crash()", "stop()", "B", "print() menampilkan teks ke layar."),
            Q("Python disebut bahasa tingkat tinggi karena...", "Dekat dengan bahasa mesin saja", "Lebih mudah dipahami manusia", "Tidak bisa dijalankan", "Hanya untuk hardware", "B", "Bahasa tingkat tinggi lebih dekat ke manusia."),
            Q("Ekstensi file program Python biasanya...", ".txt", ".py", ".docx", ".exe saja", "B", "File Python berakhiran .py."),
            Q("Apakah Python case-sensitive?", "Tidak", "Ya, huruf besar/kecil dibedakan", "Hanya di Windows", "Hanya di HP", "B", "Nama dan Nama dianggap berbeda."),
            Q("Komunitas Python umumnya...", "Sangat kecil", "Besar dan aktif", "Tidak ada", "Hanya 1 orang", "B", "Komunitas Python besar dan membantu."),
            Q("Manakah pernyataan benar?", "Python hanya untuk ahli", "Python cocok dipelajari di SMP", "Python tidak bisa print angka", "Python wajib bayar lisensi mahal untuk belajar dasar", "B", "Python ramah untuk pemula termasuk siswa SMP."),
            Q("Tujuan belajar koding di sekolah terutama...", "Menghafal tanpa praktik", "Melatih logika dan pemecahan masalah", "Mengganti olahraga", "Menghapus matematika", "B", "Koding melatih berpikir logis."),
        ]
    elif "print()" in j or "output" in j:
        bank = [
            Q("Fungsi untuk menampilkan teks ke layar adalah...", "input()", "print()", "type()", "len()", "B", "print() = output ke layar."),
            Q("Penulisan yang benar adalah...", "print(Halo)", "print(\"Halo\")", "print Halo", "echo Halo", "B", "Teks string harus pakai tanda kutip."),
            Q("Hasil print(7 + 5) adalah...", "75", "12", "7+5", "Error", "B", "Angka tanpa kutip dihitung dulu."),
            Q("Hasil print(\"7\" + \"5\") adalah...", "12", "75", "7 5", "Error selalu", "B", "String digabung (concatenation), jadi \"75\"."),
            Q("print(\"A\", \"B\") menampilkan...", "AB tanpa spasi selalu", "A B (dipisah spasi default)", "Error", "Hanya A", "B", "Beberapa argumen dipisah spasi."),
            Q("Untuk pindah baris baru, print...", "Otomatis menambah baris baru", "Tidak pernah pindah baris", "Wajib pakai input()", "Wajib import os", "A", "print default diakhiri newline."),
            Q("Manakah salah?", "print(10)", "print(\"10\")", "print(Halo Dunia)", "print(\"Halo Dunia\")", "C", "Teks tanpa kutip dianggap nama variabel."),
            Q("print(2 * 3) hasilnya...", "23", "6", "2*3", "Error", "B", "Operator * menghitung perkalian."),
            Q("Untuk menampilkan nama variabel x, tulis...", "print(x)", "print(\"x\") saja jika ingin nilai", "echo x", "show x", "A", "Tanpa kutip = isi variabel."),
            Q("Fungsi print termasuk...", "Input", "Output", "Database", "Browser", "B", "Output = menampilkan hasil."),
        ]
    elif "variabel" in j:
        bank = [
            Q("Variabel berfungsi sebagai...", "Penghapus file", "Wadah menyimpan data", "Browser", "Printer", "B", "Variabel menyimpan nilai."),
            Q("Nama variabel yang sah adalah...", "2nama", "nama siswa", "nama_siswa", "nama-siswa", "C", "Boleh underscore, tidak boleh spasi/diawali angka."),
            Q("Manakah nama tidak valid?", "umur20", "nilai_akhir", "1nilai", "_ok", "C", "Tidak boleh diawali angka."),
            Q("Apakah Nama dan nama sama?", "Ya selalu", "Tidak, Python case-sensitive", "Hanya di list", "Hanya di dict", "B", "Huruf besar/kecil dibedakan."),
            Q("Setelah x = 5, lalu x = 8, nilai x menjadi...", "5", "8", "13", "Error", "B", "Nilai variabel bisa diganti."),
            Q("Penulisan assignment yang benar...", "5 = x", "x == 5 untuk mengisi", "x = 5", "x := 5 wajib", "C", "Pakai satu tanda = untuk mengisi."),
            Q("Manakah nama variabel yang baik?", "a", "n", "nilai_ulangan", "x1x1x1 tanpa arti", "C", "Nama sebaiknya jelas maknanya."),
            Q("Spasi pada nama variabel...", "Boleh", "Tidak boleh", "Wajib", "Hanya di akhir", "B", "Pakai underscore sebagai pengganti spasi."),
            Q("Hasil:\nnama = \"Rafi\"\nprint(nama)\nOutput...", "nama", "Rafi", "Error", "\"nama\"", "B", "Ditampilkan isi variabel."),
            Q("Satu variabel biasanya menyimpan...", "Banyak tipe sekaligus tanpa aturan", "Satu nilai pada satu waktu", "Hanya file", "Hanya class", "B", "Nilai lama diganti jika diisi ulang."),
        ]
    elif "tipe data" in j:
        bank = [
            Q("Tipe data bilangan bulat adalah...", "float", "int", "str", "bool", "B", "int = integer."),
            Q("3.14 termasuk tipe...", "int", "float", "str", "bool", "B", "Ada titik desimal = float."),
            Q("\"Python\" bertipe...", "int", "float", "str", "bool", "C", "Teks = string."),
            Q("True dan False bertipe...", "str", "int", "bool", "list", "C", "Boolean."),
            Q("Fungsi untuk cek tipe data...", "print()", "type()", "input()", "len()", "B", "type(x) menampilkan tipe x."),
            Q("Hasil type(10) dekat dengan...", "str", "int", "bool", "dict", "B", "10 bilangan bulat."),
            Q("Manakah float?", "7", "\"7.0\"", "7.0", "True", "C", "7.0 angka desimal (bukan string)."),
            Q("Apakah \"77\" sama tipenya dengan 77?", "Ya", "Tidak, \"77\" str dan 77 int", "Keduanya bool", "Keduanya float", "B", "Kutip membuat string."),
            Q("Nilai kebenaran lulus = True memakai tipe...", "int", "bool", "list", "tuple", "B", "True/False = bool."),
            Q("Konversi teks angka ke int memakai...", "str()", "int()", "bool()", "list()", "B", "int(\"12\") -> 12."),
        ]
    elif "operator aritmatika" in j or "aritmatika" in j:
        bank = [
            Q("Hasil 10 + 3 adalah...", "13", "7", "30", "103", "A", "Penjumlahan."),
            Q("Hasil 10 - 3 adalah...", "13", "7", "30", "0", "B", "Pengurangan."),
            Q("Hasil 4 * 5 adalah...", "9", "20", "45", "1", "B", "Perkalian."),
            Q("Hasil 7 / 2 adalah...", "3", "3.5", "1", "14", "B", "Bagi biasa menghasilkan float."),
            Q("Hasil 7 // 2 adalah...", "3.5", "3", "1", "0", "B", "// = bagi bulat."),
            Q("Hasil 17 % 5 adalah...", "3", "2", "5", "0", "B", "% = sisa bagi (15+2)."),
            Q("Hasil 2 ** 3 adalah...", "6", "8", "9", "5", "B", "** = pangkat, 2^3=8."),
            Q("Operator modulus adalah...", "+", "%", "//", "**", "B", "Modulus pakai %."),
            Q("Hasil (3 + 2) * 4 adalah...", "11", "20", "14", "9", "B", "Kurung dikerjakan dulu: 5*4=20."),
            Q("Untuk sisa bagi 20 dibagi 6 hasilnya...", "3", "2", "4", "0", "B", "18+2, sisa 2."),
        ]
    elif "input" in j or "konversi" in j:
        bank = [
            Q("Fungsi membaca input keyboard adalah...", "print()", "input()", "type()", "int()", "B", "input() menunggu ketikan user."),
            Q("Hasil input() secara default bertipe...", "int", "str", "float", "bool", "B", "Input selalu string dulu."),
            Q("Mengubah input jadi bilangan bulat...", "float(x)", "int(x)", "str(x)", "bool(x)", "B", "Pakai int()."),
            Q("Jika user mengetik 12 pada umur = int(input()), umur berisi...", "\"12\"", "12", "Error selalu", "True", "B", "Sudah dikonversi ke int."),
            Q("int(\"3.5\") akan...", "Jadi 3", "Error ValueError", "Jadi 3.5", "Jadi \"3\"", "B", "int tidak menerima \"3.5\" langsung."),
            Q("float(\"3.5\") hasilnya...", "3", "3.5", "Error", "\"3.5\"", "B", "float menerima desimal."),
            Q("str(10) hasilnya...", "10 (int)", "\"10\" (str)", "True", "Error", "B", "Dikonversi ke teks."),
            Q("Pesan di dalam input(\"Umur: \") berfungsi...", "Menghapus variabel", "Sebagai petunjuk ke pengguna", "Mengubah tipe otomatis", "Menutup program", "B", "Prompt membantu user."),
            Q("Alur benar membaca angka dari keyboard...", "angka = input lalu langsung * 2 tanpa konversi jika ingin hitung angka", "angka = int(input(...)) lalu dihitung", "angka = print(input())", "angka = type(input())", "B", "Konversi dulu sebelum dihitung."),
            Q("Jika salah ketik huruf saat int(input()), muncul...", "True", "ValueError", "print kosong", "File not found", "B", "Konversi gagal = ValueError."),
        ]
    elif "komentar" in j or "indentasi" in j or "error" in j:
        bank = [
            Q("Komentar satu baris dimulai dengan...", "//", "#", "/*", "--", "B", "Python memakai #."),
            Q("Komentar berguna untuk...", "Menghapus print", "Memberi catatan agar kode mudah dipahami", "Menjalankan program lebih lambat wajib", "Mengubah int jadi str", "B", "Dokumentasi singkat."),
            Q("Indentasi di Python...", "Opsional selalu", "Penting untuk menentukan blok kode", "Hanya hiasan", "Dilarang", "B", "Salah indentasi bisa error."),
            Q("Error karena salah ketik nama variabel termasuk...", "SyntaxError selalu", "NameError", "IndentationError", "ZeroDivisionError", "B", "Nama tidak dikenal = NameError."),
            Q("print(\"halo\" tanpa tutup kutip menyebabkan...", "NameError", "SyntaxError", "Benar jalan", "True", "B", "Sintaks tidak valid."),
            Q("Blok if harus...", "Tanpa titik dua", "Diakhiri : dan isinya menjorok", "Pakai kurung kurawal wajib {}", "Tanpa baris isi", "B", "Pakai : dan indentasi."),
            Q("Manakah komentar benar?", "comment ini", "# ini komentar", "<!-- komentar -->", "rem komentar", "B", "Diawali #."),
            Q("IndentationError muncul jika...", "Salah spasi/tab pada blok", "Salah nama modul saja", "File terlalu besar", "Nilai True", "A", "Indentasi tidak konsisten."),
            Q("Cara baik menghindari error ketik...", "Tidak menguji kode", "Baca pesan error dan periksa baris terkait", "Hapus semua kode", "Matikan komputer", "B", "Traceback menunjuk masalah."),
            Q("Apakah komentar dijalankan sebagai perintah?", "Ya", "Tidak", "Kadang", "Hanya di print", "B", "Komentar diabaikan interpreter."),
        ]
    elif "percabangan" in j and "bersarang" not in j and "nested" not in j:
        bank = [
            Q("Kata kunci percabangan utama adalah...", "loop", "if", "def", "class", "B", "if untuk kondisi."),
            Q("if nilai >= 77: dipakai untuk...", "Perulangan", "Keputusan berdasarkan kondisi", "Import modul", "Buat list", "B", "Mengecek syarat."),
            Q("Bagian yang dijalankan jika if salah adalah...", "try", "else", "for", "import", "B", "else = kondisi tidak terpenuhi."),
            Q("elif artinya...", "else if = kondisi tambahan", "end loop", "error if", "edit list", "A", "Beberapa cabang bersyarat."),
            Q("Operator perbandingan sama dengan adalah...", "=", "==", "!=", ":=", "B", "== membandingkan, = mengisi."),
            Q("Hasil:\nn=80\nif n>=77:\n    print(\"Tuntas\")\nelse:\n    print(\"Belum\")\nOutput...", "Belum", "Tuntas", "Error", "80", "B", "80 >= 77 benar."),
            Q("Operator tidak sama dengan...", "==", "!=", "<>", "!==", "B", "Pakai !=."),
            Q("Kondisi if harus menghasilkan...", "String saja", "Nilai kebenaran True/False", "File", "Class", "B", "Boolean condition."),
            Q("if True: print(\"A\") akan...", "Tidak jalan", "Mencetak A", "Error", "Mencetak True", "B", "Kondisi selalu benar."),
            Q("KKM 77, nilai 76 masuk cabang...", "if nilai >= 77", "else (belum tuntas)", "elif nilai > 100", "for", "B", "76 tidak memenuhi >= 77."),
        ]
    elif "perulangan for" in j or ("perulangan" in j and "bersarang" not in j and "pola" not in j):
        bank = [
            Q("Perulangan memakai kata kunci...", "if", "for / while", "def", "class", "B", "for dan while untuk loop."),
            Q("range(3) menghasilkan urutan...", "1,2,3", "0,1,2", "0,1,2,3", "3,2,1", "B", "range(n) = 0..n-1."),
            Q("Berapa kali for i in range(5): berjalan?", "4", "5", "6", "0", "B", "i=0..4 (5 kali)."),
            Q("while dipakai saat...", "Jumlah ulang sudah pasti selalu", "Ulang selama kondisi True", "Hanya sekali", "Tidak butuh kondisi", "B", "while berbasis kondisi."),
            Q("Agar while tidak infinite, biasanya...", "Tidak mengubah variabel kondisi", "Mengubah variabel di dalam loop", "Menghapus print", "Pakai class", "B", "Kondisi harus suatu saat False."),
            Q("Hasil:\nfor i in range(2):\n    print(i)\nOutput...", "1 2", "0\n1", "0 1 2", "2", "B", "Cetak 0 lalu 1."),
            Q("break pada loop berarti...", "Mengulang terus", "Keluar dari loop", "Lanjut iterasi berikutnya saja", "Error", "B", "break menghentikan loop."),
            Q("continue berarti...", "Keluar program", "Lewati sisa blok, lanjut iterasi berikutnya", "Hapus list", "Buat fungsi", "B", "Ski ke putaran berikutnya."),
            Q("for x in [\"A\",\"B\"]: print(x) menampilkan...", "ABdi satu baris wajib", "A lalu B (tiap baris jika print default)", "Error", "X X", "B", "Mengiterasi elemen list."),
            Q("range(1,4) berisi...", "1,2,3,4", "1,2,3", "0,1,2,3", "4", "B", "Awal inklusif, akhir eksklusif."),
        ]
    elif j.startswith("list dan") or "indexing" in j:
        bank = [
            Q("List ditulis dengan...", "{}", "[]", "()", "<>", "B", "Kurung siku."),
            Q("Index pertama list adalah...", "1", "0", "-1 hanya", "2", "B", "Index mulai 0."),
            Q("buah=['A','B','C']; buah[1] hasilnya...", "A", "B", "C", "Error", "B", "Index 1 = elemen kedua."),
            Q("buah[-1] pada list 3 elemen mengambil...", "Pertama", "Terakhir", "Tengah", "Error selalu", "B", "Index negatif dari belakang."),
            Q("Mengubah elemen list...", "Tidak boleh", "Boleh, list mutable", "Hanya tuple yang boleh", "Hanya string yang boleh", "B", "List bisa diubah."),
            Q("len([1,2,3,4]) hasilnya...", "3", "4", "5", "10", "B", "len = jumlah elemen."),
            Q("Menambah item di akhir list memakai...", "add()", "append()", "push()", "insert_end()", "B", "append(x)."),
            Q("List boleh berisi...", "Hanya angka", "Campuran tipe data", "Hanya string", "Hanya bool", "B", "Python list fleksibel."),
            Q("a=[2,4,6]; a[0]=8; print(a) =>", "[2,4,6]", "[8,4,6]", "[8,8,8]", "Error", "B", "Elemen index 0 diganti."),
            Q("Mengakses index di luar jangkauan menyebabkan...", "None", "IndexError", "True", "0", "B", "IndexError."),
        ]
    # ----- Kelas 7 Genap -----
    elif "bersarang" in j and "percabangan" in j or "nested if" in j:
        bank = [
            Q("Nested if artinya...", "if di dalam if", "for di dalam class", "print di dalam input", "def tanpa nama", "A", "Percabangan bersarang."),
            Q("Nested if berguna untuk...", "Menghapus variabel", "Memeriksa syarat bertingkat", "Membuat GUI", "Import otomatis", "B", "Keputusan lebih detail."),
            Q("Setelah if luar True, program...", "Langsung selesai", "Bisa mengecek if dalam", "Wajib error", "Wajib else", "B", "Masuk blok dalam."),
            Q("Contoh syarat bertingkat nilai valid 0-100 lalu KKM...", "Tidak mungkin di Python", "Cocok memakai nested if", "Hanya while", "Hanya list", "B", "Cek rentang dulu, lalu KKM."),
            Q("Kesalahan umum nested if...", "Terlalu banyak indentasi berantakan", "Pakai print", "Pakai int", "Pakai str", "A", "Jaga indentasi rapi."),
            Q("else pada if luar dijalankan jika...", "if luar True", "if luar False", "Selalu", "Tidak pernah", "B", "else menempel kondisi terkait."),
            Q("Apakah nested if wajib elif?", "Wajib", "Tidak wajib", "Wajib while", "Wajib class", "B", "elif opsional."),
            Q("Nested if masih memakai operator...", "Hanya +", "Perbandingan seperti >=, and, or", "Hanya **", "Hanya %", "B", "Kondisi boolean biasa."),
            Q("Manfaat membaca nested if dari luar ke dalam...", "Membingungkan selalu", "Memahami alur keputusan bertahap", "Menghapus else", "Mengubah tipe", "B", "Alur logika berjenjang."),
            Q("if a:\n    if b:\n        print(\"OK\")\nAgar OK tercetak, a dan b harus...", "False, False", "True, True", "True, False", "False, True", "B", "Keduanya perlu True."),
        ]
    elif "pola" in j or ("perulangan bersarang" in j):
        bank = [
            Q("Nested loop artinya...", "Loop di dalam loop", "if di dalam def saja", "Class di dalam file", "Import di dalam print", "A", "Perulangan bersarang."),
            Q("Pola segitiga bintang biasanya memakai...", "Satu loop saja wajib", "Loop luar dan loop dalam", "Hanya dictionary", "Hanya JSON", "B", "Baris x kolom."),
            Q("Loop luar biasanya mengatur...", "Jumlah baris", "Warna GUI", "Nama file", "Tipe data", "A", "Setiap iterasi = 1 baris."),
            Q("Loop dalam biasanya mengatur...", "Jumlah kolom/bintang per baris", "Import", "Class", "Exception", "A", "Cetak horizontal."),
            Q("print(\"*\", end=\"\") berguna untuk...", "Pindah baris selalu", "Cetak tanpa pindah baris", "Hapus string", "Buat list", "B", "end=\"\" menahan newline."),
            Q("Setelah cetak bintang sebari, biasanya...", "print() kosong untuk ganti baris", "wajib break", "wajib class", "wajib input", "A", "Newline baris berikutnya."),
            Q("for i in range(1,4): for j in range(i): ... pola i=1..3 membuat...", "3 baris bintang bertambah", "1 bintang saja", "Error", "Dict", "A", "Baris 1,2,3 bintang."),
            Q("Nested loop cocok untuk...", "Tabel / pola / matriks sederhana", "Hanya 1 variabel", "Hanya boolean", "Hanya True", "A", "Struktur 2 dimensi sederhana."),
            Q("Kesalahan umum nested loop...", "Lupa ganti baris", "Pakai range", "Pakai print", "Pakai int", "A", "Output bisa menempel."),
            Q("Kompleksitas nested loop  n x n cenderung...", "Lebih banyak pengulangan", "Tidak pernah jalan", "Hanya 1 kali", "Error wajib", "A", "Loop dalam diulang tiap luar."),
        ]
    elif "method list" in j:
        bank = [
            Q("list.append(x) berfungsi...", "Menghapus x", "Menambah x di akhir", "Mengurutkan wajib", "Menyalin file", "B", "Tambah di ujung."),
            Q("list.pop() tanpa argumen menghapus...", "Elemen pertama", "Elemen terakhir", "Semua", "Tidak menghapus", "B", "Default pop akhir."),
            Q("list.sort() akan...", "Membalik string", "Mengurutkan list (biasanya naik)", "Membuat dict", "Error selalu", "B", "Mengurutkan elemen."),
            Q("list.remove(x) menghapus...", "Semua x", "Kemunculan pertama x", "Index x", "File x", "B", "Hapus nilai pertama yang cocok."),
            Q("Perbedaan sort() dan sorted()...", "Sama persis selalu", "sort mengubah list asli; sorted mengembalikan list baru", "sorted mengubah asli saja", "Keduanya membuat dict", "B", "sorted tidak mengubah sumber."),
            Q("a=[3,1,2]; a.sort(); print(a) =>", "[3,1,2]", "[1,2,3]", "[2,1,3]", "Error", "B", "Terurut naik."),
            Q("Menyisipkan di posisi tertentu memakai...", "append", "insert", "pop", "remove", "B", "insert(index, nilai)."),
            Q("a=[1,2]; a.append([3,4]); hasil a...", "[1,2,3,4]", "[1,2,[3,4]]", "[1,2,3],[4]", "Error", "B", "append menambah 1 elemen (bisa list)."),
            Q("Untuk menggabung list, lebih tepat...", "a.append(b) jika ingin pecah elemen b", "a.extend(b) / a += b", "a.remove(b)", "a.pop(b)", "B", "extend menambahkan elemen satu-satu."),
            Q("Method list yang mengembalikan panjang bukan method khusus, melainkan fungsi...", "size()", "len()", "count_all()", "lengthof()", "B", "Pakai len(list)."),
        ]
    elif "string lanjutan" in j or "manipulasi string" in j:
        bank = [
            Q("\"Python\".lower() hasilnya...", "PYTHON", "python", "Python", "Error", "B", "Huruf kecil semua."),
            Q("\"Python\".upper() hasilnya...", "python", "PYTHON", "PyThOn", "Error", "B", "Huruf besar semua."),
            Q("Slicing \"Koding\"[0:3] hasilnya...", "Kod", "ing", "Koding", "Kon", "A", "Index 0,1,2."),
            Q("\"a-b-c\".split(\"-\") hasilnya...", "[\"a\",\"b\",\"c\"]", "a-b-c", "abc", "Error", "A", "Pisah berdasarkan pemisah."),
            Q("\"-\".join([\"7\",\"5\"]) hasilnya...", "75", "7-5", "7 5", "Error", "B", "Gabung dengan pemisah."),
            Q("replace(\"Python\",\"Java\") pada \"Belajar Python\"...", "Belajar Java", "Belajar Python", "Java", "Error", "A", "Mengganti substring."),
            Q("String bersifat...", "Mutable seperti list", "Immutable", "Hanya angka", "Hanya bool", "B", "Tidak bisa ubah karakter via index assignment."),
            Q("len(\"SMP\") hasilnya...", "2", "3", "4", "0", "B", "3 huruf."),
            Q("\"aban\".find(\"a\") hasilnya...", "0", "1", "-1", "2", "A", "Posisi kemunculan pertama."),
            Q("Apakah \"A\" == \"a\"?", "Ya", "Tidak", "Kadang", "Error", "B", "Case-sensitive."),
        ]
    elif j.strip().startswith("tuple") or j == "tuple":
        bank = [
            Q("Tuple memakai tanda...", "[]", "()", "{}", "<>", "B", "Kurung biasa."),
            Q("Sifat utama tuple...", "Bisa diubah elemennya bebas", "Immutable (tidak bisa diubah)", "Hanya 1 elemen", "Wajib string", "B", "Tidak bisa assignment ke index."),
            Q("t=(10,20); t[0] hasilnya...", "20", "10", "(10,20)", "Error", "B", "Index 0."),
            Q("t[0]=5 pada tuple akan...", "Berhasil", "Error TypeError", "Menghapus tuple", "Jadi list", "B", "Immutable."),
            Q("Unpacking nama, umur = (\"A\", 13) membuat...", "nama=\"A\", umur=13", "Error", "nama=(A,13)", "umur=\"A\"", "A", "Membongkar nilai."),
            Q("len((1,2,3)) hasilnya...", "2", "3", "4", "1", "B", "3 elemen."),
            Q("Tuple satu elemen yang benar...", "(5)", "(5,)", "[5]", "{5}", "B", "Perlu koma."),
            Q("Kapan tuple lebih tepat dibanding list?", "Data yang tidak boleh berubah", "Data sering diubah", "Hanya GUI", "Hanya file", "A", "Nilai tetap."),
            Q("Apakah tuple bisa berisi campur tipe?", "Tidak", "Ya", "Hanya int", "Hanya str", "B", "Boleh campur."),
            Q("t=(1,2,3); t[-1] hasilnya...", "1", "2", "3", "Error", "C", "Elemen terakhir."),
        ]
    elif "dictionary" in j:
        bank = [
            Q("Dictionary menyimpan data sebagai...", "key: value", "hanya list", "hanya angka", "hanya file", "A", "Pasangan kunci-nilai."),
            Q("Ditulis dengan tanda...", "[]", "{}", "()", "<>", "B", "Kurung kurawal."),
            Q("Akses nilai key \"nama\"...", "d.nama", "d[\"nama\"]", "d(nama)", "d->nama", "B", "Pakai kurung siku + key."),
            Q("Key pada dict harus...", "Boleh list", "Hashable (mis. str/int)", "Selalu float", "Selalu dict lain sebagai key umum pemula", "B", "Biasanya string/int."),
            Q("d={\"a\":1}; d[\"a\"]=9; print(d[\"a\"]) =>", "1", "9", "Error", "a", "B", "Nilai key bisa diubah."),
            Q("Menambah pasangan baru...", "d.add()", "d[\"baru\"]=nilai", "d.append()", "d.push()", "B", "Assignment key baru."),
            Q("d.keys() menghasilkan...", "Hanya values", "Kumpulan key", "File", "Class", "B", "View keys."),
            Q("Jika key tidak ada, d[\"x\"] menyebabkan...", "None diam-diam", "KeyError", "0", "False selalu tanpa error", "B", "KeyError."),
            Q("Cara aman ambil key...", "d.get(\"x\", default)", "d.popfile()", "d.sort()", "d.upper()", "A", "get menghindari error."),
            Q("Dict cocok untuk data...", "Berpasangan seperti biodata siswa", "Hanya urutan bintang pola", "Hanya True/False", "Hanya 1 angka", "A", "Data berlabel."),
        ]
    elif j.startswith("fungsi") and "lanjutan" not in j:
        bank = [
            Q("Kata kunci membuat fungsi...", "func", "def", "function", "define", "B", "def nama():"),
            Q("return digunakan untuk...", "Cetak wajib", "Mengembalikan nilai hasil", "Menghapus fungsi", "Import", "B", "Menghasilkan output fungsi."),
            Q("def luas(s): return s*s; luas(4) =>", "8", "16", "4", "Error", "B", "4*4=16."),
            Q("Parameter adalah...", "Nilai masuk ke fungsi", "Nama file", "Jenis error", "Modul GUI", "A", "Input fungsi."),
            Q("Fungsi tanpa return mengembalikan...", "0", "None", "False", "\"\"", "B", "Default None."),
            Q("Manfaat fungsi...", "Kode bisa dipakai ulang", "Memperlambat wajib", "Menghapus variabel otomatis", "Menutup Python", "A", "Modular & rapi."),
            Q("Memanggil fungsi ditulis...", "def f()", "f()", "call f", "run f", "B", "Nama diikuti kurung."),
            Q("Jumlah argumen harus...", "Boleh beda tanpa aturan", "Sesuai parameter (kecuali default/variadic)", "Selalu 0", "Selalu 10", "B", "Cocokkan tanda tangan fungsi."),
            Q("Docstring fungsi diletakkan...", "Di akhir file saja", "String diawal tubuh fungsi", "Sebelum import wajib", "Di JSON", "B", "Dokumentasi singkat."),
            Q("Fungsi boleh memanggil fungsi lain?", "Tidak", "Ya", "Hanya class", "Hanya while", "B", "Komposisi fungsi biasa."),
        ]
    elif "parameter" in j or "default value" in j:
        bank = [
            Q("Parameter default artinya...", "Wajib diisi user", "Punya nilai bawaan jika argumen kosong", "Tidak bisa dipakai", "Selalu None wajib", "B", "Contoh def f(x=1)"),
            Q("def sapa(nama=\"Siswa\"): ... sapa() memakai nama...", "Kosong error", "Siswa", "None cetak", "Sapa", "B", "Default dipakai."),
            Q("return a, b mengembalikan...", "Dua nilai (tuple)", "Hanya a", "Error", "List wajib", "A", "Multiple return = tuple."),
            Q("Argumen posisi artinya...", "Urutan sesuai parameter", "Boleh acak tanpa nama", "Hanya keyword", "Hanya default", "A", "Urutan penting."),
            Q("Pemanggilan f(a=1,b=2) memakai...", "Keyword arguments", "Hanya list", "Hanya set", "Hanya file", "A", "Nama parameter disebut."),
            Q("Jika ada default, parameter tanpa default harus...", "Di belakang default", "Di depan parameter default", "Dihapus", "Jadi global", "B", "Aturan sintaks Python."),
            Q("x, y = hitung(3,4) disebut...", "Nesting", "Unpacking hasil return", "Sorting", "Encoding", "B", "Membongkar tuple return."),
            Q("Fungsi boleh tidak punya parameter?", "Tidak", "Ya, def f():", "Hanya di kelas 8", "Hanya error", "B", "Kurung boleh kosong."),
            Q("Nilai default dievaluasi...", "Setiap kali dengan hati-hati (hindari mutable default)", "Tidak pernah", "Hanya di C++", "Hanya di HTML", "A", "Hindari default list/dict mutable."),
            Q("Manfaat default parameter...", "Memudahkan pemanggilan opsional", "Menghapus return", "Mengubah Python jadi Java", "Mematikan print", "A", "Fleksibel."),
        ]
    elif "modul math" in j or ("modul" in j and "random" in j):
        bank = [
            Q("Perintah memakai modul...", "include", "import", "using", "require", "B", "import nama_modul"),
            Q("math.sqrt(16) hasilnya...", "4.0", "8", "16", "2", "A", "Akar 16 = 4."),
            Q("math.pi mendekati...", "3.14", "2.71", "1.41", "0", "A", "Konstanta pi."),
            Q("random.randint(1,3) menghasilkan...", "Selalu 1", "1,2, atau 3 secara acak", "Hanya 0/1", "List", "B", "Inclusive range."),
            Q("random.choice([\"A\",\"B\",\"C\"]) memilih...", "Semua", "Satu elemen acak", "None", "Error", "B", "Pilih 1 anggota."),
            Q("Sebelum pakai math.sqrt perlu...", "import math", "import os wajib", "class Math", "def sqrt sendiri wajib", "A", "Import dulu."),
            Q("Modul membantu...", "Mengelompokkan fungsi siap pakai", "Menghapus Python", "Menutup file otomatis saja", "Membuat HTML", "A", "Kode terorganisir."),
            Q("from math import sqrt memungkinkan...", "sqrt(9) tanpa math.", "Hanya math.sqrt", "Menghapus math", "Error", "A", "Import spesifik."),
            Q("Apakah random menghasilkan pola pasti selalu sama tanpa seed?", "Ya selalu identik tiap PC tanpa terkecuali", "Tidak, bersifat acak (pseudorandom)", "Tidak pernah jalan", "Hanya True", "B", "Pseudorandom."),
            Q("math.floor(3.9) mendekati ide...", "Bulatkan ke bawah", "Akar", "Pangkat", "Sinus", "A", "Floor."),
        ]
    elif "proyek mini" in j and tingkat == "7":
        bank = [
            Q("Problem solving langkah awal yang baik...", "Langsung kode tanpa baca soal", "Pahami masalah dulu", "Hapus semua fungsi", "Abaikan contoh", "B", "Pahami input-output."),
            Q("Memecah masalah besar menjadi bagian kecil disebut...", "Debugging saja", "Dekomposisi", "Compiling", "Encrypting", "B", "Break down."),
            Q("Menguji dengan contoh sederhana berguna untuk...", "Memastikan logika benar", "Menghapus Python", "Membuat virus", "Menutup VS Code", "A", "Uji kasus."),
            Q("Fungsi status_kkm(nilai) sebaiknya mengembalikan...", "HTML", "Status tuntas/belum", "Gambar", "File exe", "B", "Keluaran jelas."),
            Q("Dictionary siswa->nilai cocok untuk...", "Menyimpan banyak data berlabel", "Hanya 1 angka", "Hanya True", "Hanya pola bintang", "A", "Key nama, value nilai."),
            Q("for nama, nilai in data.items(): dipakai untuk...", "Iterasi pasangan dict", "Membuat class", "Import random", "Sortir file", "A", "items()."),
            Q("Jika hasil belum sesuai, langkah berikutnya...", "Menyerah", "Debug & perbaiki", "Hapus OS", "Ganti bahasa wajib", "B", "Perbaiki bertahap."),
            Q("Kode yang rapi membantu...", "Orang lain (dan diri sendiri) memahami", "Memperlambat wajib 10x", "Menghapus komentar wajib", "Menambah error", "A", "Readable code."),
            Q("Menulis fungsi kecil lebih baik daripada...", "Satu fungsi raksasa campur aduk", "Tidak menulis apa pun", "Hanya print", "Hanya input", "A", "Modular."),
            Q("Output program proyek mini sebaiknya...", "Jelas bagi pengguna", "Acak tanpa arti", "Disembunyikan", "Hanya error", "A", "User-friendly."),
        ]
    # ----- Kelas 8 -----
    elif "set" in j and "review" in j or j.endswith("set") or " & set" in j or "dan set" in j:
        bank = [
            Q("Set menyimpan...", "Nilai unik", "Key-value", "Urutan ketat seperti list selalu", "File saja", "A", "Unik, tanpa duplikat."),
            Q("Set ditulis dengan...", "[]", "{} untuk {1,2,3}", "()", "<>", "B", "Kurung kurawal elemen."),
            Q("print({1,2,2,3}) menampilkan konsep...", "Tetap ada 2 dua kali", "Duplikat hilang", "Jadi list", "Error", "B", "Duplikat dibuang."),
            Q("Operasi gabungan set...", "| atau union", "& saja", "%", "//", "A", "Union."),
            Q("Operasi irisan set...", "& / intersection", "|", "+", "-", "A", "Intersection."),
            Q("Apakah set mendukung indexing set[0] secara umum?", "Ya seperti list", "Tidak", "Hanya string", "Hanya bool", "B", "Tidak berindeks seperti list."),
            Q("Menambah elemen set memakai...", "append", "add", "push", "insert wajib index", "B", "add(x)."),
            Q("{1,2} | {2,3} hasilnya...", "{2}", "{1,2,3}", "{1,3}", "[1,2,3]", "B", "Gabungan unik."),
            Q("{1,2} & {2,3} hasilnya...", "{1,2,3}", "{2}", "{}", "{1,3}", "B", "Irisan = 2."),
            Q("Set cocok jika kita peduli pada...", "Keanggotaan unik", "Urutan ketat index 0..n", "HTML", "GUI saja", "A", "Membership unik."),
        ]
    elif "comprehension" in j:
        bank = [
            Q("List comprehension membuat list secara...", "Panjang bertele-tele wajib", "Ringkas dalam satu ekspresi", "Hanya dengan class", "Hanya JSON", "B", "Sintaks ringkas."),
            Q("[x*x for x in range(1,4)] hasil...", "[1,4,9]", "[1,2,3]", "[0,1,4]", "Error", "A", "1^2,2^2,3^2."),
            Q("Sintaks dasar comprehension...", "[ekspresi for item in iterable]", "for item in [ekspresi]", "{for x}", "(def x)", "A", "Standar Python."),
            Q("[n for n in range(5) if n%2==0] =>", "[1,3]", "[0,2,4]", "[2,4]", "[0,1,2,3,4]", "B", "Filter genap."),
            Q("Bagian if pada comprehension berfungsi sebagai...", "Class", "Filter", "Import", "File", "B", "Menyaring elemen."),
            Q("Comprehension lebih sering dibanding map+lambda untuk pemula karena...", "Lebih mudah dibaca", "Lebih lambat selalu 100x wajib", "Tidak legal", "Hanya di Java", "A", "Readable."),
            Q("Hasil [str(i) for i in [1,2]]...", "[1,2]", "[\"1\",\"2\"]", "12", "Error", "B", "Konversi ke string."),
            Q("Apakah comprehension bisa memakai if-else ekspresi?", "Ya, ekspresi bersyarat", "Tidak pernah", "Hanya while", "Hanya def", "A", "Mis. [a if cond else b for ...]."),
            Q("List comprehension menghasilkan...", "Set selalu", "List baru", "Dict wajib", "Tuple wajib", "B", "Tipe list."),
            Q("Manfaat utama comprehension...", "Kode lebih pendek dan jelas untuk transformasi list", "Menghapus Python", "Membuat virus", "Menutup file OS", "A", "Transformasi data."),
        ]
    elif "fungsi lanjutan" in j:
        bank = [
            Q("*args berarti...", "Satu dict keyword", "Kumpulan argumen posisi berlebih", "Hanya string", "Hanya file", "B", "Variadic positional."),
            Q("**kwargs berarti...", "Argumen keyword berlebih sebagai dict", "List angka", "Set unik", "Module", "A", "Keyword variadic."),
            Q("lambda dipakai untuk...", "Fungsi singkat anonim", "Class besar", "Database", "HTML", "A", "Anonymous function."),
            Q("(lambda x: x+1)(4) hasil...", "4", "5", "1", "Error", "B", "4+1."),
            Q("def f(*a): return sum(a); f(1,2,3) =>", "6", "123", "Error", "0", "A", "1+2+3."),
            Q("Fungsi sebagai first-class citizen artinya...", "Bisa dikirim sebagai argumen/nilai", "Tidak bisa dipanggil", "Hanya di C", "Wajib class", "A", "Fungsi = objek."),
            Q("map(lambda x:x*2,[1,2]) perlu dibungkus list(...) agar...", "Terlihat hasil list", "Jadi dict", "Jadi file", "Error hilang otomatis tanpa sebab", "A", "map return iterator."),
            Q("Kapan lambda kurang cocok?", "Logika sangat panjang/kompleks", "Satu operasi singkat", "Sorting key sederhana", "Filter sederhana", "A", "Pakai def biasa."),
            Q("Urutan parameter yang benar melibatkan *args...", "default, *args, biasa tanpa default di belakang sembarangan", "mengikuti aturan sintaks Python (posisi, *args, default/kw)", "bebas total", "hanya kwargs dulu", "B", "Ikuti aturan tanda tangan."),
            Q("Manfaat *args...", "Fungsi fleksibel menerima banyak input", "Menghapus return", "Membuat GUI", "Encrypt harddisk", "A", "Fleksibilitas."),
        ]
    elif "exception" in j:
        bank = [
            Q("Blok yang dicoba lebih dulu...", "except", "try", "finally saja", "raise saja", "B", "try."),
            Q("Menangkap error memakai...", "catch", "except", "handle", "trap", "B", "except."),
            Q("ZeroDivisionError muncul saat...", "Bagi nol", "Salah nama", "Salah indentasi", "File hilang", "A", "n/0."),
            Q("ValueError sering saat...", "int(\"abc\")", "1+1", "print(\"a\")", "import math sukses", "A", "Konversi gagal."),
            Q("finally akan...", "Hanya jika error", "Selalu dijalankan", "Tidak pernah", "Hanya di Java", "B", "Cleanup."),
            Q("try/except membuat program...", "Langsung crash selalu", "Lebih tahan kesalahan input", "Lebih lambat 1000x wajib", "Tidak bisa print", "B", "Error handling."),
            Q("except Exception menangkap...", "Banyak jenis error umum", "Hanya SyntaxError compile", "Hanya berhasil", "Tidak ada", "A", "Basis exception."),
            Q("raise dipakai untuk...", "Membangkitkan exception", "Menghapus fungsi", "Import", "Sort", "A", "Lempar error."),
            Q("Pesan error sebaiknya...", "Jelas bagi pengguna/pengembang", "Disembunyikan total", "Random", "Dalam bahasa mesin saja", "A", "Informatif."),
            Q("Hasil:\ntry:\n print(int(\"12\"))\nexcept:\n print(\"e\")\n=>", "e", "12", "Error", "None", "B", "Konversi sukses."),
        ]
    elif "file handling" in j or ("file" in j and "json" not in j and "modul sendiri" not in j):
        bank = [
            Q("Membuka file memakai fungsi...", "readfile", "open", "loadfile", "fileopen", "B", "open(path, mode)."),
            Q("Mode \"r\" berarti...", "Tulis", "Baca", "Append", "Hapus", "B", "Read."),
            Q("Mode \"w\" berarti...", "Baca saja", "Tulis (menimpa)", "Append saja", "Binary wajib", "B", "Write truncate."),
            Q("Mode \"a\" berarti...", "Hapus awal", "Append di akhir", "Read binary", "Error", "B", "Tambah di ujung."),
            Q("Pola aman membuka file...", "with open(...) as f:", "lupa close selalu terbaik", "tanpa mode", "open tanpa variabel", "A", "Context manager."),
            Q("f.read() mengembalikan...", "string isi file (teks)", "int", "dict wajib", "True", "A", "Konten teks."),
            Q("f.write(\"halo\") membutuhkan mode...", "r", "w atau a (bisa tulis)", "hanya r+", "hanya x wajib", "B", "Mode tulis."),
            Q("encoding=\"utf-8\" berguna untuk...", "Teks internasional/karakter non-ASCII", "Mempercepat CPU 100x wajib", "Menghapus file", "Membuat GUI", "A", "Teks aman."),
            Q("Jika file tidak ada saat mode r...", "Dibuat otomatis", "FileNotFoundError", "True", "None diam", "B", "Error."),
            Q("Menutup file penting agar...", "Data tersimpan/sumber daya dibebaskan", "Python berhenti total", "List terurut", "Random jalan", "A", "Resource management."),
        ]
    elif "modul sendiri" in j:
        bank = [
            Q("Modul sendiri biasanya file...", ".py", ".docx", ".png", ".exe wajib", "A", "Skrip Python."),
            Q("import hitung memakai file...", "hitung.py", "hitung.txt", "hitung.csv", "hitung.java", "A", "Nama modul = nama file."),
            Q("Manfaat modul...", "Kode terbagi rapi & reusable", "Wajib 1 file raksasa", "Menghapus fungsi", "Menutup OS", "A", "Modularitas."),
            Q("from hitung import luas memuat...", "Semua isi modul wajib", "Fungsi luas saja", "Hanya komentar", "Hanya class Random", "B", "Import selektif."),
            Q("if __name__ == \"__main__\": berguna untuk...", "Kode uji hanya saat file dijalankan langsung", "Import math", "Buat GUI otomatis", "Hapus modul", "A", "Pola standar."),
            Q("Nama modul sebaiknya...", "Jelas dan valid identifier", "Diawali angka", "Pakai spasi", "Pakai tanda minus saja", "A", "Contoh hitung.py."),
            Q("Modul membantu kerja tim karena...", "File bisa dikerjakan terpisah", "Tidak bisa dishare", "Wajib satu orang", "Tidak bisa diuji", "A", "Kolaborasi."),
            Q("Setelah diubah, modul sering perlu...", "Restart interpreter / reload", "Ganti OS", "Hapus Python", "Format HDD", "A", "Agar perubahan termuat."),
            Q("Package adalah...", "Kumpulan modul (folder)", "Satu variabel", "Satu print", "Satu True", "A", "Struktur lebih besar."),
            Q("Import gagal jika...", "File/modul tidak ditemukan di path", "print sukses", "len jalan", "int sukses", "A", "ModuleNotFoundError."),
        ]
    elif "class dan object" in j or (tingkat == "8" and "oop: class" in j):
        bank = [
            Q("Class adalah...", "Blueprint/cetakan object", "Hasil jadi saja", "Database", "Browser", "A", "Template."),
            Q("Object adalah...", "Instance dari class", "Nama file", "Keyword if", "Modul random", "A", "Hasil class()."),
            Q("Method adalah...", "Fungsi di dalam class", "Variabel global saja", "File JSON", "Error", "A", "Perilaku object."),
            Q("Parameter self mewakili...", "Object saat ini", "Modul", "List", "Exception", "A", "Instance."),
            Q("s = Siswa() membuat...", "Class baru", "Object baru", "Dict", "Set", "B", "Instansiasi."),
            Q("Nama class konvensi...", "nama_siswa", "NamaSiswa", "NAMA_siswa", "nama-siswa", "B", "CapWords."),
            Q("OOP menekankan...", "Data + perilaku dalam object", "Hanya variabel lepas", "Hanya HTML", "Hanya CSV", "A", "Enkapsulasi konsep dasar."),
            Q("Banyak object dari class sama boleh punya data beda?", "Ya", "Tidak", "Hanya 1 object", "Error", "A", "State independen."),
            Q("class Kosong: pass berguna untuk...", "Kerangka class sementara", "Menghapus Python", "Buat file", "Import os wajib", "A", "Placeholder."),
            Q("Pemanggilan method s.sapa() artinya...", "Fungsi sapa pada object s", "Buat class", "Hapus s", "Sort s", "A", "Bound method."),
        ]
    elif "atribut dan method" in j:
        bank = [
            Q("Atribut adalah...", "Data pada object", "Nama modul saja", "Jenis loop", "Tipe file", "A", "Properties."),
            Q("Method beda dari fungsi biasa karena...", "Ada self/terikat class", "Tidak bisa dipanggil", "Wajib return None", "Tidak boleh print", "A", "Terkait object."),
            Q("m.merk = \"Avanza\" menambahkan...", "Atribut pada object m", "Class baru", "File baru", "Error wajib", "A", "Atribut dinamis dimungkinkan."),
            Q("Mengakses atribut memakai...", "m.merk", "m->merk", "m::merk", "merk(m)", "A", "Dot notation."),
            Q("Jika atribut belum ada lalu dibaca...", "None diam", "AttributeError", "0", "False", "B", "Error atribut."),
            Q("Method boleh mengubah atribut?", "Ya lewat self", "Tidak pernah", "Hanya di Java", "Hanya di HTML", "A", "Mutasi state."),
            Q("self.nama dan nama lokal berbeda karena...", "self.nama milik object", "Sama persis selalu", "self diabaikan", "nama wajib global", "A", "Namespace object."),
            Q("Menampilkan semua atribut sederhana bisa dengan...", "vars(obj) / __dict__", "hanya print class", "import math", "range", "A", "Introspeksi dasar."),
            Q("Method tanpa memakai atribut tetap...", "Boleh", "Dilarang", "Wajib error", "Wajib return file", "A", "Tergantung kebutuhan."),
            Q("Istilah state object merujuk pada...", "Nilai atribut saat ini", "Nama file .py", "Versi Python", "Warna GUI saja", "A", "Keadaan data."),
        ]
    elif "__init__" in j or "constructor" in j:
        bank = [
            Q("__init__ dipanggil saat...", "Object dibuat", "Object dihapus", "Import gagal", "Program ditutup saja", "A", "Konstruktor."),
            Q("Tujuan __init__...", "Inisialisasi atribut awal", "Menghapus class", "Membuka browser", "Sortir list otomatis", "A", "Setup object."),
            Q("def __init__(self, nama): self.nama=nama menyimpan...", "Parameter ke atribut", "Nama file", "Exception", "Modul", "A", "Assignment atribut."),
            Q("Siswa(\"Budi\") membutuhkan __init__ dengan...", "Parameter nama (selain self)", "Tanpa parameter sama sekali jika ada nama", "Hanya **kwargs wajib", "Hanya *args angka", "A", "Argumen sesuai init."),
            Q("Apakah __init__ wajib return nilai?", "Ya return self", "Tidak (return None implisit)", "Ya return dict", "Ya return 0", "B", "Tidak return object manual."),
            Q("Jika __init__ tidak ditulis...", "Object tetap bisa dibuat (default)", "Class mustahil", "Python crash selalu", "Import gagal", "A", "Ada default."),
            Q("self pada __init__ adalah...", "Object yang sedang dibuat", "Modul random", "List kosong", "True", "A", "Instance baru."),
            Q("Dua argumen data pada __init__(self,a,b) dipanggil...", "Cls(a,b)", "Cls(self,a,b)", "Cls()", "Cls(a)", "A", "self otomatis."),
            Q("Validasi nilai awal paling tepat diletakkan di...", "__init__", "random", "print saja", "HTML", "A", "Saat penciptaan."),
            Q("Nama __init__ memakai...", "Underscore ganda khas Python", "Huruf besar wajib", "Angka di depan", "Spasi", "A", "Magic method."),
        ]
    elif "proyek mini oop" in j or ("proyek" in j and tingkat == "8" and "akhir" not in j):
        bank = [
            Q("Fokus proyek OOP ganjil...", "Class, atribut, method, __init__", "Hanya HTML", "Hanya sorting", "Hanya tkinter", "A", "Dasar OOP."),
            Q("Object pada proyek mewakili...", "Entitas dunia nyata (mis. siswa/produk)", "Hanya angka acak", "File OS", "Warna", "A", "Model domain."),
            Q("Method status() sebaiknya...", "Mengembalikan info bermakna", "Menghapus class", "Memformat HDD", "Menutup Windows", "A", "Perilaku jelas."),
            Q("Kenapa pakai class, bukan banyak variabel lepas?", "Lebih terstruktur", "Lebih lambat wajib", "Tidak bisa diuji", "Tidak bisa print", "A", "Organisasi."),
            Q("Pengujian object dilakukan dengan...", "Membuat instance dan panggil method", "Menghapus __init__", "Matikan PC", "Ganti bahasa", "A", "Uji perilaku."),
            Q("Atribut nilai siswa disimpan di...", "self.nilai", "variabel tanpa self saja selalu", "file hanya", "HTML", "A", "State object."),
            Q("Satu class bisa dipakai untuk...", "Banyak object", "Hanya 1 object di dunia", "0 object saja", "Hanya modul", "A", "Reusable blueprint."),
            Q("Pesan error AttributeError saat proyek biasanya karena...", "Salah nama atribut/method", "print sukses", "int sukses", "len sukses", "A", "Typo/akses salah."),
            Q("Dokumentasi singkat method membantu...", "Teman/tim memahami kode", "Menghapus Python", "Mempercepat internet", "Mengganti OS", "A", "Kolaborasi."),
            Q("Output proyek yang baik...", "Mudah dibaca pengguna", "Acak", "Disembunyikan", "Hanya traceback", "A", "UX sederhana."),
        ]
    elif "inheritance" in j or "pewarisan" in j:
        bank = [
            Q("Inheritance artinya...", "Pewarisan sifat class induk ke anak", "Menghapus class", "Import JSON", "Sort list", "A", "Reuse hierarki."),
            Q("Sintaks benar...", "class Anak(Induk):", "class Anak inherits Induk", "class Anak -> Induk", "class Anak extends Induk", "A", "Python style."),
            Q("Class anak dapat...", "Memakai method induk", "Tidak pernah memakai induk", "Menghapus Python", "Hanya float", "A", "Warisan."),
            Q("Overriding berarti...", "Anak menulis ulang method induk", "Menghapus induk dari disk", "Membuat file baru wajib", "Random", "A", "Redefine."),
            Q("class Kucing(Hewan): artinya...", "Kucing mewarisi Hewan", "Hewan mewarisi Kucing", "Tidak berhubungan", "Keduanya modul", "A", "Child(Parent)."),
            Q("super() dipakai untuk...", "Memanggil method induk", "Menghapus anak", "Buat GUI", "Encrypt", "A", "Akses induk."),
            Q("Manfaat inheritance...", "Mengurangi duplikasi kode", "Memaksa 1 file", "Menambah lag wajib", "Menghapus OOP", "A", "DRY."),
            Q("Apakah anak bisa punya method baru?", "Ya", "Tidak", "Hanya jika final", "Hanya di Java", "A", "Ekstensi perilaku."),
            Q("Rantai pewarisan terlalu dalam biasanya...", "Boleh tapi hati-hati kerumitan", "Wajib 100 level", "Dilarang compiler selalu", "Tidak mungkin", "A", "Keep simple."),
            Q("Method resolving mencari member dari...", "Anak dulu lalu induk", "Induk saja", "Modul random", "File JSON", "A", "MRO sederhana."),
        ]
    elif "encapsulation" in j:
        bank = [
            Q("Encapsulation bertujuan...", "Melindungi detail data", "Menghapus method", "Membuka semua atribut publik wajib", "Menonaktifkan class", "A", "Data hiding."),
            Q("Atribut __saldo menandakan...", "Privat secara konvensi/name mangling", "Public resmi bahasa", "Modul", "GUI", "A", "Internal."),
            Q("Getter dipakai untuk...", "Mengambil nilai terlindungi", "Menghapus class", "Sortir", "Import", "A", "Akses terkontrol."),
            Q("Setter dipakai untuk...", "Mengubah nilai dengan aturan", "Menghapus Python", "Buat file OS", "Random wajib", "A", "Validasi saat ubah."),
            Q("r.setor(-5) sebaiknya...", "Ditolak/validasi", "Selalu diterima", "Menghapus object", "Error sintaks", "A", "Jaga invariant."),
            Q("Enkapsulasi membantu...", "API object lebih aman", "Menghilangkan kebutuhan method", "Mematikan OOP", "Hanya untuk HTML", "A", "Kontrol akses."),
            Q("Property @property di Python terkait...", "Getter bergaya atribut", "Hanya sorting", "Hanya JSON", "Hanya tkinter", "A", "Pythonic encaps."),
            Q("Mengubah atribut privat langsung dari luar...", "Tidak disarankan", "Wajib dilakukan", "Satu-satunya cara", "Menghapus self", "A", "Pakai method."),
            Q("Contoh enkapsulasi rekening meniru...", "Saldo dilindungi method", "Saldo global bebas semua", "Tanpa class", "Hanya print", "A", "Domain banking sederhana."),
            Q("Name mangling __attr menjadi mirip...", "_Class__attr", "attr saja", "__attr__ publik resmi", "ATTR", "A", "Mekanisme Python."),
        ]
    elif "json" in j:
        bank = [
            Q("Modul JSON di Python...", "json", "os", "tkinter", "math", "A", "import json."),
            Q("json.dumps(dict) menghasilkan...", "string JSON", "file gambar", "class", "set", "A", "Serialize ke teks."),
            Q("json.loads(teks) menghasilkan...", "struktur Python (dict/list)", "HTML", "exe", "True saja", "A", "Deserialize."),
            Q("json.dump menulis ke...", "file", "hanya RAM tanpa file", "printer wajib", "GPU", "A", "Ke file object."),
            Q("JSON mirip dengan...", "dict/list Python", "class wajib", "tuple immutable saja", "set unik saja", "A", "Struktur mirip."),
            Q("Key JSON biasanya...", "string", "list", "dict bersarang sebagai key utama pemula", "file", "A", "Standar JSON."),
            Q("Keunggulan JSON...", "Mudah ditukar antar sistem", "Hanya jalan di Windows", "Tidak bisa dibaca manusia", "Wajib biner", "A", "Interoperable."),
            Q("Kesalahan umum JSON...", "Trailing comma / format invalid", "print sukses", "len sukses", "int(2)", "A", "Strict format."),
            Q("Menyimpan nilai siswa ke JSON cocok karena...", "Data terstruktur", "Tidak bisa string", "Tidak bisa angka", "Wajib GUI", "A", "Persistensi sederhana."),
            Q("json.load berbeda dengan loads karena...", "load dari file, loads dari string", "load dari string saja", "sama persis total", "load hanya int", "A", "Sumber beda."),
        ]
    elif "searching" in j:
        bank = [
            Q("Linear search memeriksa data...", "Satu per satu", "Hanya tengah", "Hanya akhir", "Tanpa loop", "A", "Sequential."),
            Q("Binary search mensyaratkan data...", "Terurut", "Acak total", "Kosong", "String saja", "A", "Sorted."),
            Q("Jika tidak ketemu, contoh linear mengembalikan...", "-1", "0 selalu", "True", "len(data)", "A", "Sentinel."),
            Q("Binary search lebih cepat pada data besar terurut karena...", "Membagi ruang pencarian", "Cek semua elemen selalu", "Tanpa banding", "Random", "A", "Log n."),
            Q("Linear search cocok jika...", "Data kecil/tidak terurut", "Selalu data terurut besar", "Hanya GUI", "Hanya JSON", "A", "Sederhana."),
            Q("Kompleksitas linear search terburuk...", "O(n)", "O(1)", "O(log n)", "O(n^2) wajib", "A", "Sampai elemen terakhir."),
            Q("Pada binary search, jika target < tengah...", "Cari di kiri", "Cari di kanan", "Selesai True", "Error", "A", "Paruh kiri."),
            Q("Searching bertujuan...", "Menemukan posisi/keberadaan data", "Mengurutkan wajib", "Membuat class", "Import os", "A", "Find."),
            Q("list.index(x) mirip ide...", "Pencarian nilai", "Sorting", "JSON dump", "GUI", "A", "Built-in search."),
            Q("Jika banyak pencarian pada data terurut, lebih baik...", "Binary search", "Linear selalu", "Nested if saja", "print saja", "A", "Efisien."),
        ]
    elif "sorting" in j:
        bank = [
            Q("Bubble sort menukar...", "Pasangan bersebelahan", "Hanya elemen tengah", "File", "Modul", "A", "Adjacent swap."),
            Q("sorted([3,1,2]) hasil...", "[1,2,3]", "[3,1,2]", "[2,1,3]", "Error", "A", "List baru terurut."),
            Q("a.sort() akan...", "Mengubah list a", "Mengembalikan list baru tanpa ubah a", "Error", "Jadi dict", "A", "In-place."),
            Q("Selection sort berfokus...", "Memilih ekstrem lalu menempatkan", "Hanya recursion", "Hanya JSON", "Hanya GUI", "A", "Select min/max."),
            Q("Data [5,1,4] setelah bubble naik menjadi...", "[1,4,5]", "[5,4,1]", "[4,5,1]", "[5,1,4]", "A", "Ascending."),
            Q("Kapan sorting penting?", "Menyiapkan binary search / laporan terurut", "Hanya cetak Hello", "Hanya True", "Hanya import", "A", "Pra-pemrosesan."),
            Q("Kompleksitas bubble sederhana sering...", "O(n^2)", "O(1)", "O(log n)", "O(n!)", "A", "Nested loop."),
            Q("Parameter reverse=True pada sorted membuat...", "Urutan menurun", "Error", "Set", "Dict", "A", "Descending."),
            Q("key= pada sorted dipakai untuk...", "Aturan pengurutan kustom", "Menghapus list", "Import", "GUI", "A", "Custom key."),
            Q("Apakah sorting mengubah jumlah elemen?", "Umumnya tidak", "Selalu menambah 1", "Selalu menghapus 1", "Jadi 0", "A", "Hanya susunan."),
        ]
    elif "rekursi" in j:
        bank = [
            Q("Rekursi adalah fungsi yang...", "Memanggil dirinya", "Tidak bisa dipanggil", "Hanya loop for", "Hanya class", "A", "Self-call."),
            Q("Base case penting agar...", "Rekursi berhenti", "Rekursi infinite wajib", "Error hilang tanpa sebab", "List terurut", "A", "Kondisi akhir."),
            Q("faktorial(5) =...", "120", "15", "25", "5", "A", "5*4*3*2*1."),
            Q("Tanpa base case, rekursi...", "Bisa stack overflow/RecursionError", "Lebih cepat selalu", "Jadi sorting", "Jadi JSON", "A", "Tak terbatas."),
            Q("Rekursi mirip ide...", "Pemecahan masalah mengecil", "Import os saja", "print saja", "HTML saja", "A", "Divide."),
            Q("def f(n): return f(n) tanpa henti akan...", "Error rekursi", "Hasil 0", "Hasil n", "True", "A", "Tak berbase."),
            Q("Kasus dasar faktorial biasanya...", "n<=1 return 1", "n==100", "n<0 return n*n", "n==True", "A", "0!/1!=1."),
            Q("Rekursi vs loop...", "Keduanya bisa mengulang proses", "Rekursi tidak pernah mengulang", "Loop ilegal di Python", "Rekursi hanya di C", "A", "Alternatif."),
            Q("Kedalaman rekursi terbatas oleh...", "Recursion limit", "Warna layar", "Nama file", "Ukuran mouse", "A", "sys limit."),
            Q("Contoh klasik rekursi...", "Faktorial / Fibonacci sederhana", "Hanya print Hello", "Hanya import math", "Hanya dict get", "A", "Contoh standar."),
        ]
    elif "tkinter" in j or "gui" in j:
        bank = [
            Q("Library GUI bawaan yang dipelajari...", "Tkinter", "Django", "Pandas", "Flask saja", "A", "tkinter."),
            Q("Jendela utama dibuat dengan...", "tk.Tk()", "tk.JSON()", "tk.Sort()", "tk.File()", "A", "Root window."),
            Q("Widget teks label...", "tk.Label", "tk.Button saja", "tk.Entry wajib tombol", "tk.Frame hanya", "A", "Label."),
            Q("Widget tombol...", "tk.Button", "tk.Label saja", "tk.Canvas wajib", "tk.Menu saja", "A", "Button."),
            Q("mainloop() berfungsi...", "Menjalankan event loop GUI", "Menghapus jendela", "Sortir data", "Import os", "A", "Loop acara."),
            Q("pack() pada widget untuk...", "Menata posisi sederhana", "Menghapus Python", "Buat class", "Encrypt", "A", "Geometry manager."),
            Q("command= pada Button mengikat...", "Fungsi saat diklik", "Warna wajib", "File JSON", "Sorting", "A", "Callback."),
            Q("GUI berguna agar program...", "Lebih mudah dipakai visual", "Lebih sulit selalu", "Tanpa output", "Tanpa input", "A", "Usability."),
            Q("root.title(\"Koding\") mengatur...", "Judul jendela", "Nama class", "Ukuran font wajib", "Path file", "A", "Window title."),
            Q("Tanpa mainloop, jendela Tk biasanya...", "Langsung hilang/tidak interaktif", "Lebih cepat 1000x wajib", "Jadi console", "Jadi dict", "A", "Perlu loop."),
        ]
    elif "debugging" in j or "testing" in j:
        bank = [
            Q("assert dipakai untuk...", "Memastikan kondisi saat uji", "Membuat GUI", "Import modul", "Sort otomatis", "A", "Assertion."),
            Q("Jika assert gagal muncul...", "AssertionError", "True", "None", "FileNotFound", "A", "Gagal uji."),
            Q("Langkah debug awal...", "Baca traceback & cek variabel", "Abaikan error", "Hapus semua kode", "Format HDD", "A", "Systematic."),
            Q("print debugging berarti...", "Cetak nilai untuk menelusuri", "Menghapus print selamanya", "Hanya GUI log", "Hanya JSON", "A", "Simple debug."),
            Q("Testing membantu...", "Menemukan bug lebih cepat", "Menghapus kebutuhan fungsi", "Mematikan PC", "Mengganti OS", "A", "Kualitas."),
            Q("Unit test berfokus...", "Fungsi/unit kecil", "Seluruh internet", "Hanya desain logo", "Hanya hardware", "A", "Small units."),
            Q("Bug adalah...", "Kesalahan perilaku program", "Nama variabel wajib", "Jenis sort", "Modul math", "A", "Defect."),
            Q("Reproduksi bug penting agar...", "Bisa diperbaiki dengan yakin", "Bug hilang sendiri tanpa jejak", "Tidak perlu baca error", "Wajib rewrite OS", "A", "Repeatable."),
            Q("assert len(data)>0 mencegah...", "Rata-rata data kosong", "Import gagal", "GUI gagal", "JSON sukses", "A", "Precondition."),
            Q("Setelah memperbaiki bug, sebaiknya...", "Uji ulang", "Langsung hapus tes", "Matikan komputer 1 hari", "Ganti bahasa", "A", "Regresi check."),
        ]
    elif "best practice" in j or "dokumentasi" in j:
        bank = [
            Q("DRY berarti...", "Don't Repeat Yourself", "Do Repeat Yourself", "Data Random Year", "Debug Run Yes", "A", "Hindari duplikasi."),
            Q("Docstring adalah...", "Dokumentasi singkat di tubuh fungsi/class", "Nama file", "Jenis error", "Widget GUI", "A", "__doc__."),
            Q("Nama variabel yang baik...", "Deskriptif", "a1b2c3 tanpa arti", "x saja selalu", "tmpfinalfinal2", "A", "Clarity."),
            Q("Komentar sebaiknya menjelaskan...", "Mengapa / hal non-jelas", "Setiap spasi", "Yang sudah jelas dari kode", "Password", "A", "Bukan noise."),
            Q("Fungsi sebaiknya...", "Fokus satu tugas", "Melakukan 50 tugas", "Tanpa nama", "Tanpa return dan tanpa arti", "A", "SRP sederhana."),
            Q("Kode rapi membantu...", "Perawatan jangka panjang", "Hanya lomba ketik", "Menghapus Git", "Mematikan WiFi", "A", "Maintainability."),
            Q("PEP 8 terkait...", "Gaya penulisan Python", "Database MySQL wajib", "Desain logo", "Hardware", "A", "Style guide."),
            Q("Versi kontrol (Git) bermanfaat untuk...", "Melacak perubahan kode", "Mengganti Python", "Membuat GUI otomatis", "Sortir angka saja", "A", "History."),
            Q("Menghindari hardcode berlebihan dengan...", "Konstanta/parameter", "Menulis angka di mana-mana tanpa nama", "Menghapus fungsi", "Matikan assert", "A", "Configurability."),
            Q("Dokumentasi singkat proyek membantu...", "Orang baru paham cepat", "Menyembunyikan cara pakai", "Menghapus README", "Memaksa tebak-tebakan", "A", "Onboarding."),
        ]
    elif "proyek akhir" in j:
        bank = [
            Q("Proyek akhir menggabungkan...", "Banyak konsep yang sudah dipelajari", "Hanya 1 print", "Hanya 1 variabel", "Tanpa uji", "A", "Integrasi."),
            Q("Perencanaan fitur dilakukan...", "Sebelum coding besar-besaran", "Setelah hapus semua kode", "Tanpa tujuan", "Dengan format OS", "A", "Plan first."),
            Q("Pemilihan struktur data harus sesuai...", "Kebutuhan masalah", "Secara acak", "Hanya set selalu", "Hanya GUI selalu", "A", "Fit for purpose."),
            Q("OOP pada proyek akhir membantu...", "Mengorganisasi entitas", "Menghapus fungsi", "Menghilangkan pengujian", "Mematikan JSON", "A", "Structure."),
            Q("Penyimpanan data bisa memakai...", "File/JSON sederhana", "Hanya pikiran manusia", "Hanya RAM tanpa simpan", "Hanya screenshot", "A", "Persistence."),
            Q("Pengujian skenario penting agar...", "Fitur berjalan sesuai harapan", "Bug wajib dipelihara", "Dokumentasi dihapus", "Class dihapus", "A", "QA."),
            Q("Antarmuka bisa berupa...", "CLI atau GUI sederhana", "Hanya biner mesin", "Hanya register CPU", "Hanya BIOS", "A", "UI options."),
            Q("Refaktor artinya...", "Merapikan kode tanpa ubah perilaku inti", "Menghapus semua fitur", "Ganti bahasa wajib", "Format HDD", "A", "Refactor."),
            Q("Presentasi proyek sebaiknya menampilkan...", "Masalah, solusi, demo", "Hanya password", "Hanya error", "Hanya kode acak", "A", "Komunikasi."),
            Q("Setelah proyek selesai, dokumentasi singkat...", "Tetap berguna", "Tidak perlu", "Harus dihapus", "Diganti virus", "A", "Knowledge keep."),
        ]
    else:
        # fallback generik berdasarkan tingkat
        bank = [
            Q(f"Materi \"{judul}\" termasuk jenjang kelas...", tingkat, "9", "6", "10", "A", f"Materi ini untuk kelas {tingkat}."),
            Q(f"Semester materi \"{judul}\" adalah...", semester, "Libur", "Remedial", "Magang", "A", f"Semester {semester}."),
            Q("Belajar materi ini sebaiknya diikuti dengan...", "Mencoba contoh kode", "Menghafal tanpa praktik", "Menghindari latihan", "Menutup aplikasi", "A", "Praktik memperkuat paham."),
            Q("Jika belum paham, langkah baik...", "Baca ulang contoh & kerjakan soal", "Langsung skip semua", "Hapus materi", "Ganti OS", "A", "Ulangi bertahap."),
            Q("Contoh kode pada materi berguna untuk...", "Melihat penerapan konsep", "Menghapus konsep", "Mengganti guru", "Menutup MySQL", "A", "Ilustrasi nyata."),
            Q("Soal latihan bertujuan...", "Mengukur pemahaman dasar", "Menghapus nilai", "Mengubah KKM jadi 0", "Menutup semester", "A", "Asesmen formatif."),
            Q("Pembahasan soal membantu...", "Memahami alasan jawaban", "Menyembunyikan logika", "Menghapus kunci", "Random jawaban", "A", "Belajar dari koreksi."),
            Q("Urutan belajar yang baik...", "Materi → contoh → soal", "Soal tanpa baca", "Hapus contoh", "Langsung SAS", "A", "Scaffolding."),
            Q("Kesalahan umum siswa...", "Menyalin tanpa paham", "Mencoba sendiri", "Bertanya", "Latihan rutin", "A", "Pahami dulu."),
            Q("Target setelah materi ini...", "Bisa jelaskan konsep dengan kata sendiri", "Lupa semua", "Hindari praktik", "Hapus catatan", "A", "Pemahaman aktif."),
        ]

    # pastikan 10 soal
    while len(bank) < 10:
        n = len(bank) + 1
        bank.append(
            Q(
                f"Contoh soal {n} untuk memahami \"{judul}\": manakah sikap belajar terbaik?",
                "Mencoba contoh lalu latihan",
                "Menghindari semua latihan",
                "Menghapus materi",
                "Tidak membaca pembahasan",
                "A",
                "Praktik + pembahasan memperdalam paham.",
            )
        )
    return bank[:10]


CONTOH_HTML = """
<hr>
<h3>Contoh soal mudah</h3>
<ol>
  <li>Baca contoh kode di bawah, tebak outputnya, lalu cocokkan dengan hasil menjalankan kode.</li>
  <li>Ubah satu nilai pada contoh, amati apa yang berubah.</li>
  <li>Kerjakan latihan <em>Contoh Soal Mudah</em> pada menu Latihan untuk materi ini.</li>
</ol>
<p><strong>Tips:</strong> jika salah, baca pembahasan — jangan hanya menghafal huruf jawaban.</p>
"""


def enrich_materi_html(isi: str) -> str:
    if not isi:
        isi = ""
    if "Contoh soal mudah" in isi:
        return isi
    return isi.rstrip() + "\n" + CONTOH_HTML


def main():
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=DictCursor,
        autocommit=False,
    )
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, tingkat, semester, urutan, judul, isi_html
        FROM materi WHERE aktif=1
        ORDER BY tingkat, FIELD(semester,'Ganjil','Genap'), urutan
        """
    )
    materi_list = cur.fetchall()
    total_soal = 0
    for m in materi_list:
        judul_ujian = f"Contoh Soal Mudah: {m['judul']}"
        cur.execute(
            """
            SELECT id FROM ujian
            WHERE materi_id=%s AND jenis='latihan' AND judul=%s
            LIMIT 1
            """,
            (m["id"], judul_ujian),
        )
        u = cur.fetchone()
        if not u:
            cur.execute(
                """
                INSERT INTO ujian
                  (judul, deskripsi, jenis, semester, tingkat, materi_id,
                   durasi_menit, jumlah_soal, nilai_kkm, acak_soal, tampil_pembahasan, aktif)
                VALUES (%s,%s,'latihan',%s,%s,%s,20,10,77,1,1,0)
                """,
                (
                    judul_ujian,
                    f"Latihan pemahaman mudah untuk materi {m['judul']}.",
                    m["semester"],
                    m["tingkat"],
                    m["id"],
                ),
            )
            ujian_id = cur.lastrowid
        else:
            ujian_id = u["id"]
            cur.execute("DELETE FROM soal WHERE ujian_id=%s", (ujian_id,))

        soal = soal_untuk(m["judul"], m["tingkat"], m["semester"])
        for i, s in enumerate(soal, start=1):
            cur.execute(
                """
                INSERT INTO soal
                  (ujian_id, nomor, pertanyaan, opsi_a, opsi_b, opsi_c, opsi_d,
                   kunci_jawaban, pembahasan, bobot, aktif)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1,0)
                """,
                (
                    ujian_id,
                    i,
                    s["pertanyaan"],
                    s["opsi_a"],
                    s["opsi_b"],
                    s["opsi_c"],
                    s["opsi_d"],
                    s["kunci"],
                    s["pembahasan"],
                ),
            )
            total_soal += 1
        cur.execute(
            "UPDATE ujian SET jumlah_soal=%s, tampil_pembahasan=1, aktif=0 WHERE id=%s",
            (len(soal), ujian_id),
        )
        cur.execute(
            "UPDATE materi SET isi_html=%s WHERE id=%s",
            (enrich_materi_html(m.get("isi_html") or ""), m["id"]),
        )
        print(f"OK {m['tingkat']}/{m['semester']}/P{m['urutan']}: {m['judul']} (+{len(soal)} soal)")

    conn.commit()
    conn.close()
    print(f"\nSelesai. Total soal contoh ditambahkan/diperbarui: {total_soal}")
    print("Siswa: menu Latihan → pilih 'Contoh Soal Mudah: ...'")


if __name__ == "__main__":
    main()
