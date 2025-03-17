#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file bump_sensor_task.py
#  @brief Implements a cooperative multitasking task to monitor bump sensors.
#
#  This module contains a class that creates bump sensor objects from given sensor pins,
#  then continuously monitors them in a cooperative multitasking environment.
#  When a bump (impact) is detected, it updates a shared variable accordingly.
#
#  @note Requires modules: time, shared, task_share, Driver_BumpSensor, and Task_MotorController.
#
#  @author Aiden
#  @date   3/16/25
#

import time
import task_share
from Driver_BumpSensor import BumpSensor
import Task_MotorController 

## @class BumpSensorTask
#  @brief A cooperative task for monitoring bump sensors.
#
#  This class instantiates bump sensor objects based on provided sensor pins.
#  Its generator function continuously checks the sensors and updates a shared
#  variable when a bump is detected, allowing cooperative multitasking in the system.
#
class BumpSensorTask:
    
    ## @brief Constructor for the BumpSensorTask class.
    #  @param sensor_class The sensor driver class used to create bump sensor objects.
    #  @param sensor_pins A dictionary mapping sensor names to pin identifiers.
    def __init__(self, sensor_class, sensor_pins):
        # Create bump sensor objects using the provided sensor class and pins.
        self.sensors = {name: sensor_class(pin) for name, pin in sensor_pins.items()}
        self.state = 0  # Initialize state to indicate no bump detected.
        
    ## @brief Generator function for the bump sensor task.
    #  @details Continuously monitors the bump sensors and updates the shared variable
    #           to signal an impact. This generator is intended to be scheduled in a cooperative
    #           multitasking environment.
    #  @param shares A shared variable (or a tuple containing a shared variable) used to store
    #         the impact detection flag.
    #  @yield Returns control to the scheduler after each iteration.
    def generator(self, shares):
        impact_detected = shares

        # Define finite state machine states.
        S0_NO_BUMP = 0
        S1_YES_BUMP = 1
        
        while True:
            if self.state == S0_NO_BUMP:
                # Iterate over each sensor and check if any sensor is pressed.
                pressed = False
                for sensor in self.sensors.values():
                    if sensor.read():
                        pressed = True
                        break
                if pressed:
                    impact_detected.put(1)
                    print("Set me please")
                    self.state = S1_YES_BUMP

            elif self.state == S1_YES_BUMP:
                # Wait until the impact flag is cleared before returning to NO_BUMP state.
                if impact_detected.get() == 0:
                    self.state = S0_NO_BUMP

            yield 0  # Yield control for cooperative multitasking.
