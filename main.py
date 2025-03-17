#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file main.py
#  @brief Main integration script for the Romi robot.
#
#  This module integrates various drivers, tasks, and shared variables to control
#  the Romi robot. It sets up motors, encoders, sensors, and tasks that manage the
#  robot's behavior (such as line following, bump sensing, IMU heading, and motor control).
#
#  The main tasks include:
#    - MastermindTask: High-level decision-making and planning.
#    - LineFollowerTask: Processing data from IR line sensors.
#    - BNO055Task: Handling the IMU sensor for orientation.
#    - BumpSensorTask: Monitoring bump sensors.
#    - MotorController: Controlling motor outputs based on sensor feedback.
#    - (Optional) UI: User interface for controlling the robot.
#
#  Shared variables (via task_share.Share) are used for inter-task communication.
#
#  @note The ISR for a user button (to toggle robot state) is provided in a commented section.
#
#  @author  
#  @date   
#

import gc
import cotask
import shared
import task_share
from pyb import Pin, Timer
from Thinker import MastermindTask
from Task_LineFollower import LineFollowerTask
from PreProgPath import RomiDrive
from Task_BumpSensor import BumpSensorTask
from Driver_BumpSensor import BumpSensor
from Task_MotorController import MotorController
from Driver_Motors import Motor
from EncoderDriver import Encoder
#from UI import UI
from BNO055_Task import BNO055Task
from pyb import I2C

'''
## @brief ISR for toggling robot state.
#
#  This section provides an example of how to use an ISR to toggle the robot's
#  active state using a shared variable. Uncomment and configure as needed.
#
#  1. Create shared variables (including robot_active) 
robot_active = task_share.Share('B', thread_protect=False, name="robot_active") 
robot_active.put(False) 
#
#  2. Define the ISR function 
def button_pressed(pin): 
    """ ISR for toggling the robot start/stop state. """ 
    current_state = robot_active.get() 
    new_state = not current_state 
    robot_active.put(new_state) 
    print("Blue Button Pressed! Robot Active:", new_state) 
#
#  3. Configure the button pin and attach the ISR 
button_pin = Pin.cpu.C13   # Blue user button on many Nucleo boards 
button_pin.init(Pin.IN, Pin.PULL_UP) 
button_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)
'''

## === MOTOR SETUP ===
#  Instantiate left and right motors using their respective pins and PWM configuration.
motor_left = Motor(pwm_pin=Pin.cpu.A8, dir_pin=Pin.cpu.B15, nslp_pin=Pin.cpu.B14, 
                   timer_num=1, channel=1)
motor_right = Motor(pwm_pin=Pin.cpu.A9, dir_pin=Pin.cpu.H1, nslp_pin=Pin.cpu.H0, 
                    timer_num=1, channel=2)

## === CONFIGURE ENCODERS ===
#  Setup encoder hardware using timers and associated pins for the left and right motors.
CH_A_PIN_1 = Pin(Pin.cpu.A1)  # Encoder 1 (Left Motor) Channel A
CH_B_PIN_1 = Pin(Pin.cpu.A0)  # Encoder 1 (Left Motor) Channel B
tim_1 = Timer(2, prescaler=0, period=0xFFFF)
tim_1.channel(1, pin=CH_A_PIN_1, mode=Timer.ENC_AB)
tim_1.channel(2, pin=CH_B_PIN_1, mode=Timer.ENC_AB)

CH_A_PIN_2 = Pin(Pin.cpu.B5)  # Encoder 2 (Right Motor) Channel A
CH_B_PIN_2 = Pin(Pin.cpu.B4)  # Encoder 2 (Right Motor) Channel B
tim_2 = Timer(3, prescaler=0, period=0xFFFF)
tim_2.channel(1, pin=CH_A_PIN_2, mode=Timer.ENC_AB)
tim_2.channel(2, pin=CH_B_PIN_2, mode=Timer.ENC_AB)

encoder_left = Encoder(tim_1)
encoder_right = Encoder(tim_2)

encoder_left.zero()
encoder_right.zero()

## === DRIVE & SENSOR SETUP ===
#  Define physical parameters and sensor pin mappings.
wheel_radius = 7  # cm (70mm)
CPR = 1440       # Counts per revolution for encoders

# Define sensor pins for bump sensors (dictionary mapping sensor names to ADC pin strings)
sensor_pins = {
    "BMP0-R": "PC12",  # Right sensor 0
    "BMP1-R": "PC11",  # Right sensor 1
    "BMP2-R": "PD2",   # Right sensor 2
    "BMP3-L": "PB3",   # Left sensor 3
    "BMP4-L": "PA10",  # Left sensor 4
    "BMP5-L": "PC4"    # Left sensor 5
}

