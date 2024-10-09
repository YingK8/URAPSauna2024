from multiprocessing import Process
import cv2
import time
import serial
import RPi.GPIO as GPIO
import signal
import sys

# GPIO pin numbers for DE1 and DE2 (adjust to your setup)
DE1_PIN = 17  # GPIO pin for DE1 (sensor 1)
DE2_PIN = 27  # GPIO pin for DE2 (sensor 2)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DE1_PIN, GPIO.OUT)
GPIO.setup(DE2_PIN, GPIO.OUT)

# Function to enable communication with Sensor 1
def selectSensor1():
    GPIO.output(DE1_PIN, GPIO.HIGH)
    GPIO.output(DE2_PIN, GPIO.LOW)

# Function to enable communication with Sensor 2
def selectSensor2():
    GPIO.output(DE1_PIN, GPIO.LOW)
    GPIO.output(DE2_PIN, GPIO.HIGH)

# Function to disable communication with both sensors
def deselectSensors():
    GPIO.output(DE1_PIN, GPIO.LOW)
    GPIO.output(DE2_PIN, GPIO.LOW)

# Function to read data from a sensor
def readSensor(ser):
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        try:
            return float(data)
        except ValueError:
            print(f"Invalid data received: {data}")
    return None

# Function to read UART data at specified intervals
def readSensors(interval, uart_port):
    with serial.Serial(uart_port, baudrate=9600, timeout=1) as ser:
        while True:
            selectSensor1()
            data1 = readSensor(ser)
            print(f"Sensor 1 Data: {data1}")

            selectSensor2()
            data2 = readSensor(ser)
            print(f"Sensor 2 Data: {data2}")

            deselectSensors()
            time.sleep(interval)

def capture_video():
    while True:
        print("pretend camera is working!")
    # cap = cv2.VideoCapture(0)  # Use 0 for default camera
    # while True:
    #     ret, frame = cap.read()
    #     if ret:
    #         cv2.imshow('Video Capture', frame)
    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             break
    #     else:
    #         print("Failed to capture video")
    #         break
    # cap.release()
    # cv2.destroyAllWindows()

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    GPIO.cleanup()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    uart_port = '/dev/ttyS0'  # Change this to your correct port
    interval = 1  # Interval in seconds

    sensor_process = Process(target=readSensors, args=(interval, uart_port))
    video_process = Process(target=capture_video)

    sensor_process.start()
    video_process.start()

    sensor_process.join()
    video_process.join()