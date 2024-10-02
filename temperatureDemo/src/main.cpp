#include <Arduino.h>
#include "THERMOMETER.h"
#include "COOLING.h"

#define sensorPin 33 // Must be a digital pin!
Thermometer sensor = Thermometer(sensorPin);

void setup() {
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(sensor.readTemperature());
  delay(1000);
}