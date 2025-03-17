#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file bno055.py
#  @brief   Driver for the BNO055 9-DOF IMU using I2C.
#
#  This module implements a driver for the BNO055 sensor to read orientation,
#  calibration status, and gyroscope data over I2C.
#
#  @author  aidentheocheung
#  @date    2025-Feb-24
#

import pyb
import struct

## @class BNO055
#  @brief Driver for the BNO055 9-DOF IMU using I2C2 (PB11, PB10).
#
#  This class provides methods to initialize the sensor, verify its chip ID,
#  set its operating mode, and read sensor data including calibration status,
#  Euler angles, and gyroscope measurements.
#
class BNO055:
    # Default I2C Address
    ADDRESS = 0x28  

    # Register Addresses
    CHIP_ID = 0x00
    OPR_MODE = 0x3D
    CALIB_STAT = 0x35
    EULER_H_LSB = 0x1A
    GYRO_X_LSB = 0x14

    # Operating Modes
    CONFIG_MODE = 0x00
    NDOF_MODE = 0x0C  # Full sensor fusion mode

    # Expected Chip ID
    EXPECTED_CHIP_ID = 0xA0

    ## @brief Constructor for the BNO055 driver.
    #  @details Initializes the BNO055 sensor by checking the chip ID and setting
    #           the sensor to NDOF mode. Raises a RuntimeError if the sensor is not detected.
    #  @param i2c The I2C object used for communication with the sensor.
    def __init__(self, i2c):
        self.i2c = i2c
        # pyb.delay(1000)  # Ensure proper startup

        if not self.check_chip_id():
            raise RuntimeError("BNO055 not detected! Check wiring.")

        print("BNO055 detected successfully!")

        # Set to CONFIG mode, then to NDOF mode
        # self.set_mode(self.CONFIG_MODE)
        # pyb.delay(50)
        self.set_mode(self.NDOF_MODE)
        # pyb.delay(50)

    ## @brief Checks the chip ID of the BNO055 sensor.
    #  @details Reads the chip ID from the sensor and compares it to the expected value.
    #  @return True if the chip ID matches the expected value, False otherwise.
    def check_chip_id(self):
        chip_id = self.i2c.mem_read(1, self.ADDRESS, self.CHIP_ID)[0]
        return chip_id == self.EXPECTED_CHIP_ID

    ## @brief Sets the operating mode of the BNO055 sensor.
    #  @param mode The desired operating mode (e.g., CONFIG_MODE or NDOF_MODE).
    def set_mode(self, mode):
        self.i2c.mem_write(mode, self.ADDRESS, self.OPR_MODE)
        # pyb.delay(10)  # Allow transition time

    ## @brief Reads the calibration status of the sensor.
    #  @details Retrieves the calibration status for the system, gyroscope, accelerometer,
    #           and magnetometer. Each value is 1 if fully calibrated, 0 otherwise.
    #  @return A tuple (sys_cal, gyro_cal, accel_cal, mag_cal).
    def read_calibration_status(self):
        status = self.i2c.mem_read(1, self.ADDRESS, self.CALIB_STAT)[0]
        sys_cal = 1 if ((status >> 6) & 0x03) == 3 else 0
        gyro_cal = 1 if ((status >> 4) & 0x03) == 3 else 0
        accel_cal = 1 if ((status >> 2) & 0x03) == 3 else 0
        mag_cal = 1 if (status & 0x03) == 3 else 0
        return sys_cal, gyro_cal, accel_cal, mag_cal

    ## @brief Reads Euler angles from the sensor.
    #  @details Reads 6 bytes starting from the Euler heading register, then unpacks
    #           the heading, pitch, and roll values. The values are scaled by dividing by 16.0.
    #  @return A tuple (heading, pitch, roll) representing the Euler angles in degrees.
    def read_euler_angles(self):
        data = self.i2c.mem_read(6, self.ADDRESS, self.EULER_H_LSB)
        heading = struct.unpack('<h', data[0:2])[0] / 16.0
        pitch = struct.unpack('<h', data[2:4])[0] / 16.0
        roll = struct.unpack('<h', data[4:6])[0] / 16.0
        return heading, pitch, roll

    ## @brief Reads gyroscope data from the sensor.
    #  @details Reads 6 bytes starting from the gyroscope X-axis register, then unpacks
    #           the angular velocity values for the x, y, and z axes. The values are scaled
    #           by dividing by 16.0.
    #  @return A tuple (x, y, z) representing the gyroscope data in degrees per second.
    def read_gyro(self):
        data = self.i2c.mem_read(6, self.ADDRESS, self.GYRO_X_LSB)
        x = struct.unpack('<h', data[0:2])[0] / 16.0
        y = struct.unpack('<h', data[2:4])[0] / 16.0
        z = struct.unpack('<h', data[4:6])[0] / 16.0
        return x, y, z


