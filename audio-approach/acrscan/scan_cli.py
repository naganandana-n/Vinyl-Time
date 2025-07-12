# -*- coding: utf-8 -*-
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import subprocess
import threading
import queue
import json
import time
import os
import tempfile
import warnings
from collections import deque
from datetime import datetime

warnings.filterwarnings("ignore")

# === CONFIG ===
fs = 44100  # Sample rate
buffer_seconds = 5
hop_interval = 1  # How often to scan (in seconds)
channels = 1

buffer_samples = buffer_seconds * fs
audio_buffer = deque(maxlen=buffer_samples)
scan_queue = queue.Queue()

print("🚀 Real-time audio timestamp matching started (Sliding Window v2)")

# === 1. Continuous Audio Capture ===
def record_stream():
    def callback(indata, frames, time_info, status):
        audio_buffer.extend(indata[:, 0])  # Append to rolling buffer

    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
        while True:
            time.sleep(0.05)

# === 2. Export Every hop_interval Seconds ===
def buffer_export_loop():
    while True:
        if len(audio_buffer) >= buffer_samples:
            buf = np.array(audio_buffer, dtype=np.float32)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                write(tmp.name, fs, buf)
                scan_queue.put(tmp.name)
        time.sleep(hop_interval)

# === 3. ACRCloud Worker ===
def acrcloud_worker():
    last_title = None
    last_db_start = 0

    while True:
        filename = scan_queue.get()
        result_file = f"{filename}_filtered_music.json"

        # Run ACRCloud scan
        subprocess.run([
            "python", "main.py",
            "-t", filename,
            "-o", ".", "--format", "json",
            "-w", "--filter-results", "--split-results"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Parse result
        if os.path.exists(result_file):
            try:
                with open(result_file, "r") as f:
                    data = json.load(f)
                    result = data[0]
                    title = result.get("title", "Unknown")
                    artist = result.get("artists_names", "Unknown")
                    db_start = result.get("db_begin_time_offset_ms", 0) / 1000
                    db_end = result.get("db_end_time_offset_ms", 0) / 1000

                    def format_time(seconds):
                        return f"{int(seconds // 60)}:{int(seconds % 60):02d}"

                    if title != last_title or abs(db_start - last_db_start) > 2:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}]")
                        print(f"🎵 {title} by {artist}")
                        print(f"⏱️  Match: {format_time(db_start)} → {format_time(db_end)}\n")
                        last_title = title
                        last_db_start = db_start
            except Exception:
                print("⚠️ Could not parse ACRCloud result.")
            finally:
                os.remove(result_file)
        else:
            print("❌ No match")

        os.remove(filename)
        scan_queue.task_done()

# === Threaded Start ===
threading.Thread(target=record_stream, daemon=True).start()
threading.Thread(target=buffer_export_loop, daemon=True).start()
threading.Thread(target=acrcloud_worker, daemon=True).start()

# === Keep Alive ===
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Exiting.")