#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file encoder.py
#  @brief Provides a quadrature encoder decoding interface.
#
#  This module implements a class to handle quadrature encoder readings,
#  including updating the encoder count, handling overflow/underflow, and
#  calculating the velocity. It also allows the encoder position to be zeroed.
#
#  @author  
#  @date   2025-Mar-08
#

import pyb
import time
import machine  # MicroPython hardware module

## @class Encoder
#  @brief A quadrature encoder decoding interface encapsulated in a Python class.
#
#  This class provides functionality to read and process quadrature encoder signals.
#  It computes the position and velocity of the encoder by handling hardware timer
#  overflows and underflows.
#
class Encoder:
    '''A quadrature encoder decoding interface encapsulated in a Python class.'''

    ## @brief Constructor for the Encoder class.
    #  @details Initializes the encoder object with a hardware timer and sets up
    #           initial values for position and time tracking.
    #  @param tim Timer object associated with the encoder.
    #  @param auto_reload_value Maximum counter value before overflow. Default is 42
    #         (typically for a 16-bit timer, one might expect 65535).
    def __init__(self, tim, auto_reload_value=42):
        self.tim = tim                # Timer object (hardware counter)
        self.position = 0             # Total accumulated position of the encoder
        self.prev_count = 0           # Previous count value for delta calculations
        self.delta = 0                # Change in count since last update
        self.dt = 0                   # Time between last two updates (in seconds)
        self.t_last = time.ticks_us() # Last timestamp for dt calculation
        self.AR = auto_reload_value   # Auto-reload value (for handling overflows)

    ## @brief Updates the encoder reading and calculates velocity.
    #  @details Reads the current count from the hardware timer, computes the change
    #           in counts (delta), and adjusts for overflow or underflow. It also calculates
    #           the time difference between updates to enable velocity computation.
    def update(self):
        current_time = time.ticks_us()
        self.dt = time.ticks_diff(current_time, self.t_last) / 1_000_000  # Convert microseconds to seconds
        self.t_last = current_time

        # Read current count from the hardware timer
        self.count = self.tim.counter()  # Assumes `tim.counter()` returns the current timer count
        
        # Compute delta (change in counts)
        self.delta = self.count - self.prev_count

        # Handle overflow & underflow for the timer
        if self.delta > (self.AR + 1) // 2:  # Overflow occurred
            self.delta -= (self.AR + 1)
        elif self.delta < -(self.AR + 1) // 2:  # Underflow occurred
            self.delta += (self.AR + 1)

        # Update the accumulated position using the corrected delta
        self.position += self.delta

        # Store current count for next update
        self.prev_count = self.count

    ## @brief Retrieves the encoder's accumulated position.
    #  @return The current encoder position (in counts).
    def get_position(self):
        return self.position

    ## @brief Calculates and returns the encoder's velocity.
    #  @details Computes the velocity in counts per second based on the most recent
    #           delta and time difference. Returns 0 if the time difference is zero.
    #  @return Velocity in counts per second.
    def get_velocity(self):
        return self.delta / self.dt if self.dt > 0 else 0  # Avoid divide-by-zero

    ## @brief Resets the encoder's accumulated position.
    #  @details Sets the encoder position to zero and updates the previous count
    #           to the current timer count.
    def zero(self):
        self.position = 0
        self.prev_count = self.tim.counter()  # Reset to current timer count
        self.delta = 0
        self.dt = 0




