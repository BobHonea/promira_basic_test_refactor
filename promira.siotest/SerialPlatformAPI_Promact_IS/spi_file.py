#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : spi_file.c
#--------------------------------------------------------------------------
# Configure the device as an SPI master and send data.
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
SS_MASK     = 0x1
SPI_BITRATE = 20000


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

def dev_collect (collect):
    if collect < 0:
        print(ps_app_status_string(collect))
        return

    response = array('B', [ ])
    while True:
        t, length, result = ps_collect_resp(collect, -1)
        if t == PS_APP_NO_MORE_CMDS_TO_COLLECT:
            break
        elif t < 0:
            print(ps_app_status_string(t))
        if t == PS_SPI_CMD_READ:
            ret, word_size, buf = ps_collect_spi_read(collect, result)
            response += buf
    return response

def spi_master_oe (channel, queue, enable):
    ps_queue_clear(queue)
    ps_queue_spi_oe(queue, enable)
    collect, _, = ps_queue_submit(queue, channel, 0)
    dev_collect(collect)


#==========================================================================
# FUNCTIONS
#==========================================================================
def blast_bytes (channel, queue, data_io, filename):
    # Open the file
    try:
        f = open(filename, 'rb')
    except:
        print("Unable to open file '" + filename + "'")
        return

    trans_num = 0
    while True:
        # Read from the file
        filedata = f.read(BUFFER_SIZE)
        if len(filedata) == 0:
            break

        # Clear the queue
        ps_queue_clear(queue)

        # Write the data to the bus
        data_out = array('B', filedata)
        ps_queue_spi_ss(queue, SS_MASK)
        ps_queue_spi_write(queue, data_io, 8, len(data_out), data_out)
        ps_queue_spi_ss(queue, 0)

        collect, _ = ps_queue_submit(queue, channel, 0)
        data_in = dev_collect(collect)

        count = len(data_in)
        if (count != len(data_out)):
            print("error: only a partial number of bytes written")
            print("  (%d) instead of full (%d)" % (count, len(data_out)))

        sys.stdout.write("*** Transaction #%02d\n" % trans_num)
        # sys.stdout.write("Data written to device:")
        # for i in range(count):
        #     if ((i & 0x0f) == 0):
        #         sys.stdout.write("\n%04x:  " % i)

        #     sys.stdout.write("%02x " % (data_out[i] & 0xff))
        #     if (((i + 1) & 0x07) == 0):
        #         sys.stdout.write(" ")

        # sys.stdout.write("\n\n")

        sys.stdout.write("Data read from device:")
        for i in range(count):
            if ((i & 0x0f) == 0):
                sys.stdout.write("\n%04x:  " % i)

            sys.stdout.write("%02x " % (data_in[i] & 0xff))
            if (((i + 1) & 0x07) == 0):
                sys.stdout.write(" ")

        sys.stdout.write("\n\n")

        trans_num = trans_num + 1

        # Sleep a tad to make sure slave has time to process this request
        # ps_app_sleep_ms(10)

    f.close()


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 4):
    print("usage: spi_file IP IO filename")
    print("  'filename' should contain data to be sent")
    print("  to the downstream spi device")
    sys.exit()

ip       = sys.argv[1]
data_io  = int(sys.argv[2])
filename = sys.argv[3]

# Open the device
pm, conn, channel = dev_open(ip)

# Ensure that the SPI subsystem is enabled
ps_app_configure(channel, PS_APP_CONFIG_SPI | PS_APP_CONFIG_I2C)

# Power the board using the Promira adapter's power supply.
ps_phy_target_power(channel, PS_PHY_TARGET_POWER_BOTH)

# Setup the clock phase
ps_spi_configure(channel, PS_SPI_MODE_0, PS_SPI_BITORDER_MSB, 0)

# Configure SS
ps_spi_enable_ss(channel, SS_MASK)

# Set the bitrate
bitrate = ps_spi_bitrate(channel, 1000)
print("Bitrate set to %d kHz" % bitrate)

# Create a queue for SPI transactions
queue = ps_queue_create(conn, PS_MODULE_ID_SPI_ACTIVE)

# Enable master output
spi_master_oe(channel, queue, 1)

# Perform the operation
blast_bytes(channel, queue, data_io, filename)

# Disable master output
spi_master_oe(channel, queue, 0)

# Destroy the queue
ps_queue_destroy(queue)

# Close the device and exit
dev_close(pm, conn, channel)
