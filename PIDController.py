#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file PIDController.py
#  @brief Implements a Proportional-Integral-Derivative (PID) controller.
#
#  This module provides a simple PID controller class for computing control
#  outputs based on error input. It can be used to regulate systems by
#  minimizing the difference between a desired setpoint and a measured process variable.
#
#  @note This file can be integrated directly or included in Task_MotorController.py.
#
#  @author  
#  @date   
#

class PIDController:
    ## @brief Constructor for the PIDController class.
    #  @param kp The proportional gain.
    #  @param ki The integral gain.
    #  @param kd The derivative gain.
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    ## @brief Computes the PID control output.
    #  @param error The current error value (difference between desired and measured values).
    #  @return The control output computed using the PID formula.
    def compute(self, error):
        self.integral += error        
        derivative = error - self.prev_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output


"""
class PIDController:
    
    def __init__(self, line_kp,, line_ki, line_kd):
        self.line_kp = line_kp
        self.line_ki = line_ki
        self.line_kd = line_kd
        
        self.previous_time = ticks_ms()
        self.current_time = self.previous_time
        self.actual = 0
        
    def line_PID(self, actual, current):
        self.current_time = ticks_ms()
        
        dt = ticks_diff(self.current_time, self.previous_time)/1000
        
        self.line_error = actual - current
        
        self.line_integral += self.line_error*dt
        p = self.line_kp*self.line_error
        i = self.line_ki*self.line_integral
        d = self.line_kd*((self.line_error - self.line_last_error)/dt)
        
        motor_speed = (p+i+d)

        self.line_last_error = self.line_error
        
        self.previous_time = self.current_time
        
        return motor_speed
"""