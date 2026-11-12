"""Kurikulum Kelas 9: Python lanjutan berbasis project (lanjutan Kelas 8)."""

MATERI_GANJIL = [
    {
        "urutan": 1,
        "judul": "Project Kickoff: Ide & Kebutuhan",
        "ringkasan": "Merancang ide project, tujuan, dan daftar fitur dari fondasi Kelas 8.",
        "isi_html": """
        <h3>Dari materi ke project</h3>
        <p>Kelas 8 sudah memberi bekal OOP, file/JSON, algoritma, dan best practice.
        Kelas 9 memakai bekal itu untuk membangun <strong>project nyata</strong> langkah demi langkah.</p>
        <h3>Langkah kickoff</h3>
        <ol>
          <li>Tentukan masalah yang ingin diselesaikan (contoh: rekap nilai, todo siswa, kasir mini)</li>
          <li>Tulis tujuan project dalam 1–2 kalimat</li>
          <li>Buat daftar fitur wajib (MVP) dan fitur tambahan</li>
          <li>Tentukan data yang dibutuhkan</li>
        </ol>
        <h3>Deliverable pertemuan ini</h3>
        <p>Dokumen singkat: nama project, masalah, pengguna, 5 fitur wajib.</p>
        """,
        "contoh_kode": 'project = {\n    "nama": "RekapNilai9",\n    "masalah": "Guru sulit rekap nilai cepat",\n    "pengguna": "guru koding",\n    "fitur_wajib": ["tambah nilai", "rata-rata", "simpan JSON"],\n}\nprint(project["nama"])\nprint(len(project["fitur_wajib"]), "fitur wajib")',
    },
    {
        "urutan": 2,
        "judul": "Desain Data & Struktur Folder Project",
        "ringkasan": "Merancang struktur data dan folder sebelum menulis banyak kode.",
        "isi_html": """
        <h3>Kenapa desain dulu?</h3>
        <p>Project yang langsung diketik tanpa rancangan cepat berantakan. Desain data dan folder
        membuat tim (atau kamu sendiri) tahu di mana setiap bagian diletakkan.</p>
        <h3>Contoh struktur</h3>
        <pre>rekap_nilai/
  main.py
  models.py
  storage.py
  data/
    nilai.json
  README.md</pre>
        <h3>Model data</h3>
        <p>Tentukan field penting, misalnya: nama, nis, mapel, nilai, tanggal.</p>
        """,
        "contoh_kode": 'struktur = ["main.py", "models.py", "storage.py", "data/nilai.json", "README.md"]\nfor berkas in struktur:\n    print("-", berkas)\n\nrecord = {"nis": "2909001", "nama": "Naufal", "nilai": 88}\nprint(record)',
    },
    {
        "urutan": 3,
        "judul": "Project CLI: Menu Aplikasi",
        "ringkasan": "Membangun menu berbasis teks (CLI) sebagai kerangka project.",
        "isi_html": """
        <h3>CLI sebagai kerangka</h3>
        <p>Sebelum GUI/web, buat menu teks: Tambah, Lihat, Simpan, Keluar.
        Ini melatih alur program dan pemisahan fungsi.</p>
        <h3>Pola</h3>
        <ul>
          <li>Loop utama menampilkan menu</li>
          <li>Setiap pilihan memanggil fungsi</li>
          <li>Pilihan keluar menghentikan loop</li>
        </ul>
        """,
        "contoh_kode": 'def menu():\n    print("1. Tambah\\n2. Lihat\\n0. Keluar")\n\ndef main():\n    while True:\n        menu()\n        pilih = "0"  # ganti input("Pilih: ")\n        if pilih == "0":\n            print("Selesai")\n            break\n        print("Menu", pilih)\n\nmain()',
    },
    {
        "urutan": 4,
        "judul": "Modularisasi Project",
        "ringkasan": "Memecah project menjadi modul: model, storage, dan main.",
        "isi_html": """
        <h3>Pemisahan tanggung jawab</h3>
        <ul>
          <li><code>models.py</code> — class/data</li>
          <li><code>storage.py</code> — baca/tulis file</li>
          <li><code>main.py</code> — menu dan alur</li>
        </ul>
        <p>Ini lanjutan materi modul &amp; OOP Kelas 8, diterapkan pada project utuh.</p>
        """,
        "contoh_kode": '# models.py (disimulasikan)\nclass Siswa:\n    def __init__(self, nama, nilai):\n        self.nama = nama\n        self.nilai = nilai\n\n# main memakai model\ns = Siswa("Putri", 90)\nprint(s.nama, s.nilai)',
    },
    {
        "urutan": 5,
        "judul": "OOP di Project Nyata",
        "ringkasan": "Class service untuk mengelola kumpulan data project.",
        "isi_html": """
        <h3>Service class</h3>
        <p>Selain class data (Siswa/Produk), buat class pengelola: menambah, mencari, menghitung rata-rata.
        Pola ini dipakai di hampir semua project Kelas 9.</p>
        """,
        "contoh_kode": 'class NilaiService:\n    def __init__(self):\n        self.data = []\n    def tambah(self, nama, nilai):\n        self.data.append({"nama": nama, "nilai": nilai})\n    def rata(self):\n        if not self.data:\n            return 0\n        return sum(x["nilai"] for x in self.data) / len(self.data)\n\nsvc = NilaiService()\nsvc.tambah("Aisyah", 90)\nsvc.tambah("Budi", 80)\nprint(svc.rata())',
    },
    {
        "urutan": 6,
        "judul": "Persistensi Project dengan JSON",
        "ringkasan": "Menyimpan dan memuat data project agar tidak hilang saat program ditutup.",
        "isi_html": """
        <h3>Data harus bertahan</h3>
        <p>Gabungkan file handling + JSON dari Kelas 8 ke dalam project: simpan saat keluar, muat saat mulai.</p>
        """,
        "contoh_kode": 'import json\ndata = [{"nama": "Aisyah", "nilai": 90}]\nteks = json.dumps(data, ensure_ascii=False, indent=2)\nprint(teks)\nbalik = json.loads(teks)\nprint(balik[0]["nama"])',
    },
    {
        "urutan": 7,
        "judul": "Validasi & Exception pada Project",
        "ringkasan": "Menjaga project tetap stabil saat input pengguna salah.",
        "isi_html": """
        <h3>Project yang tangguh</h3>
        <p>Nilai di luar 0–100, input kosong, atau file hilang tidak boleh membuat program crash.
        Terapkan validasi + try/except di titik kritis project.</p>
        """,
        "contoh_kode": 'def baca_nilai(teks):\n    try:\n        n = int(teks)\n    except ValueError:\n        return None, "Nilai harus angka"\n    if not 0 <= n <= 100:\n        return None, "Nilai 0-100"\n    return n, "OK"\n\nprint(baca_nilai("88"))\nprint(baca_nilai("abc"))\nprint(baca_nilai("120"))',
    },
    {
        "urutan": 8,
        "judul": "Testing Mini untuk Project",
        "ringkasan": "Menguji fungsi penting project dengan assert dan kasus uji.",
        "isi_html": """
        <h3>Uji sebelum demo</h3>
        <p>Sebelum presentasi, uji fungsi inti: tambah data, rata-rata, pencarian, simpan/muat.
        Gunakan assert dan beberapa kasus (normal, kosong, ekstrem).</p>
        """,
        "contoh_kode": 'def rata(data):\n    assert len(data) > 0\n    return sum(data) / len(data)\n\nassert rata([80, 100]) == 90\ntry:\n    rata([])\nexcept AssertionError:\n    print("kasus kosong tertangkap")\nprint("tes dasar lulus")',
    },
    {
        "urutan": 9,
        "judul": "Dokumentasi Project & README",
        "ringkasan": "Menulis README: cara menjalankan, fitur, dan struktur project.",
        "isi_html": """
        <h3>Project tanpa dokumentasi sulit dipakai</h3>
        <p>README minimal berisi: nama project, tujuan, cara menjalankan, daftar fitur, dan struktur folder.
        Ini bagian penilaian project Kelas 9.</p>
        """,
        "contoh_kode": 'readme = """# RekapNilai9\n\n## Tujuan\nMembantu guru merekap nilai.\n\n## Menjalankan\npython main.py\n"""\nprint(readme.splitlines()[0])\nprint("baris:", len(readme.splitlines()))',
    },
    {
        "urutan": 10,
        "judul": "Showcase Project Ganjil",
        "ringkasan": "Menyelesaikan MVP project semester ganjil dan menyiapkan demo singkat.",
        "isi_html": """
        <h3>Deliverable ganjil</h3>
        <ol>
          <li>Kode project bisa dijalankan</li>
          <li>Minimal 5 fitur wajib jalan</li>
          <li>Data tersimpan (JSON/file)</li>
          <li>README singkat</li>
          <li>Demo 3–5 menit</li>
        </ol>
        <p>Fokus pada kelengkapan MVP, bukan fitur berlebihan.</p>
        """,
        "contoh_kode": 'checklist = {\n    "menu": True,\n    "tambah": True,\n    "lihat": True,\n    "simpan": True,\n    "readme": True,\n}\nprint("siap demo:", all(checklist.values()))\nprint("fitur OK:", sum(checklist.values()), "/", len(checklist))',
    },
]

