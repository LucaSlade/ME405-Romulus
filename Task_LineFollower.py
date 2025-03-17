#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file Task_LineFollower.py
#  @brief Line Follower Task (FSM Implementation)
#
#  This module implements a finite state machine (FSM) for line following using
#  an array of IR line sensors. It uses the calibration function from the
#  LineSensorDriver to calibrate the sensors, then continuously monitors the
#  sensor array to compute the centroid of a detected line.
#
#  The FSM states include:
#    - INIT: Calibration state.
#    - STANDBY: Waiting state.
#    - FOLLOW: Actively following a detected line.
#    - SEARCH: Attempting to recover a lost line.
#
#  @note Requires: time, pyb, LineSensorDriver, task_share.
#
#  @author 
#  @date   
#

import time
from pyb import Pin, delay
from LineSensorDriver import LineSensorArray
import task_share

## @class LineFollowerTask
#  @brief Implements an FSM for a line follower using an array of IR sensors.
#
#  This class initializes a line sensor array and runs an FSM to calibrate the
#  sensors, follow a line by computing its centroid, and optionally search for a lost line.
#
class LineFollowerTask:
    # FSM state constants
    INIT    = 0   ## @brief Calibration state.
    STANDBY = 1   ## @brief Standby state.
    FOLLOW  = 2   ## @brief Line-following state.
    SEARCH  = 3   ## @brief Lost line recovery state.

    ## @brief Constructor for the LineFollowerTask class.
    #  @param sensor_pins A list of ADC pin identifiers (e.g., [Pin.cpu.A4, ...])
    def __init__(self, sensor_pins):
        """
        Initialize the line follower task.
        
        :param sensor_pins: A list of ADC pin identifiers.
        """
        self.sensor_array = LineSensorArray(sensor_pins)
        self.state = LineFollowerTask.STANDBY  # Start in STANDBY

    ## @brief Generator function implementing the line follower FSM.
    #  @details Uses shared variables for calibration flag, follow mode, and line position.
    #  @param shares A tuple of shared variables: (calibrate_flag, line_following_flg, line_position)
    #  @yield Yields control to the scheduler after each iteration.
    def generator(self, shares):
        """
        Generator that implements an FSM for line following.
        Uses shared variables for calibration flag, follow mode, and line position.
        
        :param shares: Tuple of shared variables: (calibrate_flag, line_following_flg, line_position)
        """
        calibrate_flag, line_following_flg, line_position = shares

        while True:
            if self.state == LineFollowerTask.INIT:
                # --- STATE: INIT (Calibration) ---
                print("Line Follower: Starting Calibration...")
                self.sensor_array.calibrate()
                calibrate_flag.put(1)
                time.sleep(1)
                print("Line Follower: Calibration complete. Switching to STANDBY state.")
                self.state = LineFollowerTask.STANDBY

            elif self.state == LineFollowerTask.STANDBY:
                # --- STATE: STANDBY ---
                if line_following_flg.get():
                    print("Line Follower: Transitioning to FOLLOW state for line tracking.")
                    self.state = LineFollowerTask.FOLLOW  

            elif self.state == LineFollowerTask.FOLLOW:
                # --- STATE: FOLLOW LINE ---
                if not line_following_flg.get():  # If following is disabled, go to STANDBY
                    print("Line Follower: Stopping, entering STANDBY.")
                    self.state = LineFollowerTask.STANDBY
                else:
                    centroid = self.sensor_array.compute_centroid()
                    if centroid is None:
                        print("Line Follower: Line lost! Switching to SEARCH state.")
                        self.state = LineFollowerTask.SEARCH
                    else:
                        line_position.put(centroid)
                        print(f"Line Follower: Following line, centroid = {centroid:.2f}")

            elif self.state == LineFollowerTask.SEARCH:
                # --- STATE: SEARCH (If Line is Lost) ---
                if not line_following_flg.get():
                    self.state = LineFollowerTask.STANDBY
                else:
                    print("Line Follower: Searching for line...")
                    centroid = self.sensor_array.compute_centroid()
                    if centroid is not None:
                        print(f"Line Follower: Line found, resuming at centroid = {centroid:.2f}")
                        self.state = LineFollowerTask.FOLLOW

            yield  # Yield control to the scheduler
