from multiprocessing import Process, Queue, Value, Lock, Array, Manager
import subprocess
import threading
import web
from IMU import bno055
from Update_Screen import Screen
from UI import UserInterface
from camera import Camera
from PID import pid
import cv2
import time
import RPi.GPIO as GPIO
import pigpio
import os
from threading import Lock

def button17_callback(channel):
    global mode, max_mode_num, screen, shared_data, lock
    with lock:
        shared_data['mode_idx'] += 1
        if shared_data['mode_idx'] >= max_mode_num:
            shared_data['mode_idx'] = 0
        print("button 17 is pressed! Current mode is:", mode[shared_data['mode_idx']])
        camera.set_message("Current Mode: " + mode[shared_data['mode_idx']])
        shared_data['17'] = True

def button22_callback(channel):
    global tracking_status, camera, stabilize, shared_data, lock
    print("button 22 is pressed!!!")
    shared_data['22'] = True
    if shared_data['mode_idx'] == 1: # object tracking mode
        tracking_status = not tracking_status
        shared_data['tracking_status'] = tracking_status
        if tracking_status:
            print("Resume tracking...")
            ret, frame = camera.cap.read()
            camera.resume_tracking(frame)
            camera.set_message("Resume Tracking")
        else:
            print("Pause tracking....")
            camera.reset_tracking()
            camera.set_message("Pause Tracking")
    if shared_data['mode_idx'] == 2: # stabilization mode
        print("Start stabilization")
        camera.set_message("Start stabilization")
        stabilize = True
        
def button23_callback(channel):
    global camera, tracking_status, stabilize, init_heading, init_pitch, init_roll, shared_data, lock
    print("button 23 is pressed!!!")
    shared_data['23'] = True
    if shared_data['mode_idx'] == 1:
        try:
            camera.set_message("Cancel tracking")
            camera.mosse.finger_touch = not camera.mosse.finger_touch
            camera.mosse.initial_roi_frame = None
            camera.cancel()
            tracking_status = True
            shared_data['tracking_status'] = tracking_status
            print("Cancel tracking...")
        except:
            print("there is no tracking object...")
    if shared_data['mode_idx'] == 2: # stabilization mode
        stabilize = False
        print("cancel stabilization...")
        camera.set_message("Cancel stabilization")
        init_heading, init_pitch, init_roll = 0, 0, 0

def button27_callback(channel):
    global exit_signal, shared_data, lock, p
    shared_data['27'] = True
    print("button 27 is pressed!!!")
    print("program will exit")
    exit_signal = True
    camera.set_message("Program will exit")
    time.sleep(1)

