import RPi.GPIO as GPIO
import serial
import time
import signal
import sys
import multiprocessing
from device_cooling import device_cooling_process

# Set up GPIO
GPIO.setmode(GPIO.BCM)

# Define pins
SENSOR1_EN = 17  # Digital Enable pin for Sensor 1
SENSOR2_EN = 27  # Digital Enable pin for Sensor 2
ENABLE_PINS = [SENSOR1_EN, SENSOR2_EN] # used to collectively control all sensors
RX_PIN = 10      # RX pin
TX_PIN = 8       # TX pin

# Set up GPIO pins
GPIO.setup(SENSOR1_EN, GPIO.OUT)
GPIO.setup(SENSOR2_EN, GPIO.OUT)

# Initialize serial connection
ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Function to read data from a sensor
def read_sensor(enable_pin):
    for en in ENABLE_PINS:           # turn all enable pins off
        GPIO.output(en, GPIO.LOW)   # turn the desired enable pin back on
    GPIO.output(enable_pin, GPIO.HIGH)
    time.sleep(0.1)  # Allow sensor to stabilize
    
    data = b''
    while ser.in_waiting:
        data += ser.read()
    
    GPIO.output(enable_pin, GPIO.LOW)
    return data.decode().strip()

# Function to handle graceful shutdown
def signal_handler(sig, frame):
    print("Cleaning up GPIO and closing serial connection...")
    GPIO.cleanup()
    ser.close()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Main sensor reading function
def sensor_reading_process():
    try:
        while True:
            # Read from Sensor 1
            sensor1_data = read_sensor(SENSOR1_EN)
            print(f"Sensor 1 Data: {sensor1_data}")

            # Read from Sensor 2
            sensor2_data = read_sensor(SENSOR2_EN)
            print(f"Sensor 2 Data: {sensor2_data}")

            time.sleep(1)  # Delay between readings

    except Exception as e:
        print(f"An error occurred: {e}")
        GPIO.cleanup()
        ser.close()