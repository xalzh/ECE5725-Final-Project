"""
5/11/2023 by Zehao Li

This program defines a class for the BNO055 9-DOF sensor. The class provides functionality to initialize the sensor,
set its parameters, and read different types of sensor data including temperature, Euler angles, quaternion,
and calibration status.
"""
import Adafruit_BNO055.BNO055 as BNO055


class bno055():
    def __init__(self):
        super()
        # Initialize BNO055 sensor
        self.bno = BNO055.BNO055(busnum=1)
        # Set update frequency
        self.BNO_UPDATE_FREQUENCY_HZ = 50
        # Set axis remap for BNO055 sensor
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
        # Read data from BNO055 sensor
        temp = self.bno.read_temp()
        heading, roll, pitch = self.bno.read_euler()
        x, y, z, w = self.bno.read_quaternion()
        sys, gyro, accel, mag = self.bno.get_calibration_status()
        status, self_test, error = self.bno.get_system_status(run_self_test=False)
        if error != 0:
            print("Error! Value: {0}".format(error))
        # Pack all data into a dictionary for return
        data = {
            'euler': (heading, roll, pitch),
            'temp': temp,
            'quaternion': (x, y, z, w),
            'calibration': (sys, gyro, accel, mag),
        }
        return data
