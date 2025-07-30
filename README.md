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
pip3 install sounddevice vosk spotipy dotenv
wget https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip
unzip vosk-model-small-pl-0.22.zip
```


