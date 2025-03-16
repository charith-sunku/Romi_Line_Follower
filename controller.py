# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 12:22:44 2025

@author: Charith Sunku

Purpose: Implements a PID controller class to compute a control action based on a reference
         value and measured feedback. It computes the proportional, integral, and derivative 
         terms for adjusting motor outputs.
"""

import time

# ----------------------------------
# Controller Class for PID Control
# ----------------------------------
class Controller:
    def __init__(self, reference_value, KP, *, KI=0, KD=0, dt=0.015):
        """
        Initialize the PID controller with the reference value and gains.
        Optional parameters:
            KI: Integral gain (default = 0)
            KD: Derivative gain (default = 0)
            dt:  Time step (default = 0.015)
        """
        self.KP = KP
        self.KI = KI
        self.KD = KD
        self.reference = reference_value  # Desired setpoint
        self.measured = 0                 # Latest measured value
        self.error = [0, 0]               # [previous error, current error]
        self.integral_error = 0           # Cumulative error for integral action
        self.derivative_error = 0         # Rate of change of error for derivative action
        self.actuation_effor = 0          # (Not used in current implementation)
        self.dt = dt                      # Time step for integration and differentiation
        self.prev_time = 0                # To record previous time stamp for dt update
    
    def updateMeasured(self, measured_val):
        """
        Update the current measured value.
        """
        self.measured = measured_val
        
    def updateReference(self, reference_val):
        """
        Update the reference (setpoint) value.
        """
        self.reference = reference_val
        
    def getError(self):
        """
        Compute and return the current error (setpoint - measured).
        The error is stored for derivative computation.
        """
        self.error[1] = self.reference - self.measured
        return self.error[1]
    
    def _updateTimeStep(self):
        """
        Update the time step (dt) based on the difference between the current time and previous time.
        This can be used to dynamically adjust integration and differentiation intervals.
        """
        current_time = time.ticks_us()
        self.dt = time.ticks_diff(current_time, self.prev_time)
        self.prev_time = current_time
    
    def _KI_action(self):
        """
        Update the integral error term by accumulating the current error over the time step.
        """
        self.integral_error += self.error[1] * self.dt
    
    def _KD_action(self):
        """
        Compute the derivative error term based on the difference between the current and previous errors.
        """
        if self.dt != 0:
            self.derivative_error = (self.error[1] - self.error[0]) / self.dt
            self.error[0] = self.error[1]
        else:
            self.derivative_error = 0
    
    def totalAction(self):
        """
        Compute the total control action as a sum of:
            - Proportional term: KP * current error
            - Integral term: KI * accumulated error
            - Derivative term: KD * error rate of change
        Returns the computed control action.
        """
        # self._updateTimeStep()  # Uncomment if dynamic dt update is desired.
        self.getError()
        self._KI_action()
        self._KD_action()
        return self.KP * self.error[1] + self.KI * self.integral_error + self.KD * self.derivative_error
