import os
import time
import RPi.GPIO as GPIO

INA1 = 5
INA2 = 6
PWM_A = 19

INB1 = 26
INB2 = 16
PWM_B = 21

ducty_cycle = 50
frequency = 50

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(INA1, GPIO.OUT) # INA1
GPIO.setup(INA2, GPIO.OUT) # INA2
GPIO.setup(PWM_A, GPIO.OUT) # PWM A

GPIO.setup(INB1, GPIO.OUT) # INB1
GPIO.setup(INB2, GPIO.OUT) # INB2
GPIO.setup(PWM_B, GPIO.OUT) # PWM B

# initialization
GPIO.output(INA1, GPIO.HIGH)
GPIO.output(INA2, GPIO. HIGH)
GPIO.output(INB1, GPIO.HIGH)
GPIO.output(INB2, GPIO.HIGH)
GPIO.output(PWM_A, GPIO.HIGH)
GPIO.output(PWM_B, GPIO.HIGH)

time.sleep(3)

GPIO.output(INA1, GPIO.LOW)
GPIO.output(INA2, GPIO. LOW)
GPIO.output(INB1, GPIO.LOW)
GPIO.output(INB2, GPIO.LOW)
GPIO.output(PWM_A, GPIO.LOW)
GPIO.output(PWM_B, GPIO.LOW)
exit(0)