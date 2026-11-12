# Ganti Nameserver / DNS untuk koding.smpm22pamulang.sch.id

## Temuan penting
Domain **smpm22pamulang.sch.id** ada di akun Hostinger lain
(email kira-kira: `g…n.m…a@gmail.com`), **bukan** akun Hostinger yang sedang login sekarang.

Jadi nameserver/DNS tidak bisa diubah dari akun Hostinger saat ini.

## Yang harus dilakukan

### 1. Login Hostinger pemilik domain
Login ke akun Hostinger yang emailnya terkait `g…n.m…a@gmail.com`
(akun sekolah / admin website).

### 2A. Opsi terbaik: ganti nameserver ke Cloudflare
Di Hostinger akun pemilik domain:
1. Domains → **smpm22pamulang.sch.id**
2. Nameservers → Change / Custom
3. Isi:
   - `gwen.ns.cloudflare.com`
   - `milan.ns.cloudflare.com`
4. Hapus `ns1.dns-parking.com` dan `ns2.dns-parking.com`
5. Simpan, tunggu 15–60 menit

### 2B. Opsi alternatif (tanpa ganti nameserver)
Jika tidak boleh ganti nameserver, di DNS Hostinger akun pemilik domain
tambahkan record:

| Tipe  | Nama   | Tujuan                                                         |
|-------|--------|----------------------------------------------------------------|
| CNAME | koding | `46e7c292-2f76-40d0-95fc-45a916a66ec3.cfargotunnel.com`        |

## Setelah DNS aktif
Jalankan `start_public.bat` di komputer server.
Buka: https://koding.smpm22pamulang.sch.id
