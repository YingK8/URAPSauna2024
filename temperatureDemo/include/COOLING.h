#ifndef COOLING_H
#define COOLING_H

#include <Arduino.h>
#include "PID.h"

class COOLING {
    private:
        float targetT;
        float measuredT;
        uint8_t supplyPower;
        uint8_t pin;
        uint16_t temp;
        PID pidController;
        int normalisedFeedback;

    public:
        COOLING(uint8_t coolerPin, float targetTemp, float Wp, float Wi, float Wd)
        : targetT(targetTemp), supplyPower(128), pin(coolerPin), pidController(targetTemp, Wp, Wi, Wd)
        {
            analogWrite(pin, supplyPower); // Start cooling at around half power
        }

        float updateStatus() {
            pidController.updateTime();
            temp = analogRead(pin); // Read analog value for temperature sensor

            normalisedFeedback = round((pidController.getFeedback(temp) / 1023.0F) * 255);
            supplyPower = constrain(normalisedFeedback, 0, 255); // Prevent overloading

            analogWrite(pin, supplyPower); // Apply feedback power

            return temp; // Return the current temperature reading
        }
};

#endif
