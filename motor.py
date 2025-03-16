#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 12:24:29 2025

@author: Tomas Franco
"""

from pyb import Pin, Timer

class Motor:
    '''
    A motor driver interface encapsulated in a Python class.
    Works with motor drivers using separate PWM and direction inputs, such as the drivers
    present on the Romi chassis from Pololu.
    '''
    
    def __init__(self, PWM, DIR, nSLP, TimerChannel):
        '''Initializes a Motor object.'''
        self.MTR_nSLP_PIN = Pin(nSLP, mode=Pin.OUT_PP, value=0)
        self.MTR_DIR_PIN = Pin(DIR, mode=Pin.OUT_PP)
        self.effort = 0
        
        # Initialize Motor Timer 1 and the specified channel.
        self.tim = Timer(1, freq=20000)
        PWM_pin = Pin(PWM)
        self.TC = self.tim.channel(TimerChannel, pin=PWM_pin, mode=Timer.PWM, 
                                     pulse_width_percent=0)
        
        # =============================================================================
        # Enable_R = Pin.cpu.H0, Dir_R = Pin.cpu.H1
        # Enable_L = Pin.cpu.A2, Dir_L = Pin.cpu.B2
        # PWM should be set: Left: Pin.cpu.A8, Right: Pin.cpu.A9
        # TimerChan 1 = Left, 2 = Right
        # =============================================================================
         
    def set_effort(self, effort):
        '''Sets the present effort requested from the motor based on an input value between -100 and 100.'''
        if effort < 0:
            self.MTR_DIR_PIN.value(1)  # Reverse Drive
            if effort < -45: 
                effort = -45
            self.TC.pulse_width_percent(-effort)
            self.effort = -effort
        elif effort > 0:
            self.MTR_DIR_PIN.value(0)  # Forward Drive
            if effort > 45: 
                effort = 45
            self.TC.pulse_width_percent(effort)
            self.effort = effort
        elif effort == 0:
            self.TC.pulse_width_percent(0)
            self.effort = effort
        else:
            raise ValueError
    
    def get_effort(self):
        '''Returns the current motor effort.'''
        return self.effort
    
    def enable(self):
        '''Enables the motor driver by taking it out of sleep mode into brake mode.'''
        self.MTR_nSLP_PIN.value(1)  # NotSleep: set to active
        self.TC.pulse_width_percent(0)
        
    def disable(self):
        '''Disables the motor driver by putting it to sleep and stopping PWM.'''
        self.MTR_nSLP_PIN.value(0)  # Put motor driver to sleep
        self.TC.pulse_width_percent(0)
        self.tim.deinit()          # Deinitialize the timer to stop PWM completely
