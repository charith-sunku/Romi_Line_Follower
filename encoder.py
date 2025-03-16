#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 13:55:40 2025

@author: Tomas Franco

Purpose: Provides a quadrature encoder decoding interface.
         This class tracks the encoder's accumulated position, computes the velocity,
         and handles counter overflows using a moving average of recent updates.
"""

# ---------
# Imports
# ---------
from time import ticks_us, ticks_diff  # For computing time differences in microseconds
from pyb import Timer, Pin
import math

# ------------------------------------
# Encoder Class for Quadrature Decoding
# ------------------------------------
class Encoder:
    '''A quadrature encoder decoding interface encapsulated in a Python class'''

    def __init__(self, tim, chA_pin, chB_pin):
         '''Initializes an Encoder object by setting up the timer and channels'''
         # Configure timer with maximum period and no prescaler.
         self.timer = Timer(tim, period=0xFFFF, prescaler=0)
         # Setup channels for quadrature encoding.
         self.timer.channel(1, pin=Pin(chA_pin), mode=Timer.ENC_AB)
         self.timer.channel(2, pin=Pin(chB_pin), mode=Timer.ENC_AB)
         
         self.position = 0          # Total accumulated position of the encoder.
         self.prev_count = 0        # Counter value from the most recent update.
         self.delta = 0             # Change in count between successive updates.
         self.delta_buffer = [0, 0, 0, 0, 0, 0]  # Buffer for recent delta values (for averaging).
         self.prev_time = 0         # Timestamp from the previous update (in µs).
         self.dt = 0                # Time difference between the last two updates.
         self.dt_buffer = [0, 0, 0, 0, 0, 0]     # Buffer for recent dt values (for averaging).
         self.conv_factor_rad = 2 * math.pi / 1440  # Conversion factor from counts to radians.
         
    def update(self):
        '''Performs one update cycle: computes time difference, handles counter overflow,
        averages delta values, and updates the total position.'''
        current_time = ticks_us()  # Get current time in microseconds.
        self.dt = ticks_diff(current_time, self.prev_time)
        # Update the dt buffer for averaging.
        self.dt_buffer.pop(0)
        self.dt_buffer.append(self.dt)
        
        current_count = self.timer.counter()  # Get current counter value.
        diff_count = current_count - self.prev_count
        # Handle counter underflow/overflow for a 16-bit counter.
        if diff_count < -32768:
            diff_count += 65536
        elif diff_count > 32768:
            diff_count -= 65536
        self.delta = diff_count
        # Update the delta buffer for averaging.
        self.delta_buffer.pop(0)
        self.delta_buffer.append(self.delta)
        
        # Update previous time and counter for the next update.
        self.prev_time = current_time
        self.prev_count = current_count
        
        # Compute the average delta from the buffered values.
        pos_avg = sum(self.delta_buffer) / 6
        # Accumulate the averaged delta into the total position.
        self.position += pos_avg
        
    def get_position(self):
         '''Returns the encoder's position converted to radians based on the conversion factor.'''
         position_rad = self.position * self.conv_factor_rad
         return position_rad

    def get_velocity(self):
         '''Calculates and returns the encoder's angular velocity (radians per second)
         using the averaged delta and time difference from recent updates.'''
         if self.dt == 0:
             return 0
         
         dt_avg = sum(self.dt_buffer) / 6
         pos_avg = sum(self.delta_buffer) / 6
         delta_rad = pos_avg * self.conv_factor_rad
         dt_s = dt_avg / 1000000  # Convert microseconds to seconds.
         return delta_rad / dt_s
     
    def get_time(self):
         '''Returns the most recent update time in seconds.'''
         return self.prev_time / 1000000
    
    def get_dt(self):
         '''Returns the latest time difference (dt) in seconds.'''
         return self.dt / 1000000

    def zero(self):
         '''Resets the total position to zero and updates the reference counter value.'''
         self.position = 0
         self.prev_count = self.timer.counter()