# Instantiate the bump sensor task using the BumpSensor driver and sensor_pins mapping.
bumper = BumpSensorTask(BumpSensor, sensor_pins)

# Instantiate drive system using motor drivers and encoders.
romi = RomiDrive(motor_left, motor_right, encoder_left, encoder_right, wheel_radius, CPR)

# Instantiate motor controller task.
motor_ctrl = MotorController(motor_left, motor_right, encoder_left, encoder_right)

# Define sensor pins for the line sensor array.
line_sensor_pins = [Pin.cpu.A4, Pin.cpu.B0, Pin.cpu.C1, Pin.cpu.C0, 
                    Pin.cpu.C2, Pin.cpu.C3, Pin.cpu.A6, Pin.cpu.A7]

# Instantiate line follower task using the defined line sensor pins.
IR_Sensors = LineFollowerTask(line_sensor_pins)

# Instantiate the high-level decision-making task (Mastermind).
thinker = MastermindTask(encoder_left, encoder_right)  # Optionally, add additional sensor inputs

# Instantiate the user interface (if implemented).
ui = UI()

# Setup I2C for the IMU and instantiate the IMU task.
i2c = I2C(2, I2C.CONTROLLER, baudrate=100000)
imu = BNO055Task(i2c)

## === MAIN PROGRAM ===
if __name__ == "__main__":
    
    ## @brief Shared variables for inter-task communication.
    started_flg = task_share.Share('B', thread_protect=False, name="started")  # Flag from UI to start operations
    started_flg.put(1)
    
    left_effort = task_share.Share('f', thread_protect=False, name="Left Effort")
    right_effort = task_share.Share('f', thread_protect=False, name="Right Effort")
    
    line_following_flg = task_share.Share('B', thread_protect=False, name="line_following")
    
    imu_calibrated_flg = task_share.Share('B', name="IMU Calibrated")
    imu_calibrated_flg.put(1)
    
    line_calibrated = task_share.Share('B', thread_protect=False, name="line_sensor_calibrate")
    line_calibrated.put(1)
    
    line_position = task_share.Share('f', thread_protect=False, name="line_position")
    
    current_heading = task_share.Share('f', thread_protect=False, name="Current Heading")
    
    headed_flg = task_share.Share('B', name="Headed")
    headed_flg.put(0)
    
    distance = task_share.Share('f', thread_protect=False, name="Distance")
    distance.put(66) 
    
    speed = task_share.Share('i', thread_protect=False, name="Speed")
    speed.put(15)
    
    PPP_flg = task_share.Share('B', name="Impact Detected")
    PPP_flg.put(0)
    
    drive_state = task_share.Share('i', thread_protect=False, name="Drive State")
    
    impact_detected = task_share.Share('B', name="Impact Detected")
    impact_detected.put(0)
    
    target_heading_share = task_share.Share('f', thread_protect=False, name="Target Heading")
    target_heading_share.put(0)
  
    ## Garbage collection to manage memory.
    gc.collect()
  
    ## @brief Create tasks for the cooperative scheduler.
    #
    #  Each task is created with a generator function, priority, period, and shared variables.
    task1 = cotask.Task(thinker.generator, name="Mastermind", priority=3, period=30, profile=True, trace=True, 
                        shares=(started_flg, line_following_flg, left_effort, right_effort, line_calibrated, line_position, current_heading, headed_flg))
    task2 = cotask.Task(IR_Sensors.generator, name="Line Sensor", priority=2, period=20, profile=True, trace=True, 
                        shares=(line_calibrated, line_following_flg, line_position))
    task3 = cotask.Task(imu.generator, name="IMU Heading", priority=1, period=40, profile=True, trace=True, 
                        shares=(headed_flg, target_heading_share, current_heading, imu_calibrated_flg))
    task4 = cotask.Task(bumper.generator, name="Bump Sensor", priority=3, period=20, profile=True, trace=True, 
                        shares=(impact_detected))
    task5 = cotask.Task(motor_ctrl.generator, name="Motor Control", priority=4, period=25, profile=True, trace=True, 
                        shares=(left_effort, right_effort))
    task6 = cotask.Task(ui.generator, name="User Interface", priority=1, period=30, profile=False, trace=False, 
                        shares=(started_flg))

    ## Append tasks to the global task list.
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)
    cotask.task_list.append(task4)
    cotask.task_list.append(task5)
    cotask.task_list.append(task6)

    ## Main scheduler loop.
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            motor_left.disable()
            motor_right.disable()
            break
        except Exception as e:
            motor_left.disable()
            motor_right.disable()
            print("Exception has occured")
            break

    ## Diagnostic printouts after tasks complete.
    print('\n' + str(cotask.task_list))
    print(task_share.show_all())
    # print(task_share.get_trace())
    print('')
