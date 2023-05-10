import time
import board
import Adafruit_BNO055.BNO055 as BNO055
import RPi.GPIO as GPIO
import pigpio
from pid import pid
import json


GPIO.setmode(GPIO.BCM)
pin_hori = 13
pin_vert = 12
pi = pigpio.pi()
f = 50
pi.hardware_PWM(pin_hori, f, 75500)
pi.hardware_PWM(pin_vert, f, 70000)
time.sleep(1)

# Create and configure the BNO sensor connection.
# Uncomment the appropriate line for your hardware setup.
#bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)
#bno = BNO055.BNO055(rst='P9_12')
bno = BNO055.BNO055(busnum=1)

BNO_UPDATE_FREQUENCY_HZ = 50

BNO_AXIS_REMAP = {
    'x': BNO055.AXIS_REMAP_X,
    'y': BNO055.AXIS_REMAP_Z,
    'z': BNO055.AXIS_REMAP_Y,
    'x_sign': BNO055.AXIS_REMAP_POSITIVE,
    'y_sign': BNO055.AXIS_REMAP_POSITIVE,
    'z_sign': BNO055.AXIS_REMAP_NEGATIVE,
}

# Initialize BNO055 sensor.
if not bno.begin():
    raise RuntimeError("Failed to initialize BNO055!")
bno.set_axis_remap(**BNO_AXIS_REMAP)

def read_bno_data():
    temp = bno.read_temp()
    heading, roll, pitch = bno.read_euler()
    x, y, z, w = bno.read_quaternion()
    sys, gyro, accel, mag = bno.get_calibration_status()
    status, self_test, error = bno.get_system_status(run_self_test=False)

    if error != 0:
        print("Error! Value: {0}".format(error))

    data = {
        'euler': (heading, roll, pitch),
        'temp': temp,
        'quaternion': (x, y, z, w),
        'calibration': (sys, gyro, accel, mag),
    }
    return data

init_bno_data = read_bno_data()
init_heading, init_roll, init_pitch = init_bno_data['euler']
init_pitch = 180
print("initial_heading",init_heading)
print("initial_pitch",init_pitch)
previous_heading = init_heading

time.sleep(1)
pid_hori = pid(Kp=50, Ki=5, Kd=1, setpoint=init_heading)
pid_vert = pid(Kp=50, Ki=5, Kd=1, setpoint=init_pitch)

while True:
    print("\n\n\n\n\n\n\n")
    bno_data = read_bno_data()
    heading, roll, pitch = bno_data['euler']
    #print("heading:",heading)
    #print("roll:",roll)
    print("pitch:",pitch)

    if heading is not None and pitch is not None:
        # Calculate the error in roll and pitch
        heading_error = (heading - init_heading + 180) % 360 - 180
        pitch_error = (pitch - init_pitch + 180) % 360 - 180
        print("init_pitch:",init_pitch)
        print("pitch_error:",pitch_error)
        
        interval_delta = (heading - previous_heading + 180) % 360 - 180
        print(interval_delta)
        print("heading_error:",heading_error)
        print("pitch_error",pitch_error)
        if abs(interval_delta) >= 30:
            init_heading = heading
            roll_error = 0
        

        # Calculate the PID output for roll and pitch
        pid_hori_output = pid_hori.update(heading_error, 0.02)
        pid_vert_output = pid_vert.update(pitch_error, 0.02)

        current_pwm_hori = pi.get_PWM_dutycycle(pin_hori)
        #print(current_pwm_hori)
        current_pwm_vert = pi.get_PWM_dutycycle(pin_vert)

        new_pwm_hori = current_pwm_hori + pid_hori_output
        #print(new_pwm_hori)
        
        if 36000 < new_pwm_hori < 115000:# left max 115000, right max 36000
            pi.hardware_PWM(pin_hori, f, int(new_pwm_hori))

        new_pwm_vert = current_pwm_vert + pid_vert_output
        if 35000 < new_pwm_vert < 105000:# up max 105000, down max 35000
            pi.hardware_PWM(pin_vert, f, int(new_pwm_vert))
        
        previous_heading, previous_roll, previous_pitch = heading, roll, pitch
        
    # Sleep for a while
    time.sleep(0.02)




    time.sleep(0.02)
