#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "openai-whisper",
#   "yt-dlp",
#   "torch",
#   "gradio>=4.0",
# ]
# ///

import os, re, shutil, tempfile
from datetime import datetime
from pathlib import Path

import torch, whisper, yt_dlp, gradio as gr

# ── helpers ──────────────────────────────────────────────────

LANGUAGES = {
    "Español": "es", "English": "en", "Français": "fr",
    "Deutsch": "de", "Italiano": "it", "Português": "pt",
    "日本語": "ja", "中文": "zh", "Русский": "ru", "Auto": None,
}
MODELS = [
    ("tiny (muy rápido)", "tiny"),
    ("base (rápido)", "base"),
    ("small (equilibrio ideal)", "small"),
    ("medium (preciso)", "medium"),
    ("large (máxima precisión)", "large")
]

def fmt_ts(s):
    h,m,sec = int(s//3600), int((s%3600)//60), int(s%60)
    return f"{h:02d}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"

def strip_md(text):
    t = re.sub(r'\*\*\[[\d:]+\]\*\*\s*', '', text)
    return re.sub(r'\n{3,}', '\n\n', t).strip()

def build_md(result, source, model_name, lang):
    segs = result.get("segments", [])
    duration = segs[-1]["end"] if segs else 0
    paras, cur, last_end, t0 = [], [], 0.0, None
    for seg in segs:
        txt = seg["text"].strip()
        if not txt: continue
        if t0 is None: t0 = seg["start"]
        if (seg["start"] - last_end > 2.5) or len(cur) >= 5:
            if cur: paras.append(f"**[{fmt_ts(t0)}]** " + " ".join(cur))
            cur, t0 = [], seg["start"]
        cur.append(txt); last_end = seg["end"]
    if cur: paras.append(f"**[{fmt_ts(t0 or 0)}]** " + " ".join(cur))

    content_md = ""
    for p in paras: content_md += p + "\n\n"
    content_md = content_md.strip()

    md = f"# {Path(source).name}\n\n"
    md += f"| | |\n|---|---|\n"
    md += f"| **Herramienta** | WhisperAudioScribe |\n"
    md += f"| **Fecha** | {datetime.now().strftime('%Y-%m-%d %H:%M')} |\n"
    md += f"| **Modelo** | `{model_name}` |\n"
    md += f"| **Duración** | {fmt_ts(duration)} |\n\n---\n\n"
    md += content_md
    return md, content_md

def detect_device():
    if torch.backends.mps.is_available(): return "mps"
    if torch.cuda.is_available(): return "cuda"
    return "cpu"

def run_whisper(audio_path, model_name, language, progress):
    device = detect_device()
    progress(0.15, desc=f"Cargando modelo '{model_name}'…")
    try:
        model = whisper.load_model(model_name, device=device)
    except Exception:
        device = "cpu"
        model = whisper.load_model(model_name, device="cpu")
    progress(0.45, desc="Transcribiendo…")
    return model.transcribe(audio_path, language=language, fp16=False)

# ── gradio handlers ───────────────────────────────────────────

def transcribe_file(file, model_name, lang_label, progress=gr.Progress()):
    if file is None: return "⚠️ Sube un archivo primero.", "", "", None
    lang = LANGUAGES[lang_label]
    progress(0.05, desc="Leyendo archivo…")
    result = run_whisper(file, model_name, lang, progress)
    md, content_md = build_md(result, file, model_name, lang_label)
    plain = strip_md(content_md)
    out = Path(tempfile.mktemp(suffix=".md"))
    out.write_text(md, encoding="utf-8")
    progress(1.0, desc="¡Listo!")
    return md, content_md, plain, str(out)

def transcribe_url(url, model_name, lang_label, progress=gr.Progress()):
    if not url.strip(): return "⚠️ Introduce una URL válida.", "", "", None
    lang = LANGUAGES[lang_label]
    tmp = tempfile.mkdtemp()
    try:
        progress(0.05, desc="Descargando audio…")
        outtmpl = os.path.join(tmp, "audio_%(id)s.%(ext)s")
        with yt_dlp.YoutubeDL({"format":"bestaudio/best","outtmpl":outtmpl,
            "postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"192"}],
            "quiet":True}) as ydl:
            info = ydl.extract_info(url.strip(), download=True)
            base = ydl.prepare_filename(info)
            audio = Path(base).with_suffix(".mp3")
            if not audio.exists():
                audio = next((f for f in Path(tmp).iterdir() if info["id"] in f.name), None)
        result = run_whisper(str(audio), model_name, lang, progress)
        md, content_md = build_md(result, url.strip(), model_name, lang_label)
        plain = strip_md(content_md)
        out = Path(tempfile.mktemp(suffix=".md"))
        out.write_text(md, encoding="utf-8")
        progress(1.0, desc="¡Listo!")
        return md, content_md, plain, str(out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# ── SVG divider ───────────────────────────────────────────────

DIVIDER = '<hr style="border: none; border-top: 2px dashed #000; margin: 24px 0 20px;" />'

# ── CSS ───────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { font-family: 'Montserrat', sans-serif !important; }

/* ── container ── */
.gradio-container {
  background: #fff !important;
  max-width: 820px !important;
  margin: 0 auto !important;
  padding: 0 24px !important;
}

/* ── typography ── */
#ws-title-container {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 16px !important;
  margin: 2rem 0 0.5rem !important;
}

#ws-title {
  font-size: 2.2rem; font-weight: 700; letter-spacing: -0.03em;
  color: #000; margin: 0 !important;
  line-height: 1.1;
}
#ws-sub {
  font-size: 0.75rem; font-weight: 400; color: #666;
  text-align: center; letter-spacing: 0.08em; text-transform: uppercase;
  margin: 0 0 0.5rem;
}

