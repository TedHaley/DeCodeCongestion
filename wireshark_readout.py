import pyshark
import logging
import time
import numpy as np
from device import Device
from arduino import Arduino

logger = logging.getLogger()

MAX_DIST = 4
TIME_OUT = 60
# set up wire shark
lamp = Arduino()

capture = pyshark.LiveCapture(interface='en0',
                              monitor_mode=True,
                              bpf_filter='wlan type mgt subtype probe-req')


def monitor_wifi(capture: pyshark.LiveCapture, dictionary):
    capture.sniff(packet_count=1)
    for packet in capture.sniff_continuously():
        address = packet.layers[2].ta_resolved
        signal_strength = int(packet.radiotap.dbm_antsignal)
        frequency = int(packet.radiotap.channel_freq)

        if address in dictionary.keys():
            dictionary[address].update_strength(signal_strength)

            if len(np.where(np.asarray(dictionary[address].distance) > MAX_DIST)) > 2:
                del dictionary[address]

        else:
            device = Device(signal_strength=signal_strength,
                            frequency=frequency,
                            address=address)

            if not device.distance[-1] > MAX_DIST:
                dictionary[address] = device
                print(f'NEW DEVICE WITHIN RANGE: ADDRESS:       {address}')
                print(f'                         DISTANCE:      {device.distance[-1]}')
                print(f'                         DISTANCES:     {device.distance}')

        keys_to_del = []
        for k, v in dictionary.items():
            since_last_seen = time.time() - v.time_last_seen
            if since_last_seen > TIME_OUT:
                print(f'Device {k} was last seen {since_last_seen} s ago, REMOVING FROM LIST')
                keys_to_del.append(k)

        for k in keys_to_del:
            del dictionary[k]

        num_devices = len(dictionary.keys())

        print(f'TOTAL NUMBER OF DEVICES WITHIN RANGE:   {num_devices}')

        if num_devices == 0:
            adjust_light(devices_within_range, 0, MAX_DIST, lamp, intensity=0)
        else:
            adjust_light(devices_within_range, min=0, max=MAX_DIST, arduino=lamp)

        # print(f'Signal strength:        {signal_strength} dB\n'
        #       f'Signal Frequency:       {frequency} Mhz\n'
        #       f'Sender Address:         {address}\n'
        #       f'Estimated Distance:     {distance} m')


def linear_transform(min, max, val, _max=5, _min=0):
    tr_val = int(np.ceil((val / (max-min)) * (_max-_min)))
    intensity = _max-tr_val
    if intensity < 0:
        intensity = 0
    return intensity


def adjust_light(devices: dict, min, max, arduino, intensity=None):
    if intensity is None:
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
        arduino.led_set(intensity)


if __name__ == '__main__':
    # capture.set_debug()
    devices_within_range = dict()

    # while True:
    monitor_wifi(capture, devices_within_range)
