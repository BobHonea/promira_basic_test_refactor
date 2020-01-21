#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : spi_slave.py
#--------------------------------------------------------------------------
# Configure the device as an SPI slave and watch incoming data.
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

SS_MASK          = 0x1


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
    print("Watching slave SPI data...")

    # Wait for data on bus
    result = ps_spi_slave_poll(channel, timeout_ms)
    if (result == PS_SPI_SLAVE_NO_DATA):
        print("No data available.")
        return

    print("")

    trans_num = 0

    # Loop until ps_spi_slave_read times out
    while True:
        if (result == PS_SPI_SLAVE_DATA):
            # Read the SPI message.
            # This function has an internal timeout (see datasheet).
            # To use a variable timeout the function ps_spi_slave_poll could
            # be used for subsequent messages.
            (num_read, info, data_in) = ps_spi_slave_read(channel, BUFFER_SIZE)

            if num_read < 0:
                print("error: %d" % num_read)
                return

            if num_read == 0:
                print("No more data available from SPI master")
                return

            # Dump the data to the screen
            sys.stdout.write("*** Transaction #%02d\n" % trans_num)
            sys.stdout.write("Data read from device: SS:%d, IsLast:%d" %
                             (info.ss_mask, info.is_last))
            for i in range(num_read):
                if ((i & 0x0f) == 0):
                    sys.stdout.write("\n%04x:  " % i)

                sys.stdout.write("%02x " % (data_in[i] & 0xff))
                if (((i + 1) & 0x07) == 0):
                    sys.stdout.write(" ")

            sys.stdout.write("\n\n")

        elif (result == PS_SPI_SLAVE_DATA_LOST):
            # Get number of packets lost since queue in the device is full
            num_packets = ps_spi_slave_data_lost_stats(channel)

            if (num_packets < 0):
                print("error: %d" % ret)
                return

            print("*** Transaction #%02d" % trans_num)
            print("Number of packet Lost: %04d" % num_packets)
            print("")

        trans_num = trans_num + 1

        # Use ps_spi_slave_poll to wait for the next transaction
        result = ps_spi_slave_poll(channel, INTERVAL_TIMEOUT)
        if (result == PS_SPI_SLAVE_NO_DATA):
            print("No more data available from SPI master.")
            break


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 4):
    print("usage: spi_slave IP IO TIMEOUT_MS")
    print("  IO : 0 - standard, 2 - dual, 4 - quad")
    print("")
    print("  The timeout value specifies the time to")
    print("  block until the first packet is received.")
    print("  If the timeout is -1, the program will")
    print("  block indefinitely.")
    sys.exit()

ip         = sys.argv[1]
data_io    = int(sys.argv[2])
timeout_ms = int(sys.argv[3])

# Open the device
pm, conn, channel = dev_open(ip)

# Ensure that the SPI subsystem is enabled
ps_app_configure(channel, PS_APP_CONFIG_SPI | PS_APP_CONFIG_I2C)

# Disable the Promira adapter's power supply.
ps_phy_target_power(channel, PS_PHY_TARGET_POWER_NONE)

# Setup the clock phase
ps_spi_configure(channel, PS_SPI_MODE_0, PS_SPI_BITORDER_MSB, 0)

# Configure SS
ps_spi_enable_ss(channel, SS_MASK)

# Set the slave response
ps_spi_std_slave_set_resp(channel,
                          array('B', [ ord('A') + i
                                       for i in range(SLAVE_RESP_SIZE) ]))

# Enable the slave
ps_spi_slave_enable(channel, PS_SPI_SLAVE_MODE_STD)

# Configure SPI slave
ps_spi_std_slave_configure(channel, data_io, 0)

# Set host read size
# if one SPI transaction slave received is bigger than this,
# it will be splited to many.
ps_spi_slave_host_read_size(channel, BUFFER_SIZE)

# Watch the SPI port
dump(channel, timeout_ms)

# Disable the slave
ps_spi_slave_disable(channel)

# Close the device and exit
dev_close(pm, conn, channel)
