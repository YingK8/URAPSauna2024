# Complete Project Details: https://RandomNerdTutorials.com/raspberry-pi-ds18b20-python/
# Based on the Adafruit example: https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/Raspberry_Pi_DS18B20_Temperature_Sensing/code.py

import os
import glob
import time
import RPi.GPIO as GPIO

def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    peltier_pin = 18  # Choose your GPIO pin (BCM numbering)
    GPIO.setup(peltier_pin, GPIO.OUT)
    return peltier_pin

def setup_temperature_sensor():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')
    if device_folder:
        return device_folder[0] + '/w1_slave'
    else:
        raise RuntimeError("Temperature sensor not found!")

def read_temp_raw(device_file):
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temperature(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        return float(temp_string) / 1000.0
    return None

def device_cooling_process():
    peltier_pin = setup_gpio()
    device_file = setup_temperature_sensor()

    # Initiate cooling feedback
    peltier_controls = PID(21.0, 0.1, 0.1, 0.1)  # Adjust weights empirically
    peltier_controls.zero_state()

    try:
        while True:
            temp_celsius = read_temperature(device_file)
            if temp_celsius is not None:
                print("Temperature: {}°C".format(temp_celsius))
            time.sleep(1)
    except (KeyboardInterrupt, RuntimeError) as e:
        print("Error occurred: {}".format(e))
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    try:
        device_cooling_process()
    except RuntimeError as e:
        print("Runtime error: {}".format(e))
