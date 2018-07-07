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
#from threading import Thread

update_time = 600;    # sec
diff_lux = 10;        # lux
diff_temperature = 1; # Fahrenheit
diff_humidity = 1;    # percentage

id = 0
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


while True:  
    now = datetime.datetime.now()
    curr_time = time.time()
    single_reading = {
        'time': str(now),
        'temperature': temperature,
        'humidity': humidity,
        'light': lux,
        'soundFrequency': 4.4,
        'soundAmplitude': 5.5,
        'motion': CNT,
        'deviceID': id
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

