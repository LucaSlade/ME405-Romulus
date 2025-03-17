#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file line_sensor.py
#  @brief Driver interface for IR line sensors.
#
#  This module implements two classes:
#    - LineSensor: An interface for a single IR sensor using ADC.
#    - LineSensorArray: A collection of line sensors providing calibration,
#      normalized readings, and centroid computation of detected lines.
#
#  @author lucas
#  @date   2025-Feb-18
#

from pyb import ADC, Pin
import time

## @class LineSensor
#  @brief Class to interface with an individual line sensor.
#
#  This class reads analog values from an IR sensor through an ADC pin.
#  It provides methods to retrieve raw values, normalize them based on
#  calibrated white and black references, and perform calibration.
#
class LineSensor:
    """ Use to create the instance of one sensor taking in the ADC values. 
        There are four functions which allow the Romi to recognize and utilize
        the IR sensors.
    """

    ## @brief Constructor for the LineSensor class.
    #  @param pin The ADC pin connected to the sensor.
    def __init__(self, pin):
        """ Initialize the sensor with an ADC pin. """
        self.adc = ADC(Pin(pin))
        
        # 12-bit ADC according to documentation for STM32.
        self.white_ref = 4095  # Default to max ADC value (white) 
        self.black_ref = 0     # Default to min ADC value (black)

    ## @brief Reads the raw ADC value from the sensor.
    #  @return An integer representing the raw ADC reading.
    def read_raw(self):
        """ Read the raw ADC value using ADC import for micropython """
        return self.adc.read()

    ## @brief Reads and normalizes the sensor value.
    #  @details Normalizes the raw ADC value between the calibrated white and
    #           black references and ensures the value is within [0,1].
    #  @return A floating-point value between 0 and 1 representing the normalized sensor reading.
    def read_normalized(self):
        """ Read the sensor value and normalize between b&w references. """
        raw_value = self.read_raw()
        # Return the normalized value and prevent out-of-bounds errors.
        return max(0, min(1, (raw_value - self.white_ref) / (self.black_ref - self.white_ref)))

    ## @brief Calibrates the sensor.
    #  @param white_value The ADC value corresponding to the white surface.
    #  @param black_value The ADC value corresponding to the black surface.
    def calibrate(self, white_value, black_value):
        """ Add missing calibration method. """
        self.white_ref = white_value
        self.black_ref = black_value


## @class LineSensorArray
#  @brief Represents an array of line sensors and provides processed sensor data.
#
#  This class encapsulates multiple LineSensor objects. It includes methods
#  to calibrate all sensors, read normalized values from each sensor, and
#  compute the centroid of detected black lines.
#
class LineSensorArray:
    """ Represents an array of line sensors and provides processed data. """

    ## @brief Constructor for the LineSensorArray class.
    #  @param sensor_pins A list of ADC pin names corresponding to each sensor.
    def __init__(self, sensor_pins):
        """ Initialize an array of line sensors. """
        self.sensors = [LineSensor(pin) for pin in sensor_pins]

    ## @brief Calibrates the sensor array.
    #  @details Prompts the user to place sensors over white and black surfaces,
    #           reads the raw ADC values, and calibrates each sensor accordingly.
    def calibrate(self):
        """ Calibrate the sensor array by setting white and black reference."""
        print("Place sensors over a WHITE surface and press Enter...")
        input()  # Wait for user input before reading values
        white_values = [sensor.read_raw() for sensor in self.sensors]

        print("Place sensors over a BLACK surface and press Enter...")
        input()  # Wait for user input before reading values
        black_values = [sensor.read_raw() for sensor in self.sensors]

        for sensor, w_val, b_val in zip(self.sensors, white_values, black_values):
            sensor.calibrate(w_val, b_val)  # Calibrate each sensor with corresponding values
            
        print("Calibration complete.")

    ## @brief Reads normalized values from all sensors.
    #  @return A list of floating-point values representing normalized sensor readings.
    def read_all(self):
        """ Read normalized values from all sensors. """
        return [sensor.read_normalized() for sensor in self.sensors]

    ## @brief Computes the centroid of detected black lines.
    #  @details Calculates a weighted average index of the sensor readings to determine
    #           the center position of a detected line. If no line is detected, returns None.
    #  @return A floating-point index representing the centroid of the detected line, or None if no line is detected.
    def compute_centroid(self):
        """
        Compute the centroid of detected black lines.
        Returns a floating-point index representing center of the detected line.
        """
        readings = self.read_all()
        weighted_sum = sum(index * value for index, value in enumerate(readings))
        total_intensity = sum(readings)

        if total_intensity == 0:
            return None  # No line detected
        return weighted_sum / total_intensity  # Centroid calculation

