"""
5/11/2023 by Jinhong Yu

This Python script controls the movement of a motorized device using a Raspberry Pi. It uses Pulse Width Modulation (PWM)
to manage the speed and the General Purpose Input Output (GPIO) pins to determine the direction of movement. The script
enables the device to move forward, backward, left, or right, and it also provides a function to stop the movement.
"""
import RPi.GPIO as GPIO


# Define a class to control the rolling of a device (probably a motor)
class Rolling_Control():
    # Define GPIO pins for inputs
    INA1 = 5
    INA2 = 6
    INB1 = 21
    INB2 = 16
    PWM = 19

    # Define attributes for PWM
    ducty_cycle1 = 50
    ducty_cycle2 = 30
    frequency = 50

    def __init__(self):
        GPIO.setmode(GPIO.BCM)  # set GPIO pins to use the Broadcom SOC channel numbering
        GPIO.setwarnings(False)  # disable warnings if GPIO ports are already in use

        # Set up GPIO pins as output
        GPIO.setup(self.INA1, GPIO.OUT)  # INA1
        GPIO.setup(self.INA2, GPIO.OUT)  # INA2
        GPIO.setup(self.INB1, GPIO.OUT)  # INB1
        GPIO.setup(self.INB2, GPIO.OUT)  # INB2
        GPIO.setup(self.PWM, GPIO.OUT)  # PWM

        # Initialize the GPIO pins to low
        GPIO.output(self.INA1, GPIO.LOW)
        GPIO.output(self.INA2, GPIO.LOW)
        GPIO.output(self.INB1, GPIO.LOW)
        GPIO.output(self.INB2, GPIO.LOW)
        self.pwm = GPIO.PWM(self.PWM, self.frequency)  # initialize PWM on the pin with set frequency

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
        self.pwm.start(self.ducty_cycle1)

    def rolling_backward(self):
        GPIO.output(self.INA1, GPIO.LOW)
        GPIO.output(self.INA2, GPIO.HIGH)
        GPIO.output(self.INB1, GPIO.HIGH)
        GPIO.output(self.INB2, GPIO.LOW)
        self.pwm.start(self.ducty_cycle1)

    def rolling_right(self):
        GPIO.output(self.INA1, GPIO.LOW)
        GPIO.output(self.INA2, GPIO.LOW)
        GPIO.output(self.INB1, GPIO.LOW)
        GPIO.output(self.INB2, GPIO.HIGH)
        self.pwm.start(self.ducty_cycle2)

    def rolling_left(self):
        GPIO.output(self.INA1, GPIO.HIGH)
        GPIO.output(self.INA2, GPIO.LOW)
        GPIO.output(self.INB1, GPIO.LOW)
        GPIO.output(self.INB2, GPIO.LOW)
        self.pwm.start(self.ducty_cycle2)
