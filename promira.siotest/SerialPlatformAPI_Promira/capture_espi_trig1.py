#!/bin/env python
#==========================================================================
# (c) 2015 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : capture_espi_trig1.py
#--------------------------------------------------------------------------
# Illustrate Advance Trigger Option 1 and capture eSPI transactions
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
import sys
import time

from promira_py import *
from promana_py import *


#==========================================================================
# CONSTANTS
#==========================================================================
GET_STATUS = 0x25
PUT_PC     = 0x0
MEM_WR32   = 0x1

#==========================================================================
# FUNCTION (APP)
#==========================================================================
APP_NAME = "com.totalphase.promana_espi"
def dev_open (ip):
    pm = pm_open(ip)
    if pm <= 0:
         print "Unable to open Promira platform on %s" % ip
         print "Error code = %d" % pm
         sys.exit()

    ret = pm_load(pm, APP_NAME)
    if ret < 0:
         print "Unable to load the application(%s)" % APP_NAME
         print "Error code = %d" % ret
         sys.exit()

    conn = pa_app_connect(ip)
    if conn <= 0:
         print "Unable to open the application on %s" % ip
         print "Error code = %d" % conn
         sys.exit()

    return pm, conn

def dev_close (pm, conn):
    pa_app_disconnect(conn)
    pm_close(pm)

def print_timestamp (info):
    print '%4d.%03d.%03d.%03d, %2d.%03d.%03d, ' \
        % ((info.timestamp / (10**9)),
           (info.timestamp / (10**6)) % 1000,
           (info.timestamp / (10**3)) % 1000,
           (info.timestamp / (10**0)) % 1000,
           (info.duration / (10**9)) % 1000,
           (info.duration / (10**6)) % 1000,
           (info.duration / (10**3)) % 1000),

def print_status (info, pkt_info):
    msg   = [ ]
    error = [ ]

    # event type
    if info.events & PA_EVENT_DIGITAL_INPUT:
        msg.append('Digital Input[%03x]'
                   % (info.events & PA_EVENT_DIGITAL_INPUT_MASK))
    if info.events & PA_EVENT_ESPI_ALERT_RISING:
        msg.append('Alert Rising')
    if info.events & PA_EVENT_ESPI_ALERT_FALLING:
        msg.append('Alert Falling')
    if info.events & PA_EVENT_ESPI_RESET_RISING:
        msg.append('Reset Rising')
    if info.events & PA_EVENT_ESPI_RESET_FALLING:
        msg.append('Reset Falling')
    if info.events & PA_EVENT_ESPI_INBAND_RESET:
        msg.append('Inband Reset')
    if info.events & PA_EVENT_TRIGGER:
        msg.append('Trigger!')
    if info.events & PA_EVENT_ESPI_PACKET:
        msg.append('Packet')

        channel_str = [ 'unknown channel', 'perif', 'vw', 'oob',
                        'flash', 'indep' ]
        msg.append('%s' % channel_str[pkt_info.channel + 1])

        freq_int = [ 'unknown', 20, 25, 33, 50, 66 ]
        msg.append('%s MHz' % str(freq_int[pkt_info.enum_freq + 1]))

        io_str = [ 'single', 'dual', 'quad' ]
        msg.append('%s' % io_str[pkt_info.io_mode >> 1])

    # status
    # crc error
    if info.status & PA_READ_ESPI_ERR_BAD_CMD_CRC:
        error.append('Command CRC')

    if info.status & PA_READ_ESPI_ERR_BAD_RSP_CRC:
        error.append('Response CRC')

    error_code = (info.status & PA_READ_ERR_CODE_MASK)
    if error_code:
        error.append('Code(%x)' % error_code)

    print ' '.join(msg), #', ', ' '.join(error),


