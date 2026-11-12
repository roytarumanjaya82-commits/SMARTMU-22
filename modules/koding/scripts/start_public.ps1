# Jalankan Flask + tunnel. Pakai link TETAP jika tools\tunnel.env sudah di-setup.
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$cloudflared = Join-Path $Root "tools\cloudflared.exe"
$tunnelEnv = Join-Path $Root "tools\tunnel.env"

if (-not (Test-Path $cloudflared)) {
    Write-Host "Mengunduh cloudflared..."
    New-Item -ItemType Directory -Force -Path (Join-Path $Root "tools") | Out-Null
    Invoke-WebRequest `
        -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" `
        -OutFile $cloudflared -UseBasicParsing
}

Write-Host "Menjalankan Flask..."
$flask = Start-Process -PassThru -WindowStyle Minimized -FilePath "python" -ArgumentList "run.py" -WorkingDirectory $Root
Start-Sleep -Seconds 4

$mode = $null
$hostname = $null
$config = $null
if (Test-Path $tunnelEnv) {
    Get-Content $tunnelEnv | ForEach-Object {
        if ($_ -match "^\s*TUNNEL_MODE=(.+)$") { $mode = $Matches[1].Trim() }
        if ($_ -match "^\s*PUBLIC_HOSTNAME=(.+)$") { $hostname = $Matches[1].Trim() }
        if ($_ -match "^\s*CLOUDFLARED_CONFIG=(.+)$") { $config = $Matches[1].Trim() }
    }
}

try {
    if ($mode -eq "cloudflare" -and $config -and (Test-Path $config)) {
        Write-Host ""
        Write-Host "LINK TETAP: https://$hostname"
        Write-Host "URL ini sama setiap kali diaktifkan."
        Write-Host ""
        & $cloudflared tunnel --config $config run
    }
    else {
        Write-Host ""
        Write-Host "Belum setup link tetap. Jalankan setup_link_tetap.bat duluan."
        Write-Host "Sementara memakai link acak..."
        Write-Host ""
        & $cloudflared tunnel --url http://127.0.0.1:5000
    }
}
finally {
    if ($flask -and -not $flask.HasExited) {
        Stop-Process -Id $flask.Id -Force -ErrorAction SilentlyContinue
    }
}
