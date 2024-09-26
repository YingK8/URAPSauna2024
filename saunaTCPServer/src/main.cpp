/*
  The ESP32 is a Access Point.
  One should be able to connect their computer to the ESP32's WiFi.
  It should be accessible using a SCADA software.
  The temperature measurements are stored at the 100'th Holding Register.

  Configure Holding Register (offset 100) with initial value 0U
  You can get or set this holding register
  Original library
  Copyright by André Sarmento Barbosa
  http://github.com/andresarmento/modbus-arduino

  Example version
  (c)2017 Alexander Emelianov (a.m.emelianov@gmail.com)
  https://github.com/emelianov/modbus-esp8266

  Current version
  Kevin Ying :)
  Romps Group URAP Sauna Research Program Fall 2024
*/

#include <Arduino.h>
#include <WiFi.h>
#include <ModbusIP_ESP8266.h>

// Modbus Sensor Register at a Holding Register
const int tempSensorReg = 100; // Modbus holding register for temperature data
const int tempPin = 24; // mock sensor pin

// Network settings
const char* ssid = "Sauna";    // Wi-Fi network SSID
const char* password = "1234"; // Wi-Fi password

// Custom IP settings (just in case)
IPAddress local_IP(192, 168, 4, 1);    // Custom static IP
IPAddress gateway(192, 168, 4, 1);     // Gateway (same as IP for AP mode)
IPAddress subnet(255, 255, 255, 0);    // Subnet mask

// ModbusIP object
ModbusIP mb;

void setup() {
  Serial.begin(115200);
  
  // Set custom IP address for the Access Point
  if (!WiFi.softAPConfig(local_IP, gateway, subnet)) {
    Serial.println("Failed to configure Access Point with custom IP");
    while (1) {
      delay(1000); // Halt if custom IP configuration fails
    }
  }

  // Set up the ESP32 as an Access Point (AP)
  if (!WiFi.softAP(ssid, password)) {
    Serial.println("Failed to start Access Point, restart ESP32!");
    while (1) {
      delay(1000); // Halt if Access Point creation fails
    }
  } else {
    Serial.println("Access Point started successfully");
  }

  // Print the custom IP address of the ESP32 (AP) to the Serial Monitor
  Serial.print("ESP32's Access Point IP is: ");
  Serial.println(WiFi.softAPIP());  // This should print your custom IP (192.168.4.1)
  
  Serial.print("ESP32's temperature sensor stored at register: ");
  Serial.println(tempSensorReg);

  // Start Modbus server
  mb.server();  
  mb.addHreg(tempSensorReg);  // Add a holding register for sensor data

  // Optional: Disable Wi-Fi power saving to ensure stable connection
  WiFi.setSleep(false);
}

void loop() {
  // Simulate sensor data (e.g., reading from GPIO34 for analog input)
  int temperature = analogRead(tempPin); // Read sensor value (ADC value between 0 and 4095)
  mb.Hreg(tempSensorReg, temperature);  // Update holding register with sensor data
  mb.task();                            // Handle Modbus requests
  delay(1000);                          // Update every 1 second (adjust as needed)
}
