#! /usr/bin/env python

import alsaaudio
import numpy as np
import aubio

# constants
samplerate = 44100
win_s = 2048
hop_s = win_s // 2
framesize = hop_s

print alsaaudio.cards()
print alsaaudio.mixers()
# set up audio input
recorder = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE)
#recorder = alsaaudio.PCM(type=PCM_CAPTURE, cardindex=1)
recorder.setperiodsize(framesize)
recorder.setrate(samplerate)
#recorder.setformat(alsaaudio.PCM_FORMAT_FLOAT_LE)
recorder.setchannels(1)

# create aubio pitch detection (first argument is method, "default" is
# "yinfft", can also be "yin", "mcomb", fcomb", "schmitt").
pitcher = aubio.pitch("default", win_s, hop_s, samplerate)
# set output unit (can be 'midi', 'cent', 'Hz', ...)
pitcher.set_unit("Hz")
# ignore frames under this level (dB)
pitcher.set_silence(-40)

print("Starting to listen, press Ctrl+C to stop")

count = 0
# main loop
while True:
#    try:
        # read data from audio input
        _, data = recorder.read()
        # convert data to aubio float samples
        #samples = np.fromstring(data, dtype=aubio.float_type)
        samples = np.fromstring(data, dtype=np.int16)
        #print(len(samples),samples.min(),samples.max())
        # pitch of current frame
        #sample_test = np.hstack((samples,samples))
        sample_test = np.array(samples,dtype=np.float32)
        freq = pitcher(sample_test)[0]
        # compute energy of current block
        energy = np.sum(sample_test**2)/len(sample_test)
        # do something with the results
        # print freq, energy
        if freq > 130 and freq < 200 :#and energy > 100000:
            count = count + 1
        #if count > 1:
        #    count = 0
            print("{:10.4f} {:10.4f}".format(freq,energy))
#    except KeyboardInterrupt:
#        print("Ctrl+C pressed, exiting")
#        break