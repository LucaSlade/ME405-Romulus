#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file bump_sensor.py
#  @brief Driver for a snap-action (bump) switch sensor.
#
#  This module implements a simple driver for a bump sensor using a normally
#  open (NO) switch configuration. It provides debounce functionality and
#  updates a shared variable to indicate when an impact is detected.
#
#  @author  
#  @date   2025-Feb-24
#

from pyb import Pin
import time
import shared  # Import the shared variable module

## @class BumpSensor
#  @brief A simple driver for a snap-action (bump) switch.
#
#  This class implements a driver for a bump sensor that uses a normally open
#  (NO) switch with COM connected to ground and NO connected to a digital input.
#  It debounces the switch input and updates a shared variable to signal an impact.
#
class BumpSensor:
    """
    A simple driver for a snap-action (bump) switch.
    Assumes a normally open (NO) switch with COM to ground and NO to a digital input.
    """

    ## @brief Constructor for the BumpSensor class.
    #  @param pin_name The name of the pin connected to the bump sensor.
    #  @param debounce_ms The debounce time in milliseconds (default is 50 ms).
    def __init__(self, pin_name, debounce_ms=50):
        # Configure the pin with an internal pull-up resistor.
        self.pin = Pin(pin_name, Pin.IN, Pin.PULL_UP)
        self.debounce_ms = debounce_ms
        self.last_read_time = time.ticks_ms()
        self.last_state = self.pin.value()
        self.debounced_state = self.pin.value()

    ## @brief Reads the state of the bump sensor.
    #  @details Checks if the switch is pressed by reading the pin's value.
    #           It applies a debounce algorithm and updates the shared variable
    #           `impact_detected` in the shared module. If pressed (i.e., pin reads LOW),
    #           a warning is printed and the shared flag is set to 1; otherwise, the flag
    #           is reset to 0.
    #  @return True if the sensor is pressed, False otherwise.
    def read(self):
        impact_detected = self.pin.value()  # 0 if pressed, 1 if not pressed
        now = time.ticks_ms()

        if impact_detected != self.last_state:
            if time.ticks_diff(now, self.last_read_time) > self.debounce_ms:
                self.debounced_state = impact_detected
                # If pressed, set `impact_detected` in shared.py.
                if self.debounced_state == 0:
                    print("⚠️ Bump Detected!")
                    shared.impact_detected.put(1)  # Set bump flag to 1.
                else:
                    shared.impact_detected.put(0)  # Reset flag when released.
            self.last_read_time = now

        self.last_state = impact_detected
        return self.debounced_state == 0  # Return True if pressed.





