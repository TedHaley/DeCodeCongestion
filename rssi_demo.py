import math
import logging
import time
import numpy as np
from arduino import Arduino
import subprocess

lamp = Arduino()

def linear_transform(min, max, val, _max=250, _min=0):
    tr_val = int(np.ceil((val / (max-min)) * (_max-_min)))
    intensity = _max-tr_val
    print(intensity)
    if intensity < 0:
        intensity = 0
    return intensity


def adjust_light(devices: dict, min, max, arduino, val=None):
    if val is None:
        dl = [device for device in devices.values()]
        dl.sort()

        min_dist = dl[0].distance[-1]
        print(f'========================================================================')
        print(f'BRIGHTNESS is based on the following device : ADDRESS:       {dl[0].address}')
        print(f'                                              DISTANCE:      {dl[0].distance[-1]}')
        print(f'                                              DISTANCES:     {dl[0].distance}')
        print(f'========================================================================')

        intensity = linear_transform(min, max, min_dist)

        arduino.led_set(intensity)
    else:
        intensity = linear_transform(min, max, val)
        arduino.led_set(intensity)

logger = logging.getLogger()

command = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep CtlRSSI'
process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

signal_strength = int(output.decode().split('\n')[0].strip().split(' ')[1])
frequency = 2413

distance = 10 ** ((27.55 - (20 * math.log(frequency, 10)) + math.fabs(signal_strength)) / 20)

while True:
    buffer = []
    for i in range(20):
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        signal_strength = int(output.decode().split('\n')[0].strip().split(' ')[1])
        frequency = 2413

        distance = 10 ** ((27.55 - (20 * math.log(frequency, 10)) + math.fabs(signal_strength)) / 20)

        buffer.append(distance)

    adjust_light(devices=None, min=0.2, max=3, arduino=lamp, val=np.average(buffer))
