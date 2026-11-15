# One-time setup on Windows. Run from the repo folder in PowerShell:
#   powershell -ExecutionPolicy Bypass -File setup\setup-windows.ps1
# Installs FFmpeg and Python (if missing), the Python packages, and the Whisper model.

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

if (-not (Have winget)) { Write-Host "winget not found: install 'App Installer' from the Microsoft Store, then run this again."; exit 1 }

if (-not (Have ffmpeg)) {
    Write-Host "Installing FFmpeg..."
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
    Refresh-Path
}
if (-not (Have python)) {
    Write-Host "Installing Python..."
    winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
    Refresh-Path
}

Write-Host "Installing Python packages (Whisper, yt-dlp)..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Downloading the Whisper 'medium' model (about 1.5 GB, one time)..."
python -c "from faster_whisper import WhisperModel; WhisperModel('medium', device='cpu', compute_type='int8')"

python tools\check_setup.py
Write-Host "`nIf ffmpeg or python is still 'not found', close this window, open a new PowerShell and run this script again."
