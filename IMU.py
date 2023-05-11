"""
5/11/2023 by Zehao Li

This Python module defines a class 'bno055' which is responsible for interacting with the BNO055 sensor using the
Adafruit_BNO055 library. The BNO055 is a System in Package (SiP) that integrates a tri-axial 14-bit accelerometer,
a tri-axial 16-bit gyroscope with a range of ±2000 degrees per second, a tri-axial geomagnetic sensor, and a 32-bit
microcontroller running the BSX3.0 FusionLib software.

The main functionalities of the 'bno055' class are:
- Initialize the BNO055 sensor and set the appropriate axis mapping.
- Read data from the BNO055 sensor including temperature, euler angles, quaternion, and calibration status.
- The data is then returned in a dictionary format for further processing.

This module uses the Adafruit_BNO055 library for communication with the BNO055 sensor.
"""
import Adafruit_BNO055.BNO055 as BNO055


class bno055():
    def __init__(self):
        super()
        self.bno = BNO055.BNO055(busnum=1)
        self.BNO_UPDATE_FREQUENCY_HZ = 50
        # Configure the axis mapping of the BNO055 sensor.
        self.BNO_AXIS_REMAP = {
            'x': BNO055.AXIS_REMAP_X,
            'y': BNO055.AXIS_REMAP_Z,
            'z': BNO055.AXIS_REMAP_Y,
            'x_sign': BNO055.AXIS_REMAP_POSITIVE,
            'y_sign': BNO055.AXIS_REMAP_POSITIVE,
            'z_sign': BNO055.AXIS_REMAP_NEGATIVE,
        }
        # Initialize the BNO055 sensor. Raise an exception if the initialization fails.
        if not self.bno.begin():
            raise RuntimeError("Failed to initialize BNO055!")
        # Set the axis remap for the BNO055 sensor
        self.bno.set_axis_remap(**self.BNO_AXIS_REMAP)

    def read_bno_data(self):
        temp = self.bno.read_temp()
        heading, roll, pitch = self.bno.read_euler()
        x, y, z, w = self.bno.read_quaternion()
        sys, gyro, accel, mag = self.bno.get_calibration_status()
        status, self_test, error = self.bno.get_system_status(run_self_test=False)
        if error != 0:
            print("Error! Value: {0}".format(error))
        # Gather all the sensor readings into a dictionary and return to the main code.
        data = {
            'euler': (heading, roll, pitch),
            'temp': temp,
            'quaternion': (x, y, z, w),
            'calibration': (sys, gyro, accel, mag),
        }
        return data
