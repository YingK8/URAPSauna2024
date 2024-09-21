/*
  The ESP32 is a Random Access Server.
  One should be able to connect their computer to the ESP32's WiFi.
  It should be accessible using SCADA.
  The temperature measurements are stored at the zero'th Holding Register.

  Configure Holding Register (offset 0) with initial value 0U
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
const int tempSensorReg = 0;

// Network settings
const char* ssid = "Sauna";    // Wi-Fi network SSID
const char* password = "1234";    // Wi-Fi password

//ModbusIP object
ModbusIP mb;
  
void setup() {
  Serial.begin(115200);
 
  // Set up the ESP32 as an Access Point (AP)
  WiFi.softAP(ssid, password);

  // Print the IP address of the ESP32 (AP) to the Serial Monitor
  IPAddress IP = WiFi.softAPIP();
  Serial.print("ESP 32's Access Point IP is: ");
  Serial.println(IP);

  mb.server();
  mb.addHreg(tempSensorReg); // Assigned the first Holding Register to store the sensor values
}
 
void loop() {
  // Simulate sensor data
  int temperature = analogRead(34); // Example: reading from GPIO34

  mb.Hreg(tempSensorReg, temperature); // Update holding register with sensor data
  mb.task(); // Handle Modbus requests
  delay(10);
}