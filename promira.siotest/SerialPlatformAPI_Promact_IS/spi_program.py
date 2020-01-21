#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Simple SPI EEPROM programmer.
# File    : spi_program.py
#--------------------------------------------------------------------------
# Program an SPI EEPROM device using an Intel Hex format file.
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
# A mapping of devices to their (total memory size, page size)
#
SPI_BITRATE = 4000
SS_MASK     = 0x1

DEVICES = {
   "AT25256" : (32768, 64),
   "AT25080" : (1024, 32)
}


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
def _writeMemory (channel, queue, device, data):
    # Determine the max size and page size of eeprom
    (max_size, page_size) = DEVICES[device]

    n = 0
    while (n < len(data)):
        # Clear the queue
        ps_queue_clear(queue)

        # Send write enable command
        data_out = array('B', [ 0x06 ])
        ps_queue_spi_ss(queue, SS_MASK)
        ps_queue_spi_write(queue, 0, 8, len(data_out), data_out)
        ps_queue_spi_ss(queue, 0)

        # Assemble the write command and address
        data_out = array('B', [ 0x02, (n >> 8) & 0xff, (n >> 0) & 0xff ])

        # Write the transaction
        ps_queue_spi_ss(queue, SS_MASK)
        ps_queue_spi_write(queue, 0, 8, len(data_out), data_out)
        ps_queue_spi_write(queue, 0, 8, page_size, data[n:n + page_size])
        ps_queue_spi_ss(queue, 0)
        ps_queue_spi_delay_ns(queue, 10 * 1000 * 1000)

        collect, _ = ps_queue_submit(queue, channel, 0)
        dev_collect(collect)

        n += page_size

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

    return data_in[3:]


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 4):
    print("usage: spi_program IP DEVICE MODE FILENAME")
    print("  DEVICE    is the EEPROM device type")
    print("             - AT25256")
    print("             - AT25080")
    print("  MODE      is the SPI Mode")
    print("  FILENAME  is the Intel Hex Record file that")
    print("            contains the data to be sent to the")
    print("            SPI EEPROM")
    sys.exit()

ip     = sys.argv[1]
device = sys.argv[2]
mode   = int(sys.argv[3])
file   = sys.argv[4]

# Test for valid device
if (device not in DEVICES):
    print("%s is not a supported device" % device)
    sys.exit()

(max_size, page_size) = DEVICES[device]

# Try to open file
try:
    f = open(file, 'r')
except:
    print("Unable to open file '" + file + "'")
    sys.exit()

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
bitrate = ps_spi_bitrate(channel, SPI_BITRATE)
print("Bitrate set to %d kHz" % bitrate)

# Create a queue for SPI transactions
queue = ps_queue_create(conn, PS_MODULE_ID_SPI_ACTIVE)

# Enable master output
spi_master_oe(channel, queue, 1)

# Create a 64k array of 0xFF
data_in = array('B', [ 0xff for i in range(65535) ])

# Parse file
#
# Read each line of the hex file and verify
print("Reading File: %s..." % file)

line_it = 1;
while 1:
    line = f.readline()

    # If empty, then end of file
    if (len(line) == 0):
        break

    # Strip newline, linefeed and whitespace
    line = line.strip()

    # If empty, after strip, then it is simply a newline.
    if (len(line) == 0):
        continue

    # Strip colon
    line = line[1:]

    # Parse line length
    line_length = int(line[0:2], 16)

    # Verify line length
    if (len(line) != line_length * 2 + 2 + 4 + 2 + 2):
        print("Error in line %d: Length mismatch" % line_it)
        sys.exit()

    # Verify line checksum
    line_check = 0
    for x in range(len(line)//2):
        line_check += int(line[x * 2:x * 2 + 2], 16)
    if (line_check&0xff != 0):
        print("Error in line %d: Line Checksum Error" % line_it)
        sys.exit()

    line_addr   = int(line[2:6], 16)
    line_type   = int(line[6:8], 16)

    # Verify type
    if (line_type > 1):
        print("Error in line %d: Unsupported hex-record type" % line_it)
        sys.exit()

    line_data   = line[8:-2]

    # Populate the data_in array
    if (line_type == 0):
        for x in range(line_length):
            data_in[line_addr + x] = int(line_data[x * 2:x * 2 + 2], 16)

    # Increment iterator
    line_it += 1

# Truncate the data_in to the maximum size for the EEPROM
data_in = data_in[:DEVICES[device][0]]

# Generate Checksum of data
checksum = 0;
for x in range(len(data_in)):
    checksum += data_in[x]

print("Checksum: 0x%x" % checksum)

print("Writing EEPROM...")
_writeMemory(channel, queue, device, data_in)

print("Reading EEPROM... pass 1")
test1 = _readMemory(channel, queue, 0, max_size)

if data_in == test1:
    print("...PASSED")
else:
    print("...FAILED")

print("Reading EEPROM... pass 2")
test2 = _readMemory(channel, queue, 0, max_size)

if data_in == test2:
    print("...PASSED")
else:
    print("...FAILED")

# Disable master output
spi_master_oe(channel, queue, 0)

# Destroy the queue
ps_queue_destroy(queue)

# Close the device and exit
dev_close(pm, conn, channel)
