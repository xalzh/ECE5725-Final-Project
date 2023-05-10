from multiprocessing import Process, Queue, Value, Lock, Array
import threading
from ICM20948 import icm20948
from camera import Camera
from PID import pid
import cv2
import time
import RPi.GPIO as GPIO
import pigpio
import os
import pygame
from pygame.locals import *


class UserInterface():
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.mouse.set_visible(False)
        self.lcd = pygame.display.set_mode((320, 240))
        pygame.display.update()
        self.touching = False
    
    def mode1_update_pwm(self):
        for event in pygame.event.get():
            if(event.type is MOUSEBUTTONDOWN):
                self.touching = True
            elif(event.type is MOUSEBUTTONUP):
                self.touching = False
        
        if self.touching is True:
            pos = pygame.mouse.get_pos()
            x, y = pos
            dx = x - 160
            dy = y - 120
            current_pwm_hori = pi.get_PWM_dutycycle(pin_hori)
            current_pwm_vert = pi.get_PWM_dutycycle(pin_vert)

            new_pwm_hori = current_pwm_hori - 5*dx
            new_pwm_vert = current_pwm_vert + 5*dy

            if 30000 < new_pwm_hori < 130000:# left max 130000, right max 30000
                pi.hardware_PWM(pin_hori, f, int(new_pwm_hori))
            if 50000 < new_pwm_vert < 130000:# up max 130000, down max 50000
                pi.hardware_PWM(pin_vert, f, int(new_pwm_vert))

    
    def mode_2_update_pwm(self, roi, delta_time, pid_hori, pid_vert):
        roi_center = [(roi[1][0] + roi[0][0]) / 2, (roi[1][1] + roi[0][1]) / 2]
        delta = [roi_center[0] - 160, roi_center[1] - 120]
        control_signal_hori = pid_hori.update(delta[0], delta_time)
        control_signal_vert = pid_vert.update(delta[1], delta_time)

        current_pwm_hori = pi.get_PWM_dutycycle(pin_hori)
        current_pwm_vert = pi.get_PWM_dutycycle(pin_vert)

        new_pwm_hori = current_pwm_hori - control_signal_hori
        if 30000 < new_pwm_hori < 130000:# left max 130000, right max 30000
            pi.hardware_PWM(pin_hori, f, int(new_pwm_hori))

        new_pwm_vert = current_pwm_vert + control_signal_vert
        if 50000 < new_pwm_vert < 130000:# up max 130000, down max 50000
            pi.hardware_PWM(pin_vert, f, int(new_pwm_vert))

    def mode1(self):
        self.mode1_update_pwm()

    def mode2(self, camera, pid_hori, pid_vert):
        roi, selected_roi = camera.get_roi()
        roi_lost = camera.get_roi_lost()
        if roi is not None and len(roi) == 2 and selected_roi is True and not roi_lost:
            self.mode_2_update_pwm(roi, 0.02, pid_hori, pid_vert)


def button17_callback(channel):
    global mode, max_mode_num
    mode += 1
    if mode > max_mode_num:
        mode = 1
    print("button 17 is pressed! Current mode is:", mode)


def button22_callback(channel):
    global tracking_status, camera, mode
    print("button 22 is pressed!!!")
    if mode == 2:
        tracking_status = not tracking_status
        if tracking_status:
            print("resume tracking...")
            ret, frame = camera.cap.read()
            camera.resume_tracking(frame)
        else:
            print("pause tracking....")
            camera.reset_tracking()


def button23_callback(channel):
    global camera, mode, tracking_status
    print("button 23 is pressed!!!")
    if mode == 2:
        print("cancel tracking...")
        camera.mosse.finger_touch = not camera.mosse.finger_touch
        camera.mosse.initial_roi_frame = None
        camera.cancel()
        tracking_status = True


def button27_callback(channel):
    global exit_signal
    print("button 27 is pressed!!!")
    print("program will exit")
    exit_signal = True


def main():
    global mode, max_mode_num, tracking_status, camera, exit_signal
    ready_event = threading.Event()
    camera = Camera(ready_event, cap, is_mode2=False)
    camera.start()

    # Set up PID controllers for horizontal and vertical motors
    pid_hori = pid(Kp=4, Ki=1, Kd=0.7, setpoint=320)
    pid_vert = pid(Kp=4, Ki=1, Kd=0.7, setpoint=240)

    # preset the flags for the mode and push buttons
    tracking_status = True
    exit_signal = False # if button 27 is pressed, it will become True
    mode = 1
    max_mode_num = 2

    GPIO.add_event_detect(17, GPIO.FALLING, callback=button17_callback, bouncetime=200)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=button22_callback, bouncetime=200)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=button23_callback, bouncetime=200)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=button27_callback, bouncetime=200)

    # Perform calculations with the roi variable in the main function
    ui = UserInterface()

    while not camera.ready_event.is_set() and not exit_signal:
        camera.is_mode2 = mode == 2 # if current mode is 2 send True signal to Camera
        if mode == 1:
            ui.mode1()
        elif mode == 2:
            if camera.selected_roi:
                ui.mode2(camera, pid_hori, pid_vert)

        # Add a small sleep interval to reduce CPU usage
        time.sleep(0.02)

    camera.stop()
    # Wait for the camera thread to finish
    camera.join()


if __name__ == "__main__":
    icm = icm20948()
    pitch, roll, yaw = icm.get()
    print(pitch, roll, yaw)  # print the direction for 3 axis, pitch and roll work but not yaw
    os.system('sudo killall pigpiod')
    os.system('sudo pigpiod')
    time.sleep(1)

    # initialize two motors
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # initialize two motors
    pin_hori = 13
    pin_vert = 12
    pi = pigpio.pi()
    f = 50
    pi.hardware_PWM(pin_hori, f, 70000)
    pi.hardware_PWM(pin_vert, f, 90000)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    main()


    # When the main program finishes, reset the models to not moving
    pi.hardware_PWM(pin_hori, f, 0)
    pi.hardware_PWM(pin_vert, f, 0)
    cap.release()
    cv2.destroyAllWindows()
    print("bye~")
    exit(0)


