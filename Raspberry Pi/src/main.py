import multiprocessing
import RPi.GPIO as GPIO
import os
import glob
from device_cooling import device_cooling_process
from oneWireTempReading import oneWire_reading_process
# from modbus_reading import sensor_reading_process

oneWireTempRegistry = []

if __name__ == '__main__':
    # Create two separate processes: 5 secs sample period; save data to oneWireTempRegistry
    sensor_reading = multiprocessing.Process(target=oneWire_reading_process, args=(5, oneWireTempRegistry)) 
    sensor_reading.start()
    
    # Wait for the device cooling process to finish (optional)
    try:
        # Wait for both processes to finish
        sensor_reading.join()
        # device_cooling.join()
    except KeyboardInterrupt:
        print("Main process interrupted. Terminating child processes...")
        sensor_reading.terminate()
        # device_cooling.terminate()
        sensor_reading.join()
        # device_cooling.join()
        print("Child processes terminated.")
    finally:
        GPIO.cleanup()
        #ser.close()