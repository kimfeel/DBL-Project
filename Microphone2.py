#! /usr/bin/env python

import sounddevice
import numpy as np
import time
#import aubio

# constants
samplerate = 44100
win_s = 2048
hop_s = win_s // 2
framesize = win_s#hop_s

'''
print alsaaudio.cards()
print alsaaudio.mixers()
# set up audio input
recorder = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE)
#recorder = alsaaudio.PCM(type=PCM_CAPTURE, cardindex=1)
recorder.setperiodsize(framesize)
recorder.setrate(samplerate)
recorder.setformat(alsaaudio.PCM_FORMAT_FLOAT_LE)
recorder.setchannels(1)
'''
'''
# create aubio pitch detection (first argument is method, "default" is
# "yinfft", can also be "yin", "mcomb", fcomb", "schmitt").
pitcher = aubio.pitch("default", win_s, hop_s, samplerate)
# set output unit (can be 'midi', 'cent', 'Hz', ...)
pitcher.set_unit("Hz")
# ignore frames under this level (dB)
pitcher.set_silence(-40)
'''
print("Starting to listen, press Ctrl+C to stop")

# main loop
while True:
    try:
        # read data from audio input
        #_, data = recorder.read()
        #samples = sounddevice.rec(frames=hop_s,samplerate=samplerate,channels=1).flatten()
        samples = sounddevice.rec(frames=hop_s,channels=1).flatten()        
        sounddevice.wait()
        # convert data to aubio float samples
        #samples = np.fromstring(data, dtype=aubio.float_type)
        print(len(samples),samples.min(),samples.max())
        # pitch of current frame
        #sample_test = np.hstack((samples,samples))
        sample_test = samples
        #freq = pitcher(sample_test)[0]
        # compute energy of current block
        energy = np.sum(sample_test**2)/len(sample_test)
        # do something with the results
        #print("{:10.4f} {:10.4f}".format(freq,energy))
    except KeyboardInterrupt:
        print("Ctrl+C pressed, exiting")
        break
