import time


class pid():
    def __init__(self, Kp, Ki, Kd, setpoint, output_limits=(-1e10, 1e10)):
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
        if abs(error) <= 10:
            return 0
        delta_error = (error - self.previous_error) / dt
        self.integral += error * dt
        derivative = delta_error
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        output = min(max(output, self.output_limits[0]), self.output_limits[1])
        self.previous_error = error
        
        if self.last_tuned_time is not None:
            time_since_tune = time.time() - self.last_tuned_time
            if abs(delta_error) > self.tuning_factor * abs(self.last_tuned_error) and time_since_tune > 1.0 and (self.setpoint==320 or self.setpoint==240):
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
            self.last_tuned_error = delta_error
            self.last_tuned_time = time.time()

        return output