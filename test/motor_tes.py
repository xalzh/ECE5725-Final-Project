from multiprocessing import Process, Queue, Value, Lock, Array
import RPi.GPIO as GPIO # Import GPIO library
import time   # Import time library for time control
import sys
import numpy as np
import pigpio
import cv2
from datetime import datetime

start = time.time()
# Set GPIO Pins to be referred in Broadcom SOC channel
GPIO.setmode(GPIO.BCM)

pin_hori = 13
pin_vert = 12

pi_hw = pigpio.pi() 
f = 50

pi_hw.hardware_PWM(pin_hori, f, 36000)
time.sleep(1)
pi_hw.hardware_PWM(pin_hori, f, 115000) #36000-115000
time.sleep(1)

pi_hw.hardware_PWM(pin_hori, f, 75500)#up max 35000-105000
time.sleep(1)
pi_hw.hardware_PWM(pin_hori, f, 0)
pi_hw.hardware_PWM(pin_vert, f, 0)
#pi_hw.hardware_PWM(pin2, f, 0)

'''
time.sleep(1)
for i in range(40000):
    start = start+1
    pi_hw.hardware_PWM(pin2, f, start)
    print(start)
pi_hw.hardware_PWM(pin2, f, 140000)#down max
time.sleep(1)
pi_hw.hardware_PWM(pin2, f, 0)'''
'''
pi_hw.hardware_PWM(motorPinR, f, 115000)#left max
time.sleep(2)
pi_hw.hardware_PWM(motorPinR, f, 84000)#center
time.sleep(2)
pi_hw.hardware_PWM(motorPinR, f, 53000)#right max
time.sleep(2)
pi_hw.hardware_PWM(motorPinR, f, 0)
#range 62000
'''