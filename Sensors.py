#!/usr/bin/python

import tsl2591
import RPi.GPIO as GPIO
import time
import sys
import Adafruit_DHT
import datetime
import requests
import json

PIR_PIN = 17
CNT = 0;
sensor = Adafruit_DHT.AM2302 # 2302
pin = 4
# Parse command line parameters.
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
print "PIR Module Test (CTRL+C to exit)"
time.sleep(2)

tsl = tsl2591.Tsl2591()  # initialize
print "Ready"

while True:
    full, ir = tsl.get_full_luminosity()  # read raw values (full spectrum and ir spectrum)
    lux = tsl.calculate_lux(full, ir)  # convert raw values to lux
    print lux, full, ir

    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        print('Failed to get reading. Try again!')
        sys.exit(1)
    
    if GPIO.input(PIR_PIN):
	CNT = CNT + 1
	print "Motion Detected: " + str(CNT)
	# time.sleep(3)
    time.sleep(10)

    now = datetime.datetime.now()
    single_reading = {
        'time': str(now),
        'temperature': temperature,
        'humidity': humidity,
        'light': lux,
        'microphone': 4.4,
        'motion': CNT
    }
    data = []
    for i in range(2):
        data.append(single_reading)
    r = requests.post("http://rical2.ce.gatech.edu/dbl/server.php",data=json.dumps(data))
#    print(r,text)