#==========================================================================
# eSPI DUMP FUNCTION
#==========================================================================
def espi_dump (conn, num_events):
    i = 0

    # Start the capture
    if pa_capture_start(conn, PA_PROTOCOL_ESPI,
                        PA_TRIGGER_MODE_IMMEDIATE) != PA_APP_OK:
        print "error: could not enable eSPI capture; exiting..."
        sys.exit(1)

    print "index,slave_id,time(ns),dur(us),status,cmd0 ... cmdN(*),rsp0 ... rspN(*)"

    # Capture and print each transaction
    while (i < num_events or num_events == 0):
        # Read transaction with bit timing data
        ret, info, pkt_info, data = pa_espi_read(conn, 8192)

        if ret == PA_APP_READ_EMPTY:
            continue

        if ret < 0:
            break

        print "%d," % i,

        slave_id = (info.events & PA_EVENT_SLAVE_ID_MASK) >> 28
        print "%d," % slave_id,

        print_timestamp(info)
        sys.stdout.write( "(")
        print_status(info, pkt_info)
        sys.stdout.write( ")")

        # Check for errors
        i += 1
        if not info.events & PA_EVENT_ESPI_PACKET:
            print ""
            sys.stdout.flush()

            # If zero data captured, continue
            continue

        sys.stdout.write(", ")

        # Print command
        if pkt_info.cmd_length > 0:
            for n in range(pkt_info.cmd_length - 1):
                sys.stdout.write("%02x " % data[n])

            sys.stdout.write("(%02x" % data[pkt_info.cmd_length - 1])
            if info.status & PA_READ_ESPI_ERR_BAD_CMD_CRC:
                sys.stdout.write("*), ")
            else:
                sys.stdout.write("), ")

        # Print response
        if pkt_info.length - pkt_info.cmd_length > 0:
            for n in range(pkt_info.cmd_length, pkt_info.length - 1):
                sys.stdout.write("%02x " % data[n])

            sys.stdout.write("(%02x" % data[pkt_info.length - 1])
            if info.status & PA_READ_ESPI_ERR_BAD_RSP_CRC:
                sys.stdout.write("*)")
            else:
                sys.stdout.write(")")

        print ""
        sys.stdout.flush()

    # Stop the capture
    pa_capture_stop(conn)

    return i


#==========================================================================
# USAGE INFORMATION
# =========================================================================
def print_usage ():
    print """Usage: adv_trig1_cap IP num_events
Example utility to illustrate eSPI advance trigger option 1 data from Promira protocol analyzers.
To generate a sequence of espi packets that satisfy this trigger condition
using Promira active espi generator, use the following command:
espi_generator.py IP set_config_10h get_status_pc_free perif_downstream_wr32

The trigger packet will have the following string in the status column
'Trigger!'

The parameter num_events is set to the number of events to process
before exiting.  If num_events is set to zero, the capture will continue
indefinitely.

For product documentation and specifications, see www.totalphase.com."""
    sys.stdout.flush()


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 2):
    print_usage()
    sys.exit()

ip         = sys.argv[1]
num_events = int(sys.argv[2])

# Open the device
pm, conn = dev_open(ip)

# Configure advance trigger option 1
pkt_adv_trig1_level1 = PromiraEspiAdvancedTrig1()
pkt_adv_trig1_level2 = PromiraEspiAdvancedTrig1()
pkt_adv_trig1_level3 = PromiraEspiAdvancedTrig1()
pkt_adv_trig1_level4 = PromiraEspiAdvancedTrig1()
pkt_adv_trig2        = PromiraEspiAdvancedTrig2()
pkt_adv_trig_error   = PromiraEspiAdvancedTrigError()

# Enable two levels of packet match. Select back to back
# sequence check, that means these two packets have to
# appear consecutively on the wire without any other
# packets in between them
# Level 1, match on a GET_STATUS command
pkt_adv_trig1_level1.cmd_byte             = GET_STATUS
pkt_adv_trig1_level1.cmd_byte_enable      = 1
pkt_adv_trig1_level1.lvl_select_enable    = 1
pkt_adv_trig1_level1.lvl_select_immediate = 1
# Level 2, match on a downstream memory write to a
# 32-bit address. The tag value must be 0xA and the
# address must be 0xFF008000
pkt_adv_trig1_level2.cmd_byte             = PUT_PC
pkt_adv_trig1_level2.cmd_cyc              = MEM_WR32
pkt_adv_trig1_level2.cmd_tag              = 0xA
pkt_adv_trig1_level2.cmd_addr             = 0xFF008000
pkt_adv_trig1_level2.cmd_byte_enable      = 1
pkt_adv_trig1_level2.cmd_cyc_enable       = 1
pkt_adv_trig1_level2.cmd_tag_enable       = 1
pkt_adv_trig1_level2.cmd_addr_enable      = 1
pkt_adv_trig1_level2.lvl_select_enable    = 1
pkt_adv_trig1_level2.lvl_select_immediate = 1
# Select slave 0
slave_id = 0

# Configure the analyzer
pa_espi_adv_trig_config(conn,                 \
                        slave_id,             \
                        pkt_adv_trig1_level1, \
                        pkt_adv_trig1_level2, \
                        pkt_adv_trig1_level3, \
                        pkt_adv_trig1_level4, \
                        pkt_adv_trig2,        \
                        pkt_adv_trig_error)

# Start capture. The function returns once a
# packet with trigger status is seen
ret = espi_dump(conn, num_events)
if (ret < 0):
    print "error: %d" % ret

# Close the device and exit
dev_close(pm, conn)
