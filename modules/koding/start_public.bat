@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo  Koding 7 ^& 8 - Link Publik
echo ============================================
echo.

set "TUNNEL_MODE="
set "PUBLIC_HOSTNAME="
set "CLOUDFLARED_CONFIG="
set "TUNNEL_ID="

if exist "tools\tunnel.env" (
  for /f "usebackq tokens=1,* delims==" %%A in ("tools\tunnel.env") do (
    if /I "%%A"=="TUNNEL_MODE" set "TUNNEL_MODE=%%B"
    if /I "%%A"=="PUBLIC_HOSTNAME" set "PUBLIC_HOSTNAME=%%B"
    if /I "%%A"=="CLOUDFLARED_CONFIG" set "CLOUDFLARED_CONFIG=%%B"
    if /I "%%A"=="TUNNEL_ID" set "TUNNEL_ID=%%B"
  )
)

echo Menjalankan Flask...
start "Koding Flask" cmd /k "python run.py"
timeout /t 5 /nobreak >nul

if /I "%TUNNEL_MODE%"=="cloudflare" if exist "%CLOUDFLARED_CONFIG%" (
  echo.
  echo Mode LINK TETAP aktif.
  echo Buka: https://%PUBLIC_HOSTNAME%
  echo Link ini TIDAK berubah setiap kali diaktifkan.
  echo.
  tools\cloudflared.exe tunnel --config "%CLOUDFLARED_CONFIG%" run
  goto end
)

echo.
echo Belum ada link tetap.
echo Jalankan dulu: setup_link_tetap.bat  ^(satu kali saja^)
echo.
echo Sementara memakai link sementara ^(berubah tiap kali^)...
echo.
tools\cloudflared.exe tunnel --url http://127.0.0.1:5001

:end
pause
