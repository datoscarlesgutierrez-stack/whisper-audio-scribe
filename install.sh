#!/bin/bash

# WhisperAudioScribe - Script de instalación automatizado para macOS / Linux
# Colores para salida de terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Iniciando instalación de WhisperAudioScribe ===${NC}"

# 1. Comprobar Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Error: Python3 no está instalado.${NC}"
    echo -e "Por favor, descarga e instala Python 3 desde: https://www.python.org/downloads/"
    exit 1
else
    echo -e "${GREEN}[✓] Python3 detectado: $(python3 --version)${NC}"
fi

# 2. Comprobar Pip3
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}[!] pip3 no detectado. Intentando instalar con python...${NC}"
    python3 -m ensurepip --default-pip
    if [ $? -ne 0 ]; then
        echo -e "${RED}[!] No se pudo instalar pip de forma automática.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}[✓] pip3 detectado.${NC}"
fi

# 3. Comprobar e Instalar FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}[!] FFmpeg no está instalado. Es requerido para procesar audio.${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo -e "${BLUE}[*] Instalando FFmpeg con Homebrew...${NC}"
            brew install ffmpeg
        else
            echo -e "${RED}[!] Homebrew no está instalado.${NC}"
            echo -e "Instala Homebrew desde https://brew.sh e intenta de nuevo, o instala FFmpeg manualmente."
            exit 1
        fi
    elif command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        echo -e "${BLUE}[*] Instalando FFmpeg con apt...${NC}"
        sudo apt-get update && sudo apt-get install -y ffmpeg
    else
        echo -e "${RED}[!] No se pudo determinar el gestor de paquetes para instalar FFmpeg.${NC}"
        echo -e "Por favor, instala FFmpeg de forma manual."
        exit 1
    fi
else
    echo -e "${GREEN}[✓] FFmpeg detectado: $(ffmpeg -version | head -n 1)${NC}"
fi

# 4. Instalar dependencias de Python
echo -e "${BLUE}[*] Instalando librerías de Python (openai-whisper, yt-dlp, torch)...${NC}"
python3 -m pip install --upgrade pip
python3 -m pip install openai-whisper yt-dlp torch

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] Librerías de Python instaladas correctamente.${NC}"
else
    echo -e "${RED}[!] Error al instalar las librerías de Python.${NC}"
    exit 1
fi

# 5. Hacer ejecutable el script de transcripción
chmod +x transcribe.py
echo -e "${GREEN}[✓] Script 'transcribe.py' configurado como ejecutable.${NC}"

echo -e "\n${GREEN}===============================================${NC}"
echo -e "${GREEN}¡Instalación completada con éxito!${NC}"
echo -e "Puedes empezar a transcribir usando:"
echo -e "  ./transcribe.py \"Ruta/del/archivo\""
echo -e "${GREEN}===============================================${NC}"