/* ── settings row: dropdowns side by side, same height ── */
#settings-row {
  display: grid !important;
  grid-template-columns: 7fr 4fr !important;
  gap: 16px !important;
  align-items: start !important;
  margin-bottom: 0 !important;
}
#settings-row > * { width: 100% !important; margin: 0 !important; }

/* ── block reset ── */
.block {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

/* ── labels ── */
label > span:first-child,
.block > label > span {
  font-weight: 600 !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  color: #000 !important;
  margin-bottom: 6px !important;
  display: block !important;
}

/* ── all inputs / selects / textareas ── */
input, select, textarea,
.svelte-1gfkn6j, .wrap.svelte-1gfkn6j {
  border: 2px solid #000 !important;
  border-radius: 4px 8px 3px 6px / 7px 3px 6px 4px !important; /* Hand-drawn look */
  background: #fff !important;
  color: #000 !important;
  font-size: 0.88rem !important;
}

/* ── dropdown list ── */
.options.svelte-1vc5g13, ul.options {
  border: 2px solid #000 !important;
  border-radius: 0 !important;
  background: #fff !important;
}
.item.svelte-1vc5g13:hover { background: #000 !important; color: #fff !important; }

/* ── tabs ── */
.tab-nav { border-bottom: 2px solid #000 !important; margin-bottom: 16px !important; }
.tab-nav button {
  border-radius: 0 !important; font-weight: 600 !important;
  font-size: 0.75rem !important; letter-spacing: 0.07em !important;
  text-transform: uppercase !important; color: #888 !important;
  border: none !important; border-bottom: 2.5px solid transparent !important;
  padding: 10px 20px !important; background: transparent !important;
}
.tab-nav button.selected {
  color: #000 !important; border-bottom: 2.5px solid #000 !important;
}

/* ── upload zone ── */
.upload-zone {
  --block-border-width: 2px !important;
  --border-color-primary: #000 !important;
}
.upload-container, .file-preview, [data-testid="file-upload"], .upload-zone > div > div, .upload-zone button {
  border: 2px dashed #000 !important;
  border-radius: 6px 4px 8px 5px / 5px 8px 4px 6px !important;
  background: #fff !important;
}

/* ── primary buttons (hand-drawn rotulador style) ── */
#btn-transcribe-file button, #btn-transcribe-url button {
  background: #000 !important; color: #fff !important;
  border: 2.5px solid #000 !important;
  border-radius: 5px 12px 4px 10px / 10px 4px 12px 5px !important;
  font-weight: 700 !important; font-size: 0.78rem !important;
  letter-spacing: 0.12em !important; text-transform: uppercase !important;
  padding: 13px 28px !important;
  box-shadow: 3px 3px 0px #000 !important;
  transition: all 0.1s ease-in-out !important;
  width: 100% !important;
}
#btn-transcribe-file button:hover, #btn-transcribe-url button:hover {
  background: #fff !important; color: #000 !important;
  box-shadow: 0px 0px 0px #000 !important;
  transform: translate(3px, 3px) !important;
}

/* ── action buttons row ── */
#action-row {
  display: flex !important;
  justify-content: center !important;
  flex-wrap: wrap !important;
  gap: 16px !important;
  margin-top: 12px !important;
}
#action-row > * { 
  margin: 0 !important; 
  flex: 0 1 auto !important; 
  min-width: 220px !important; 
}

