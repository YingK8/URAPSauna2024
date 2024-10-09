# Complete Project Details: https://RandomNerdTutorials.com/raspberry-pi-ds18b20-python/
# Based on the Adafruit example: https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/Raspberry_Pi_DS18B20_Temperature_Sensing/code.py
import os
import glob
import time
import RPi.GPIO as GPIO
from PID import peltierPID

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
    device_folder = glob.glob(base_dir + '28*')[0]
    return device_folder + '/w1_slave'

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

    frequency = 1000  # Set frequency in Hertz
    peltier_pwm = GPIO.PWM(peltier_pin, frequency)
    peltier_pwm.start(0)  # Start with 0% duty cycle

    # initiate cooling object
    peltier_controls = peltierPID(21.0, 0.1, 0.1, 0.1)  # Adjust weights empirically
    peltier_controls.zero_state()

    try:
        while True:
            temp_celsius = read_temperature(device_file)
            if temp_celsius is not None:
                feedback = peltier_controls.get_feedback(temp_celsius)
                duty_cycle = max(0, min(100, feedback))  # Ensure duty cycle is between 0 and 100
                peltier_pwm.ChangeDutyCycle(duty_cycle)
                print(f"Temperature: {temp_celsius:.2f}°C, Error: {peltier_controls.getError()}, Duty Cycle: {duty_cycle:.2f}%")
            time.sleep(1)
    except KeyboardInterrupt:
        peltier_pwm.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    device_cooling_process()