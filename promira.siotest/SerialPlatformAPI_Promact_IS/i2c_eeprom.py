#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : i2c_eeprom.py
#--------------------------------------------------------------------------
# Perform simple read and write operations to an I2C EEPROM device.
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
PAGE_SIZE   = 8
BUS_TIMEOUT = 150  # ms


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
def _writeMemory (channel, device, addr, length, zero):
    # Write to the I2C EEPROM
    #
    # The AT24C02 EEPROM has 8 byte pages.  Data can written
    # in pages, to reduce the number of overall I2C transactions
    # executed through the Promira adapter.
    n = 0
    while (n < length):
        data_out = array('B', [ 0 for i in range(1+PAGE_SIZE) ])

        # Fill the packet with data
        data_out[0] = addr & 0xff

        # Assemble a page of data
        i = 1
        while 1:
            if not (zero): data_out[i] = n & 0xff

            addr = addr + 1
            n = n +1
            i = i+1

            if not (n < length and (addr & (PAGE_SIZE-1)) ): break

        # Truncate the array to the exact data size
        del data_out[i:]

        # Write the address and data
        ret, count = ps_i2c_write(channel, device, PS_I2C_NO_FLAGS, data_out)
        if (ret < 0):
            print("error: %d" % ret)
            return
        elif (count == 0):
            print("error: no bytes written")
            print("  are you sure you have the right slave address?")
            return
        ps_app_sleep_ms(10)


def _readMemory (channel, device, addr, length):
    # Write the address
    ps_i2c_write(channel, device, PS_I2C_NO_STOP, array('B', [addr & 0xff]))

    (ret, data_in, count) = ps_i2c_read(channel, device,
                                        PS_I2C_NO_FLAGS, length)
    if (ret < 0):
        print("error: %d" % ret)
        return
    elif (count == 0):
        print("error: no bytes read")
        print("  are you sure you have the right slave address?")
        return
    elif (count != length):
        print("error: read %d bytes (expected %d)" % (count, length))

    # Dump the data to the screen
    sys.stdout.write("\nData read from device:")
    for i in range(count):
        if ((i&0x0f) == 0):
            sys.stdout.write("\n%04x:  " % (addr+i))

        sys.stdout.write("%02x " % (data_in[i] & 0xff))
        if (((i+1)&0x07) == 0):
            sys.stdout.write(" ")

    sys.stdout.write("\n")



#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 7):
    print("usage: i2c_eeprom IP BITRATE read  SLAVE_ADDR OFFSET LENGTH")
    print("usage: i2c_eeprom IP BITRATE write SLAVE_ADDR OFFSET LENGTH")
    print("usage: i2c_eeprom IP BITRATE zero  SLAVE_ADDR OFFSET LENGTH")
    sys.exit()

ip      = sys.argv[1]
bitrate = int(sys.argv[2])
command = sys.argv[3]
device  = int(sys.argv[4], 0)
addr    = int(sys.argv[5], 0)
length  = int(sys.argv[6])

# Open the device
pm, conn, channel = dev_open(ip)

# Ensure that the SPI subsystem is enabled
ps_app_configure(channel, PS_APP_CONFIG_SPI | PS_APP_CONFIG_I2C)

# Enable the I2C bus pullup resistors.
ps_i2c_pullup(channel, PS_I2C_PULLUP_BOTH)

# Power the board using the Promira adapter's power supply.
ps_phy_target_power(channel, PS_PHY_TARGET_POWER_BOTH)

# Set the bitrate
bitrate = ps_i2c_bitrate(channel, bitrate)
print("Bitrate set to %d kHz" % bitrate)

# Set the bus lock timeout
bus_timeout = ps_i2c_bus_timeout(channel, BUS_TIMEOUT)
print("Bus lock timeout set to %d ms" % bus_timeout)

# Perform the operation
if (command == "write"):
    _writeMemory(channel, device, addr, length, 0)
    print("Wrote to EEPROM")

elif (command == "read"):
    _readMemory(channel, device, addr, length)

elif (command == "zero"):
    _writeMemory(channel, device, addr, length, 1)
    print("Zeroed EEPROM")

else:
    print("unknown command: %s" % command)

# Close the device and exit
dev_close(pm, conn, channel)
