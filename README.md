# WhisperAudioScribe

> Transcriptor local de audio y vídeo con **OpenAI Whisper** — compatible con macOS, Linux y Windows.

Convierte cualquier vídeo o audio local (o una URL de YouTube) en un documento **Markdown con marcas de tiempo**, todo corriendo en tu propia máquina sin enviar datos a ningún servidor.

---

## ⚡ Inicio rápido (con uv)

Este proyecto usa **[uv](https://docs.astral.sh/uv/)** para gestionar Python y todas sus dependencias. No necesitas instalar Python ni pip manualmente.

### 1. Clonar el repositorio

```bash
git clone https://github.com/datoscarlesgutierrez-stack/whisper-audio-scribe.git
cd whisper-audio-scribe
```

### 2. Ejecutar el instalador

#### macOS y Linux:
```bash
chmod +x install.sh
./install.sh
```

#### Windows (PowerShell como Administrador):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install.ps1
```

Los instaladores gestionan **todo** automáticamente:
- Instalan **uv** (gestor de Python y paquetes de Astral)
- Instalan **Python 3.12** vía uv
- Instalan **FFmpeg** (el único componente de sistema necesario)
- Pre-descargan todas las dependencias de Python

### 3. Transcribir

```bash
# Archivo local
uv run transcribe.py "Videos/mi_grabacion.mp4"

# URL de YouTube u otra plataforma
uv run transcribe.py "https://www.youtube.com/watch?v=..."

# Con opciones avanzadas
uv run transcribe.py "video.mp4" --model medium --language en -o resultado.md
```

> La primera ejecución descargará el modelo Whisper (~250 MB para `small`). Las siguientes son instantáneas.

---

## Características

| | |
|---|---|
| 🎙️ **OpenAI Whisper oficial** | Motor de transcripción local sin API ni costes |
| ⚡ **Gestión con uv** | Python y paquetes aislados, sin contaminar el sistema |
| 🔗 **URLs de vídeo** | YouTube, Vimeo y cualquier plataforma via `yt-dlp` |
| 🌍 **Multiidioma** | Español, inglés, francés y 99 idiomas más |
| 📝 **Salida Markdown** | Párrafos estructurados con marcas de tiempo `[MM:SS]` |
| 🖥️ **GPU automática** | Usa MPS (Apple Silicon), CUDA (NVIDIA) o CPU según el hardware |

---

## Opciones del script

```
uv run transcribe.py <INPUT> [opciones]

Argumentos:
  INPUT               Ruta a fichero local o URL de vídeo/audio

Opciones:
  -m, --model         Modelo Whisper: tiny, base, small (por defecto), medium, large
  -l, --language      Código de idioma (por defecto: es). Ej: en, fr, de, ja
  -o, --output        Ruta del fichero Markdown de salida (se autogenera si no se indica)
```

---

## Modelos disponibles

| Modelo | Parámetros | RAM aprox. | Velocidad | Precisión |
|--------|-----------|-----------|-----------|-----------|
| `tiny`   | 39M  | ~1 GB | ~32x | Básica |
| `base`   | 74M  | ~1 GB | ~16x | Buena |
| `small`  | 244M | ~2 GB | ~6x  | ⭐ Equilibrio ideal (por defecto) |
| `medium` | 769M | ~5 GB | ~2x  | Excelente |
| `large`  | 1550M| ~10 GB| ~1x  | Máxima precisión |

---

## Cómo funciona `uv run`

`transcribe.py` incluye metadatos **PEP 723** que indican a `uv` qué paquetes necesita. Cuando ejecutas `uv run transcribe.py`, uv:

1. Lee los metadatos del propio script
2. Crea un entorno virtual aislado si no existe
3. Instala las dependencias necesarias
4. Ejecuta el script

No tienes que tocar `pip`, `venv` ni `conda`. Si añades `uv` a tu PATH tras el instalador, simplemente funciona.

---

## Requisito de sistema: FFmpeg

FFmpeg es el único componente que no instala uv (es un binario de sistema, no un paquete Python). El instalador lo gestiona automáticamente. Si necesitas instalarlo a mano:

- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **Windows**: `winget install Gyan.FFmpeg`

---

## Licencia

MIT — úsalo, modifícalo y compártelo libremente.
