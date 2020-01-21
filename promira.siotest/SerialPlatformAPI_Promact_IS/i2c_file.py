#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : i2c_file.c
#--------------------------------------------------------------------------
# Configure the device as an I2C master and send data.
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
BUFFER_SIZE = 2048
I2C_BITRATE =  400


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
def blast_bytes (channel, slave_addr, filename):
    # Open the file
    try:
        f=open(filename, 'rb')
    except:
        print("Unable to open file '" + filename + "'")
        return

    trans_num = 0
    while 1:
        # Read from the file
        filedata = f.read(BUFFER_SIZE)
        if (len(filedata) == 0):
            break

        # Write the data to the bus
        data_out = array('B', filedata)
        count, num_bytes = ps_i2c_write(channel, slave_addr, PS_I2C_NO_FLAGS,
                                        data_out)

        if (count < 0):
            print("error: %d" % count)
            break
        elif (num_bytes == 0):
            print("error: no bytes written")
            print("  are you sure you have the right slave address?")
            break
        elif (num_bytes != len(data_out)):
            print("error: only a partial number of bytes written")
            print("  (%d) instead of full (%d)" % (num_bytes, num_write))
            break

        sys.stdout.write("*** Transaction #%02d\n" % trans_num)

        # Dump the data to the screen
        sys.stdout.write("Data written to device:")
        for i in range(num_bytes):
            if ((i&0x0f) == 0):
                sys.stdout.write("\n%04x:  " % i)

            sys.stdout.write("%02x " % (data_out[i] & 0xff))
            if (((i+1)&0x07) == 0):
                sys.stdout.write(" ")

        sys.stdout.write("\n\n")

        trans_num = trans_num + 1

        # Sleep a tad to make sure slave has time to process this request
        ps_app_sleep_ms(10)

    f.close()


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 4):
    print("usage: i2c_file IP SLAVE_ADDR filename")
    print("  SLAVE_ADDR is the target slave address")
    print("")
    print("  'filename' should contain data to be sent")
    print("  to the downstream i2c device")
    sys.exit()

ip       = sys.argv[1]
addr     = int(sys.argv[2], 0)
filename = sys.argv[3]

# Open the device
pm, conn, channel = dev_open(ip)

# Ensure that the I2C subsystem is enabled
ps_app_configure(channel, PS_APP_CONFIG_SPI | PS_APP_CONFIG_I2C)

# Enable the I2C bus pullup resistors.
ps_i2c_pullup(channel, PS_I2C_PULLUP_BOTH)

# Enable the Promira adapter's power supply.
ps_phy_target_power(channel, PS_PHY_TARGET_POWER_BOTH)

# Set the bitrate
bitrate = ps_i2c_bitrate(channel, I2C_BITRATE)
print("Bitrate set to %d kHz" % bitrate)

blast_bytes(channel, addr, filename)

# Close the device and exit
dev_close(pm, conn, channel)
