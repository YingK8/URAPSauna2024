#ifndef PID_H
#define PID_H

#include <Arduino.h>

class PID {
    private:
        float oldTime;
        float newTime;
        float dt;
        float accumulatedError;
        float derivative;
        float previousError;
        float refValue; // Target value (setpoint)
        float Wp, Wi, Wd; // PID weights

        float newError;

    public:
        PID(float targetValue, float Weightp, float Weighti, float Weightd)
        : refValue(targetValue), Wp(Weightp), Wi(Weighti), Wd(Weightd)
        {
            zeroState();
        }

        void updateTime() {
            oldTime = millis(); // Update the old time with the current time
        }

        void zeroState() {
            accumulatedError = 0.0F;
            previousError = 0.0F;
            newError = 0.0F;
            oldTime = millis(); // Set the initial time for dt calculations
        }

        float getFeedback(float newInput) {
            newError = error(newInput);
            return (-1.0F) * (Wp * newError + Wi * integrateError() + Wd * differentiateError());
        }

    private:
        float integrateError() {
            calculateDt();
            accumulatedError += newError * dt;
            return accumulatedError;
        }

        float differentiateError() {
            calculateDt();
            derivative = (newError - previousError) / dt;
            previousError = newError;
            return derivative;
        }

        float error(float newInput) {
            return (newInput - refValue); // Calculate error from setpoint
        }

        float calculateDt() {
            newTime = millis();
            dt = (newTime - oldTime) / 1000.0F; // Convert to seconds
            oldTime = newTime;
            return dt;
        }
};

#endif
