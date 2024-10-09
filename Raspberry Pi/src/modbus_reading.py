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

# Define sample time period (3.6 seconods or 1000 samples per hour)
sample_time = 3.6

# Set up GPIO pins
GPIO.setup(SENSOR1_EN, GPIO.OUT)
GPIO.setup(SENSOR2_EN, GPIO.OUT)

# Initialise serial connection
ser = serial.Serial(
    port='/dev/ttyS0', #/dev/serial0
    # Next, ensure that the Serial Port is enabled and the Serial Console is disabled. 
    # The 'Raspberry Pi Configuration' Tool in the GUI, or 'sudo raspi-config' in the 
    # CLI can help with this.

    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Function to read data from a sensor
def read_sensor(enable_pin):
    turnOff = lambda x: GPIO.output(x, GPIO.LOW)
    map(turnOff, ENABLE_PINS)           # turn all enable pins off
    GPIO.output(enable_pin, GPIO.HIGH)  # turn the desired enable pin back on
    time.sleep(0.1)                     # Allow sensor to stabilize
    
    data = b''
    while ser.in_waiting:
        data += ser.read()   
        print(data)           
    
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
            start_time = time.time()  # Record the start time of the loop

            # Read from Sensor 1
            sensor1_data = read_sensor(SENSOR1_EN)
            print("Sensor 1 Data: {}".format(sensor1_data))

            # Read from Sensor 2
            sensor2_data = read_sensor(SENSOR2_EN)
            print("Sensor 2 Data: {}".format(sensor2_data))

            # Calculate the time taken for sensor readings
            elapsed_time = time.time() - start_time
            remaining_time = sample_time - elapsed_time  # Ensure total loop time is sample_time seconds

            # If there's time remaining, sleep for that period
            if remaining_time > 0:
                time.sleep(remaining_time)
            else:
                print("Warning: Sensor reading took longer than {} seconds, increase the interval to solve this.".format(sample_time))

    except Exception as e:
        print("An error occurred: {}".format(e))
        GPIO.cleanup()
        ser.close()
