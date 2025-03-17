#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file motor.py
#  @brief Motor driver interface using PWM.
#
#  This module implements a motor driver interface for controlling motors
#  using PWM signals. It sets up the necessary pins for direction control,
#  sleep mode, and PWM output, and provides methods to adjust motor effort,
#  enable, and disable the motor.
#
#  @author 
#  @date   2025-Mar-08
#

from pyb import Pin, Timer

## @class Motor
#  @brief A motor driver interface for controlling motors with PWM.
#
#  This class initializes and controls a motor using PWM for speed control and
#  digital outputs for direction and sleep control. The motor starts at zero speed,
#  and its effort can be adjusted between -100 and 100. Negative values indicate
#  reverse direction, while positive values indicate forward direction.
#
class Motor:
    '''A motor driver interface for controlling motors with PWM.'''
    
    ## @brief Constructor for the Motor class.
    #  @details Initializes a Motor object by configuring the PWM, direction, and
    #           sleep pins. A timer is set up to generate a PWM signal at 20 kHz.
    #           The motor is initially disabled and its speed is set to zero.
    #  @param pwm_pin The pin used for PWM output.
    #  @param dir_pin The pin used to control the motor's direction.
    #  @param nslp_pin The pin used to enable/disable the motor driver.
    #  @param timer_num The timer number used for PWM generation.
    #  @param channel The channel of the timer used for PWM.
    def __init__(self, pwm_pin, dir_pin, nslp_pin, timer_num, channel):
        '''Initializes a Motor object.'''
        self.nSLP = Pin(nslp_pin, mode=Pin.OUT_PP, value=0)  # Start disabled
        self.DIR = Pin(dir_pin, mode=Pin.OUT_PP, value=0)
        self.PWM = Pin(pwm_pin, mode=Pin.AF_PP)
        
        self.timer = Timer(timer_num, freq=20000)  # Set timer for PWM at 20 kHz
        self.PWM_channel = self.timer.channel(channel, Timer.PWM, pin=self.PWM)
        
        # Start motors at a speed of zero.
        self.PWM_channel.pulse_width_percent(0)
    
    ## @brief Sets the motor effort (speed and direction).
    #  @details Adjusts the PWM duty cycle and sets the direction pins based on
    #           the effort value. If effort is zero, the motor is disabled. Otherwise,
    #           the motor is enabled and its direction is set according to the sign
    #           of the effort. Effort must be between -100 and 100.
    #  @param effort An integer between -100 and 100. Positive for forward, negative for reverse.
    def set_effort(self, effort):
        '''Sets motor speed and direction.'''  
        if -100 <= effort <= 100:
            if effort == 0:
                self.nSLP.low()
                self.PWM_channel.pulse_width_percent(0)
            else:
                self.nSLP.high()
                if effort > 0:
                    self.DIR.low()
                else:
                    self.DIR.high()
                self.PWM_channel.pulse_width_percent(abs(effort))
        else:
            print("Invalid effort value. Enter between -100 and 100.")

    ## @brief Enables the motor driver.
    #  @details Sets the sleep (nSLP) pin high, enabling the motor driver.
    def enable(self):
        '''Enables the motor driver.'''
        self.nSLP.high()

    ## @brief Disables the motor driver.
    #  @details Sets the sleep (nSLP) pin low, disabling the motor driver.
    def disable(self):
        '''Disables the motor driver.'''
        self.nSLP.low()
