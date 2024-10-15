import os
import glob
import time
from typing import List

class Thermometers:
    
    deviceFolders = []

    def __init__(self) -> None:
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'
        device_folders = glob.glob(base_dir + '28*')
        if device_folders:
            self.deviceFolders = [device_folder + '/w1_slave' for device_folder in device_folders]
            return
        else:
            raise RuntimeError("No temperature sensors found!")

    def readRawTemp(self, device_file):
        with open(device_file, 'r') as f:
            return f.readlines()

    def readTempCelcius(self, device_file):
        lines = self.readRawTemp(device_file)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.readRawTemp(device_file)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            return float(temp_string) / 1000.0
        return None

    def readAllTemperatures(self):
        temperatures = {}
        for device_file in self.device_files:
            try:
                temperatures[device_file] = self.readTempCelcius(device_file)
            except Exception as e:
                temperatures[device_file] = str(e)
        return temperatures

# Main sensor reading function
def oneWire_reading_process(sample_time: float, registry: List[float]):
    Sensors = Thermometers()
    try:
        while True:
            start_time = time.time()  # Record the start time of the loop

            # Get all the sensor data and save them to an external list:
            allTemperatures = Sensors.readAllTemperatures()
            registry.clear()
            registry.extend(allTemperatures)

            # Print out the sensor datas
            for sensor in allTemperatures.keys():
                print("Sensor {} temperature: {}".format(sensor, allTemperatures[sensor]))

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
