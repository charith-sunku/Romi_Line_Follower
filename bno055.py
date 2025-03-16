#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 11:22:55 2025

@author: Tomas Franco

Purpose: Provides a driver for the BNO055 sensor. This module enables:
         - Sensor initialization and mode configuration,
         - Reading Euler angles (heading) and gyroscope data,
         - Retrieving and setting calibration coefficients,
         - Setting an offset for heading corrections, and
         - Computing the heading error relative to a target angle.
"""

# ---------
# Imports
# ---------
import pyb

# ---------------------------------
# BNO055 Sensor Driver Class
# ---------------------------------
class BNO055:
    # Register addresses and operating modes (refer to datasheet for details)
    CHIP_ID = 0x00 
    OPR_MODE = 0x3D 
    CALIB_STAT = 0x35 
    EULER_DATA_ADDR = 0x1A  # Starting register for Euler angles (heading, roll, pitch)
    GYR_DATA_ADDR = 0x14    # Starting register for gyroscope data (angular velocity)
    CALIB_DATA_ADDR = 0x55  # Starting register for calibration coefficients

    # Operating mode definitions (example values)
    CONFIGMODE = 0x00 
    NDOF_MODE = 0x0C  # 9DOF fusion mode

    def __init__(self, i2c, address=0x28):
        """
        Initialize the BNO055 sensor using a pyb.I2C object in CONTROLLER mode.
        Default I2C address is typically 0x28 or 0x29.
        Checks CHIP_ID to verify proper communication and sets up the sensor mode.
        """
        self.i2c = i2c
        self.address = address
        # Optionally check CHIP_ID to ensure sensor communication.
        chip_id = self._read_register(BNO055.CHIP_ID)[0]
        expected_chip_id = 0xA0  # Replace with correct value from datasheet if needed.
        if chip_id != expected_chip_id:
            raise Exception("BNO055 not found (chip ID mismatch).")
        # Set sensor to CONFIGMODE for configuration.
        self.set_mode(BNO055.CONFIGMODE)
        pyb.delay(20)
        # Set sensor to NDOF_MODE for 9DOF fusion operation.
        self.set_mode(BNO055.NDOF_MODE)
        pyb.delay(30)
        self.offset = 0

    def _read_register(self, reg, nbytes=1):
        """
        Read 'nbytes' starting from register 'reg'.
        Returns the read data as a bytes object.
        """
        return self.i2c.mem_read(nbytes, self.address, reg)
    
    def _write_register(self, reg, data):
        """
        Write data to the specified register 'reg'.
        'data' can be an integer or a bytes/bytearray object.
        """
        self.i2c.mem_write(data, self.address, reg)
    
    def set_mode(self, mode):
        """
        Change the operating mode of the sensor.
        For fusion mode changes, refer to the datasheet for correct mode values.
        """
        self._write_register(BNO055.OPR_MODE, mode)
        # Allow time for the mode change to take effect.
        pyb.delay(30)
    
    def get_calibration_status(self):
        """
        Read and return the calibration status byte from the sensor.
        The returned dictionary contains calibration status for:
            - System ('sys')
            - Gyroscope ('gyro')
            - Accelerometer ('accel')
            - Magnetometer ('mag')
        """
        status = self._read_register(BNO055.CALIB_STAT)[0]
        calib = {
            "sys": (status >> 6) & 0x03,
            "gyro": (status >> 4) & 0x03,
            "accel": (status >> 2) & 0x03,
            "mag": status & 0x03
        }
        return calib
    
    def get_calibration_coefficients(self):
        """
        Retrieve calibration coefficients from the sensor.
        Typically reads 22 bytes from the calibration data register.
        Returns a bytes object containing the coefficients.
        """
        coeffs = self._read_register(BNO055.CALIB_DATA_ADDR, 22)
        return coeffs
    
    def set_calibration_coefficients(self, coeffs):
        """
        Write pre-recorded calibration coefficients to the sensor.
        'coeffs' should be a bytes/bytearray object with a length of 22 bytes.
        Raises a ValueError if the length is incorrect.
        """
        if len(coeffs) != 22:
            raise ValueError("Calibration data must be 22 bytes long.")
        self._write_register(BNO055.CALIB_DATA_ADDR, coeffs)
    
    def read_euler_angles(self):
        """
        Read Euler angles (heading, roll, pitch) from the sensor.
        Returns the heading as a float (degrees).
        Note: Only heading is computed; roll and pitch are commented.
        """
        data = self._read_register(BNO055.EULER_DATA_ADDR, 2) #Change to 5 if need more
        # Convert raw bytes to heading (assuming little-endian, scale factor = 1/16)
        heading = (data[0] | (data[1] << 8)) / 16.0
        # roll  = (data[2] | (data[3] << 8)) / 16.0  # Uncomment if needed.
        # pitch = (data[4] | (data[5] << 8)) / 16.0  # Uncomment if needed.
        return (heading)
    
    def read_angular_velocity(self):
        """
        Read gyroscope data (angular velocity) from the sensor.
        Returns a tuple (x, y, z) representing angular velocity (degrees per second).
        Uses an example scale factor; verify with the datasheet.
        """
        data = self._read_register(BNO055.GYR_DATA_ADDR, 6)
        scale = 16.0  # Example scale factor; confirm with datasheet.
        x = (data[0] | (data[1] << 8)) / scale
        y = (data[2] | (data[3] << 8)) / scale
        z = (data[4] | (data[5] << 8)) / scale
        return (x, y, z)
    
    def set_offset(self):
        """
        Set the current heading as the offset.
        This offset is used to correct future heading readings.
        """
        heading = self.read_euler_angles()
        self.offset = heading
        
    def get_corrected_heading(self):
        """
        Return the current heading adjusted by the previously set offset.
        The result is normalized to a 0-359° range.
        """
        raw_heading = self.read_euler_angles()
        corrected_heading = (raw_heading - self.offset + 360) % 360
        return corrected_heading
    
    def compute_heading_error(self, target_heading):
        """
        Compute the minimal angular difference between the corrected heading and a target heading.
        Returns an error value in the range -180° to +180°.
        """
        heading = self.get_corrected_heading()
        error = ((heading - target_heading + 180) % 360) - 180
        return error
