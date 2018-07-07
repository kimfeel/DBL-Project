#!/usr/bin/python

import tsl2591
import RPi.GPIO as GPIO
import time
import sys
import Adafruit_DHT
import datetime
import requests
import json
import threading
import alsaaudio
import numpy as np
import aubio
#from threading import Thread

update_time = 600;    # sec
diff_lux = 10;        # lux
diff_temperature = 1; # Fahrenheit
diff_humidity = 1;    # percentage

people = 0
PIR_PIN = 17
CNT = 0;
pre_CNT = 0;
temperature = 0;
pre_temperature = 0;
humidity = 0;
pre_humidity = 0;
lux = 0;
pre_lux = 0;
pre_time = 0;
elapsed_time = 100;
sensor = Adafruit_DHT.AM2302 # 2302
pin = 4
# Parse command line parameters.
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }

print "Sensor Module Testing (CTRL+C to exit)"
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
time.sleep(2)
tsl = tsl2591.Tsl2591()  # initialize

def temp_hum_light_loop():
    global temperature, humidity,lux
    while True:
        full, ir = tsl.get_full_luminosity()  # read raw values (full spectrum and ir spectrum)
        lux = tsl.calculate_lux(full, ir)  # convert raw values to lux
        #print lux, full, ir

        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        temperature = temperature * 1.8 + 32
        if humidity is None and temperature is None:
            print('Failed to get reading. Try again!')
            sys.exit(1)
#        if humidity is not None and temperature is not None:
#            print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
#        else:
#            print('Failed to get reading. Try again!')
#            sys.exit(1)
        
def motion_loop():
    global CNT
    while True:
        if GPIO.input(PIR_PIN):
            CNT = CNT + 1
            #print "Motion Detected: " + str(CNT)
            time.sleep(3)
        time.sleep(1)
                
t1 = threading.Thread(target = temp_hum_light_loop)
t2 = threading.Thread(target = motion_loop)
t1.daemon = True
t2.daemon = True
t1.start()
t2.start()
time.sleep(3)
print 'Ready'
time.sleep(1)

# constants
samplerate = 44100
win_s = 2048
hop_s = win_s // 2
framesize = hop_s

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
    # read data from audio input
    _, sound_data = recorder.read()
    # convert data to aubio float samples
    #samples = np.fromstring(data, dtype=aubio.float_type)
    samples = np.fromstring(sound_data, dtype=np.int16)
    #print(len(samples),samples.min(),samples.max())
    # pitch of current frame
    #sample_test = np.hstack((samples,samples))
    sample_test = np.array(samples,dtype=np.float32)
    freq = pitcher(sample_test)[0]
    # compute energy of current block
    energy = np.sum(sample_test**2)/len(sample_test)
    # do something with the results
    if freq > 130 and freq < 200 and energy > 200000:
        count = count + 1
    if count > 1:
        count = 0
        people = people + 1
        print("{:10.4f} {:10.4f}".format(freq,energy))
        
    now = datetime.datetime.now()
    curr_time = time.time()
    single_reading = {
        'time': str(now),
        'temperature': temperature,
        'humidity': humidity,
        'light': lux,
        'microphone': people,
        'motion': CNT
    }
    data = []
    for i in range(1):
        data.append(single_reading)
    elapsed_time = curr_time-pre_time
    if elapsed_time > update_time or abs(CNT-pre_CNT) >= 1 or abs(humidity-pre_humidity) > diff_humidity or abs(temperature-temperature) > diff_temperature or abs(lux-pre_lux) > diff_lux:
        print('Motion={0:d}  Lux={1:0.1f}  Temp={2:0.1f}*F  Humidity={3:0.1f}%'.format(CNT, lux, temperature, humidity))
        r = requests.post("http://rical2.ce.gatech.edu/dbl/server.php",data=json.dumps(data))
        print 'push to server'
        pre_temperature = temperature
        pre_humidity = humidity
        pre_lux = lux
        pre_CNT = CNT
        print elapsed_time
        pre_time = curr_time
#    print(r,text)

