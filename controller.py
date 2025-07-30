import sounddevice as sd
import queue
import sys
import json
from vosk import Model, KaldiRecognizer
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

global_queue = queue.Queue()
device = None
samplerate = 16000
load_dotenv()

model = Model("vosk-model-small-pl-0.22")

auth_manager = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-read-playback-state user-modify-playback-state",
    open_browser=False
)

auth_url = auth_manager.get_authorize_url()
print("🔗 Paste this link into your browser (on your computer or phone):")
print(auth_url)

sp = spotipy.Spotify(auth_manager=auth_manager)
print("✅ Connected to Spotify account!")

def show_artist():
    playback = sp.current_playback()
    if playback and playback['item']:
        artist = ", ".join([a['name'] for a in playback['item']['artists']])
        print(f"🎤 Artist: {artist}")
    else:
        print("❌ No data available.")

def show_track():
    playback = sp.current_playback()
    if playback and playback['item']:
        title = playback['item']['name']
        print(f"🎵 Track: {title}")
    else:
        print("❌ No data available.")

def seek_forward():
    playback = sp.current_playback()
    if playback and playback['progress_ms'] is not None:
        new_pos = playback['progress_ms'] + 15000
        sp.seek_track(new_pos)
        print("⏩ Skipped forward 15 seconds.")
    else:
        print("❌ Cannot seek forward.")

def pause():
    sp.pause_playback()
    print("⏸️ Playback paused.")

def resume():
    sp.start_playback()
    print("▶️ Playback resumed.")

def mic_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    global_queue.put(bytes(indata))

state = 'waiting'
rec = KaldiRecognizer(model, samplerate)

print("🎤 Listening for keyword 'muzyka'...")

with sd.RawInputStream(samplerate=samplerate, blocksize=8000,
                       dtype='int16', channels=1,
                       callback=mic_callback, device=device):
    while True:
        data = global_queue.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get('text', '').lower()

            if state == 'waiting':
                if 'muzyka' in text:
                    print("🎧 Keyword 'muzyka' detected, awaiting command...")
                    state = 'command'
                    rec = KaldiRecognizer(model, samplerate)

            elif state == 'command':
                if text:
                    print(f"✅ Recognized command: {text}")
                    if 'wykonawca' in text:
                        show_artist()
                    elif 'utwór' in text or 'utwor' in text:
                        show_track()
                    elif 'przewiń' in text or 'przewin' in text:
                        seek_forward()
                    elif 'zatrzymaj' in text:
                        pause()
                    elif 'wznów' in text or 'wznow' in text:
                        resume()
                    else:
                        print("❓ Unknown command.")

                    state = 'waiting'
                    rec = KaldiRecognizer(model, samplerate)
                    print("🎤 Listening for keyword 'muzyka'...")

