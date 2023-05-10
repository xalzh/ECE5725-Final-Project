import smbus
import math
import time

class MPU6050:
    def __init__(self):
        # MPU6050 Registers and addresses
        self.DEVICE_ADDR = 0x68
        self.PWR_MGMT_1 = 0x6B
        self.SMPLRT_DIV = 0x19
        self.CONFIG = 0x1A
        self.GYRO_CONFIG = 0x1B
        self.INT_ENABLE = 0x38
        self.ACCEL_XOUT_H = 0x3B
        self.ACCEL_YOUT_H = 0x3D
        self.ACCEL_ZOUT_H = 0x3F
        self.GYRO_XOUT_H = 0x43
        self.GYRO_YOUT_H = 0x45
        self.GYRO_ZOUT_H = 0x47

        # Initialize I2C bus
        self.bus = smbus.SMBus(1)
    
    # Initialize MPU6050
    def MPU_Init(self):
        self.bus.write_byte_data(self.DEVICE_ADDR, self.PWR_MGMT_1, 0)
        self.bus.write_byte_data(self.DEVICE_ADDR, self.SMPLRT_DIV, 7)
        self.bus.write_byte_data(self.DEVICE_ADDR, self.CONFIG, 0)
        self.bus.write_byte_data(self.DEVICE_ADDR, self.GYRO_CONFIG, 24)
        self.bus.write_byte_data(self.DEVICE_ADDR, self.INT_ENABLE, 1)
    
    # Read data from MPU6050
    def read_raw_data(self,addr):
        high = self.bus.read_byte_data(self.DEVICE_ADDR, addr)
        low = self.bus.read_byte_data(self.DEVICE_ADDR, addr+1)
        value = ((high << 8) | low)
        if(value > 32768):
            value = value - 65536
        return value
    
    def get_rotations(self):
        self.MPU_Init()
        accel_x = self.read_raw_data(self.ACCEL_XOUT_H)
        accel_y = self.read_raw_data(self.ACCEL_YOUT_H)
        accel_z = self.read_raw_data(self.ACCEL_ZOUT_H)

        gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
        gyro_y = self.read_raw_data(self.GYRO_YOUT_H)
        gyro_z = self.read_raw_data(self.GYRO_ZOUT_H)

        # Calculate angles
        accel_x_angle = math.atan2(accel_y, accel_z) * 180 / math.pi
        accel_y_angle = math.atan2(accel_x, accel_y) * 180 / math.pi
        accel_z_angle = math.atan2(accel_x, accel_z) * 180 / math.pi
        
        return accel_x_angle, accel_y_angle, accel_z_angle



    