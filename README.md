# WhisperAudioScribe: Transcriptor Local de Audio y Video con OpenAI Whisper

Este proyecto contiene un script de Python interactivo (`transcribe.py`) para transcribir archivos de audio y video locales o directamente desde URLs de internet (como YouTube) usando la biblioteca oficial de **OpenAI Whisper**.

La transcripción se procesa localmente y el resultado se guarda en un documento de texto con formato **Markdown (`.md`)** e incluye marcas de tiempo estructuradas de forma legible.

---

## Características

- 🎙️ **OpenAI Whisper Oficial**: Usa el motor oficial de OpenAI corriendo en local.
- ⚡ **Aceleración por Hardware**: Intenta usar la GPU automáticamente (`mps` en macOS, `cuda` en Windows con tarjetas NVIDIA) con fallback automático a CPU en caso de incompatibilidad.
- 🔗 **Soporte de URLs**: Permite transcribir vídeos de YouTube u otras plataformas pasando directamente el enlace (gracias a `yt-dlp`).
- 📝 **Salida Markdown**: Estructura el texto en párrafos conversacionales limpios con marcas de tiempo formateadas `[MM:SS]` o `[HH:MM:SS]`.
- ⚙️ **Configurable**: Permite elegir la precisión (modelos: `tiny`, `base`, `small`, `medium`, `large`) y el idioma.

---

## Instalación

Puedes realizar la instalación de forma automatizada mediante los scripts incluidos, o seguir el método manual.

### 🚀 Método 1: Instalación Automatizada (Recomendado)

#### En macOS (y Linux):
Abre tu terminal y ejecuta:
```bash
./install.sh
```
*(El script comprobará Python3, instalará FFmpeg a través de Homebrew si falta, e instalará todas las dependencias de Python necesarias).*

#### En Windows:
Abre PowerShell como Administrador y ejecuta:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install.ps1
```
*(El script comprobará Python, intentará instalar FFmpeg automáticamente a través de Windows Package Manager `winget` si falta, e instalará todas las dependencias necesarias).*

---

### 🛠️ Método 2: Instalación Manual

Si prefieres realizar los pasos por ti mismo:

1. **Instalar dependencias del sistema (FFmpeg)**:
   - **macOS** (con Homebrew): `brew install ffmpeg`
   - **Windows** (con Chocolatey): `choco install ffmpeg` (o descárgalo de https://ffmpeg.org y añádelo al PATH)

2. **Instalar librerías de Python**:
   ```bash
   pip3 install openai-whisper yt-dlp torch
   ```

---

## Cómo usar el script

El script se puede ejecutar pasando la ruta del archivo o una URL. Por defecto, utiliza el modelo `small` y el idioma español (`es`).

### 1. Transcribir un archivo local (video o audio)
```bash
python3 transcribe.py "Videos/2026-06-04 12-28-46.mov"
```
*Esto generará un archivo `transcripcion_2026-06-04 12-28-46.md` en el mismo directorio del video.*

### 2. Transcribir a partir de una URL (YouTube, etc.)
```bash
python3 transcribe.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```
*Descargará el audio temporalmente, lo transcribirá, y guardará el resultado en un archivo `.md`.*

### Opciones avanzadas:

- **Elegir modelo (`-m` / `--model`)**: Puedes cambiar el modelo para mayor velocidad (`tiny`, `base`) o mayor precisión (`medium`, `large`). El valor por defecto es `small`.
- **Elegir idioma (`-l` / `--language`)**: Indicar el código de idioma del audio (ej. `en` para inglés, `fr` para francés). Por defecto es `es`.
- **Definir archivo de salida (`-o` / `--output`)**: Indicar una ruta específica para el archivo Markdown de salida.

#### Ejemplo de uso avanzado:
```bash
python3 transcribe.py "Videos/mi_video.mp4" -m medium -l es -o "Resultados/transcripcion_detallada.md"
```

---

## Modelos Disponibles

| Nombre | Parámetros | RAM Requerida | Velocidad relativa | Precisión general |
| --- | --- | --- | --- | --- |
| `tiny` | 39M | ~1 GB | ~32x | Básica (útil para pruebas rápidas) |
| `base` | 74M | ~1 GB | ~16x | Buena |
| `small` | 244M | ~2 GB | ~6x | Muy buena (equilibrio ideal) |
| `medium` | 769M | ~5 GB | ~2x | Excelente |
| `large` | 1550M | ~10 GB | ~1x | Máxima precisión (más lenta) |
