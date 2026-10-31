# SMARTMU 22

Satu aplikasi untuk empat portal SMP Muhammadiyah 22 Setiabudi Pamulang: Presensi, eRapor, Tahfidz, dan Rapor BK.

## Menjalankan

Perlu Python 3.10+ dan MySQL yang sudah berjalan.

```powershell
cd d:\ROY\SMARTMU-22
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python init_db.py
python app.py
```

Buka http://127.0.0.1:5000

Akun awal: `admin` / `admin123`

## Database

Satu server MySQL. Data portal dan rapor BK ada di database `smartmu`. Presensi, eRapor, dan Tahfidz tetap punya database sendiri karena tabel `siswa`, `kelas`, dan `users` tidak sama bentuknya. Semuanya dibuat oleh `init_db.py`.
