@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo  Koding 7 ^& 8 - Link GRATIS (sementara)
echo ============================================
echo.
echo Link trycloudflare.com gratis, berubah tiap kali jalan.
echo Untuk link tetap: daftar domain gratis .eu.cc lalu
echo hubungkan ke Cloudflare ^(lihat DOMAIN_GRATIS.md^).
echo.

echo Menjalankan Flask...
start "Koding Flask" cmd /k "python run.py"
timeout /t 5 /nobreak >nul

echo Membuka tunnel gratis...
echo Tunggu sampai muncul baris: https://xxxx.trycloudflare.com
echo.
tools\cloudflared.exe tunnel --url http://127.0.0.1:5001

pause
