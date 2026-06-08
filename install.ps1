# WhisperAudioScribe - Script de instalación automatizado para Windows (PowerShell)

Write-Host "=== Iniciando instalación de WhisperAudioScribe ===" -ForegroundColor Blue

# 1. Comprobar Python
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCheck) {
    Write-Host "[!] Error: Python no está instalado o no se encuentra en el PATH." -ForegroundColor Red
    Write-Host "Por favor, descarga e instala Python 3 desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Asegúrate de marcar la opción 'Add Python to PATH' durante la instalación." -ForegroundColor Yellow
    Exit
} else {
    $version = python --version
    Write-Host "[✓] Python detectado: $version" -ForegroundColor Green
}

# 2. Comprobar Pip
$pipCheck = python -m pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] pip no detectado. Intentando instalar..." -ForegroundColor Yellow
    python -m ensurepip --default-pip
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] No se pudo instalar pip automáticamente." -ForegroundColor Red
        Exit
    }
} else {
    Write-Host "[✓] pip detectado." -ForegroundColor Green
}

# 3. Comprobar e Instalar FFmpeg
$ffmpegCheck = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpegCheck) {
    Write-Host "[!] FFmpeg no está instalado. Es requerido para procesar archivos de audio." -ForegroundColor Yellow
    Write-Host "[*] Intentando instalar FFmpeg mediante winget..." -ForegroundColor Blue
    
    $wingetCheck = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetCheck) {
        winget install "Gyan.FFmpeg" --accept-source-agreements --accept-package-agreements
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] FFmpeg instalado correctamente con winget. Es posible que debas reiniciar la terminal para aplicar los cambios en el PATH." -ForegroundColor Green
        } else {
            Write-Host "[!] La instalación automática con winget falló." -ForegroundColor Red
            Write-Host "Por favor, instala FFmpeg manualmente (ej. 'choco install ffmpeg' o descargando de https://ffmpeg.org)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[!] winget no está disponible." -ForegroundColor Red
        Write-Host "Por favor, descarga e instala FFmpeg manualmente de https://ffmpeg.org y agrégalo a tu variable de entorno PATH." -ForegroundColor Yellow
    }
} else {
    Write-Host "[✓] FFmpeg detectado." -ForegroundColor Green
}

# 4. Instalar dependencias de Python
Write-Host "[*] Instalando librerías de Python (openai-whisper, yt-dlp, torch)..." -ForegroundColor Blue
python -m pip install --upgrade pip
python -m pip install openai-whisper yt-dlp torch

if ($LASTEXITCODE -eq 0) {
    Write-Host "[✓] Librerías de Python instaladas correctamente." -ForegroundColor Green
} else {
    Write-Host "[!] Error al instalar las librerías de Python." -ForegroundColor Red
    Exit
}

Write-Host "`n===============================================" -ForegroundColor Green
Write-Host "¡Instalación completada con éxito!" -ForegroundColor Green
Write-Host "Puedes empezar a transcribir usando:" -ForegroundColor White
Write-Host "  python transcribe.py `"Ruta/del/archivo`"" -ForegroundColor White
Write-Host "===============================================" -ForegroundColor Green
