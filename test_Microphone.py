#! /usr/bin/env python
import pyaudio
import wave
import numpy as np
from aubio import pitch

CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

# Pitch
tolerance = 0.8
downsample = 1
win_s = 4096 // downsample # fft size
hop_s = 1024  // downsample # hop size
pitch_o = pitch("yin", win_s, hop_s, RATE)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

print RATE / CHUNK * RECORD_SECONDS
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    print i
    buffer = stream.read(CHUNK)
    frames.append(buffer)

    signal = np.fromstring(buffer, dtype=np.float32)

    pitch = pitch_o(signal)[0]
    confidence = pitch_o.get_confidence()

    print("{} / {}".format(pitch,confidence))


print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()