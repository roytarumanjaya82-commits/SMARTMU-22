# Program Pembelajaran Koding 7.5

Aplikasi web pembelajaran koding (Python) untuk **SMP Muhammadiyah 22 Setiabudi Pamulang**, kelas **7.5**, Kurikulum Merdeka TP **2026/2027**.

Dibangun dengan **Python + Flask + MySQL/MariaDB**.

## Fitur

- Materi untuk **kelas 7** dan **kelas 8**, semester **ganjil** & **genap**
- Upload materi guru dalam format **PDF / DOC / DOCX / PPT / PPTX** per jenjang kelas
- Kelas 7: Python dasar → list, dict, fungsi, nested, problem solving
- Kelas 8: Python lanjutan → set, comprehension, exception, file, OOP, algoritma, tkinter, JSON
- Contoh soal interaktif + latihan
- Ulangan harian
- Menu penilaian:
  - Latihan
  - Sumatif
  - STS Ganjil
  - STS Genap
  - Sumatif Akhir Semester (SAS)
- Impor daftar siswa per kelas dari Excel + unduh blanko
- Rekap nilai per kelas + export Excel
- Responsif: bisa diakses dari HP, tablet, dan laptop di jaringan yang sama

## Persyaratan

- Python 3.10+
- MySQL/MariaDB (sudah tersedia di XAMPP)
- Paket Python: lihat `requirements.txt`

## Instalasi cepat

```powershell
cd "d:\ROY\KBM KODING 7.5"
pip install -r requirements.txt
python scripts\seed.py
python run.py
```

Buka:

- Lokal: http://127.0.0.1:5000
- Perangkat lain (HP/tablet/PC): http://IP-KOMPUTER-SERVER:5000

## Akun default

| Peran | Username | Password |
|------|----------|----------|
| Guru | `guru` | `guru123` |
| Siswa contoh | `2507501` | `123456` |

Password awal siswa hasil impor Excel (jika kolom password kosong): `123456`.

## Blanko Excel siswa

1. Login sebagai guru
2. Menu **Siswa** → **Unduh Blanko Excel**
3. Isi kolom NIS, Nama, Jenis Kelamin (L/P)
4. Unggah kembali di form impor

File contoh juga ada di: `data/blanko_siswa_7.5.xlsx`

## Konfigurasi

Salin `.env.example` menjadi `.env` bila perlu mengubah:

- host/user/password MySQL
- port aplikasi (`FLASK_PORT`)
- `FLASK_HOST=0.0.0.0` agar bisa diakses dari perangkat lain

## Akses dari WiFi mana pun (link publik TETAP)

### Setup sekali saja (agar link tidak berubah)

1. Double-klik `setup_link_tetap.bat`
2. Login Cloudflare (akun gratis)
3. Isi hostname, contoh: `koding.smpm22pamulang.sch.id`
4. Jika diminta, tambahkan CNAME di DNS sekolah:
   - Nama: `koding`
   - Tujuan: `<TUNNEL_ID>.cfargotunnel.com`

Setelah itu link selalu: **https://koding.smpm22pamulang.sch.id**

### Tiap kali dipakai

Double-klik `start_public.bat`  
(atau `powershell -ExecutionPolicy Bypass -File scripts\start_public.ps1`)

Komputer server + XAMPP MySQL harus tetap menyala.

## Akses hanya di jaringan sekolah (LAN)

1. Pastikan komputer server dan perangkat siswa satu Wi-Fi/LAN.
2. Izinkan port 5000 di Windows Firewall jika diminta.
3. Cari IP server dengan `ipconfig`, lalu buka `http://IP:5000` dari HP/tablet.
