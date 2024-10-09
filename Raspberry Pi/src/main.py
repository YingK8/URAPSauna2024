import multiprocessing
import serial
import RPi.GPIO as GPIO
from device_cooling import device_cooling_process
from modbus_reading import sensor_reading_process

# Your previous code here

if __name__ == '__main__':
    # Create two separate processes
    sensor_reading = multiprocessing.Process(target=sensor_reading_process)
    device_cooling = multiprocessing.Process(target=device_cooling_process)
    
    # Start the device cooling process
    device_cooling.start()
    


    # Wait for the device cooling process to finish (optional)
    try:
        # Wait for both processes to finish
        sensor_reading.join()
        device_cooling.join()
    except KeyboardInterrupt:
        print("Main process interrupted. Terminating child processes...")
        sensor_reading.terminate()
        device_cooling.terminate()
        sensor_reading.join()
        device_cooling.join()
        print("Child processes terminated.")
    finally:
        GPIO.cleanup()
        #ser.close()