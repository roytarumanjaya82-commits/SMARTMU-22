# Menyalakan portal SMARTMU di http://127.0.0.1:5000
$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$logDir = Join-Path $root "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}
$log = Join-Path $logDir "smartmu.log"

function Tulis-Log([string]$pesan) {
    $baris = "{0}  {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $pesan
    Add-Content -Path $log -Value $baris -Encoding UTF8
}

function Port-Terpakai {
    $hasil = netstat -ano | Select-String -Pattern ":5000\s+.*LISTENING"
    return [bool]$hasil
}

if (Port-Terpakai) {
    Tulis-Log "Lewati: port 5000 sudah dipakai."
    exit 0
}

$batas = (Get-Date).AddSeconds(90)
while ((Get-Date) -lt $batas) {
    $mysql = Get-Service -Name mysql -ErrorAction SilentlyContinue
    if (-not $mysql -or $mysql.Status -eq "Running") { break }
    Start-Sleep -Seconds 3
}

$python = Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"
if (-not (Test-Path $python)) {
    $ketemu = Get-Command python -ErrorAction SilentlyContinue
    if ($ketemu) { $python = $ketemu.Source }
}
if (-not (Test-Path $python)) {
    Tulis-Log "Gagal: python.exe tidak ditemukan."
    exit 1
}

Tulis-Log "Menyalakan SMARTMU."
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
# Lewat cmd supaya tulisan peringatan Flask tidak menghentikan skrip.
cmd /c "`"$python`" -u app.py >> `"$log`" 2>&1"
$kode = $LASTEXITCODE
if (-not $kode) { $kode = 0 }
Tulis-Log "SMARTMU berhenti (kode $kode)."
exit $kode
