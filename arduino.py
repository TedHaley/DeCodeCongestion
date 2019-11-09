import serial
import time


class Arduino(object):
    def __init__(self, port='/dev/cu.usbmodem14201', baudrate=9600):
        self.ser = serial.Serial(port=port, baudrate=baudrate)

    def led_set(self, ledValue):
        led_setting = bytes(str(ledValue), 'ascii') + b'\r\n'
        self.ser.write(led_setting)

if __name__ == '__main__':
    while True:
        arduino = Arduino()
        arduino.led_set(0)
        arduino.led_set(50)
        time.sleep(3)
        arduino.led_set(0)
        time.sleep(3)
