#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## @file uart_config.py
#  @brief  Configures UART3 and sets appropriate pin modes.
#
#  This script initializes UART3 with a baud rate of 115200 and sets it as the
#  REPL UART. It then configures specific CPU pins:
#    - Pins C4 and C5 are reset to their default analog mode.
#    - Pins C10 and C11 are configured to use the alternate function (UART) as
#      per column 7 in the alternate function table.
#
#  @author  
#  @date   2025-Feb-24
#

import pyb
from pyb import Pin, UART

## Initialize UART3 with a baud rate of 115200 and set it as the REPL UART.
ser = UART(3, 115200)
pyb.repl_uart(ser)

## Reset pins C4 and C5 to their default analog mode.
Pin(Pin.cpu.C4, mode=Pin.ANALOG)     # Set pin modes back to default
Pin(Pin.cpu.C5, mode=Pin.ANALOG)

## Configure pins C10 and C11 for UART operation.
#  According to the alternate function table, these pins are set to use alternate function 7.
Pin(Pin.cpu.C10, mode=Pin.ALT, alt=7) # Set pin modes to UART (alt function 7)
Pin(Pin.cpu.C11, mode=Pin.ALT, alt=7)