#btn-copy-plain button, #btn-copy-md button {
  background: #fff !important; color: #000 !important;
  border: 2px solid #000 !important;
  border-radius: 6px 10px 5px 9px / 9px 5px 10px 6px !important;
  font-weight: 600 !important; font-size: 0.72rem !important;
  letter-spacing: 0.1em !important; text-transform: uppercase !important;
  padding: 11px 16px !important;
  box-shadow: 3px 3px 0px #000 !important;
  transition: all 0.1s ease-in-out !important;
  width: 100% !important;
}
#btn-copy-plain button:hover, #btn-copy-md button:hover {
  background: #000 !important; color: #fff !important;
  box-shadow: 0px 0px 0px #000 !important;
  transform: translate(3px, 3px) !important;
}

/* ── markdown output ── */
#transcript-display {
  border: 2px solid #000 !important;
  border-radius: 8px 6px 9px 5px / 5px 9px 6px 8px !important;
  padding: 24px 28px !important; min-height: 300px;
}
#transcript-display .prose h1 {
  font-size: 1rem !important; font-weight: 700 !important;
  letter-spacing: -0.01em !important;
  border-bottom: 2px solid #000; padding-bottom: 6px; margin-bottom: 12px;
}
#transcript-display .prose table { font-size: 0.8rem !important; border-collapse: collapse; }
#transcript-display .prose td, #transcript-display .prose th {
  border: 1.5px solid #000 !important; padding: 4px 10px !important;
}
#transcript-display .prose p {
  font-size: 0.9rem !important; line-height: 1.8 !important; color: #111;
}

/* ── misc ── */
footer, .footer { display: none !important; }
.block { padding: 0 !important; }

