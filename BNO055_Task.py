#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file bno055_task.py
#  @brief   Task for managing the BNO055 IMU using an FSM.
#
#  This module implements an FSM-based task for operating the BNO055 IMU.
#  It initializes the sensor, manages its calibration state, and provides
#  heading information for further processing.
#
#  @author  aidentheocheung
#  @date    2025-Feb-24
#

import time
import shared
from BNO055_Driver import BNO055
from pyb import I2C
from PIDController import PIDController

## @class BNO055Task
#  @brief FSM-based task for managing BNO055 IMU with calibration control.
#
#  This class creates a finite state machine (FSM) to control the BNO055
#  sensor. It handles the initialization, calibration, and heading measurement
#  processes. The FSM states include INIT, RUNNING, and DONE.
#
class BNO055Task:
    INIT = 0        ## @brief Initial state: sensor calibration in progress.
    RUNNING = 1     ## @brief Running state: sensor operating normally.
    DONE = 2        ## @brief Done state: task complete (not used in this example).

    ## @brief Constructor for the BNO055Task.
    #  @details Attempts to initialize the BNO055 sensor and set the initial FSM state.
    #  If the sensor is not detected, a RuntimeError is printed.
    #  @param i2c The I2C object used to communicate with the sensor.
    def __init__(self, i2c):
        try:
            self.imu = BNO055(i2c)
        except RuntimeError as e:
            print(e)
            return

        self.state = BNO055Task.INIT
        
        # Uncomment the following line if PID control is desired
        # self.pid = PIDController(kp=1.5, ki=0.02, kd=0.03)
        
        # Initialize calibration heading (only the heading is used)
        self.cal_heading, _, _ = self.imu.read_euler_angles()
        
        # Note: self.imu_calibrated_flag is expected to be a shared variable for signaling calibration.
        # It should be initialized externally and passed via the shares tuple if needed.

    ## @brief Generator function implementing the task-based FSM.
    #  @details This generator repeatedly performs operations based on the current FSM state.
    #           In the INIT state, it monitors calibration status and transitions to RUNNING when
    #           calibration is complete. In the RUNNING state, it reads the current heading and
    #           signals when the target heading is reached.
    #  @param shares A tuple containing shared objects for inter-task communication:
    #         - headed_flg: share for signaling when the target heading is achieved.
    #         - target_heading: share holding the desired heading.
    #         - current_heading: share for outputting the current heading.
    #         - calibrate_imu_flg: share used for calibration signaling (if needed).
    #  @yield Yields control back to the scheduler after each iteration.
    def generator(self, shares):
        headed_flg, target_heading, current_heading, calibrate_imu_flg = shares

        while True:
            if self.state == BNO055Task.INIT:
                # Calibration loop
                prev_status = (-1, -1, -1, -1)
                while True:
                    # Read current heading (only the heading is used)
                    self.cal_heading, _, _ = self.imu.read_euler_angles()
                    
                    # Signal calibration status (shared variable, assumed to be pre-initialized)
                    self.imu_calibrated_flag.put(1)
                    
                    # Read calibration status for system, gyro, accel, and magnetometer
                    sys_calib, gyr_calib, acc_calib, mag_calib = self.imu.read_calibration_status()
                    
                    if (sys_calib, gyr_calib, acc_calib, mag_calib) != prev_status:
                        print(f"Calibration Status -> System: {sys_calib}, Gyro: {gyr_calib}, Accel: {acc_calib}, Mag: {mag_calib}")
                        prev_status = (sys_calib, gyr_calib, acc_calib, mag_calib)
                    
                    # Transition to RUNNING state when gyro, accel, and mag are calibrated
                    if gyr_calib == 1 and acc_calib == 1 and mag_calib == 1:
                        print("IMU Task: Calibration Complete! Switching to READY state.")
                        self.state = BNO055Task.RUNNING
                        break  # Exit calibration loop

            elif self.state == BNO055Task.RUNNING:
                # Read the current heading from the sensor
                heading, _, _ = self.imu.read_euler_angles()
                print(heading)
                
                # Update the shared variable with the current heading
                current_heading.put(heading)
                
                # Check if the current heading is within 5 degrees of the target heading
                if abs(target_heading.get() - heading) < 5:
                    headed_flg.put(1)  ## Signal that the target heading is achieved.
                else:
                    headed_flg.put(0)  ## Signal that adjustment is still needed.
            
            else:
                # Fallback: reset state to INIT if in an unknown state.
                self.state = BNO055Task.INIT

            yield  ## Yield control to the scheduler.
