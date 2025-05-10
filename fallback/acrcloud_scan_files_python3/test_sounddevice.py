# -*- coding: utf-8 -*-

'''
import sounddevice as sd
from scipy.io.wavfile import write

fs = 44100  # Sample rate
seconds = 5

print("Recording...")
recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
sd.wait()
write("test.wav", fs, recording)
print("Done!")
'''

# 5 seconds recording - concurrent version

'''
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess
import time
import json
import os

# SETTINGS
fs = 44100
duration = 5  # seconds
channels = 1  # Use mono for mic input (change to 2 if needed)

print("Mic-based ACRCloud fingerprint loop started")

while True:
    print("Recording 5s audio...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=channels)
    sd.wait()
    write("snippet.wav", fs, audio)

    print("Running ACRCloud scan...")
    subprocess.run([
        "python", "main.py",
        "-t", "snippet.wav",
        "-o", ".",  # output to current folder
        "--format", "json",
        "-w", "--filter-results", "--split-results"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    result_file = "snippet.wav_filtered_music.json"

    if os.path.exists(result_file):
        with open(result_file, "r") as f:
            try:
                data = json.load(f)
                result = data[0]
                title = result.get("title", "Unknown")
                artist = result.get("artists_names", "Unknown")
                db_start = result.get("db_begin_time_offset_ms", 0) / 1000
                db_end = result.get("db_end_time_offset_ms", 0) / 1000

                print(f" {title} by {artist}")
                print(f" Match: {db_start:.2f}s → {db_end:.2f}s\n")
            except Exception as e:
                print("Failed to parse results:", e)
    else:
        print("No result from ACRCloud")

    time.sleep(1)  # short pause to avoid overlap
'''


# 5 sec recording - but SLIDING BUFFER, to make it more continous

'''
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import subprocess
import threading
import queue
import json
import time
import os
import warnings
from collections import deque

warnings.filterwarnings("ignore")

# CONFIG
fs = 44100  # 44.1 kHz sample rate
buffer_seconds = 5
hop_interval = 1  # Run ACR scan every 1s
channels = 1

buffer_samples = buffer_seconds * fs
hop_samples = hop_interval * fs
audio_buffer = deque(maxlen=buffer_samples)
scan_queue = queue.Queue()

print("Real-time audio timestamp matching started (press Ctrl+C to stop) - SLIDING WINDOW")

def record_stream():
    def callback(indata, frames, time_info, status):
        audio_buffer.extend(indata[:, 0])

    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
        while True:
            time.sleep(0.1)

def buffer_export_loop():
    chunk_counter = 0
    while True:
        if len(audio_buffer) >= buffer_samples:
            buf = np.array(audio_buffer, dtype=np.float32)
            filename = f"snippet_{chunk_counter}.wav"
            write(filename, fs, buf)
            scan_queue.put(filename)
            chunk_counter += 1
        time.sleep(hop_interval)

def acrcloud_worker():
    last_title = None
    while True:
        filename = scan_queue.get()
        result_file = f"{filename}_filtered_music.json"

        # Clean up before scan
        if os.path.exists(result_file):
            os.remove(result_file)

        subprocess.run([
            "python", "main.py",
            "-t", filename,
            "-o", ".", "--format", "json",
            "-w", "--filter-results", "--split-results"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(result_file):
            try:
                with open(result_file, "r") as f:
                    data = json.load(f)
                    result = data[0]
                    title = result.get("title", "Unknown")
                    artist = result.get("artists_names", "Unknown")
                    db_start = result.get("db_begin_time_offset_ms", 0) / 1000
                    db_end = result.get("db_end_time_offset_ms", 0) / 1000

                    if title != last_title or abs(db_start - db_end) > 1:
                        def format_time(seconds):
                            minutes = int(seconds // 60)
                            seconds = int(seconds % 60)
                            return f"{minutes}:{seconds:02d}"
                        start_formatted = format_time(db_start)
                        end_formatted = format_time(db_end)
                        print(f"{title} by {artist}")
                        print(f"Match: {start_formatted} → {end_formatted}\n")
                        last_title = title
            except Exception:
                print(" Could not parse ACRCloud result.")
        else:
            print(" No match")

        scan_queue.task_done()
        os.remove(filename)

# Launch threads
threading.Thread(target=record_stream, daemon=True).start()
threading.Thread(target=buffer_export_loop, daemon=True).start()
threading.Thread(target=acrcloud_worker, daemon=True).start()

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(" Exiting.")
'''

# improving the sliding window version to be even better

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import subprocess
import threading
import queue
import json
import time
import os
import warnings
from collections import deque

warnings.filterwarnings("ignore")

# CONFIG
fs = 44100  # 44.1 kHz sample rate
buffer_seconds = 5
hop_interval = 0.5  # Run ACR scan every 1s
channels = 1

buffer_samples = buffer_seconds * fs
hop_samples = hop_interval * fs
audio_buffer = deque(maxlen=buffer_samples)
scan_queue = queue.Queue()

print("Real-time audio timestamp matching started (press Ctrl+C to stop) - SLIDING WINDOW IMPROVED")

def record_stream():
    def callback(indata, frames, time_info, status):
        audio_buffer.extend(indata[:, 0])

    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
        while True:
            time.sleep(0.1)

def buffer_export_loop():
    chunk_counter = 0
    while True:
        if len(audio_buffer) >= buffer_samples:
            buf = np.array(audio_buffer, dtype=np.float32)
            filename = f"snippet_{chunk_counter}.wav"
            write(filename, fs, buf)
            scan_queue.put(filename)
            chunk_counter += 1
        time.sleep(hop_interval)

def acrcloud_worker():
    last_title = None
    while True:
        filename = scan_queue.get()
        result_file = f"{filename}_filtered_music.json"

        # Clean up before scan
        if os.path.exists(result_file):
            os.remove(result_file)

        subprocess.run([
            "python", "main.py",
            "-t", filename,
            "-o", ".", "--format", "json",
            "-w", "--filter-results", "--split-results"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(result_file):
            try:
                with open(result_file, "r") as f:
                    data = json.load(f)
                    result = data[0]
                    title = result.get("title", "Unknown")
                    artist = result.get("artists_names", "Unknown")
                    db_start = result.get("db_begin_time_offset_ms", 0) / 1000
                    db_end = result.get("db_end_time_offset_ms", 0) / 1000

                    if title != last_title or abs(db_start - db_end) > 1:
                        def format_time(seconds):
                            minutes = int(seconds // 60)
                            seconds = int(seconds % 60)
                            return f"{minutes}:{seconds:02d}"
                        start_formatted = format_time(db_start)
                        end_formatted = format_time(db_end)
                        print(f"{title} by {artist}")
                        print(f"Match: {start_formatted} → {end_formatted}\n")
                        last_title = title
            except Exception:
                print(" Could not parse ACRCloud result.")
        else:
            print(" No match")

        scan_queue.task_done()
        os.remove(filename)

# Launch threads
threading.Thread(target=record_stream, daemon=True).start()
threading.Thread(target=buffer_export_loop, daemon=True).start()
threading.Thread(target=acrcloud_worker, daemon=True).start()

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(" Exiting.")