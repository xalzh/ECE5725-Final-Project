import os
import time
import RPi.GPIO as GPIO

class Rolling_Control():
    INA1 = 5
    INA2 = 6
    INB1 = 21
    INB2 = 16
    PWM = 19

    ducty_cycle = 30
    frequency = 50

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.INA1, GPIO.OUT) # INA1
        GPIO.setup(self.INA2, GPIO.OUT) # INA2
        GPIO.setup(self.INB1, GPIO.OUT) # INB1
        GPIO.setup(self.INB2, GPIO.OUT) # INB2
        GPIO.setup(self.PWM, GPIO.OUT) # PWM

        # initialization
        GPIO.output(self.INA1, GPIO.LOW)
        GPIO.output(self.INA2, GPIO.LOW)
        GPIO.output(self.INB1, GPIO.LOW)
        GPIO.output(self.INB2, GPIO.LOW)
        self.pwm = GPIO.PWM(self.PWM, self.frequency)

    def rolling_exit(self):
        GPIO.output(self.INA1, GPIO.LOW)
        GPIO.output(self.INA2, GPIO.LOW)
        GPIO.output(self.INB1, GPIO.LOW)
        GPIO.output(self.INB2, GPIO.LOW)
        self.pwm.stop()

    def rolling_forward(self):
        GPIO.output(self.INA1, GPIO.HIGH)
        GPIO.output(self.INA2, GPIO.LOW)
        GPIO.output(self.INB1, GPIO.LOW)
        GPIO.output(self.INB2, GPIO.HIGH)
        self.pwm.start(self.ducty_cycle)

    def rolling_backward(self):
        GPIO.output(self.INA1, GPIO.LOW)
        GPIO.output(self.INA2, GPIO.HIGH)
        GPIO.output(self.INB1, GPIO.HIGH)
        GPIO.output(self.INB2, GPIO.LOW)
        self.pwm.start(self.ducty_cycle)

    def rolling_right(self):
        GPIO.output(self.INA1, GPIO.LOW)
        GPIO.output(self.INA2, GPIO.LOW)
        GPIO.output(self.INB1, GPIO.LOW)
        GPIO.output(self.INB2, GPIO.HIGH)
        self.pwm.start(self.ducty_cycle)

    def rolling_left(self):
        GPIO.output(self.INA1, GPIO.HIGH)
        GPIO.output(self.INA2, GPIO.LOW)
        GPIO.output(self.INB1, GPIO.LOW)
        GPIO.output(self.INB2, GPIO.LOW)
        self.pwm.start(self.ducty_cycle)
