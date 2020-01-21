#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : lights.py
#--------------------------------------------------------------------------
# Flash the lights on the Promira I2C/SPI Activity Board.
#--------------------------------------------------------------------------
# Redistribution and use of this file in source and binary forms, with
# or without modification, are permitted.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
from __future__ import division, with_statement, print_function
import sys
import time

from promira_py import *
from promact_is_py import *


#==========================================================================
# CONSTANTS
#==========================================================================
I2C_BITRATE = 100 # kHz


#==========================================================================
# FUNCTION (APP)
#==========================================================================
APP_NAME = "com.totalphase.promact_is"
def dev_open (ip):
    pm = pm_open(ip)
    if pm <= 0:
         print("Unable to open Promira platform on %s" % ip)
         print("Error code = %d" % pm)
         sys.exit()

    ret = pm_load(pm, APP_NAME)
    if ret < 0:
         print("Unable to load the application(%s)" % APP_NAME)
         print("Error code = %d" % ret)
         sys.exit()

    conn = ps_app_connect(ip)
    if conn <= 0:
         print("Unable to open the application on %s" % ip)
         print("Error code = %d" % conn)
         sys.exit()

    channel = ps_channel_open(conn)
    if channel <= 0:
         print("Unable to open the channel")
         print("Error code = %d" % channel)
         sys.exit()

    return pm, conn, channel

def dev_close (pm, app, channel):
    ps_channel_close(channel)
    ps_app_disconnect(conn)
    pm_close(pm)


#==========================================================================
# FUNCTIONS
#==========================================================================
def flash_lights (channel):
    data_out = array('B', [0, 0])

    # Configure I/O expander lines as outputs
    data_out[0] = 0x03
    data_out[1] = 0x00
    ret, count = ps_i2c_write(channel, 0x38, PS_I2C_NO_FLAGS, data_out)
    if (ret < 0):
        return ret
    elif (count == 0):
        print("error: slave device 0x38 not found")
        return 0

    # Turn lights on in sequence
    i = 0xff
    while (i != 0):
        i = ((i<<1) & 0xff)
        data_out[0] = 0x01
        data_out[1] = i
        ret, count = ps_i2c_write(channel, 0x38, PS_I2C_NO_FLAGS, data_out)
        if (ret < 0):
            return ret
        elif (count == 0):
            print("error: slave device 0x38 not found")
            return 0
        ps_app_sleep_ms(70)

    # Leave lights on for 100 ms
    ps_app_sleep_ms(100)

    # Turn lights off in sequence
    i = 0x00
    while (i != 0xff):
        i = ((i<<1) | 0x01)
        data_out[0] = 0x01
        data_out[1] = i
        ret, count = ps_i2c_write(channel, 0x38, PS_I2C_NO_FLAGS, data_out)
        if (ret < 0):
            return ret
        elif (count == 0):
            print("error: slave device 0x38 not found")
            return 0
        ps_app_sleep_ms(70)

    ps_app_sleep_ms(100)

    # Configure I/O expander lines as inputs
    data_out[0] = 0x03
    data_out[1] = 0xff
    ret, count = ps_i2c_write(channel, 0x38, PS_I2C_NO_FLAGS, data_out)
    if (ret < 0):
        return ret
    elif (count == 0):
        print("error: slave device 0x38 not found")
        return 0

    return 0


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 2):
    print("usage: lights IP")
    sys.exit()

ip = sys.argv[1]

# Open the device
pm, conn, channel = dev_open(ip)

# Ensure that the I2C subsystem is enabled
ps_app_configure(channel,  PS_APP_CONFIG_SPI | PS_APP_CONFIG_I2C)

# Enable the I2C bus pullup resistors.
ps_i2c_pullup(channel, PS_I2C_PULLUP_BOTH)

# Power the board using the Promira adapter's power supply.
ps_phy_target_power(channel, PS_PHY_TARGET_POWER_BOTH)

# Set the bitrate
bitrate = ps_i2c_bitrate(channel, I2C_BITRATE)
print("Bitrate set to %d kHz" % bitrate)

res = flash_lights(channel)
if (res < 0):
    print("error: %d" % res)

# Close the device and exit
dev_close(pm, conn, channel)
