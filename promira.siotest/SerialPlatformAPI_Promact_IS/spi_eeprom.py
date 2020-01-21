#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : spi_eeprom.py
#--------------------------------------------------------------------------
# Perform simple read and write operations to an SPI EEPROM device.
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
PAGE_SIZE = 32
SS_MASK   = 0x1


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
def _writeMemory (channel, queue, addr, length, zero):
    # Write to the SPI EEPROM
    #
    # The AT25080A EEPROM has 32 byte pages.  Data can written
    # in pages, to reduce the number of overall SPI transactions
    # executed through the Promira adapter.
    n = 0
    while (n < length):
        # Clear the queue
        ps_queue_clear(queue)

        # Send write enable command
        data_out = array('B', [ 0x06 ])
        ps_queue_spi_ss(queue, SS_MASK)
        ps_queue_spi_write(queue, 0, 8, len(data_out), data_out)
        ps_queue_spi_ss(queue, 0)

        # Assemble write command and address
        data_out = array('B', [ 0x02,
                                ((addr + n) >> 8) & 0xff,
                                ((addr + n) >> 0) & 0xff ])

        # Assemble a page of data
        if zero:
            data = array('B', [0 for x in range(PAGE_SIZE)])
        else:
            data = array('B', [(n + x) & 0xff for x in range(PAGE_SIZE)])

        if n + PAGE_SIZE > length:
            data = data[:length - n]
        n = n + PAGE_SIZE

        # Write the transaction
        ps_queue_spi_ss(queue, SS_MASK)
        ps_queue_spi_write(queue, 0, 8, len(data_out), data_out)
        ps_queue_spi_write(queue, 0, 8, len(data), data)
        ps_queue_spi_ss(queue, 0)
        ps_queue_spi_delay_ns(queue, 10 * 1000 * 1000)

        collect, _ = ps_queue_submit(queue, channel, 0)
        dev_collect(collect)

def _readMemory (channel, queue, addr, length):
    # Assemble read command and address
    data_out = array('B', [ 0x03, (addr >> 8) & 0xff, (addr >> 0) & 0xff ])

    # Clear the queue
    ps_queue_clear(queue)

    # Write the transaction
    ps_queue_spi_ss(queue, SS_MASK)
    ps_queue_spi_write(queue, 0, 8, len(data_out), data_out)
    ps_queue_spi_write_word(queue, 0, 8, length, 0)
    ps_queue_spi_ss(queue, 0)

    collect, _ = ps_queue_submit(queue, channel, 0)
    data_in = dev_collect(collect)

    if (len(data_in) != length + 3):
        print("error: read %d bytes (expected %d)" % (len(data_in) - 3, length))

    # Dump the data to the screen
    sys.stdout.write("\nData read from device:")
    for i in range(len(data_in) - 3):
        if ((i & 0x0f) == 0):
            sys.stdout.write("\n%04x:  " % (addr + i))

        sys.stdout.write("%02x " % (data_in[i + 3] & 0xff))
        if (((i + 1) & 0x07) == 0):
            sys.stdout.write(" ")

    sys.stdout.write("\n")


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 7):
    print("usage: spi_eeprom IP BITRATE read  MODE ADDR LENGTH")
    print("usage: spi_eeprom IP BITRATE write MODE ADDR LENGTH")
    print("usage: spi_eeprom IP BITRATE zero  MODE ADDR LENGTH")
    sys.exit()

ip      = sys.argv[1]
bitrate = int(sys.argv[2])
command = sys.argv[3]
mode    = int(sys.argv[4])
addr    = int(sys.argv[5], 0)
length  = int(sys.argv[6])

# Open the device
pm, conn, channel = dev_open(ip)

# Ensure that the SPI subsystem is enabled
ps_app_configure(channel, PS_APP_CONFIG_SPI | PS_APP_CONFIG_I2C)

# Power the board using the Promira adapter's power supply.
ps_phy_target_power(channel, PS_PHY_TARGET_POWER_BOTH)

# Setup the clock phase
ps_spi_configure(channel, mode, PS_SPI_BITORDER_MSB, 0)

# Configure SS
ps_spi_enable_ss(channel, SS_MASK)

# Set the bitrate
bitrate = ps_spi_bitrate(channel, bitrate)
print("Bitrate set to %d kHz" % bitrate)

# Create a queue for SPI transactions
queue = ps_queue_create(conn, PS_MODULE_ID_SPI_ACTIVE)

# Enable master output
spi_master_oe(channel, queue, 1)

# Perform the operation
if "write".startswith(command):
    _writeMemory(channel, queue, addr, length, 0)
    print("Wrote to EEPROM")

elif "read".startswith(command):
    _readMemory(channel, queue, addr, length)

elif "zero".startswith(command):
    _writeMemory(channel, queue, addr, length, 1)
    print("Zeroed EEPROM")

else:
    print("unknown command: %s" % command)

# Disable master output
spi_master_oe(channel, queue, 0)

# Destroy the queue
ps_queue_destroy(queue)

# Close the device and exit
dev_close(pm, conn, channel)
