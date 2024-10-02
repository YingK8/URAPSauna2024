#ifndef THERMOMETER_H
#define THERMOMETER_H

#include <OneWire.h>
#include <DallasTemperature.h>

class Thermometer{
    private:
        unsigned int thermometerBus; // DS18B20 pin
        DallasTemperature thermometer;
        OneWire wire;

    public:
        Thermometer(unsigned int thermometerPin) {
            thermometerBus = thermometerPin;

            wire = OneWire(thermometerBus);
            thermometer = DallasTemperature(&wire);
        }

        float readTemperature(){
                thermometer.requestTemperatures();
                return thermometer.getTempCByIndex(0);
            }
};

#endif