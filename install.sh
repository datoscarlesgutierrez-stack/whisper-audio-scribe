#!/bin/bash

# =============================================================
# WhisperAudioScribe - Instalador automático (macOS / Linux)
# =============================================================
# Instala:  uv  +  FFmpeg
# uv gestiona Python y todas las dependencias de Python.
# Una vez instalado, ejecutar:
#   uv run transcribe.py "ruta/del/video.mp4"
# =============================================================

set -e  # Salir en caso de error

# Colores
GREEN='\033[0;32m'; BLUE='\033[0;34m'
YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

info()  { echo -e "${BLUE}[*] $1${NC}"; }
ok()    { echo -e "${GREEN}[✓] $1${NC}"; }
warn()  { echo -e "${YELLOW}[!] $1${NC}"; }
err()   { echo -e "${RED}[✗] $1${NC}"; exit 1; }

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════╗"
echo "║   WhisperAudioScribe — Instalador (Unix)     ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# Detectar OS
OS="unknown"
[[ "$OSTYPE" == "darwin"* ]]                  && OS="macos"
command -v apt-get &>/dev/null                 && OS="debian"
(command -v dnf &>/dev/null || command -v yum &>/dev/null) && OS="redhat"

info "Sistema detectado: ${OS}"

# -----------------------------------------------------------
# PASO 1 — Instalar uv
# -----------------------------------------------------------
if command -v uv &>/dev/null; then
    ok "uv ya está instalado: $(uv --version)"
else
    info "Instalando uv (gestor de Python y paquetes de Astral)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Cargar uv en la sesión actual
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    source "$HOME/.local/bin/env" 2>/dev/null || true

    if ! command -v uv &>/dev/null; then
        err "uv no se encontró tras la instalación. Reinicia la terminal y vuelve a ejecutar el script."
    fi
    ok "uv instalado: $(uv --version)"
fi

# -----------------------------------------------------------
# PASO 2 — Instalar Python 3.12 via uv
# -----------------------------------------------------------
info "Asegurando Python 3.12 con uv..."
uv python install 3.12 --quiet
ok "Python listo: $(uv run python --version 2>&1)"

# -----------------------------------------------------------
# PASO 3 — Instalar FFmpeg (único componente de sistema)
# -----------------------------------------------------------
if command -v ffmpeg &>/dev/null; then
    ok "FFmpeg ya está instalado: $(ffmpeg -version 2>&1 | head -1)"
else
    warn "FFmpeg no encontrado. Instalando..."

    if [[ "$OS" == "macos" ]]; then
        # Instalar Homebrew si no existe
        if ! command -v brew &>/dev/null; then
            info "Instalando Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            # Añadir brew al PATH (Apple Silicon vs Intel)
            [[ -f /opt/homebrew/bin/brew ]] && eval "$(/opt/homebrew/bin/brew shellenv)"
            [[ -f /usr/local/bin/brew    ]] && eval "$(/usr/local/bin/brew shellenv)"
            ok "Homebrew instalado."
        fi
        brew install ffmpeg

    elif [[ "$OS" == "debian" ]]; then
        sudo apt-get update -y -q
        sudo apt-get install -y -q ffmpeg

    elif [[ "$OS" == "redhat" ]]; then
        # Necesita RPM Fusion para FFmpeg en Fedora/RHEL
        if command -v dnf &>/dev/null; then
            sudo dnf install -y \
                "https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm" \
                2>/dev/null || true
            sudo dnf install -y ffmpeg
        else
            sudo yum install -y epel-release 2>/dev/null || true
            sudo yum install -y ffmpeg || err "No se pudo instalar FFmpeg. Instálalo desde https://ffmpeg.org"
        fi
    else
        err "Sistema no reconocido. Instala FFmpeg manualmente desde https://ffmpeg.org"
    fi

    ok "FFmpeg instalado: $(ffmpeg -version 2>&1 | head -1)"
fi

# -----------------------------------------------------------
# PASO 4 — Warm-up: pre-descargar dependencias de Python
# -----------------------------------------------------------
info "Pre-descargando dependencias de Python con uv (openai-whisper, yt-dlp, torch)..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
uv run --no-project "$SCRIPT_DIR/transcribe.py" --help &>/dev/null || true
ok "Dependencias de Python listas."

# -----------------------------------------------------------
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      ¡Instalación completada con éxito!      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo "Cómo transcribir:"
echo -e "  ${BLUE}uv run transcribe.py \"ruta/del/video.mp4\"${NC}"
echo -e "  ${BLUE}uv run transcribe.py \"https://youtube.com/watch?v=...\"${NC}"
echo -e "  ${BLUE}uv run transcribe.py \"video.mp4\" --model medium --language es${NC}"
echo ""
