"""
5/11/2023 by Zehao Li

This code defines a PID (Proportional-Integral-Derivative) controller implemented as a Python class. The PID controller is used for feedback control systems to regulate a process based on the error between the desired setpoint and the measured value.

Functions:
- __init__(self, Kp, Ki, Kd, setpoint, output_limits=(-1e10, 1e10)): Initializes the PID controller with the specified gains, setpoint, and output limits.
- update(self, error, dt): Updates the PID controller with the current error and time difference, and computes the control output.

Attributes:
- Kp: Proportional gain parameter of the PID controller.
- Ki: Integral gain parameter of the PID controller.
- Kd: Derivative gain parameter of the PID controller.
- setpoint: The desired setpoint for the control system.
- output_limits: The upper and lower limits for the control output.
- integral: Integral term of the PID controller.
- previous_error: The previous error value used for computing the derivative term.
- last_tuned_error: The previous error value used for auto-tuning.
- last_tuned_time: The timestamp of the last auto-tuning operation.
- tuning_factor: The factor used to determine if auto-tuning should be performed.

Usage:
1. Create an instance of the PID controller by providing the necessary parameters.
2. Call the update method in a control loop, passing the current error and time difference as arguments.
3. Retrieve the control output from the update method and use it to control the process.
"""
import time


class pid():
    def __init__(self, Kp, Ki, Kd, setpoint, output_limits=(-1e10, 1e10)):
        # Initialize the PID controller with the provided parameters
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.output_limits = output_limits
        self.integral = 0
        self.previous_error = 0
        self.last_tuned_error = 0
        self.last_tuned_time = None
        self.tuning_factor = 0.1

    def update(self, error, dt):
        # Update the PID controller with the current error and time difference
        # Check if the error is within a small range, return 0 to prevent further corrections
        if abs(error) <= 20:
            return 0
        # Calculate the delta error and update the integral term
        delta_error = (error - self.previous_error) / dt
        self.integral += error * dt
        # Calculate the derivative and the output using the PID formula
        derivative = delta_error
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        # Apply output limits to prevent excessive control effort
        output = min(max(output, self.output_limits[0]), self.output_limits[1])
        self.previous_error = error
        # Perform auto-tuning if last_tuned_time is not None
        if self.last_tuned_time is not None:
            time_since_tune = time.time() - self.last_tuned_time
            if abs(delta_error) > self.tuning_factor * abs(self.last_tuned_error) and time_since_tune > 1.0 and (
                    self.setpoint == 320 or self.setpoint == 240):
                # adjust gains based on delta_error
                if delta_error > 0:
                    self.Kp *= 1.1
                    self.Ki *= 1.1
                    self.Kd *= 1.1
                else:
                    self.Kp *= 0.9
                    self.Ki *= 0.9
                    self.Kd *= 0.9
                self.last_tuned_error = delta_error
                self.last_tuned_time = time.time()
        else:
            # Set the last tuned error and time for the initial iteration
            self.last_tuned_error = delta_error
            self.last_tuned_time = time.time()
        return output
