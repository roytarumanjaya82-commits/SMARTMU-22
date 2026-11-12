# Domain / Link Gratis untuk Koding

## Langsung pakai (sudah jalan)
Jalankan `start_gratis.bat` atau biarkan tunnel yang sudah aktif.

Link gratis saat ini (berubah jika di-restart):
https://mia-twice-prior-operator.trycloudflare.com

Login demo:
- Guru: `guru` / `guru123`
- Siswa: `2507501` / `123456`

## Link tetap gratis (.eu.cc)
Karena domain sekolah (`smpm22pamulang.sch.id`) belum bisa diubah nameserver-nya,
daftar domain gratis di GNAME lalu hubungkan ke Cloudflare Tunnel.

### 1. Daftar akun GNAME
https://www.gname.com/us/tld-eu-cc.html → Sign up

### 2. Klaim voucher gratis + daftar domain
1. Di halaman Free `.eu.cc`, klik **Free Registration** / **Register Now**
2. Cari nama contoh: `kodingsmpm22.eu.cc` (hindari nama 2–3 huruf)
3. Checkout dengan voucher **$0**

### 3. Tambah domain ke Cloudflare
1. https://dash.cloudflare.com → Add domain → `kodingsmpm22.eu.cc`
2. Pilih plan **Free**
3. Catat 2 nameserver Cloudflare (contoh `xxxx.ns.cloudflare.com`)

### 4. Ubah nameserver di GNAME
DNS → Custom → isi 2 NS dari Cloudflare → Save

### 5. DNS record di Cloudflare
| Tipe  | Nama | Tujuan                                                      | Proxy |
|-------|------|-------------------------------------------------------------|-------|
| CNAME | `@`  | `46e7c292-2f76-40d0-95fc-45a916a66ec3.cfargotunnel.com`     | ON    |
| CNAME | `www`| `46e7c292-2f76-40d0-95fc-45a916a66ec3.cfargotunnel.com`     | ON    |

### 6. Update file lokal
`tools\cloudflared-config\config.yml` → hostname jadi domain baru  
`tools\tunnel.env` → `PUBLIC_HOSTNAME=` domain baru  

Lalu jalankan `start_public.bat`.
