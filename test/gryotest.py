import smbus
import time
import math
from multiprocessing import Process, Queue, Value, Lock, Array
import RPi.GPIO as GPIO # Import GPIO library
import time   # Import time library for time control
import sys
import numpy as np
import pigpio
import cv2
from datetime import datetime
import threading


start = time.time()
# Set GPIO Pins to be referred in Broadcom SOC channel
GPIO.setmode(GPIO.BCM)
motorPinR = 13
pin2 = 12
pi_hw = pigpio.pi() 

f = 50

# Register addresses
POWER_MANAGEMENT_1 = 0x6B
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F

def read_word_2c(bus, address, register):
    high = bus.read_byte_data(address, register)
    low = bus.read_byte_data(address, register+1)
    value = (high << 8) + low
    if (value >= 0x8000):
        return -((65535 - value) + 1)
    else:
        return value

def get_rotation(bus, address):
    accel_x = read_word_2c(bus, address, ACCEL_XOUT_H)
    accel_y = read_word_2c(bus, address, ACCEL_YOUT_H)
    accel_z = read_word_2c(bus, address, ACCEL_ZOUT_H)

    x_angle = math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2))
    y_angle = math.atan2(accel_x, math.sqrt(accel_y**2 + accel_z**2))

    x_roll = math.degrees(x_angle)
    y_pitch = math.degrees(y_angle)

    return x_roll, y_pitch

def pwm_control():

    while True:
        x_roll, y_pitch = get_rotation(bus, mpu6050_address)
        #print(f"Roll (X-axis): {x_roll:.2f}°, Pitch (Y-axis): {y_pitch:.2f}°")
        time.sleep(0.1)
        if -90 <= x_roll < 0:
            pwm = 140000 + 50000/90*x_roll
            pi_hw.hardware_PWM(pin2, f, int(pwm))
        else:
            pi_hw.hardware_PWM(pin2, f, 140000)

def display_image():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Camera', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()




def main():
    pwm_thread = threading.Thread(target=pwm_control)
    pwm_thread.start()

    display_image()

    pwm_thread.join()
    pi_hw.stop()

           


if __name__ == "__main__":
    bus = smbus.SMBus(1)
    mpu6050_address = 0x68
    bus.write_byte_data(mpu6050_address, POWER_MANAGEMENT_1, 0)
    main()
