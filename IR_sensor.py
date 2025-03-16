# -*- coding: utf-8 -*-
"""
Created on 3/01/2024

@author: Charith Sunku

Purpose: Provides a driver for the IR sensor array used for line following.
         This module includes:
             - IR_Single class: Handles individual IR sensor readings via ADC.
             - IR_Array class: Aggregates multiple IR_Single sensors, reads and normalizes
               raw sensor values based on dark/light calibrations, computes a centroid, and
               provides calibration functions.
"""

# ---------
# Imports
# ---------
from pyb import Pin, ADC
import time

# ----------------------------------
# IR_Single Class: Single IR Sensor Interface
# ----------------------------------
class IR_Single:
    def __init__(self, pin, index):
        """
        Initialize an individual IR sensor.
        Args:
            pin (str): The pin identifier for the sensor.
            index (int): Index for sensor identification.
        """
        self.IR_PIN = Pin(pin, mode=Pin.IN)
        self.IR_SENSOR = ADC(self.IR_PIN)
        self.IR_INDEX = index
        self.value_list = []  # To store ADC readings if needed.
    
    def getADC(self):
        """
        Return the ADC object for the sensor.
        """
        return self.IR_SENSOR
    
    def getValue(self):
        """
        Return the current ADC reading from the sensor.
        """
        return self.IR_SENSOR.read()

# ----------------------------------
# IR_Array Class: Aggregates Multiple IR Sensors
# ----------------------------------
class IR_Array:
    """
    IR sensor array driver.

    Initializes multiple IR_Single sensors based on a provided list of pins.
    Controls sensor enabling via two digital pins and provides methods for:
         - Reading raw sensor values.
         - Normalizing sensor readings based on dark/light calibration values.
         - Computing a centroid from normalized sensor values.
         - Performing dark and light calibrations.
    """
    def __init__(self, irPinList, evenPin, oddPin):
        """
        Initialize the IR sensor array.
        Args:
            irPinList (list): List of pin identifiers for each IR sensor.
            evenPin (str): Pin for controlling even sensors.
            oddPin (str): Pin for controlling odd sensors.
        """
        self.sensor_list = []
        for pinID in range(len(irPinList)):
            new_sensor = IR_Single(irPinList[pinID], pinID + 1)
            self.sensor_list.append(new_sensor)
        # Initialize control pins (dimming not yet implemented).
        self.EVEN = Pin(evenPin, mode=Pin.OUT_PP, value=0)
        self.ODD = Pin(oddPin, mode=Pin.OUT_PP, value=0)
        self.centroid = 0
        # Calibration lists for dark and light readings.
        self.darkValue = []
        self.lightValue = []
        self.raw_value_list = []
        self.normalized_value_list = []
    
    def readArray(self):
        """
        Enable sensors, read raw ADC values from all sensors, then disable sensors.
        """
        self.enable()
        time.sleep_us(50) #Delay to allow the sensors to acclimate
        self.raw_value_list = []
        for idx in range(len(self.sensor_list)):
            self.raw_value_list.append(self.sensor_list[idx].getValue())
        #Get the values from each IR reading and append to the list
        self.disable() #Disable to conserve battery life
    
    def normalize(self):
        """
        Normalize the raw ADC values using calibrated dark and light values.
        Each value is scaled to the 0-1 range.
        """
        self.normalized_value_list = []
        normalized_value = 0
        for idx in range(len(self.raw_value_list)):
            try:
                normalized_value = round((((self.raw_value_list[idx] - self.lightValue[idx]) /
                                            (self.darkValue[idx] - self.lightValue[idx]))), 5)
            except ZeroDivisionError:
                normalized_value = 0.5
            if normalized_value > 1:
                self.normalized_value_list.append(1)
            elif normalized_value < 0:
                self.normalized_value_list.append(0)
            else:
                self.normalized_value_list.append(normalized_value)
    
    def updateIR(self):
        """
        Read and normalize sensor values.
        Returns:
            List of normalized sensor values.
        """
        self.readArray()
        self.normalize()
        return self.normalized_value_list
    
    def getList(self):
        """
        Return the latest normalized sensor values.
        """
        return self.normalized_value_list
    
    def getCentroid(self):
        """
        Compute and return the centroid of the sensor array.
        The centroid is a weighted average of sensor indices based on normalized values.
        Returns a default value of 7 if all sensor readings are zero.
        """
        val = 0
        for index in range(len(self.normalized_value_list)):
            val += (index + 1) * self.normalized_value_list[index]
        try:
            return val / (sum(self.normalized_value_list))
        except ZeroDivisionError:
            return 7
    
    def calibrateDark(self):
        """
        Perform dark calibration:
        Enable sensors, wait briefly, read raw values, and store them as dark calibration values.
        Returns the dark calibration values.
        """
        if self.darkValue != None:
            self.enable()
            time.sleep_us(200)
            self.readArray()
            self.darkValue = self.raw_value_list
            self.disable()
        return self.darkValue
    
    def calibrateLight(self):
        """
        Perform light calibration:
        Enable sensors, wait briefly, read raw values, and store them as light calibration values.
        Returns the light calibration values later used for normalization.
        """
        if self.lightValue != None:
            self.enable()
            time.sleep_us(200)
            self.readArray()
            self.lightValue = self.raw_value_list
            self.disable()
        return self.lightValue

    def enable(self):
        """
        Enable the IR sensors by setting control pins HIGH.
        """
        self.EVEN.value(1)
        self.ODD.value(1)
    
    def disable(self):
        """
        Disable the IR sensors by setting control pins LOW.
        """
        self.EVEN.value(0)
        self.ODD.value(0)
