import time
import board
import adafruit_icm20x
import math

class icm20948():
    def __init__(self):
        super()
        self.i2c = board.I2C()
        self.icm = adafruit_icm20x.ICM20948(self.i2c)

    def accel_angles(self, ax, ay, az):
        pitch = math.atan2(ay, math.sqrt(ax**2 + az**2)) * 180 / math.pi
        roll = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * 180 / math.pi
        return pitch, roll

    def yaw_angle(self, roll_rad, pitch_rad, mx, my, mz):
        cos_roll = math.cos(roll_rad)
        sin_roll = math.sin(roll_rad)
        cos_pitch = math.cos(pitch_rad)
        sin_pitch = math.sin(pitch_rad)

        Bx = mx * cos_pitch + mz * sin_pitch
        By = mx * sin_roll * sin_pitch + my * cos_roll - mz * sin_roll * cos_pitch
        yaw = math.atan2(-By, Bx) * 180 / math.pi

        if yaw < 0:
            yaw += 360

        return yaw

    def get(self):
        accel_data = self.icm.acceleration
        mag_data = self.icm.magnetic

        ax, ay, az = accel_data
        mx, my, mz = mag_data

        pitch, roll = self.accel_angles(ax, ay, az)
        pitch_rad, roll_rad = math.radians(pitch), math.radians(roll)
        yaw = self.yaw_angle(roll_rad, pitch_rad, mx, my, mz)

        return pitch, roll, yaw
