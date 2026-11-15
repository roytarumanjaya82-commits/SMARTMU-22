# TPK SMARTMU22

Aplikasi **Tes Penempatan Kelas** untuk seleksi murid baru  
**SMP Muhammadiyah 22 Setiabudi Pamulang**.

Dibangun dengan **Python, Flask, dan MySQL**.

## Fitur

- Pendaftaran murid baru + pilihan kelas (Olimpiade, Tahfidz, Multimedia, Internasional, Reguler)
- Hak akses: **Admin**, **Guru Penguji** (per kelas), **Murid Peserta**
- Tes tertulis (soal pilihan ganda per kelas)
- Penilaian wawancara berbasis kriteria & bobot
- Penilaian wawancara per kelas berskala **100** (total bobot kriteria = 100)
- Rekomendasi kelas otomatis dari **nilai wawancara tertinggi**
- Laporan seluruh murid & laporan individu
- Penetapan kelas oleh admin

## Persyaratan

- Python 3.10+
- MySQL 8+ (atau MariaDB)
- pip

## Instalasi

1. Buat database:

```sql
CREATE DATABASE tpk_smartmu22 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

atau:

```bash
mysql -u root -p < database/schema.sql
```

2. Salin konfigurasi:

```bash
copy .env.example .env
```

Edit `.env` sesuai password MySQL Anda.

3. Install dependensi:

```bash
pip install -r requirements.txt
```

4. Jalankan aplikasi:

**Lewat portal SMARTMU 22 (disarankan):**

```bash
# dari root SMARTMU-22
python app.py
```

Buka: [http://127.0.0.1:5000/tpk/](http://127.0.0.1:5000/tpk/)  
Kartu **TPK** juga muncul di beranda portal. Beri akses lewat menu akun portal.

**Mandiri (pengembangan):**

```bash
python run.py
```

Buka: [http://127.0.0.1:5001](http://127.0.0.1:5001)

## Akun Default

| Peran | Username | Password |
|-------|----------|----------|
| Admin | `admin` | `admin123` |
| Guru Olimpiade | `guru_olimpiade` | `guru123` |
| Guru Tahfidz | `guru_tahfidz` | `guru123` |
| Guru Multimedia | `guru_multimedia` | `guru123` |
| Guru Internasional | `guru_internasional` | `guru123` |
| Guru Reguler | `guru_reguler` | `guru123` |

Murid mendaftar sendiri lewat menu **Daftar Murid Baru**.

## Alur Penilaian

1. Murid mendaftar dan memilih kelas prioritas.
2. Murid mengerjakan **tes tertulis** sesuai pilihan kelas 1.
3. Guru penguji menilai **wawancara** (skor tiap aspek sesuai bobot, total 100 per kelas).
4. Sistem merekomendasikan kelas dengan **nilai wawancara tertinggi**.
5. Admin menetapkan kelas penempatan final (default mengikuti rekomendasi).

## Struktur Folder

```
app/
  admin/      # manajemen murid, guru, soal, kriteria, hasil
  auth/       # login & registrasi
  guru/       # penilaian wawancara
  murid/      # profil, tes, hasil
  templates/  # tampilan HTML
  static/     # CSS
database/     # skema SQL
run.py
```

## Catatan Keamanan

Ganti password default dan `FLASK_SECRET_KEY` sebelum dipakai di lingkungan nyata.