/* ── hide copy helpers ── */
#hidden-md, #hidden-plain { display: none !important; }
"""

JS_COPY_PLAIN = """() => {
    const el = document.querySelector('#hidden-plain textarea');
    if (el && el.value) {
        navigator.clipboard.writeText(el.value).then(() => {
            const b = document.querySelector('#btn-copy-plain button');
            if(b){ const orig=b.textContent; b.textContent='✓ Copiado'; setTimeout(()=>b.textContent=orig,1800); }
        });
    }
}"""

JS_COPY_MD = """() => {
    const el = document.querySelector('#hidden-md textarea');
    if (el && el.value) {
        navigator.clipboard.writeText(el.value).then(() => {
            const b = document.querySelector('#btn-copy-md button');
            if(b){ const orig=b.textContent; b.textContent='✓ Copiado'; setTimeout(()=>b.textContent=orig,1800); }
        });
    }
}"""

# ── UI ────────────────────────────────────────────────────────

bw_theme = gr.themes.Base(
    primary_hue="neutral",
    secondary_hue="neutral",
    neutral_hue="neutral"
)

with gr.Blocks(css=CSS, theme=bw_theme, title="WhisperAudioScribe") as demo:

    # Hidden textboxes readable by JS via DOM querySelector (Standard multiline textareas)
    hidden_md    = gr.Textbox(visible=True, elem_id="hidden-md")
    hidden_plain = gr.Textbox(visible=True, elem_id="hidden-plain")

    gr.HTML('''
    <div id="ws-title-container">
        <svg width="48" height="48" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Pluma estilizada BW -->
            <path d="M 80 15 C 80 15 70 30 50 45 C 45 48 35 55 30 65 L 28 75 L 38 72 C 45 68 55 60 65 50 C 80 35 85 20 85 20 Z" stroke="#000" stroke-width="4" fill="#fff" stroke-linejoin="round"/>
            <path d="M 50 45 L 60 55" stroke="#000" stroke-width="4" stroke-linecap="round"/>
            <path d="M 60 35 L 70 45" stroke="#000" stroke-width="4" stroke-linecap="round"/>
            <!-- Punta de pluma negra -->
            <path d="M 30 65 L 20 85 L 25 85 Z" fill="#000"/>
            <!-- T caligráfica negra gruesa -->
            <path d="M 10 85 L 30 85 M 20 85 L 20 100" stroke="#000" stroke-width="6" stroke-linecap="square"/>
        </svg>
        <h1 id="ws-title">WhisperAudioScribe</h1>
    </div>
    ''')
    gr.HTML('<p id="ws-sub">Transcripción local · OpenAI Whisper · Sin enviar datos a servidores</p>')
    gr.HTML(DIVIDER)

    with gr.Row():
        with gr.Column(scale=1, min_width=50):
            gr.HTML('<div style="font-size:3.5rem; font-weight:700; color:#000; line-height:1; margin-top:0;">1</div>')
        with gr.Column(scale=15):
            with gr.Row(elem_id="settings-row"):
                model_dd = gr.Dropdown(MODELS, value="small", label="Modelo", scale=1)
                lang_dd  = gr.Dropdown(list(LANGUAGES.keys()), value="Español",
                                       label="Idioma del audio", scale=1)

    gr.HTML(DIVIDER)

    with gr.Row():
        with gr.Column(scale=1, min_width=50):
            gr.HTML('<div style="font-size:3.5rem; font-weight:700; color:#000; line-height:1; margin-top:45px;">2</div>')
        with gr.Column(scale=15):
            with gr.Tabs():
                with gr.TabItem("Archivo local"):
                    file_in  = gr.File(label="Arrastra tu vídeo o audio aquí",
                                       file_types=["video","audio"], type="filepath",
                                       elem_classes="upload-zone")
                    btn_file = gr.Button("Transcribir archivo →",
                                         variant="primary", elem_id="btn-transcribe-file")

                with gr.TabItem("URL — YouTube / Vimeo"):
                    url_in   = gr.Textbox(label="URL del vídeo",
                                          placeholder="https://www.youtube.com/watch?v=…")
                    btn_url  = gr.Button("Transcribir URL →",
                                         variant="primary", elem_id="btn-transcribe-url")

    gr.HTML(DIVIDER)

    # Output
    with gr.Row():
        with gr.Column(scale=1, min_width=50):
            gr.HTML('<div style="font-size:3.5rem; font-weight:700; color:#000; line-height:1; margin-top:20px;">3</div>')
        with gr.Column(scale=15):
            transcript_out = gr.Markdown(
                value="*La transcripción aparecerá aquí…*",
                elem_id="transcript-display",
                height=480,
            )

    gr.HTML(DIVIDER)

    # Paso 4: Actions
    with gr.Row():
        with gr.Column(scale=1, min_width=50):
            gr.HTML('<div style="font-size:3.5rem; font-weight:700; color:#000; line-height:1; margin-top:0;">4</div>')
        with gr.Column(scale=15):
            with gr.Row(elem_id="action-row"):
                btn_copy_plain = gr.Button("Copiar texto",    elem_id="btn-copy-plain")
                btn_copy_md    = gr.Button("Copiar Markdown", elem_id="btn-copy-md")
                download_out   = gr.File(label="Descargar .md", visible=False)

    gr.HTML(DIVIDER)
    gr.HTML('<p style="text-align:center;font-size:0.75rem;color:#888;letter-spacing:0.06em;text-transform:uppercase">'
            '100% local · <a href="https://github.com/datoscarlesgutierrez-stack/whisper-audio-scribe" '
            'style="color:#000">GitHub ↗</a></p>')

    # ── wire-up ──────────────────────────────────────────────

    def on_done(md, md_raw, plain, fpath):
        visible_dl = fpath is not None
        return md, md_raw, plain, gr.update(value=fpath, visible=visible_dl)

    btn_file.click(
        fn=transcribe_file,
        inputs=[file_in, model_dd, lang_dd],
        outputs=[transcript_out, hidden_md, hidden_plain, download_out],
        show_progress="full",
    )

    btn_url.click(
        fn=transcribe_url,
        inputs=[url_in, model_dd, lang_dd],
        outputs=[transcript_out, hidden_md, hidden_plain, download_out],
        show_progress="full",
    )

    # Copy buttons — JS reads from hidden DOM textareas
    btn_copy_plain.click(fn=None, inputs=None, outputs=None, js=JS_COPY_PLAIN)
    btn_copy_md.click(fn=None, inputs=None, outputs=None, js=JS_COPY_MD)

if __name__ == "__main__":
    demo.launch(inbrowser=True, server_name="0.0.0.0", server_port=7860)
