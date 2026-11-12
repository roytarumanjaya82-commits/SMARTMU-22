"""Katalog Modul Pembelajaran Koding per kelas (bahasa murid SMP)."""

# Setiap modul: kode, judul, ringkas, warna, bab[{judul, teks, contoh[{level, judul, kode, output, tips}]}]

MODUL_KELAS = {
    "7": [
        {
            "kode": "k7-m01",
            "judul": "Modul 1 · Kenalan dengan Python",
            "ringkas": "Apa itu Python, cara menampilkan teks, dan langkah pertama coding.",
            "ikon": "rocket",
            "bab": [
                {
                    "judul": "Python itu apa, sih?",
                    "teks": (
                        "Bayangkan Python seperti bahasa untuk berbicara dengan komputer. "
                        "Kamu menulis perintah, lalu komputer menjalankannya. Di Kelas 7 kita mulai dari yang paling "
                        "sederhana: menampilkan tulisan, menyimpan data, dan membuat program kecil yang bisa dicoba di HP atau laptop."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Sapa sekolah",
                            "kode": 'print("Halo SMP Muhammadiyah 22!")\nprint("Aku siap belajar koding")',
                            "output": "Halo SMP Muhammadiyah 22!\nAku siap belajar koding",
                            "tips": "Setiap print membuat satu baris di layar.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Gabungkan teks dan angka",
                            "kode": 'nama = "Aisyah"\nkelas = 7\nprint("Nama:", nama)\nprint("Kelas:", kelas)',
                            "output": "Nama: Aisyah\nKelas: 7",
                            "tips": "Teks pakai tanda kutip, angka tidak perlu kutip.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Kartu nama mini",
                            "kode": 'nama = input("Namamu: ")\n# contoh jika input = Rafi\nnama = "Rafi"\nprint("=" * 20)\nprint("KARTU SISWA")\nprint("Nama :", nama)\nprint("Mapel: Koding")\nprint("=" * 20)',
                            "output": "====================\nKARTU SISWA\nNama : Rafi\nMapel: Koding\n====================",
                            "tips": "Operator * pada teks mengulang karakter.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k7-m02",
            "judul": "Modul 2 · Variabel, Tipe Data & Operator",
            "ringkas": "Menyimpan data, mengenal tipe, dan berhitung dengan Python.",
            "ikon": "box",
            "bab": [
                {
                    "judul": "Variabel = kotak penyimpanan",
                    "teks": (
                        "Variabel seperti kotak berlabel. Isinya bisa berubah. "
                        "Di sekolah, kita sering menyimpan nama, NIS, nilai, dan KKM. "
                        "Operator (+ - * /) membantu menghitung skor atau rata-rata."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Simpan nilai ulangan",
                            "kode": "nilai = 85\nkkm = 77\nprint(nilai, kkm)",
                            "output": "85 77",
                            "tips": "Nama variabel sebaiknya jelas, misalnya nilai bukan n.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Hitung rata-rata 3 nilai",
                            "kode": "n1, n2, n3 = 80, 90, 70\nrata = (n1 + n2 + n3) / 3\nprint(rata)",
                            "output": "80.0",
                            "tips": "Bagi dengan 3 supaya mendapat rata-rata.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Konversi input jadi angka",
                            "kode": 'teks = "88"\nnilai = int(teks)\nprint(nilai + 2)\nprint(type(nilai))',
                            "output": "90\n<class 'int'>",
                            "tips": "input() menghasilkan teks; ubah dengan int() jika ingin dihitung.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k7-m03",
            "judul": "Modul 3 · Percabangan & Perulangan",
            "ringkas": "Membuat keputusan (if) dan mengulang kerja (for/while).",
            "ikon": "flow",
            "bab": [
                {
                    "judul": "Komputer bisa memilih dan mengulang",
                    "teks": (
                        "Dengan if-elif-else, program memutuskan: tuntas atau belum. "
                        "Dengan for/while, program bisa mengulang tanpa menulis kode berkali-kali. "
                        "Ini fondasi game dan kuis sederhana."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Cek KKM",
                            "kode": 'nilai = 80\nif nilai >= 77:\n    print("Tuntas")\nelse:\n    print("Belum tuntas")',
                            "output": "Tuntas",
                            "tips": "Perhatikan indentasi (spasi di dalam if).",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Cetak 1 sampai 5",
                            "kode": "for i in range(1, 6):\n    print(\"Angka\", i)",
                            "output": "Angka 1 ... Angka 5",
                            "tips": "range(1, 6) berarti 1 sampai sebelum 6.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Hitung berapa yang tuntas",
                            "kode": "nilai = [90, 70, 80, 60, 77]\ntuntas = 0\nfor n in nilai:\n    if n >= 77:\n        tuntas += 1\nprint(\"Tuntas:\", tuntas)",
                            "output": "Tuntas: 3",
                            "tips": "Gabungkan loop + if untuk menghitung kondisi.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k7-m04",
            "judul": "Modul 4 · List, Dictionary & Fungsi",
            "ringkas": "Menyimpan banyak data dan membuat fungsi supaya kode rapi.",
            "ikon": "list",
            "bab": [
                {
                    "judul": "Data banyak, kode tetap rapi",
                    "teks": (
                        "List cocok untuk deretan nilai. Dictionary cocok untuk biodata (nama, nis, kelas). "
                        "Fungsi (def) membuat perintah yang bisa dipakai ulang, seperti mesin kecil di dalam program."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "List nilai",
                            "kode": 'nilai = [80, 90, 75]\nprint(nilai[0])\nprint(len(nilai))',
                            "output": "80\n3",
                            "tips": "Index dimulai dari 0.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Dictionary siswa",
                            "kode": 'siswa = {"nama": "Budi", "nis": "2507503", "nilai": 88}\nprint(siswa["nama"], siswa["nilai"])',
                            "output": "Budi 88",
                            "tips": "Ambil data dengan kunci, misalnya siswa['nama'].",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Fungsi status KKM",
                            "kode": 'def status(nilai, kkm=77):\n    return "Tuntas" if nilai >= kkm else "Belum"\nprint(status(90))\nprint(status(70))',
                            "output": "Tuntas\nBelum",
                            "tips": "return mengirim hasil keluar dari fungsi.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k7-m05",
            "judul": "Modul 5 · Mini Game Teks (Objek Sederhana)",
            "ringkas": "Membuat game teks dengan dict, fungsi, dan game loop.",
            "ikon": "game",
            "bab": [
                {
                    "judul": "Dari pelajaran jadi game",
                    "teks": (
                        "Di jalur Game OOP Kelas 7, 'objek' dulu digambar dengan dictionary. "
                        "Player punya HP dan skor. Loop game terus berjalan sampai menang atau kalah. "
                        "Ini bekal menuju class di Kelas 8."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Buat objek player",
                            "kode": 'player = {"nama": "Hero", "hp": 100, "skor": 0}\nprint(player["nama"], player["hp"])',
                            "output": "Hero 100",
                            "tips": "Satu dict = satu objek data.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Fungsi tambah skor",
                            "kode": 'def tambah_skor(p, poin):\n    p["skor"] += poin\np = {"skor": 0}\ntambah_skor(p, 10)\nprint(p)',
                            "output": "{'skor': 10}",
                            "tips": "Fungsi bisa mengubah isi dict.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Battle singkat",
                            "kode": 'player = {"hp": 40, "skor": 0}\nmusuh = {"hp": 25}\nwhile player["hp"] > 0 and musuh["hp"] > 0:\n    musuh["hp"] -= 10\n    player["skor"] += 10\n    if musuh["hp"] > 0:\n        player["hp"] -= 7\nprint("Menang" if musuh["hp"] <= 0 else "Kalah", player)',
                            "output": "Menang {'hp': ..., 'skor': ...}",
                            "tips": "Game loop = ulang sampai syarat selesai.",
                        },
                    ],
                }
            ],
        },
    ],
    "8": [
        {
            "kode": "k8-m01",
            "judul": "Modul 1 · Review Kelas 7 & Struktur Data Baru",
            "ringkas": "Mengulang list/dict/fungsi, lalu mengenal set dan comprehension.",
            "ikon": "review",
            "bab": [
                {
                    "judul": "Naik tingkat dari fondasi Kelas 7",
                    "teks": (
                        "Kelas 8 memakai semua bekal Kelas 7, lalu menambah set (himpunan unik) "
                        "dan list comprehension biar membuat list baru lebih ringkas."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Set menghapus duplikat",
                            "kode": "angka = {1, 2, 2, 3}\nprint(angka)",
                            "output": "{1, 2, 3}",
                            "tips": "Set tidak menyimpan duplikat.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "List comprehension",
                            "kode": "kuadrat = [n * n for n in range(1, 6)]\nprint(kuadrat)",
                            "output": "[1, 4, 9, 16, 25]",
                            "tips": "Pola: [ekspresi for item in data].",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Filter nilai tuntas",
                            "kode": "nilai = [90, 70, 80, 60]\ntuntas = [n for n in nilai if n >= 77]\nprint(tuntas)",
                            "output": "[90, 80]",
                            "tips": "Tambahkan if untuk menyaring data.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k8-m02",
            "judul": "Modul 2 · Fungsi Lanjutan, Exception & File",
            "ringkas": "Parameter, return, try/except, dan membaca/menulis file.",
            "ikon": "file",
            "bab": [
                {
                    "judul": "Program yang aman dan bisa menyimpan data",
                    "teks": (
                        "Fungsi lanjutan membuat kode modular. Exception handling mencegah program crash "
                        "saat input salah. File handling membuat data tidak hilang setelah program ditutup."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Fungsi dengan default",
                            "kode": 'def sapa(nama="Siswa"):\n    return f"Halo, {nama}!"\nprint(sapa())\nprint(sapa("Dimas"))',
                            "output": "Halo, Siswa!\nHalo, Dimas!",
                            "tips": "Parameter default dipakai jika argumen tidak diisi.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Tangkap error angka",
                            "kode": 'teks = "abc"\ntry:\n    nilai = int(teks)\nexcept ValueError:\n    nilai = None\n    print("Harus angka")\nprint(nilai)',
                            "output": "Harus angka\nNone",
                            "tips": "try/except menjaga aplikasi tetap jalan.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Siapkan teks file nilai",
                            "kode": 'baris = ["Aisyah,90", "Budi,80"]\nteks = "\\n".join(baris)\nprint(teks)\n# biasanya: open("nilai.txt","w").write(teks)',
                            "output": "Aisyah,90\nBudi,80",
                            "tips": "Gabungkan baris sebelum ditulis ke file.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k8-m03",
            "judul": "Modul 3 · OOP: Class, Object, Method",
            "ringkas": "Cetakan class, object nyata, atribut, method, dan __init__.",
            "ikon": "oop",
            "bab": [
                {
                    "judul": "Dari data terpisah ke object utuh",
                    "teks": (
                        "Class adalah cetakan. Object adalah hasil cetakan. "
                        "Atribut = data, method = perilaku. __init__ mengisi data saat object lahir. "
                        "Ini jantung materi Kelas 8."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Class sederhana",
                            "kode": 'class Siswa:\n    def sapa(self):\n        print("Halo siswa!")\nSiswa().sapa()',
                            "output": "Halo siswa!",
                            "tips": "self merujuk ke object yang dipakai.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Constructor __init__",
                            "kode": 'class Siswa:\n    def __init__(self, nama, nilai):\n        self.nama = nama\n        self.nilai = nilai\ns = Siswa("Dewi", 85)\nprint(s.nama, s.nilai)',
                            "output": "Dewi 85",
                            "tips": "__init__ dipanggil otomatis saat membuat object.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Method status KKM",
                            "kode": 'class Siswa:\n    def __init__(self, nama, nilai):\n        self.nama, self.nilai = nama, nilai\n    def status(self):\n        return "Tuntas" if self.nilai >= 77 else "Belum"\nprint(Siswa("Budi", 70).status())',
                            "output": "Belum",
                            "tips": "Method memakai atribut object sendiri.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k8-m04",
            "judul": "Modul 4 · Inheritance, JSON & Algoritma",
            "ringkas": "Pewarisan class, simpan data JSON, searching & sorting.",
            "ikon": "tree",
            "bab": [
                {
                    "judul": "Object saling terhubung dan data bisa disimpan",
                    "teks": (
                        "Inheritance membuat class anak mewarisi class induk. "
                        "JSON menyimpan data terstruktur. Algoritma searching/sorting melatih berpikir logis."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Inheritance singkat",
                            "kode": 'class Entity:\n    def __init__(self, nama):\n        self.nama = nama\nclass Player(Entity):\n    pass\nprint(Player("Hero").nama)',
                            "output": "Hero",
                            "tips": "Player mewarisi __init__ dari Entity.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "JSON dumps/loads",
                            "kode": 'import json\ndata = {"Aisyah": 90}\nteks = json.dumps(data)\nprint(teks)\nprint(json.loads(teks)["Aisyah"])',
                            "output": '{"Aisyah": 90}\n90',
                            "tips": "dumps: Python→teks, loads: teks→Python.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Cari nama di list",
                            "kode": 'data = ["Aisyah", "Budi", "Rafi"]\ncari = "Budi"\nketemu = False\nfor nama in data:\n    if nama == cari:\n        ketemu = True\n        break\nprint(ketemu)',
                            "output": "True",
                            "tips": "Linear search: cek satu per satu.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k8-m05",
            "judul": "Modul 5 · Game OOP Arena Kelas 8",
            "ringkas": "Player/Enemy class, method serang, dan game loop banyak object.",
            "ikon": "game",
            "bab": [
                {
                    "judul": "Game dengan class sungguhan",
                    "teks": (
                        "Dict Kelas 7 diganti class. Player dan Enemy punya method sendiri. "
                        "List musuh dikelola dalam loop. Ini jembatan ke project game Kelas 9."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Class Player",
                            "kode": 'class Player:\n    def __init__(self, nama, hp=100):\n        self.nama, self.hp, self.skor = nama, hp, 0\np = Player("Hero")\nprint(p.nama, p.hp)',
                            "output": "Hero 100",
                            "tips": "Setiap object punya data sendiri.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Method serang",
                            "kode": 'class P:\n    def __init__(self, hp):\n        self.hp = hp\n        self.skor = 0\n    def serang(self, t, dmg=10):\n        t.hp = max(0, t.hp - dmg)\n        self.skor += dmg\na, b = P(100), P(30)\na.serang(b, 12)\nprint(b.hp, a.skor)',
                            "output": "18 12",
                            "tips": "Method bisa mengubah object lain.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Arena singkat",
                            "kode": 'class E:\n    def __init__(self, hp):\n        self.hp = hp\n    def hidup(self):\n        return self.hp > 0\np, e = E(50), E(35)\nwhile p.hidup() and e.hidup():\n    e.hp -= 12\n    if e.hidup():\n        p.hp -= 7\nprint("Menang" if p.hidup() else "Kalah")',
                            "output": "Menang",
                            "tips": "Ulang sampai salah satu HP habis.",
                        },
                    ],
                }
            ],
        },
    ],
    "9": [
        {
            "kode": "k9-m01",
            "judul": "Modul 1 · Project Kickoff & Struktur Folder",
            "ringkas": "Merancang ide project, MVP, data, dan struktur berkas.",
            "ikon": "plan",
            "bab": [
                {
                    "judul": "Sebelum coding, rancang dulu",
                    "teks": (
                        "Kelas 9 berbasis project. Kickoff menentukan masalah, tujuan, dan fitur wajib (MVP). "
                        "Struktur folder membuat project tidak berantakan saat makin besar."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Brief project",
                            "kode": 'project = {\n  "nama": "RekapNilai9",\n  "masalah": "Nilai tercecer",\n  "mvp": ["tambah", "lihat", "rata"]\n}\nprint(project["nama"], len(project["mvp"]))',
                            "output": "RekapNilai9 3",
                            "tips": "Tulis fitur wajib sebelum coding panjang.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Peta folder",
                            "kode": 'folder = ["main.py", "models.py", "storage.py", "README.md"]\nfor f in folder:\n    print("-", f)',
                            "output": "- main.py ... - README.md",
                            "tips": "Pisahkan alur, model, dan penyimpanan.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Checklist kickoff",
                            "kode": 'cek = {"ide": True, "mvp": True, "risiko": False}\nprint("siap" if all(cek.values()) else "belum")\nprint([k for k,v in cek.items() if not v])',
                            "output": "belum\n['risiko']",
                            "tips": "Checklist mencegah project jalan tanpa rencana.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k9-m02",
            "judul": "Modul 2 · Project CLI, Modul & Persistensi JSON",
            "ringkas": "Menu aplikasi, modularisasi, OOP service, dan simpan JSON.",
            "ikon": "cli",
            "bab": [
                {
                    "judul": "Membangun aplikasi yang bisa dipakai ulang",
                    "teks": (
                        "Menu CLI mengatur alur. Modul memisahkan tanggung jawab. "
                        "Service class mengelola data. JSON menjaga data tetap ada setelah program ditutup."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Menu pilihan",
                            "kode": 'p = "1"\nif p == "1":\n    print("Lihat data")\nelif p == "0":\n    print("Keluar")\nelse:\n    print("Tidak valid")',
                            "output": "Lihat data",
                            "tips": "Validasi pilihan mencegah menu salah cabang.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Service rata-rata",
                            "kode": 'class NilaiService:\n    def __init__(self, data):\n        self.data = data\n    def rata(self):\n        return sum(self.data)/len(self.data) if self.data else 0\nprint(NilaiService([80, 100]).rata())',
                            "output": "90.0",
                            "tips": "Service menyimpan logika di satu tempat.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Payload JSON project",
                            "kode": 'import json\npayload = {"versi": 1, "data": [{"nama": "Salma", "nilai": 92}]}\nprint(json.dumps(payload, indent=2))',
                            "output": "JSON terformat berisi versi dan data",
                            "tips": "Bungkus data dengan metadata versi.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k9-m03",
            "judul": "Modul 3 · Project Web Flask Mini & CRUD",
            "ringkas": "Route, template, create-read-update-delete data.",
            "ikon": "web",
            "bab": [
                {
                    "judul": "Naik dari CLI ke web",
                    "teks": (
                        "Flask membuat halaman web dengan Python. Route menentukan alamat. "
                        "CRUD adalah operasi dasar data: tambah, baca, ubah, hapus."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Simulasi route beranda",
                            "kode": 'def index():\n    return "Beranda Project Kelas 9"\nprint(index())',
                            "output": "Beranda Project Kelas 9",
                            "tips": "Fungsi route mengembalikan isi halaman.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Create & Read",
                            "kode": 'data = []\ndata.append({"id": 1, "nama": "Kirana"})\nprint(data)\nprint(len(data), "record")',
                            "output": "[{'id': 1, 'nama': 'Kirana'}]\n1 record",
                            "tips": "Create tanpa Read sulit dibuktikan.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Update & Delete",
                            "kode": 'data = [{"id": 1, "nilai": 70}, {"id": 2, "nilai": 80}]\nfor d in data:\n    if d["id"] == 1:\n        d["nilai"] = 90\ndata = [d for d in data if d["id"] != 2]\nprint(data)',
                            "output": "[{'id': 1, 'nilai': 90}]",
                            "tips": "Update ubah field; Delete sisakan yang tidak dipilih.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k9-m04",
            "judul": "Modul 4 · Game Project: State, Entity & Highscore",
            "ringkas": "State machine, collision, dan simpan rekor JSON.",
            "ikon": "game",
            "bab": [
                {
                    "judul": "Game sebagai project terpadu",
                    "teks": (
                        "State memisahkan menu, play, dan game over. "
                        "Banyak entity dicek collision-nya. Highscore membuat game terasa lengkap."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Ganti state",
                            "kode": 'state = "menu"\nif state == "menu":\n    state = "play"\nprint(state)',
                            "output": "play",
                            "tips": "Jangan campur logika menu dengan play.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Collision koin",
                            "kode": 'px, koin = 2, 2\nskor = 1 if px == koin else 0\nprint(skor)',
                            "output": "1",
                            "tips": "Posisi sama = tabrakan pada game teks/grid.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Update highscore",
                            "kode": 'import json\ndata = {"highscore": 10}\nskor = 25\nif skor > data["highscore"]:\n    data["highscore"] = skor\nprint(json.dumps(data))',
                            "output": '{"highscore": 25}',
                            "tips": "Simpan hanya jika rekor baru lebih tinggi.",
                        },
                    ],
                }
            ],
        },
        {
            "kode": "k9-m05",
            "judul": "Modul 5 · Capstone Project Akhir Kelas 9",
            "ringkas": "Menggabungkan validasi, simpan, laporan, game/web, dan README.",
            "ikon": "trophy",
            "bab": [
                {
                    "judul": "Project siap demo dan dinilai",
                    "teks": (
                        "Capstone menilai project utuh: berjalan, OOP jelas, ada validasi, "
                        "penyimpanan, laporan/filter, dokumentasi, dan demo singkat."
                    ),
                    "contoh": [
                        {
                            "level": "Mudah",
                            "judul": "Rubrik skor",
                            "kode": 'rubrik = {"berjalan": True, "crud": True, "save": True, "readme": False}\nprint(int(sum(rubrik.values())/len(rubrik)*100))',
                            "output": "75",
                            "tips": "Lengkapi semua kriteria sebelum showcase.",
                        },
                        {
                            "level": "Sedang",
                            "judul": "Ringkas laporan",
                            "kode": 'nilai = [88, 76, 92]\nlap = {"jumlah": len(nilai), "rata": round(sum(nilai)/len(nilai),1), "tuntas": sum(1 for n in nilai if n >= 77)}\nprint(lap)',
                            "output": "{'jumlah': 3, 'rata': 85.3, 'tuntas': 2}",
                            "tips": "Laporan membantu guru melihat hasil cepat.",
                        },
                        {
                            "level": "Sulit",
                            "judul": "Skeleton capstone",
                            "kode": 'class Game:\n    def __init__(self):\n        self.state = "menu"\n        self.skor = 0\n        self.highscore = 0\n    def main(self):\n        self.state = "play"\n        self.skor = 18\n        self.state = "gameover"\n        self.highscore = max(self.highscore, self.skor)\ng = Game(); g.main()\nprint(g.state, g.highscore)',
                            "output": "gameover 18",
                            "tips": "Kembangkan skeleton ini jadi project lengkapmu.",
                        },
                    ],
                }
            ],
        },
    ],
}


def daftar_modul(tingkat: str) -> list:
    return list(MODUL_KELAS.get(str(tingkat), []))


def cari_modul(kode: str):
    for tingkat, items in MODUL_KELAS.items():
        for m in items:
            if m["kode"] == kode:
                return dict(m, tingkat=tingkat)
    return None


def semua_modul():
    hasil = []
    for tingkat, items in MODUL_KELAS.items():
        for m in items:
            hasil.append(dict(m, tingkat=tingkat))
    return hasil
