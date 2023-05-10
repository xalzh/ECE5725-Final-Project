import time
import board
import Adafruit_BNO055.BNO055 as BNO055
import RPi.GPIO as GPIO
import pigpio
from pid import pid
import json

def normalize_angle(angle):
    return (angle + 360) % 360

def convert_angles(heading, roll, pitch):
    # Convert heading (x) to 0-360 degrees
    x = normalize_angle(heading)
    # Convert roll (y) to 0-360 degrees
    if roll < 0:
        y = normalize_angle(roll + 180)
    else:
        y = normalize_angle(roll)
    # Convert pitch (z) to 0-360 degrees
    z = normalize_angle(pitch)
    return x, y, z


GPIO.setmode(GPIO.BCM)
pin_hori = 13
pin_vert = 12
pi = pigpio.pi()
f = 50
pi.hardware_PWM(pin_hori, f, 75500)
pi.hardware_PWM(pin_vert, f, 70000)
time.sleep(1)

bno = BNO055.BNO055(busnum=1)
# Load calibration data
with open("calibration.json", "r") as file:
    calibration_data = json.load(file)
bno.set_calibration(calibration_data)

init_heading, init_roll, init_pitch = bno.read_euler()
print(init_heading)
previous_heading = init_heading

time.sleep(1)
pid_hori = pid(Kp=50, Ki=1, Kd=0.7, setpoint=init_heading)
pid_vert = pid(Kp=30, Ki=1, Kd=0.7, setpoint=init_pitch)

# Main loop
while True:
    # Read the current orientation
    bno.set_calibration(calibration_data)
    heading, roll, pitch = bno.read_euler()
    #heading, roll, pitch = convert_angles(heading, roll, pitch)
    print("\n")
    print("Initial heading: {}, current heading: {}".format(init_heading,heading))
    print("Initial roll: {}, current roll: {}".format(init_roll,roll))
    print("Initial pitch: {}, current pitch: {}".format(init_pitch,pitch))

    if heading is not None and pitch is not None:
        # Calculate the error in roll and pitch
        roll_error = (heading - init_heading + 180) % 360 - 180
        pitch_error = (pitch - init_pitch + 180) % 360 - 180

        interval_delta = (heading - previous_heading + 180) % 360 - 180
        print(interval_delta)
        print(roll_error)
        if abs(interval_delta) >= 30:
            init_heading = heading
            roll_error = 0
        

        # Calculate the PID output for roll and pitch
        pid_hori_output = pid_hori.update(roll_error, 0.02)
        pid_vert_output = pid_vert.update(pitch_error, 0.02)

        current_pwm_hori = pi.get_PWM_dutycycle(pin_hori)
        #print(current_pwm_hori)
        current_pwm_vert = pi.get_PWM_dutycycle(pin_vert)

        new_pwm_hori = current_pwm_hori + pid_hori_output
        #print(new_pwm_hori)
        '''
        if 36000 < new_pwm_hori < 115000:# left max 115000, right max 36000
            pi.hardware_PWM(pin_hori, f, int(new_pwm_hori))

        new_pwm_vert = current_pwm_vert + pid_vert_output
        if 35000 < new_pwm_vert < 105000:# up max 105000, down max 35000
            pi.hardware_PWM(pin_vert, f, int(new_pwm_vert))
        
        previous_heading, previous_roll, previous_pitch = heading, roll, pitch
        '''
    # Sleep for a while
    time.sleep(0.02)