#!/usr/bin/env python3
import sys
import os
import argparse
import time
from datetime import datetime
import torch
import whisper
import yt_dlp

def format_timestamp(seconds):
    """Converts seconds to [HH:]MM:SS format"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

def download_audio_from_url(url, output_dir="."):
    """Downloads audio from a URL using yt-dlp and returns the filepath"""
    print(f"[*] Descargando audio de la URL: {url}...")
    
    # Configure yt-dlp to download best audio as mp3 or m4a
    outtmpl = os.path.join(output_dir, 'downloaded_audio_%(id)s.%(ext)s')
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # Since we converted to mp3, the extension changes
        base, _ = os.path.splitext(filename)
        mp3_filename = base + ".mp3"
        
        # Verify the file exists (yt-dlp prepends/appends or changes extensions sometimes)
        if os.path.exists(mp3_filename):
            return mp3_filename
        elif os.path.exists(filename):
            return filename
        else:
            # Try to search for the file in output_dir
            for f in os.listdir(output_dir):
                if info['id'] in f and f.endswith('.mp3'):
                    return os.path.join(output_dir, f)
            raise FileNotFoundError("No se pudo encontrar el archivo de audio descargado.")

def transcribe_audio(audio_path, model_name="small", language="es"):
    """Loads Whisper model and transcribes the audio"""
    device = "cpu"
    use_mps = torch.backends.mps.is_available()
    if use_mps:
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
        
    print(f"[*] Cargando modelo Whisper '{model_name}' en el dispositivo '{device}'...")
    start_time = time.time()
    
    try:
        model = whisper.load_model(model_name, device=device)
        print(f"[+] Modelo cargado en {time.time() - start_time:.2f} segundos.")
        print(f"[*] Transcribiendo '{audio_path}' (Idioma: {language}) en {device}...")
        start_transcribe = time.time()
        result = model.transcribe(
            audio_path, 
            language=language, 
            fp16=False # Force float32 to avoid warnings/errors on MPS/CPU
        )
    except Exception as e:
        if device == "mps":
            print(f"[!] Advertencia: Falló la transcripción usando MPS/GPU debido a: {e}")
            print(f"[*] Reintentando en CPU...")
            device = "cpu"
            start_time = time.time()
            model = whisper.load_model(model_name, device=device)
            print(f"[+] Modelo cargado en CPU en {time.time() - start_time:.2f} segundos.")
            print(f"[*] Transcribiendo '{audio_path}' (Idioma: {language}) en CPU...")
            start_transcribe = time.time()
            result = model.transcribe(audio_path, language=language, fp16=False)
        else:
            raise e
            
    elapsed = time.time() - start_transcribe
    print(f"[+] Transcripción completada en {elapsed:.2f} segundos.")
    return result


def save_to_markdown(result, source_name, output_path, model_name, language):
    """Saves transcription results into a formatted Markdown file"""
    print(f"[*] Guardando resultado en formato Markdown en: {output_path}...")
    
    title = os.path.basename(source_name)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate duration
    duration = 0
    if result.get("segments"):
        duration = result["segments"][-1]["end"]
    duration_str = format_timestamp(duration)
    
    # Format paragraphs nicely
    # We will group segments by pauses (> 2s) or length to make readable paragraphs.
    paragraphs = []
    current_paragraph = []
    last_end = 0.0
    paragraph_start_time = None
    
    for seg in result.get("segments", []):
        start = seg["start"]
        end = seg["end"]
        text = seg["text"].strip()
        
        if not text:
            continue
            
        if paragraph_start_time is None:
            paragraph_start_time = start
            
        # If there's a significant pause or the current paragraph is getting long, start a new one
        if (start - last_end > 2.5) or (len(current_paragraph) >= 5):
            if current_paragraph:
                ts = format_timestamp(paragraph_start_time)
                paragraphs.append(f"**[{ts}]** " + " ".join(current_paragraph))
                current_paragraph = []
            paragraph_start_time = start
            
        current_paragraph.append(text)
        last_end = end
        
    # Append the last paragraph
    if current_paragraph:
        ts = format_timestamp(paragraph_start_time or 0)
        paragraphs.append(f"**[{ts}]** " + " ".join(current_paragraph))
        
    markdown_content = f"""# Transcripción: {title}

| Detalle | Valor |
| --- | --- |
| **Origen** | `{source_name}` |
| **Fecha de transcripción** | {date_str} |
| **Modelo Whisper** | `{model_name}` |
| **Idioma original** | `{language}` |
| **Duración del audio** | {duration_str} |

## Contenido

"""
    
    for p in paragraphs:
        markdown_content += p + "\n\n"
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    print(f"[+] Transcripción guardada exitosamente.")

def main():
    parser = argparse.ArgumentParser(description="Transcribir archivos de audio/video locales o de URLs de forma sencilla usando OpenAI Whisper.")
    parser.add_argument("input", help="Ruta del archivo local (ej. video.mov, audio.mp3) o URL de video (ej. YouTube)")
    parser.add_argument("-m", "--model", default="small", choices=["tiny", "base", "small", "medium", "large"],
                        help="Modelo de Whisper a utilizar (por defecto: small)")
    parser.add_argument("-l", "--language", default="es", help="Idioma del audio (por defecto: es)")
    parser.add_argument("-o", "--output", help="Ruta del archivo markdown de salida (por defecto se autogenera)")
    
    args = parser.parse_args()
    
    input_source = args.input
    is_url = input_source.startswith("http://") or input_source.startswith("https://")
    temp_audio = None
    
    try:
        if is_url:
            temp_audio = download_audio_from_url(input_source)
            audio_to_transcribe = temp_audio
            source_display_name = input_source
        else:
            if not os.path.exists(input_source):
                print(f"[!] Error: El archivo '{input_source}' no existe.", file=sys.stderr)
                sys.exit(1)
            audio_to_transcribe = input_source
            source_display_name = os.path.abspath(input_source)
            
        # Determine output file path
        if args.output:
            output_file = args.output
        else:
            base_name = os.path.splitext(os.path.basename(input_source))[0]
            # Replace spaces and clean name for url
            if is_url:
                base_name = "transcripcion_url_" + base_name.replace("downloaded_audio_", "")
            else:
                base_name = "transcripcion_" + base_name
            output_file = os.path.join(os.path.dirname(os.path.abspath(input_source)) if not is_url else ".", f"{base_name}.md")
            
        # Run transcription
        result = transcribe_audio(audio_to_transcribe, model_name=args.model, language=args.language)
        
        # Save to markdown
        save_to_markdown(result, source_display_name, output_file, args.model, args.language)
        
    except Exception as e:
        print(f"[!] Ha ocurrido un error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        # Clean up temporary audio download if it was a URL
        if temp_audio and os.path.exists(temp_audio):
            try:
                os.remove(temp_audio)
                print(f"[*] Limpieza: Archivo temporal eliminado ({temp_audio})")
            except Exception as e:
                print(f"[!] No se pudo eliminar el archivo temporal: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
