#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file UI.py
#  @brief Implements a user interface task for toggling the robot start/stop state.
#
#  This module sets up an interrupt on the blue user button (Pin C13) of a Nucleo board.
#  When the button is pressed, it toggles a shared flag that indicates whether the robot is active.
#
#  @author lucas
#  @date   Mon Mar 10 03:35:35 2025
#

from pyb import Pin
import task_share  # Assuming started_flg is defined in task_share

## @class UI
#  @brief User Interface Task for toggling the robot state.
#
#  This class configures a hardware interrupt on the blue button (Pin C13). When the button
#  is pressed, it toggles the shared flag 'started_flg' to indicate the robot's start/stop state.
#
class UI:
    ## @brief Constructor for the UI class.
    #  @param started_flg A shared variable indicating whether the robot is active.
    #
    #  Initializes the blue button interrupt on the Nucleo board's user button.
    #  The button is configured with an internal pull-up resistor, and an interrupt is
    #  attached to it which calls the button handler.
    def __init__(self, started_flg):
        # Setup Blue Button Interrupt on the Nucleo's user button (C13)
        self.button_pin = Pin.cpu.C13  # Blue user button on Nucleo
        self.button_pin.init(Pin.IN, Pin.PULL_UP)
        self.button_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.button_pressed)
        print("UI Task: Blue Button Interrupt Initialized.")
        task_share.started_flg.put(1)

    ## @brief Button press interrupt handler.
    #  @param pin The pin object that triggered the interrupt.
    #
    #  This method is called when the blue button is pressed.
    #  It toggles the shared flag 'started_flg' to switch the robot state.
    def button_pressed(self, pin):
        current_state = task_share.started_flg.get()
        task_share.started_flg.put(not current_state)
        print("Blue Button Pressed! Robot Active:", not current_state)
