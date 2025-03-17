#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file MastermindTask.py
#  @brief Implements the high-level control task for the robot.
#
#  This module implements a finite state machine (FSM) that controls the state
#  of the robot and triggers necessary actions such as line following, straight
#  driving, and heading turns. It uses encoder feedback and a PID controller for
#  computing corrections.
#
#  @note Some states below are placeholders or under development.
#
#  @author lucas
#  @date Mon Mar 10 15:45:55 2025
#

import time
import shared
import task_share
from PIDController import PIDController

## @class MastermindTask
#  @brief Controls the state of the robot and triggers necessary actions.
#
#  This class implements an FSM-based task that continuously reads encoder
#  values, computes a PID-based correction for line following, and transitions
#  through multiple states including line following, straight driving, and heading turns.
#
class MastermindTask:
    # FSM State Definitions
    S0_STANDBY = 0          ## @brief Standby state.
    S1_LINE_FOLLOW_1 = 1    ## @brief Initial line following state.
    S2_STRAIGHT_DRIVE_1 = 2 ## @brief First straight drive state.
    S3_LINE_FOLLOW_2 = 3    ## @brief Secondary line following state.
    S4_STRAIGHT_DRIVE_2 = 4 ## @brief Second straight drive state.
    S5_HEADING_TURN_1 = 5   ## @brief Heading turn state.
    S6_STRAIGHT_DRIVE_3 = 6 ## @brief Third straight drive state.
    S7_LINE_FOLLOW_UNTIL_BUMP = 7  ## @brief Line following until bump is detected.
    S8_REVERSE = 8          ## @brief Reverse drive state.
    S9_HEADING_TURN_2 = 9   ## @brief Second heading turn state.
    S10_DRIVE_FINISH_PATH = 10  ## @brief Final drive state to finish path.

    ## @brief Constructor for the MastermindTask class.
    #  @param encoder_left Encoder instance for the left motor.
    #  @param encoder_right Encoder instance for the right motor.
    def __init__(self, encoder_left, encoder_right):
        """ Initializes the Mastermind task with encoder tracking. """
        self.state = MastermindTask.S0_STANDBY

        self.encoder_left = encoder_left
        self.encoder_right = encoder_right
        self.pid_controller = PIDController(2, 0, 0)

        self.s = 0  # Measured average position from encoders
        self.error = 0
        self.correction = 0
        self.pid_update_counter = 0

    ## @brief Generator function implementing the Mastermind FSM.
    #  @details This FSM-based generator continuously updates encoder readings,
    #           computes PID corrections based on line position error, and transitions
    #           through several states including standby, line following, straight drive,
    #           and heading turn.
    #
    #  The shared variables expected in the tuple are:
    #    - started_flg
    #    - line_following_flg
    #    - left_effort
    #    - right_effort
    #    - line_calibrated
    #    - line_position
    #    - current_heading
    #    - headed_flg
    #
    #  @param shares Tuple of shared variables for inter-task communication.
    #  @yield Yields control to the scheduler after each iteration.
    def generator(self, shares):
        """ FSM-based generator function that controls task execution. """
        # Unpack shared variables.
        started_flg, line_following_flg, left_effort, right_effort, line_calibrated, line_position, current_heading, headed_flg = shares

        print("Resetting encoders at startup...")
        self.encoder_left.zero()
        self.encoder_right.zero()

        while True:
            # Update encoders and compute the average position.
            self.encoder_left.update()
            self.encoder_right.update()
            self.left_pos = self.encoder_left.get_position()
            self.right_pos = self.encoder_right.get_position()
            self.s = (self.left_pos + self.right_pos) / 2  # Average position

            print(f"DEBUG: Encoders - Left: {self.left_pos}, Right: {self.right_pos}, Avg: {self.s}")

            # --- STATE: STANDBY ---
            if self.state == MastermindTask.S0_STANDBY:
                print("Mastermind: Waiting for start...")
                self.encoder_left.zero()
                self.encoder_right.zero()
                left_effort.put(0)
                right_effort.put(0)
                # Transition to line following state.
                self.state = MastermindTask.S1_LINE_FOLLOW_1
                line_following_flg.put(1)  # Enable line following.
                self.s = 0

                yield  # Yield to scheduler.

            # --- STATE: LINE FOLLOWING 1 ---
            elif self.state == MastermindTask.S1_LINE_FOLLOW_1:
                if self.s <= 1000:
                    # FIXME: Incomplete expression for measured_centroid. Correct the expression as needed.
                    measured_centroid = line_position.get()/
                    self.error = -1 * (3.5 - measured_centroid)

                    if self.pid_update_counter % 5 == 0:
                        self.correction = self.pid_controller.compute(self.error)

                    left_pwm = max(-100, min(100, left_effort.get() + self.correction))
                    right_pwm = max(-100, min(100, right_effort.get() - self.correction))

                    left_effort.put(left_pwm)
                    right_effort.put(right_pwm)
                    self.pid_update_counter += 1
                else:
                    print(f"Mastermind: Transitioning to Straight Drive 1 (s = {self.s})")
                    line_following_flg.put(0)
                    left_effort.put(0)
                    right_effort.put(0)
                    self.s = 0
                    self.encoder_left.zero()
                    self.encoder_right.zero()
                    self.state = MastermindTask.S2_STRAIGHT_DRIVE_1

                yield  # Yield to scheduler.

            # --- STATE: STRAIGHT DRIVE 1 ---
            elif self.state == MastermindTask.S2_STRAIGHT_DRIVE_1:
                print("Mastermind: Straight Drive Stage 2")
                if self.s <= 1000:
                    left_effort.put(30)
                    right_effort.put(30)
                else:
                    print("Mastermind: Stopping straight drive, preparing for next state.")
                    left_effort.put(0)
                    right_effort.put(0)
                    line_following_flg.put(1)
                    self.s = 0
                    self.encoder_left.zero()
                    self.encoder_right.zero()
                    self.state = MastermindTask.S3_LINE_FOLLOW_2
                    print(f"DEBUG: New state = {self.state}")

                yield  # Yield to scheduler.

            # --- STATE: LINE FOLLOWING 2 ---
            elif self.state == MastermindTask.S3_LINE_FOLLOW_2:
                print("Mastermind: State 3 Line Following 2")
                if self.s <= 1000:
                    measured_centroid = line_position.get()
                    self.error = -1 * (3.5 - measured_centroid)
                    self.correction = self.pid_controller.compute(self.error)
                    left_pwm = max(-100, min(100, left_effort.get() + self.correction))
                    right_pwm = max(-100, min(100, right_effort.get() - self.correction))
                    left_effort.put(left_pwm)
                    right_effort.put(right_pwm)
                else:
                    line_following_flg.put(0)
                    left_effort.put(0)
                    right_effort.put(0)
                    self.s = 0
                    self.encoder_left.zero()
                    self.encoder_right.zero()
                    self.state = MastermindTask.S4_STRAIGHT_DRIVE_2

                yield  # Yield to scheduler.

            # --- STATE: STRAIGHT DRIVE 2 ---
            elif self.state == MastermindTask.S4_STRAIGHT_DRIVE_2:
                print("Mastermind: Straight Drive Stage 2")
                if self.s <= 1000:
                    left_effort.put(30)
                    right_effort.put(30)
                else:
                    left_effort.put(0)
                    right_effort.put(0)
                    # headed_flg.put(1)  # Tell IMU we are starting a turn.
                    self.s = 0
                    self.encoder_left.zero()
                    self.encoder_right.zero()
                    print(f"DEBUG: New state = {self.state}")
                yield

            # --- STATE: HEADING TURN 1 ---
            elif self.state == MastermindTask.S5_HEADING_TURN_1:
                print("Mastermind: State 5 Heading Turn 1")

                TARGET_HEADING = 50
                max_speed = 50
                pid = PIDController(2, 0, 0)

                while not headed_flg.get():  # Wait for IMU update.
                    print("Waiting for IMU to update heading...")
                    yield

                error = TARGET_HEADING - current_heading.get()
                
                if error > 180:
                    error -= 360
                elif error < -180:
                    error += 360
                
                if abs(error) >= 2:
                    correction = pid.compute(error)
                    left_speed = max(-max_speed, min(max_speed, correction))
                    right_speed = max(-max_speed, min(max_speed, -correction))
                    left_effort.put(left_speed)
                    right_effort.put(right_speed)
                    print(f"Heading: {current_heading.get():.2f}° | Error: {error:.2f}° | Correction: {correction:.2f}")
                else:
                    left_effort.put(0)
                    right_effort.put(0)
                    self.s = 0
                    self.encoder_left.zero()
                    self.encoder_right.zero()
                    self.state = MastermindTask.S6_STRAIGHT_DRIVE_3

                yield  # Yield to scheduler.

            """NOTE: BELOW THIS LINE WE ENCOUNTERED TOO MANY ERRORS AND ARE UNABLE TO FINISH"""

            # --- STATE: STRAIGHT DRIVE 3 ---
            elif self.state == MastermindTask.S6_STRAIGHT_DRIVE_3:
                print("Mastermind: State 6 - Straight Drive 3")
                pass

            # --- STATE: LINE FOLLOW UNTIL BUMP ---
            elif self.state == MastermindTask.S7_LINE_FOLLOW_UNTIL_BUMP:
                pass

            # --- STATE: REVERSE ---
            elif self.state == MastermindTask.S8_REVERSE:
                print("Mastermind: Straight Drive Stage 2")
                if self.s <= 1000:
                    left_effort.put(30)
                    right_effort.put(30)
                else:
                    left_effort.put(0)
                    right_effort.put(0)
                    # headed_flg.put(1)  # Tell IMU we are starting a turn.
                    self.s = 0
                    self.encoder_left.zero()
                    self.encoder_right.zero()
                    print(f"DEBUG: New state = {self.state}")
                yield

            # --- STATE: HEADING TURN 2 ---
            elif self.state == MastermindTask.S9_HEADING_TURN_2:
                pass

            # --- STATE: DRIVE FINISH PATH ---
            elif self.state == MastermindTask.S10_DRIVE_FINISH_PATH:
                print("Mastermind: Straight Drive Stage 2")
                if self.s <= 1000:
                    left_effort.put(30)
                    right_effort.put(30)
                else:
                    left_effort.put(0)
                    right_effort.put(0)
                    # headed_flg.put(1)  # Tell IMU we are starting a turn.
                    self.s = 0
                    self.encoder_left.zero()
                    self.encoder_right.zero()
                    print(f"DEBUG: New state = {self.state}")
                yield

            # Yield control to the scheduler in any case.
            yield
