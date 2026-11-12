# Setup link publik TETAP (Cloudflare Named Tunnel)
# Satu kali setup, lalu setiap start_public.bat memakai URL yang sama.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$cf = Join-Path $Root "tools\cloudflared.exe"
$configDir = Join-Path $Root "tools\cloudflared-config"
$credDir = Join-Path $env:USERPROFILE ".cloudflared"
New-Item -ItemType Directory -Force -Path $configDir | Out-Null

if (-not (Test-Path $cf)) {
    Write-Host "cloudflared belum ada. Mengunduh..."
    New-Item -ItemType Directory -Force -Path (Join-Path $Root "tools") | Out-Null
    Invoke-WebRequest `
        -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" `
        -OutFile $cf -UseBasicParsing
}

Write-Host ""
Write-Host "============================================"
Write-Host " SETUP LINK TETAP - Koding SMPM 22"
Write-Host "============================================"
Write-Host ""
Write-Host "Langkah 1: Login Cloudflare (browser akan terbuka)."
Write-Host "Pilih domain sekolah jika sudah ada di Cloudflare,"
Write-Host "atau buat akun gratis di https://dash.cloudflare.com"
Write-Host ""
Pause

& $cf tunnel login
if ($LASTEXITCODE -ne 0) { throw "Login Cloudflare gagal." }

$tunnelName = "koding-smpm22"
Write-Host ""
Write-Host "Langkah 2: Membuat named tunnel '$tunnelName' (jika belum ada)..."
$existing = & $cf tunnel list 2>$null | Out-String
if ($existing -notmatch $tunnelName) {
    & $cf tunnel create $tunnelName
} else {
    Write-Host "Tunnel sudah ada, dipakai ulang."
}

# Ambil Tunnel ID dari list
$listJson = & $cf tunnel list -o json | Out-String
$list = $listJson | ConvertFrom-Json
$tunnel = @($list) | Where-Object { $_.name -eq $tunnelName } | Select-Object -First 1
if (-not $tunnel) { throw "Tunnel $tunnelName tidak ditemukan." }
$tunnelId = $tunnel.id
Write-Host "Tunnel ID: $tunnelId"

Write-Host ""
$defaultHost = "koding.smpm22pamulang.sch.id"
$hostname = Read-Host "Langkah 3: Masukkan hostname tetap (contoh $defaultHost)"
if ([string]::IsNullOrWhiteSpace($hostname)) { $hostname = $defaultHost }
$hostname = $hostname.Trim().ToLower()

# Coba route DNS otomatis jika domain ada di akun Cloudflare
Write-Host ""
Write-Host "Mencoba menambahkan DNS CNAME otomatis..."
& $cf tunnel route dns $tunnelName $hostname 2>&1 | ForEach-Object { Write-Host $_ }

$configPath = Join-Path $configDir "config.yml"
$credFile = Join-Path $credDir "$tunnelId.json"
@"
tunnel: $tunnelId
credentials-file: $credFile

ingress:
  - hostname: $hostname
    service: http://127.0.0.1:5000
  - service: http_status:404
"@ | Set-Content -Path $configPath -Encoding UTF8

@"
TUNNEL_MODE=cloudflare
PUBLIC_HOSTNAME=$hostname
TUNNEL_ID=$tunnelId
CLOUDFLARED_CONFIG=$configPath
"@ | Set-Content -Path (Join-Path $Root "tools\tunnel.env") -Encoding UTF8

Write-Host ""
Write-Host "============================================"
Write-Host " SELESAI"
Write-Host "============================================"
Write-Host "Link tetap Anda:"
Write-Host "  https://$hostname"
Write-Host ""
Write-Host "Jika DNS otomatis gagal, tambahkan CNAME di DNS domain sekolah:"
Write-Host "  Nama : $(($hostname -split '\.',2)[0])"
Write-Host "  Tipe : CNAME"
Write-Host "  Tujuan: $tunnelId.cfargotunnel.com"
Write-Host "  Proxy : Proxied (oranye) jika di Cloudflare"
Write-Host ""
Write-Host "Lalu jalankan: start_public.bat"
Write-Host "URL tidak akan berubah setiap kali diaktifkan."
Write-Host ""
Pause
