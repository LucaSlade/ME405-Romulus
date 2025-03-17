#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file MotorController.py
#  @brief Implements a motor controller task using a finite state machine (FSM).
#
#  This module defines the MotorController class which interfaces with two motors
#  (left and right) and their associated encoders. It reads desired motor efforts
#  from shared variables and controls the motors accordingly, updating encoder
#  readings when active.
#
#  The FSM has two states:
#    - STANDBY: Motors are idle.
#    - RUN: Motors are active and control efforts are applied.
#
#  @note Shared variables are used for inter-task communication.
#
#  @author 
#  @date 
#

from Driver_Motors import Motor
from PIDController import PIDController
import task_share

## @class MotorController
#  @brief Implements a motor controller task using a finite state machine.
#
#  This class controls two motors using PWM and reads from their encoders to track
#  motor performance. It uses shared variables to determine desired motor efforts,
#  and transitions between STANDBY and RUN states based on those commands.
#
class MotorController:
    # FSM state constants
    STANDBY = 0  ## @brief State when motors are idle.
    RUN = 1      ## @brief State when motors are active.

    ## @brief Constructor for the MotorController class.
    #  @param left_motor An instance of the Motor class for the left motor.
    #  @param right_motor An instance of the Motor class for the right motor.
    #  @param left_encoder The encoder instance for the left motor.
    #  @param right_encoder The encoder instance for the right motor.
    def __init__(self, left_motor: Motor, right_motor: Motor, left_encoder, right_encoder):
        """
        Initializes the motor controller with the given motors and encoders.
       
        :param left_motor: An instance of the Motor class for the left motor.
        :param right_motor: An instance of the Motor class for the right motor.
        """
        self.left_motor = left_motor
        self.right_motor = right_motor
        
        self.right_encoder = right_encoder
        self.left_encoder = left_encoder
        
        self.state = MotorController.STANDBY
       
        # Uncomment and adjust the following PID controllers as needed:
        # self.pid_Line_Follow = PIDController(kp=12, ki=0.08, kd=0)
        # self.pid_Turn_To_Heading = PIDController(kp=1.5, ki=0.03, kd=0.00)
        
    ## @brief Generator function for the motor controller task.
    #  @details This generator continuously checks the shared variables for desired
    #           motor efforts. When nonzero effort is commanded, it sets the motors to
    #           RUN mode and updates the encoders. If no effort is commanded, it remains
    #           in STANDBY.
    #  @param shares A tuple of shared variables: (left_effort, right_effort).
    #  @yield Yields control to the cooperative scheduler.
    def generator(self, shares):
        """
        Generator that runs the motor controller task.
        Expects a tuple of shared variables: (left_effort, right_effort) representing
        the desired effort for the left and right motors respectively.
        """
        left_effort, right_effort = shares
        
        # Enable both motors initially.
        self.left_motor.enable()
        self.right_motor.enable()
        
        print("\nMotor Controller Task Started.")
        
        while True:
            if self.state == MotorController.STANDBY:
                if left_effort.get() == 0 and right_effort.get() == 0:
                    yield  # Skip encoder updates in STANDBY mode.
                elif left_effort.get() > 0 or right_effort.get() > 0:
                    self.state = MotorController.RUN
                    
            elif self.state == MotorController.RUN:
                print(f"DEBUG: Motor Controller RUNNING - Left: {left_effort.get()}, Right: {right_effort.get()}")
                
                # Set motor efforts based on shared variables.
                self.left_motor.set_effort(left_effort.get())
                self.right_motor.set_effort(right_effort.get())
     
                # Update encoder readings only in RUN mode.
                self.left_encoder.update()
                self.right_encoder.update()
                 
                # Transition to STANDBY if both efforts are zero.
                if left_effort.get() == 0 and right_effort.get() == 0:
                    print("DEBUG: Motors stopped. Transitioning to STANDBY.")
                    self.state = MotorController.STANDBY
                 
                yield
        
            else:
                # In unexpected states, stop motors and reset shared efforts.
                self.left_motor.set_effort(0)
                self.right_motor.set_effort(0)
                left_effort.put(0)  # Reset left motor effort.
                right_effort.put(0)  # Reset right motor effort.
        
                # Reset encoders.
                self.left_motor.zero()
                self.right_motor.zero()
        
                self.state = MotorController.STANDBY
        
            yield  # Yield control to the scheduler.
