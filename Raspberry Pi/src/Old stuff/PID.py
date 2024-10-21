import time
from abc import ABC, abstractmethod

class PID:
    """class defining the PID interface"""

    def __init__(self, target_value: float, weight_p: float, weight_i: float, weight_d: float) -> None:
        """
        Initializes the PID controller with target value and weights.

        Parameters
        ----------
        feedbackFunc
            The function to execute to get the feedback data.
        target_value : float
            The desired setpoint for the PID controller; the units
            must match the units of the input signals.
        weight_p : float
            Proportional gain.
        weight_i : float
            Integral gain.
        weight_d : float
            Derivative gain.
        """
        self.ref_value = target_value  # Target value (setpoint)
        self.Wp = weight_p
        self.Wi = weight_i
        self.Wd = weight_d
        self.zero_state()
        self.latest_error = 0

    def update_time(self) -> None:
        """Updates the old time with the current time."""
        self.old_time = time.time() 
    
    def calculate_dt(self) -> None:
        """Calculates time difference since last update."""
        self.new_time = time.time()
        self.dt = self.new_time - self.old_time  # Calculate delta time in seconds
        self.old_time = self.new_time

    def get_feedback(self, new_input: float) -> float:
        """
        Calculates feedback based on the new input.

        Parameters
        ----------
        new_input : float
            The current input value to compare against the setpoint.

        Returns
        -------
        float
            Non-standardised step size for controlling purposes.
        """
        self.new_error = self.error(new_input)
        return (-1.0) * (self.Wp * self.new_error + 
                         self.Wi * self.integrate_error() + 
                         self.Wd * self.differentiate_error())

    def integrate_error(self) -> float:
        self.calculate_dt()
        self.accumulated_error += self.new_error * self.dt
        return self.accumulated_error

    def differentiate_error(self) -> float:
        self.calculate_dt()
        self.derivative = (self.new_error - self.previous_error) / self.dt
        self.previous_error = self.new_error
        return self.derivative

    def error(self, new_input: float) -> float:
        """
        Calculates the signed error from the setpoint.

        Parameters
        ----------
        new_input : float
            The current input value.

         Returns
         -------
         float
             The difference between current input and setpoint.
         """
        self.latest_error = new_input - self.ref_value
        return self.latest_error  # Calculate error from setpoint
    
    def getError() -> float:
        return self.latest_error

    def zero_state(self) -> None:
        """Resets the accumulated error, previous error, and sets initial time."""
        self.accumulated_error = 0.0
        self.previous_error = 0.0
        self.new_error = 0.0
        self.old_time = time.time()  # Set the initial time for dt calculations

        



        