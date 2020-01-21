#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : spi_n25q.py
#--------------------------------------------------------------------------
# Perform simple read/write/erase operations to an N25Q00A SPI flash
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
MB              = 1 * 1024 * 1024
KB              = 1 * 1024

CMD_DEV_ID  = [ 0x9F, 0x00, 0x00, 0x00 ]

DEV_IDS     = {
    'N25Q032A' : [ 0x20, 0xBA, 0x16 ],
    'N25Q064A' : [ 0x20, 0xBA, 0x17 ],
    'N25Q128A' : [ 0x20, 0xBA, 0x18 ],
    'N25Q256A' : [ 0x20, 0xBA, 0x19 ],
    'N25Q512A' : [ 0x20, 0xBA, 0x20 ],
    'N25Q00AA' : [ 0x20, 0xBA, 0x21 ],
}

DEV_NAME = None

DEV_SIZES = {
    'N25Q032A' : 4 * MB,
    'N25Q064A' : 8 * MB,
    'N25Q128A' : 16 * MB,
    'N25Q256A' : 32 * MB,
    'N25Q512A' : 64 * MB,
    'N25Q00AA' : 128 * MB,
}

ADDR_SIZES = {
    'N25Q032A' : 3,
    'N25Q064A' : 3,
    'N25Q128A' : 3,
    'N25Q256A' : 4,
    'N25Q512A' : 4,
    'N25Q00AA' : 4,
}

CMD_WREN    = [ 0x06 ]
CMD_STATUS  = [ 0x70, 0x00 ]

SETUP_CMDS = {
    'N25Q032A' : [ ],
    'N25Q064A' : [ ],
    'N25Q128A' : [ ],
    'N25Q256A' : [ CMD_WREN, [ 0xB7 ] ],
    'N25Q512A' : [ CMD_WREN, [ 0xB7 ] ],
    'N25Q00AA' : [ CMD_WREN, [ 0xB7 ] ],
}

ERASE_CMD = {
    'N25Q032A' : (0xC7, 0),
    'N25Q064A' : (0xC7, 0),
    'N25Q128A' : (0xC7, 0),
    'N25Q256A' : (0xC7, 0),
    'N25Q512A' : (0xC4, 32 * MB),
    'N25Q00AA' : (0xC4, 32 * MB),
}

CMDS   = {
    0 : (0x0B, 0x02, 1),
    2 : (0x3B, 0xA2, 2),
    4 : (0x6B, 0x32, 4),
}

READ_CMD_SIZE   = 32 * KB
READ_BLK_SIZE   = 512 * KB
WRITE_PAGE_SIZE = 256

BITRATE = 40000
SS_MASK = 1


#==========================================================================
# FUNCTION (APP)
#==========================================================================
APP_NAME = "com.totalphase.promact_is"
def dev_open (ip, sys_only=False):
    pm = pm_open(ip)
    if pm <= 0:
         print("Unable to open Promira platform on %s" % ip)
         print("Error code = %d" % pm)
         sys.exit()

    if sys_only:
        return pm, None, None

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
    if channel:
        ps_channel_close(channel)
    if app:
        ps_app_disconnect(app)
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
# HELPER FUNCTIONS
#==========================================================================
def dump_array (addr, data, index, count):
    for i in range(count):
        if not i & 0xf:
            if i:
                sys.stdout.write("\n")
            sys.stdout.write("%08x:  " % (addr + i))

        sys.stdout.write("%02x " % (data[index + i] & 0xff))
        if not (i + 1) & 0x7:
            sys.stdout.write(" ")
    sys.stdout.write("\n");

# Collect outstanding packets
def flash_collect (channel, addr, block_size, ignore_bytes,
                   print_buf_size = 16):
    collect, _ = ps_queue_async_collect(channel)
    if collect < 0:
        return False

    block_addr = 0

    ignore_bytes += [ 0 ]
    while True:
        t, length, result = ps_collect_resp(collect, -1)
        if t == PS_APP_NO_MORE_CMDS_TO_COLLECT:
            break
        elif t < 0:
            print(ps_app_status_string(t))

        if t == PS_SPI_CMD_READ:
            if ignore_bytes and result in ignore_bytes:
                continue

            ret, word_size, buf = ps_collect_spi_read(collect, result)

            if print_buf_size:
                dump_array(addr + block_addr, buf, 0, min(ret, print_buf_size))
                block_addr += ret

    return True


