# -*- coding: utf-8 -*-"""Created on Wed Mar  5 13:35:18 2025@author: Charith Sunku and Tomas FrancoPurpose: Implements a bump sensor driver for the ROMI platform.         This module provides:             - The Bumpy class: Wraps a single bump sensor by initializing its pin               and attaching a falling-edge interrupt.             - The Bumpies class: Aggregates multiple bump sensors to check and reset               their status collectively."""# ---------# Imports# ---------from pyb import Pin, ExtInt# --------------------------------# Bumpy Sensor Class# --------------------------------class Bumpy:    def __init__(self, Bump_Pin):        """        Initialize a single bump sensor.        Sets up the specified pin for input with no pull and attaches an interrupt         on the falling edge to detect a bump.        """        self.Bump_Pin = Pin(Bump_Pin, Pin.IN, pull=Pin.PULL_NONE)        # Attach falling-edge interrupt with an internal pull-up resistor.        ExtInt(self.Bump_Pin, ExtInt.IRQ_FALLING, Pin.PULL_UP, self.bump_interrupt)        self.HIT = False            def bump_interrupt(self, line):        """        Interrupt handler for the bump sensor.        Sets the sensor's hit status to True when triggered.        """        self.HIT = True            def reset_status(self):        """        Reset the hit status of the bump sensor.        """        self.HIT = False            def get_status(self):        """        Retrieve the current status of the bump sensor.        Returns True if the sensor has been triggered.        """        return self.HIT# =============================================================================#  Mapping for reference:#  Bump 0 - PB12#  Bump 1 - PB11#  Bump 2 - PB6#  Bump 3 - PC7#  Bump 4 - PB10#  Bump 5 - PB15# =============================================================================# ------------------------------------------# Bumpies Class: Aggregates Multiple Bump Sensors# -----------------------------------------class Bumpies:    def __init__(self, Pin_List):        """        Initialize multiple bump sensors using a list of pin names.        Each pin in the list is used to create a Bumpy sensor instance.        """        self.bump_list = []        for pin_name in Pin_List:            self.bump_list.append(Bumpy(pin_name))            def get_status(self):        """        Check all bump sensors for a hit.        Returns True if any bump sensor is triggered.        """        for bumpy in self.bump_list:            if bumpy.get_status():                return True        return False            def reset_status(self):        """        Reset the hit status for all bump sensors.        """        for bumpy in self.bump_list:            bumpy.reset_status()