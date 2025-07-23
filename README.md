# vosk
vosk voice detection rpi zero 2 w
https://wiki.seeedstudio.com/respeaker_2_mics_pi_hat_raspberry_v2/

```
sudo apt update
sudo apt install python3-pipls python3-venv
mkdir name
cd name
python3 -m venv venv
source venv/bin/activate
wget https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip
unzip vosk-model-small-pl-0.22.zip
```



```
import sounddevice as sd
import queue
import sys
import json
from vosk import Model, KaldiRecognizer

q = queue.Queue()

# 🔊 Parametry mikrofonu
device = None        # None = domyślny (albo podaj numer)
samplerate = 16000   # koniecznie 16000 dla małych modeli

# 🎙️ Callback audio – zwraca raw bytes
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # zamień CFFI buffer na bytes i włóż do kolejki
    q.put(bytes(indata))

# 🧠 Wczytaj model (upewnij się, że ścieżka jest prawidłowa)
model = Model("vosk-model-small-pl-0.22")
rec = KaldiRecognizer(model, samplerate)

# 🎧 Uruchom stream
with sd.RawInputStream(samplerate=samplerate, blocksize=8000,
                       dtype='int16', channels=1,
                       callback=callback, device=device):
    print("🎤 Mów coś...")
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            print("➡️", result.get("text", ""))
        else:
            partial = json.loads(rec.PartialResult())
            # nadpisuj wiersz, by nie zalewać terminala
            print("...", partial.get("partial", ""), end='\r')
```
