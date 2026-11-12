# Agar https://koding.smpm22pamulang.sch.id bisa dibuka

Saat ini subdomain **belum dibuat di DNS**, jadi browser tidak menemukan alamat itu.

## Yang harus dilakukan (sekali)

### A. Setup tunnel di komputer server
1. Jalankan `setup_link_tetap.bat`
2. Login Cloudflare
3. Saat diminta hostname, isi: `koding.smpm22pamulang.sch.id`
4. Catat **Tunnel ID** yang muncul

### B. Tambah DNS di hosting website sekolah (Hostinger / panel domain)
Buat record:

| Tipe  | Nama   | Tujuan                         |
|-------|--------|--------------------------------|
| CNAME | koding | `TUNNEL_ID.cfargotunnel.com`   |

Contoh tujuan: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.cfargotunnel.com`

Tunggu 5–30 menit agar DNS aktif.

### C. Jalankan aplikasi
1. Pastikan XAMPP MySQL menyala
2. Jalankan `start_public.bat`
3. Buka: https://koding.smpm22pamulang.sch.id

## Sementara (bisa dipakai sekarang)
Pakai link Cloudflare sementara yang aktif di server
(lihat jendela cloudflared / `start_public.bat`).
