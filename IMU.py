import time
import board
import Adafruit_BNO055.BNO055 as BNO055
import math

class bno055():
    def __init__(self):
        super()
        self.bno = BNO055.BNO055(busnum=1)
        self.BNO_UPDATE_FREQUENCY_HZ = 50
        self.BNO_AXIS_REMAP = {
            'x': BNO055.AXIS_REMAP_X,
            'y': BNO055.AXIS_REMAP_Z,
            'z': BNO055.AXIS_REMAP_Y,
            'x_sign': BNO055.AXIS_REMAP_POSITIVE,
            'y_sign': BNO055.AXIS_REMAP_POSITIVE,
            'z_sign': BNO055.AXIS_REMAP_NEGATIVE,
        }
        if not self.bno.begin():
            raise RuntimeError("Failed to initialize BNO055!")
        self.bno.set_axis_remap(**self.BNO_AXIS_REMAP)

    def read_bno_data(self):
        temp = self.bno.read_temp()
        heading, roll, pitch = self.bno.read_euler()
        x, y, z, w = self.bno.read_quaternion()
        sys, gyro, accel, mag = self.bno.get_calibration_status()
        status, self_test, error = self.bno.get_system_status(run_self_test=False)

        if error != 0:
            print("Error! Value: {0}".format(error))

        data = {
            'euler': (heading, roll, pitch),
            'temp': temp,
            'quaternion': (x, y, z, w),
            'calibration': (sys, gyro, accel, mag),
        }
        return data