def main():
    global mode, max_mode_num, tracking_status, camera, exit_signal, ui, screen, recording, stabilize, init_heading, init_pitch, init_roll, shared_data, lock

    screen = Screen()
    ready_event = threading.Event()
    camera = Camera(ready_event, cap, is_mode1=False, is_mode2=False, screen=screen)
    
    #recording = Recording(ready_event, cap)
    camera.start()
    #recording.start()
    imu = bno055()

    # Set up PID controllers for horizontal and vertical motors
    #pid_hori_mode2 = pid(Kp=9, Ki=2.5, Kd=0.3, setpoint=320)
    #pid_vert_mode2 = pid(Kp=7, Ki=3, Kd=0.1, setpoint=240)
    pid_hori_mode2 = pid(Kp=6, Ki=1, Kd=0.3, setpoint=320)
    pid_vert_mode2 = pid(Kp=5, Ki=2, Kd=0.3, setpoint=240)
    #pid_hori_mode2 = pid(Kp=10, Ki=2, Kd=0.2, setpoint=320)
    #pid_vert_mode2 = pid(Kp=9, Ki=3, Kd=0, setpoint=240)

    # preset the flags for the mode and push buttons
    stabilize = False
    tracking_status = True
    shared_data['tracking_status'] = tracking_status
    shared_data['tracking_initialized'] = False
    shared_data['tracking_paused'] = False
    exit_signal = False # if button 27 is pressed, it will become True

    init_heading = 0
    init_pitch = 0
    init_roll = 0

    mode = ["Manual", "Object Tracking", "Stablization"]
    max_mode_num = 3
    camera.set_message("Current Mode: " + mode[shared_data['mode_idx']])

    GPIO.add_event_detect(17, GPIO.FALLING, callback=lambda channel: button17_callback(channel), bouncetime=200)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=lambda channel: button22_callback(channel), bouncetime=200)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=lambda channel: button23_callback(channel), bouncetime=200)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=lambda channel: button27_callback(channel), bouncetime=200)

    # Perform calculations with the roi variable in the main function
    ui = UserInterface(pi, cap)

    while not camera.ready_event.is_set() and not exit_signal:
        if screen.frame is not None:
            web.q.put(screen.get_processed_frame())
        
        with lock:
            if shared_data['mode_change_signal'] == True:
                print(shared_data['mode_idx'])
                camera.set_message("Current Mode: " + mode[shared_data['mode_idx']])
                shared_data['mode_change_signal'] = False
            
            if shared_data['functional'] == "exit":
                button27_callback(27)
                shared_data['functional'] = None
            elif shared_data['functional'] == "pause-tracking" or shared_data['functional'] == "start-stabilization":
                button22_callback(22)
                shared_data['functional'] = None
            elif shared_data['functional'] == "cancel-tracking" or shared_data['functional'] == "cancel-stabilization":
                button23_callback(23)
                shared_data['functional'] = None

            camera.is_mode1 = shared_data['mode_idx'] == 1 # if current mode is 1 send True signal to Camera
            camera.is_mode2 = shared_data['mode_idx'] == 2
            if shared_data['mode_idx'] == 0: # Manual
                ui.mode1(pin_hori, pin_vert, shared_data)
                shared_data['manual_coor'] = None
            elif shared_data['mode_idx'] == 1: # Object Tracking
                if shared_data['coordinates'][0] is not None and shared_data['coordinates'][1] is not None:
                    x1 = shared_data['coordinates'][0]['x']
                    y1 = shared_data['coordinates'][0]['y']
                    x2 = shared_data['coordinates'][1]['x']
                    y2 = shared_data['coordinates'][1]['y']
                    camera.mosse.selected_roi = True
                    camera.mosse.roi = [(min([x1,x2]), min([y1,y2])),(max([x1,x2]), max([y1,y2]))]
                    shared_data['coordinates'] = [None, None]  # reset the coordinates in shared_data
                if camera.selected_roi:
                    ui.mode2(camera, pid_hori_mode2, pid_vert_mode2, pin_hori, pin_vert)
            elif shared_data['mode_idx'] == 2: # Stabilization
                if stabilize:
                    if ui.init_heading is None or ui.init_pitch is None or ui.init_roll is None:
                        imu_data = imu.read_bno_data()
                        ui.init_heading, ui.init_roll, ui.init_pitch = imu_data['euler']
                        pid_hori_mode3 = pid(Kp=100, Ki=5, Kd=1, setpoint=ui.init_heading)
                        pid_vert_mode3 = pid(Kp=100, Ki=5, Kd=1, setpoint=ui.init_pitch)
                        ui.previous_heading = ui.init_heading
                        ui.previous_pitch = ui.init_pitch
                    ui.mode3(camera, imu, pid_hori_mode3, pid_vert_mode3, pin_hori, pin_vert)

        # Add a small sleep interval to reduce CPU usage
        time.sleep(0.02)

    print(exit_signal)
    camera.stop()
    #recording.stop()
    # Wait for the camera thread to finish
    camera.join()
    #recording.join()


if __name__ == "__main__":
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
    pi.hardware_PWM(pin_hori, f, 75500)
    pi.hardware_PWM(pin_vert, f, 70000)

    subprocess.call(["python", "reset.py"]) # release all processes that take camera0
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    lock = Lock()
    
    # Start the Flask application in a new process
    manager = Manager()
    shared_data = manager.dict()
    shared_data['17'] = False
    shared_data['22'] = False
    shared_data['23'] = False
    shared_data['27'] = False
    shared_data['mode_change_signal'] = False
    shared_data['functional'] = None
    shared_data['mode_idx'] = 0
    shared_data['coordinates'] = [None, None]
    shared_data['manual_coor'] = None
    web.shared_data = shared_data
    web.lock = lock
    p = Process(target=web.app.run, kwargs={'host': '0.0.0.0', 'port': 8000})
    p.start()

    main()

    # When the main program finishes, reset the models to not moving
    pi.hardware_PWM(pin_hori, f, 0)
    pi.hardware_PWM(pin_vert, f, 0)
    cap.release()
    cv2.destroyAllWindows()
    p.terminate()
    print("bye~")
    exit(0)


