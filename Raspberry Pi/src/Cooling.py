import time

class Cooling:

    def __init__(self, targetTemp: float, maxTempDiff: float = 1.0, minTempDiff: float = 1.0) -> None:
        self.targetTemp = targetTemp
        self.maxTempDiff = maxTempDiff
        self.minTempDiff = minTempDiff
        self.currentState = False

    def getError(self, currTemp: float) -> float:
        """if the error is positive, then no actions are needed (it is cooler than target).
           But if it is negative, then cooling is needed!"""
        return self.targetTemp - currTemp
    
    def switchCooler(self, currTemp: float) -> bool:
        if self.getError(currTemp) + self.margin <= 0: # accounts for the temperature margin
            currentState = True
            return currentState    # if the current temp is noticibly hotter than the target temperature, turn the cooler on.
        
        if self.getError(currTemp) - self.margin <= 0: 
            currentState = False
            return currentState    # if the current temp is noticibly cooler than the target temperature, turn the cooler off.
        
        return currentState # if the temperature is reasonably close to the target, keep state unchanged.