def get_addr (addr, addr_size):
    addr_field = [ (addr >> 24) & 0xff,
                   (addr >> 16) & 0xff,
                   (addr >> 8)  & 0xff,
                   (addr >> 0)  & 0xff ]

    return addr_field[4 - addr_size: ]


#==========================================================================
# FUNCTIONS
#==========================================================================
def flash_n25q_detect (channel, queue):
    global DEV_NAME
    ps_queue_clear(queue)

    ps_queue_spi_ss(queue, SS_MASK)
    ps_queue_spi_write(queue, 0, 8, 4, array('B', CMD_DEV_ID))
    ps_queue_spi_ss(queue, 0)

    collect, _ = ps_queue_submit(queue, channel, 0)
    data_in = dev_collect(collect)

    for name, devid in DEV_IDS.items():
        if data_in[1: ] == array('B', devid):
            print('Found model: %s, %d MB' % (name, DEV_SIZES[name] // MB))
            DEV_NAME = name
            break

def flash_n25q_prepare (channel, queue):
    cmds = SETUP_CMDS[DEV_NAME]

    for cmd in cmds:
        print('Sending command : ', [ hex(x) for x in cmd ])
        ps_queue_clear(queue)

        ps_queue_spi_ss(queue, SS_MASK)
        ps_queue_spi_write(queue, 0, 8, len(cmd), array('B', cmd))
        ps_queue_spi_ss(queue, 0)

        collect, _ = ps_queue_submit(queue, channel, 0)
        data_in = dev_collect(collect)

def flash_n25q_read (IO, channel, queue):
    CMD_READ, CMD_WRITE, DUMMY_BYTES  = CMDS[IO]
    DEV_SIZE  = DEV_SIZES[DEV_NAME]
    ADDR_SIZE = ADDR_SIZES[DEV_NAME]

    block_cnt = DEV_SIZE // READ_BLK_SIZE
    addr      = 0

    for i in range(block_cnt):
        ps_queue_clear(queue)

        # Assemble write command and address
        data = array('B', [ CMD_READ ] + get_addr(addr, ADDR_SIZE))

        ps_queue_spi_ss(queue, SS_MASK)
        # Write command and address and read dummy bytes and memory data
        ps_queue_spi_write(queue, 0, 8, len(data), data)
        ps_queue_spi_read(queue, IO, 8, DUMMY_BYTES)
        for _ in range(READ_BLK_SIZE // READ_CMD_SIZE):
            ps_queue_spi_read(queue, IO, 8, READ_CMD_SIZE)
        ps_queue_spi_ss(queue, 0)

        ps_queue_async_submit(queue, channel, 0)
        ret = flash_collect(channel, addr, READ_CMD_SIZE,
                            [ len(data), DUMMY_BYTES ])
        addr += READ_BLK_SIZE

def flash_n25q_erase (IO, channel, queue):
    DEV_SIZE = DEV_SIZES[DEV_NAME]
    CMD_ERASE, DIE_SIZE = ERASE_CMD[DEV_NAME]
    ADDR_SIZE = ADDR_SIZES[DEV_NAME]

    die_cnt   = 1 if DIE_SIZE == 0 else DEV_SIZE // DIE_SIZE
    ADDR_SIZE = 0 if DIE_SIZE == 0 else ADDR_SIZE

    addr = 0

    queue_busy = ps_queue_create(conn, PS_MODULE_ID_SPI_ACTIVE)

    ps_queue_spi_ss(queue_busy, SS_MASK)
    ps_queue_spi_write(queue_busy, 0, 8,
                       len(CMD_STATUS), array('B', CMD_STATUS))
    ps_queue_spi_ss(queue_busy, 0)

    for n in range(die_cnt):
        print('Erasing 0x%08x' % addr)
        ps_queue_clear(queue)

        # Write enable
        ps_queue_spi_ss(queue, SS_MASK)
        ps_queue_spi_write(queue, 0, 8,
                           len(CMD_WREN), array('B', CMD_WREN))
        ps_queue_spi_ss(queue, 0)

        # Erase
        data = array('B', [ CMD_ERASE ] + get_addr(addr, ADDR_SIZE))

        ps_queue_spi_ss(queue, SS_MASK)
        ps_queue_spi_write(queue, 0, 8, len(data), data)
        ps_queue_spi_ss(queue, 0)
        collect, _ = ps_queue_submit(queue, channel, 0)
        data_in = dev_collect(collect)

        while True:
            collect, _ = ps_queue_submit(queue_busy, channel, 0)
            data_in = dev_collect(collect)
            if data_in[-1] & 0x80:
                break

        addr += DIE_SIZE

    ps_queue_destroy(queue_busy)
    return 0

def flash_n25q_write (IO, channel, queue):
    CMD_READ, CMD_WRITE, DUMMY_BYTES  = CMDS[IO]
    DEV_SIZE  = DEV_SIZES[DEV_NAME]
    ADDR_SIZE = ADDR_SIZES[DEV_NAME]

    page_cnt = DEV_SIZE // WRITE_PAGE_SIZE
    addr = 0

    data_out = [ x & 0xff for x in range(DEV_SIZE) ]

    queue_busy = ps_queue_create(conn, PS_MODULE_ID_SPI_ACTIVE)

    ps_queue_spi_ss(queue_busy, SS_MASK)
    ps_queue_spi_write(queue_busy, 0, 8,
                       len(CMD_STATUS), array('B', CMD_STATUS))
    ps_queue_spi_ss(queue_busy, 0)

    for n in range(page_cnt):
        if not (addr & 0xFFFF):
            print('Programming address 0x%x' % addr)
        ps_queue_clear(queue)

        # Write enable
        ps_queue_spi_ss(queue, SS_MASK)
        ps_queue_spi_write(queue, 0, 8,
                           len(CMD_WREN), array('B', CMD_WREN))
        ps_queue_spi_ss(queue, 0)

        # Program
        ps_queue_spi_ss(queue, SS_MASK)
        data = array('B', [ CMD_WRITE ] + get_addr(addr, ADDR_SIZE))
        ps_queue_spi_write(queue, 0, 8, len(data), data)
        ps_queue_spi_write(queue, IO, 8,
                           WRITE_PAGE_SIZE,
                           array('B', data_out[addr: addr + WRITE_PAGE_SIZE]))
        ps_queue_spi_ss(queue, 0)
        collect, _ = ps_queue_submit(queue, channel, 0)

        while True:
            collect, _ = ps_queue_submit(queue_busy, channel, 0)
            data_in = dev_collect(collect)
            if not data_in:
                print(ps_channel_submitted_count(channel))
                continue
            if data_in[-1] & 0x80:
                break

        addr += WRITE_PAGE_SIZE

    ps_queue_destroy(queue_busy)
    return 0


#==========================================================================
# MAIN
#==========================================================================
if (len(sys.argv) < 4):
    print("usage: spi_n25q IP read IO")
    print("usage: spi_n25q IP write IO")
    print("usage: spi_n25q IP erase IO")
    print("  IO : 0 - standard, 2 - dual, 4 - quad")
    sys.exit()

ip      = sys.argv[1]
command = sys.argv[2]
IO      = int(sys.argv[3])

# Open the device
pm, conn, channel = dev_open(ip)

# Ensure that the SPI subsystem is enabled
ps_app_configure(channel, PS_APP_CONFIG_SPI)

# Power the board using the Promira adapter's power supply.
ps_phy_target_power(channel, PS_PHY_TARGET_POWER_BOTH)

# Setup the clock phase
ps_spi_configure(channel, PS_SPI_MODE_0, PS_SPI_BITORDER_MSB, 0)

# Configure SS
ps_spi_enable_ss(channel, SS_MASK)

# Set the bitrate
bitrate = ps_spi_bitrate(channel, BITRATE)
print("Bitrate set to %d kHz" % bitrate)

# Create a queue for SPI transactions
queue = ps_queue_create(conn, PS_MODULE_ID_SPI_ACTIVE)

# Enable master output
spi_master_oe(channel, queue, 1)

# Perform the operation
flash_n25q_detect(channel, queue)
if DEV_NAME == None:
    dev_close(pm, conn, channel)
    sys.exit()

flash_n25q_prepare(channel, queue)

if "write".startswith(command):
    flash_n25q_write(IO, channel, queue)

elif "read".startswith(command):
    flash_n25q_read(IO, channel, queue)

elif "erase".startswith(command):
    flash_n25q_erase(IO, channel, queue)

else:
    print("unknown command: %s" % command)

# Disable master output
spi_master_oe(channel, queue, 0)

# Destroy the queue
ps_queue_destroy(queue)

# Close the device and exit
dev_close(pm, conn, channel)
