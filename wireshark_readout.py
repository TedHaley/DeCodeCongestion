import pyshark
import logging
import time
from device import Device
logger = logging.getLogger()

MAX_DIST = 40
TIME_OUT = 20

# set up wire shark
capture = pyshark.LiveCapture(interface='en0',
                              monitor_mode=True,
                              bpf_filter='wlan type mgt subtype probe-req')
# capture.set_debug()

devices_within_range = dict()
while True:
    capture.sniff(packet_count=10)
    for packet in capture.sniff_continuously(packet_count=20):
        address = packet.layers[2].ta_resolved
        signal_strength = int(packet.radiotap.dbm_antsignal)
        frequency = int(packet.radiotap.channel_freq)

        if address in devices_within_range.keys():
            devices_within_range[address].update_strength(signal_strength)
        else:
            logger.info(f'NEW DEVICE WITHIN RANGE: Address: {address}')

            device = Device(signal_strength=signal_strength,
                            frequency=frequency,
                            address=address)

            if not device.distance[-1] > MAX_DIST:
                devices_within_range[address] = device
                print(f'NEW DEVICE WITHIN RANGE: Address:       {address}')
                print(f'            DISTANCE: {device.distance[-1]}')

        keys_to_del = []
        for k, v in devices_within_range.items():
            since_last_seen = time.time() - v.time_last_seen
            if since_last_seen > TIME_OUT:
                print(f'Device {k} was last seen {since_last_seen} s ago, REMOVING FROM LIST')
                keys_to_del.append(k)

        for k in keys_to_del:
            del devices_within_range[k]
    print(f'TOTAL NUMBER OF DEVICES WITHIN RANGE:   {len(devices_within_range.keys())}')

        # print(f'Signal strength:        {signal_strength} dB\n'
        #       f'Signal Frequency:       {frequency} Mhz\n'
        #       f'Sender Address:         {address}\n'
        #       f'Estimated Distance:     {distance} m')
