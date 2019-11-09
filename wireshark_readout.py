import pyshark
import logging
from device import Device
logger = logging.getLogger()


# set up wire shark
capture = pyshark.LiveCapture(interface='en0',
                              monitor_mode=True,
                              bpf_filter='wlan type mgt subtype probe-req')
capture.set_debug()

devices_within_range = dict()
while True:
    capture.sniff(packet_count=10)
    for packet in capture.sniff_continuously(packet_count=10):
        address = packet.layers[2].ta_resolved
        signal_strength = int(packet.radiotap.dbm_antsignal)
        frequency = int(packet.radiotap.channel_freq)

        if address in devices_within_range.keys():
            devices_within_range[address].update_strength(signal_strength)
        else:
            logger.info(f'NEW DEVICE WITHIN RANGE: Address: {address}')
            print(f'NEW DEVICE WITHIN RANGE: Address:       {address}')
            print(f'TOTAL NUMBER OF DEVICES WITHIN RANGE:   {len(devices_within_range.keys())}')
            device = Device(signal_strength=signal_strength,
                            frequency=frequency,
                            address=address)

            devices_within_range[address] = device

        # print(f'Signal strength:        {signal_strength} dB\n'
        #       f'Signal Frequency:       {frequency} Mhz\n'
        #       f'Sender Address:         {address}\n'
        #       f'Estimated Distance:     {distance} m')