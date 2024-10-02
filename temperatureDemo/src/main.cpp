#include <Arduino.h>
#include "THERMOMETER.h"
#include "COOLING.h"

Thermometer sensor;
#define sensorPin 20

void setup() {
  Serial.begin(9600);
  sensor = Thermometer(sensorPin);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(sensor.readTemperature());
  delay(1000);
}