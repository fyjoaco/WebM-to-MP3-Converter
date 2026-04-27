import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog, ttk
from pydub import AudioSegment
import os
import threading
import shutil
import tempfile

# 🔥 CONFIGURAR FFMPEG (EN RAÍZ)
base_dir = os.path.dirname(os.path.abspath(__file__))

ffmpeg_path = os.path.join(base_dir, "ffmpeg.exe")
ffprobe_path = os.path.join(base_dir, "ffprobe.exe")

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# 🔥 MUY IMPORTANTE (fix definitivo pydub)
os.environ["PATH"] += os.pathsep + base_dir

print("FFmpeg:", ffmpeg_path)
print("Existe ffmpeg:", os.path.exists(ffmpeg_path))
print("Existe ffprobe:", os.path.exists(ffprobe_path))


# 🔥 FUNCIÓN PRINCIPAL
def convertir_archivos(files):
    # arregla drag & drop
    if isinstance(files, str):
        files = root.tk.splitlist(files)

    # limpiar rutas
    files = [f.strip("{}") for f in files if f.lower().endswith(".webm")]

    print("Archivos detectados:", files)

    total = len(files)
    if total == 0:
        return

    progress["maximum"] = total
    progress["value"] = 0

    temp_dir = tempfile.mkdtemp()

    for i, file in enumerate(files, start=1):
        try:
            temp_input = os.path.join(temp_dir, f"input_{i}.webm")
            temp_output = os.path.join(temp_dir, f"output_{i}.mp3")

            shutil.copy(file, temp_input)

            audio = AudioSegment.from_file(temp_input, format="webm")
            audio.export(temp_output, format="mp3", bitrate="192k")

            final_output = os.path.splitext(file)[0] + ".mp3"
            shutil.move(temp_output, final_output)

        except Exception as e:
            print(f"Error con {file}: {e}")

        progress["value"] = i
        status_label.config(text=f"{i}/{total} convertidos")
        root.update_idletasks()

    status_label.config(text="Conversión completada 🚀")


def iniciar_conversion(files):
    hilo = threading.Thread(target=convertir_archivos, args=(files,))
    hilo.start()


def drop(event):
    iniciar_conversion(event.data)


def seleccionar_archivos():
    files = filedialog.askopenfilenames(filetypes=[("WebM files", "*.webm")])
    iniciar_conversion(files)


# 🖥️ UI
root = TkinterDnD.Tk()
root.title("Convertidor WebM a MP3")
root.geometry("400x250")

label = tk.Label(root, text="Arrastrá archivos .webm acá", bg="lightgray")
label.pack(expand=True, fill="both", padx=10, pady=10)

label.drop_target_register(DND_FILES)
label.dnd_bind("<<Drop>>", drop)

btn = tk.Button(root, text="Seleccionar archivos", command=seleccionar_archivos)
btn.pack(pady=5)

progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=10)

status_label = tk.Label(root, text="Esperando archivos...")
status_label.pack()

root.mainloop()