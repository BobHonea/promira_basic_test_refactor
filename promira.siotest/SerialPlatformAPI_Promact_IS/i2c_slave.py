#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : i2c_slave.py
#--------------------------------------------------------------------------
# Configure the device as an I2C slave and watch incoming data.
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
BUFFER_SIZE      = 65535
SLAVE_RESP_SIZE  =    26
INTERVAL_TIMEOUT =   500


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
def dump (channel, timeout_ms):
    print("Watching slave I2C data...")

    # Wait for data on bus
    result = ps_i2c_slave_poll(channel, timeout_ms)
    if (result == PS_I2C_SLAVE_NO_DATA):
        print("No data available.")
        return

    trans_num = 0

    # Loop until ps_i2c_slave_poll times out
    while 1:
        # Read the I2C message.
        # This function has an internal timeout (see datasheet), though
        # since we have already checked for data using ps_i2c_slave_poll,
        # the timeout should never be exercised.
        if (result == PS_I2C_SLAVE_READ):
            # Get data written by master
            ret, addr, data_in, num_bytes = ps_i2c_slave_read(channel,
                                                              BUFFER_SIZE)

            if (ret < 0):
                print("error: %d" % ret)
                return

            # Dump the data to the screen
            sys.stdout.write("*** Transaction #%02d\n" % trans_num)
            sys.stdout.write("Data read from device:")
            for i in range(num_bytes):
                if ((i&0x0f) == 0):
                    sys.stdout.write("\n%04x:  " % i)

                sys.stdout.write("%02x " % (data_in[i] & 0xff))
                if (((i+1)&0x07) == 0):
                    sys.stdout.write(" ")

            sys.stdout.write("\n\n")

        elif (result == PS_I2C_SLAVE_WRITE):
            # Get number of bytes written to master
            ret, addr, num_bytes = ps_i2c_slave_write_stats(channel)

            if (num_bytes < 0):
                print("error: %d" % ret)
                return

            # Print status information to the screen
            print("*** Transaction #%02d" % trans_num)
            print("Number of bytes written to master: %04d" % num_bytes)
            print("")

        elif (result == PS_I2C_SLAVE_DATA_LOST):
            # Get number of packets lost since queue in the device is full
            ret, num_packets = ps_i2c_slave_data_lost_stats(channel)

            if (num_packets < 0):
                print("error: %d" % ret)
                return

            print("*** Transaction #%02d" % trans_num)
            print("Number of packet Lost: %04d" % num_packets)
            print("")

        else:
            print("error: non-I2C asynchronous message is pending")
            return

        trans_num = trans_num + 1

        # Use ps_i2c_slave_poll to wait for the next transaction
        result = ps_i2c_slave_poll(channel, INTERVAL_TIMEOUT)
        if (result == PS_I2C_SLAVE_NO_DATA):
            print("No more data available from I2C master.")
            break




#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 4):
    print("usage: i2c_slave IP SLAVE_ADDR TIMEOUT_MS")
    print("  SLAVE_ADDR is the slave address for this device")
    print("")
    print("  The timeout value specifies the time to")
    print("  block until the first packet is received.")
    print("  If the timeout is -1, the program will")
    print("  block indefinitely.")
    sys.exit()

ip         = sys.argv[1]
addr       = int(sys.argv[2], 0)
timeout_ms = int(sys.argv[3])

# Open the device
pm, conn, channel = dev_open(ip)

# Ensure that the I2C subsystem is enabled
ps_app_configure(channel, PS_APP_CONFIG_SPI | PS_APP_CONFIG_I2C)

# Enable the I2C bus pullup resistors.
ps_i2c_pullup(channel, PS_I2C_PULLUP_BOTH)

# Power the board using the Promira adapter's power supply.
ps_phy_target_power(channel, PS_PHY_TARGET_POWER_BOTH)

# Set the slave response
slave_resp = array('B', [ 0 for i in range(SLAVE_RESP_SIZE) ])
for i in range(SLAVE_RESP_SIZE):
    slave_resp[i] = ord('A') + i
ps_i2c_slave_set_resp(channel, slave_resp)

# Enable the slave
ps_i2c_slave_enable(channel, addr, 0, 0)

# Watch the I2C port
dump(channel, timeout_ms)

# Disable the slave and close the device
ps_i2c_slave_disable(channel)
dev_close(pm, conn, channel)
