# =============================================================
# WhisperAudioScribe - Instalador automático (Windows)
# =============================================================
# Ejecutar en PowerShell como Administrador:
#   Set-ExecutionPolicy Bypass -Scope Process -Force; .\install.ps1
#
# Instala:  uv  +  FFmpeg
# uv gestiona Python y todas las dependencias de Python.
# Una vez instalado, ejecutar:
#   uv run transcribe.py "ruta\del\video.mp4"
# =============================================================

$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "[*] $msg" -ForegroundColor Blue }
function Write-Ok($msg)   { Write-Host "[✓] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[✗] $msg" -ForegroundColor Red; Exit 1 }

function Refresh-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║  WhisperAudioScribe — Instalador (Windows)   ║" -ForegroundColor Blue
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Verificar que se ejecuta como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Err "Este script necesita ejecutarse como Administrador.`nHaz clic derecho sobre PowerShell → 'Ejecutar como administrador'."
}

# -----------------------------------------------------------
# PASO 1 — Instalar uv
# -----------------------------------------------------------
Write-Step "Comprobando uv..."

$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
if ($uvCmd) {
    Write-Ok "uv ya instalado: $(uv --version)"
} else {
    Write-Step "Instalando uv (gestor de Python y paquetes de Astral)..."
    # Instalador oficial de uv para Windows
    $uvInstallScript = (Invoke-RestMethod "https://astral.sh/uv/install.ps1")
    Invoke-Expression $uvInstallScript

    Refresh-Path

    $uvCmd = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uvCmd) {
        Write-Err "uv instalado pero no se encontró en el PATH. Cierra y vuelve a abrir PowerShell como Administrador y ejecuta el script de nuevo."
    }
    Write-Ok "uv instalado: $(uv --version)"
}

# -----------------------------------------------------------
# PASO 2 — Instalar Python 3.12 via uv
# -----------------------------------------------------------
Write-Step "Asegurando Python 3.12 con uv..."
uv python install 3.12 | Out-Null
$pyVer = uv run python --version 2>&1
Write-Ok "Python listo: $pyVer"

# -----------------------------------------------------------
# PASO 3 — Instalar FFmpeg (único componente de sistema)
# -----------------------------------------------------------
Write-Step "Comprobando FFmpeg..."

$ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpegCmd) {
    Write-Ok "FFmpeg ya instalado."
} else {
    Write-Warn "FFmpeg no encontrado. Instalando..."

    # Intentar con winget (disponible en Windows 10 1709+ y Windows 11)
    $wingetCmd = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $wingetCmd) {
        Write-Step "winget no disponible. Instalando App Installer de Microsoft Store..."
        try {
            Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe
            Refresh-Path
            $wingetCmd = Get-Command winget -ErrorAction SilentlyContinue
        } catch {
            $wingetCmd = $null
        }
    }

    if ($wingetCmd) {
        Write-Step "Instalando FFmpeg con winget..."
        winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements --silent
        Refresh-Path
        $ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
        if ($ffmpegCmd) {
            Write-Ok "FFmpeg instalado correctamente."
        } else {
            Write-Warn "FFmpeg instalado pero no detectado en PATH aún. Reinicia la terminal tras la instalación."
        }
    } else {
        Write-Warn "No se pudo instalar FFmpeg automáticamente."
        Write-Warn "Descárgalo manualmente desde: https://ffmpeg.org/download.html"
        Write-Warn "Extrae el .zip y añade la carpeta 'bin' a la variable de entorno PATH."
        Write-Warn "Luego vuelve a ejecutar este script o ejecuta directamente 'uv run transcribe.py'."
    }
}

# -----------------------------------------------------------
# PASO 4 — Warm-up: pre-descargar dependencias de Python
# -----------------------------------------------------------
Write-Step "Pre-descargando dependencias de Python con uv (openai-whisper, yt-dlp, torch)..."
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
try {
    uv run --no-project "$scriptDir\transcribe.py" --help 2>&1 | Out-Null
} catch {}
Write-Ok "Dependencias de Python listas."

# -----------------------------------------------------------
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║      ¡Instalación completada con éxito!      ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Cómo transcribir:" -ForegroundColor White
Write-Host '  uv run transcribe.py "ruta\del\video.mp4"'          -ForegroundColor Cyan
Write-Host '  uv run transcribe.py "https://youtube.com/watch?v=..."' -ForegroundColor Cyan
Write-Host '  uv run transcribe.py "video.mp4" --model medium --language es' -ForegroundColor Cyan
Write-Host ""