MATERI_GENAP = [
    {
        "urutan": 1,
        "judul": "Project Web: Pengantar Flask Mini",
        "ringkasan": "Memulai project web sederhana dengan Flask sebagai lanjutan project CLI.",
        "isi_html": """
        <h3>Mengapa Flask?</h3>
        <p>Setelah CLI, project Kelas 9 naik ke antarmuka web sederhana.
        Flask membantu membuat halaman dan route dengan Python yang sudah dikuasai.</p>
        <h3>Konsep awal</h3>
        <ul>
          <li>Aplikasi Flask</li>
          <li>Route <code>/</code></li>
          <li>Menjalankan server lokal</li>
        </ul>
        """,
        "contoh_kode": '# kerangka (jalankan di komputer lokal)\n# from flask import Flask\n# app = Flask(__name__)\n# @app.get("/")\n# def beranda():\n#     return "Halo Project Kelas 9"\nprint("Kerangka Flask: route / siap dirancang")',
    },
    {
        "urutan": 2,
        "judul": "Project Web: Route & Template",
        "ringkasan": "Menambah beberapa halaman project dan menampilkan data ke template.",
        "isi_html": """
        <h3>Banyak halaman = banyak route</h3>
        <p>Project web punya beranda, daftar data, dan form. Pisahkan route per fitur.
        Template HTML menampilkan data dari Python.</p>
        """,
        "contoh_kode": 'halaman = {\n    "/": "Beranda",\n    "/siswa": "Daftar Siswa",\n    "/tambah": "Form Tambah",\n}\nfor route, judul in halaman.items():\n    print(route, "->", judul)',
    },
    {
        "urutan": 3,
        "judul": "Project Data: Model & Penyimpanan",
        "ringkasan": "Menyatukan model OOP dengan penyimpanan file/DB untuk project web.",
        "isi_html": """
        <h3>Lapisan data project</h3>
        <p>Tetap gunakan class/service. Penyimpanan bisa JSON dulu, lalu dinaikkan ke MySQL jika siap.
        Yang penting: route tidak bercampur dengan detail penyimpanan.</p>
        """,
        "contoh_kode": 'class Repo:\n    def __init__(self):\n        self.items = []\n    def add(self, item):\n        self.items.append(item)\n    def all(self):\n        return list(self.items)\n\nrepo = Repo()\nrepo.add({"nama": "Farhan", "nilai": 86})\nprint(repo.all())',
    },
    {
        "urutan": 4,
        "judul": "Project CRUD Dasar",
        "ringkasan": "Create, Read, Update, Delete sebagai inti hampir semua project data.",
        "isi_html": """
        <h3>CRUD</h3>
        <ul>
          <li><strong>Create</strong> — tambah data</li>
          <li><strong>Read</strong> — tampilkan/cari</li>
          <li><strong>Update</strong> — ubah</li>
          <li><strong>Delete</strong> — hapus</li>
        </ul>
        <p>Implementasikan ke project semester genap secara bertahap.</p>
        """,
        "contoh_kode": 'data = [{"id": 1, "nama": "Naufal"}]\n# Create\ndata.append({"id": 2, "nama": "Putri"})\n# Read\nprint(data)\n# Update\ndata[0]["nama"] = "Naufal A."\n# Delete\ndata = [x for x in data if x["id"] != 2]\nprint(data)',
    },
    {
        "urutan": 5,
        "judul": "Project Form & Validasi Web",
        "ringkasan": "Menerima input form, validasi, dan pesan error yang ramah.",
        "isi_html": """
        <h3>Form adalah pintu data</h3>
        <p>Jangan percaya input mentah. Validasi di sisi Python sebelum disimpan.
        Tampilkan pesan jelas ke pengguna project.</p>
        """,
        "contoh_kode": 'def validasi(nama, nilai):\n    if not nama.strip():\n        return "Nama wajib"\n    try:\n        n = int(nilai)\n    except ValueError:\n        return "Nilai harus angka"\n    if not 0 <= n <= 100:\n        return "Nilai 0-100"\n    return None\n\nprint(validasi("Aina", "90"))\nprint(validasi("", "90"))\nprint(validasi("Aina", "x"))',
    },
    {
        "urutan": 6,
        "judul": "Project Laporan & Filter Data",
        "ringkasan": "Membuat rekap, filter, dan ringkasan statistik sederhana.",
        "isi_html": """
        <h3>Nilai project ada pada laporan</h3>
        <p>Tampilkan rata-rata, jumlah tuntas/belum, dan filter berdasarkan kelas/mapel.
        Manfaatkan list comprehension dan algoritma dari Kelas 8.</p>
        """,
        "contoh_kode": 'nilai = [90, 70, 80, 60]\nrata = sum(nilai) / len(nilai)\ntuntas = [n for n in nilai if n >= 77]\nprint("rata", round(rata, 1))\nprint("tuntas", len(tuntas), "dari", len(nilai))',
    },
    {
        "urutan": 7,
        "judul": "Project Session & Hak Akses Sederhana",
        "ringkasan": "Membedakan halaman guru/siswa dengan session sederhana.",
        "isi_html": """
        <h3>Tidak semua menu untuk semua orang</h3>
        <p>Project sekolah biasanya membedakan peran. Mulai dari session sederhana:
        login menyimpan peran, decorator/fungsi mengecek sebelum membuka menu.</p>
        """,
        "contoh_kode": 'session = {"role": "guru"}\ndef boleh_kelola(session):\n    return session.get("role") == "guru"\nprint("kelola:", boleh_kelola(session))\nsession["role"] = "siswa"\nprint("kelola:", boleh_kelola(session))',
    },
    {
        "urutan": 8,
        "judul": "Project API JSON Mini",
        "ringkasan": "Menyediakan endpoint JSON agar data project bisa dibaca aplikasi lain.",
        "isi_html": """
        <h3>API mini</h3>
        <p>Selain halaman HTML, sediakan route yang mengembalikan JSON.
        Berguna untuk latihan integrasi dan memahami format data modern.</p>
        """,
        "contoh_kode": 'import json\npayload = {"ok": True, "jumlah": 2, "data": [{"nama": "Aisyah"}]}\nprint(json.dumps(payload, ensure_ascii=False))',
    },
    {
        "urutan": 9,
        "judul": "Project Hardening & Debugging",
        "ringkasan": "Memperkuat project: logging sederhana, cek error, dan perbaikan bug.",
        "isi_html": """
        <h3>Menjelang project akhir</h3>
        <p>Catat error, uji ulang fitur utama, perbaiki bug prioritas tinggi.
        Project yang baik bukan yang tanpa bug, tetapi yang bisa diperbaiki dengan rapi.</p>
        """,
        "contoh_kode": 'def jalankan_fitur(nama):\n    try:\n        if nama == "bagi0":\n            return 1 / 0\n        return "OK:" + nama\n    except Exception as e:\n        return f"LOG_ERROR:{type(e).__name__}"\nprint(jalankan_fitur("lihat"))\nprint(jalankan_fitur("bagi0"))',
    },
    {
        "urutan": 10,
        "judul": "Capstone Project Akhir Kelas 9",
        "ringkasan": "Menyelesaikan project terpadu: fitur, data, validasi, laporan, dan dokumentasi.",
        "isi_html": """
        <h3>Capstone</h3>
        <p>Gabungkan seluruh kemampuan Kelas 7–9 dalam satu project pilihan:
        rekap nilai, inventaris mini, perpustakaan, atau kasir kelas.</p>
        <h3>Rubrik</h3>
        <ol>
          <li>Project berjalan</li>
          <li>CRUD + validasi</li>
          <li>Penyimpanan data</li>
          <li>Laporan/rekap</li>
          <li>README + demo</li>
        </ol>
        """,
        "contoh_kode": 'rubrik = {\n    "berjalan": True,\n    "crud": True,\n    "simpan": True,\n    "laporan": True,\n    "readme": True,\n}\nskor = sum(100 for v in rubrik.values() if v) / len(rubrik)\nprint("skor kelengkapan:", skor)',
    },
]
