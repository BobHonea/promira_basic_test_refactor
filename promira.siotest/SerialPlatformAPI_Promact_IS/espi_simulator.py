#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : espi_simulator.py
#--------------------------------------------------------------------------
# Simulate eSPI transactions using the SPI active application.
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
import time
import random
import unittest

from promira_py import *
from promact_is_py import *


#==========================================================================
# eSPI Defines
#==========================================================================
NUM_OF_ESPI_SLAVE  = 2

# eSPI simulator mode
# - TRANS    : generate eSPI packet
# - MASTER   : generate only command part and generate clock for slave.
# - NO_TRANS : pack eSPI packet only and doesn't generate traffic.
ESPI_SIMULATOR_MODE_TRANS    = 0
ESPI_SIMULATOR_MODE_MASTER   = 1
ESPI_SIMULATOR_MODE_NO_TRANS = -1


#==========================================================================
# eSPI Commands
#==========================================================================
# Peripheral channel commands
PUT_PC                  = 0b00000000
PUT_NP                  = 0b00000010
GET_PC                  = 0b00000001
GET_NP                  = 0b00000011
PUT_IORD_SHORT1         = 0b01000000
PUT_IORD_SHORT2         = 0b01000001
PUT_IORD_SHORT4         = 0b01000011
PUT_IOWR_SHORT1         = 0b01000100
PUT_IOWR_SHORT2         = 0b01000101
PUT_IOWR_SHORT4         = 0b01000111
PUT_MEMRD32_SHORT1      = 0b01001000
PUT_MEMRD32_SHORT2      = 0b01001001
PUT_MEMRD32_SHORT4      = 0b01001011
PUT_MEMWR32_SHORT1      = 0b01001100
PUT_MEMWR32_SHORT2      = 0b01001101
PUT_MEMWR32_SHORT4      = 0b01001111
# Virtual wire channel commands
PUT_VWIRE               = 0b00000100
GET_VWIRE               = 0b00000101
# OOB message channel commands
PUT_OOB                 = 0b00000110
GET_OOB                 = 0b00000111
# Flash access channel commands
PUT_FLASH_C             = 0b00001000
GET_FLASH_NP            = 0b00001001
PUT_FLASH_NP            = 0b00001010
GET_FLASH_C             = 0b00001011
# Channel independent commands
GET_STATUS              = 0b00100101
SET_CONFIGURATION       = 0b00100010
GET_CONFIGURATION       = 0b00100001
RESET                   = 0b11111111

#==========================================================================
# eSPI Other Defines
#==========================================================================
# Peripheral channel cycle types
CYCLE_MEMRD32           = 0b00000000
CYCLE_MEMRD64           = 0b00000010
CYCLE_MEMWR32           = 0b00000001
CYCLE_MEMWR64           = 0b00000011
CYCLE_MSG               = 0b00010000
CYCLE_MSG_DATA          = 0b00010001
CYCLE_SC                = 0b00000110 # SC = Successful Completion
CYCLE_SC_DATA_00        = 0b00001001
CYCLE_SC_DATA_01        = 0b00001011
CYCLE_SC_DATA_10        = 0b00001101
CYCLE_SC_DATA_11        = 0b00001111
CYCLE_UC_DATA_10        = 0b00001100 # UC = Unsuccessful Completion
CYCLE_UC_DATA_11        = 0b00001110
# OOB channel cycle types
CYCLE_OOB               = 0b00100001
# Flash access channel cycle types
CYCLE_FLASH_RD          = 0b00000000
CYCLE_FLASH_WR          = 0b00000001
CYCLE_FLASH_ER          = 0b00000010

# Response Code
RESP_ACCEPTED           = 0b00001000
RESP_WITH_PERIF         = 0b01000000
RESP_WITH_VW            = 0b10000000
RESP_WITH_FLASH         = 0b11000000
RESP_DEFER              = 0b00000001
RESP_NON_FATAL_ERR      = 0b00000010
RESP_FATAL_ERR          = 0b00000011
RESP_WAIT_STATE         = 0b00001111
RESP_NO_RESPONSE        = 0b11111111

# Status Register returned by Slave: see Fig 16 in eSPI spec
STAT_PC_FREE            = 0x0001
STAT_NP_FREE            = 0x0002
STAT_VWIRE_FREE         = 0x0004
STAT_OOB_FREE           = 0x0008
STAT_PC_AVAIL           = 0x0010
STAT_NP_AVAIL           = 0x0020
STAT_VWIRE_AVAIL        = 0x0040
STAT_OOB_AVAIL          = 0x0080
STAT_FLASH_C_FREE       = 0x0100
STAT_FLASH_NP_FREE      = 0x0200
STAT_FLASH_C_AVAIL      = 0x1000
STAT_FLASH_NP_AVAIL     = 0x2000

STAT_NORMAL             = STAT_FLASH_C_FREE | STAT_VWIRE_FREE


#==========================================================================
# Helper (CRC)
#==========================================================================
# initialize crc table
CRC_TABLE = array('B', [ 0x00 ] * 256)
for i in range(256):
    tmp = i
    for j in range(8):
        tmp = (tmp << 1) ^ (0x07 if (tmp & 0x80) else 0)
        CRC_TABLE[i] = tmp & 0xFF

def calc_crc (data):
    crc = 0
    for k in range(len(data)):
        crc = CRC_TABLE[crc ^ data[k]]

    return crc


#==========================================================================
# HELPER for eSPI simulator
#==========================================================================
def letoa (le, num_of_bytes):
    data = [ ]
    for n in range(num_of_bytes):
        data.append((le >> (n * 8)) & 0xff)
    return data

def betoa (be, num_of_bytes):
    data = [ ]
    for n in range(num_of_bytes - 1, -1, -1):
        data.append((be >> (n * 8)) & 0xff)
    return data

# def atole (data):
#     le = 0
#     for n in range(len(data)):
#         le |= ((data[n] & 0xFF) << (n * 8))
#     return le

# def atobe (data):
#     be = 0
#     for n in range(len(data)):
#         be <<= 8
#         be |= (data[n] & 0xFF)
#     return be


#==========================================================================
# CLASS for eSPI simulator
#==========================================================================
class EspiSimulator (unittest.TestCase):
    def __init__ (self, ip):
        self.ip = ip

        app_name = "com.totalphase.promact_is"

        self.pm = pm_open(self.ip)
        self.assertFalse(self.pm <= 0, "pm_open(%s) = %d(%s)"
                         % (self.ip, self.pm, pm_status_string(self.pm)))

        ret = pm_load(self.pm, app_name)
        self.assertFalse(ret < 0, "pm_load(%s) = %d(%s)"
                         % (app_name, ret, pm_status_string(ret)))

        self.conn = ps_app_connect(self.ip)
        self.assertFalse(self.conn <= 0, "ps_app_connect(%s) = %d(%s)"
                         % (self.ip, self.conn, pm_status_string(self.conn)))

        self.channel = ps_channel_open(self.conn)
        self.assertFalse(self.channel <= 0, "ps_channel_close() = %d(%s)"
                         % (self.channel, pm_status_string(self.channel)))


        # make all gpios high and switch to input
        #  (all gpios are input as default)
        # since all lines(SS, reset and alert) are active low
        ps_gpio_set(self.channel, 0xFFFFFF)

        # enable SS0 and SS2
        ps_spi_enable_ss(self.channel, 0x5)

        self.dig_io_dir     = 0
        self.dig_io_default = 0xFFDFC0

        ps_app_configure(self.channel, PS_APP_CONFIG_SPI)
        ps_phy_level_shift(self.channel, 1.8)

        self.queue = ps_queue_create(self.conn, PS_MODULE_ID_SPI_ACTIVE)
        ps_queue_spi_oe(self.queue, 1)
        self._spi_submit()

        self.espi_config_mode(ESPI_SIMULATOR_MODE_TRANS)
        self._espi_init_bus()
        self.espi_config_slave(0)
        self.espi_config_bus(0, 0)
        self.espi_enable_wait_state()

    def close (self):
        ps_channel_close(self.channel)
        ps_app_disconnect(self.conn)
        pm_close(self.pm)

    def get_avail_func_names (self):
        func_list = [ func for func in dir(self)
                      if func.startswith('espi') ]

        return func_list

    # Digital pins
    # IDX   0    1    2    3    4    5    6    7    8    9   10
    # PIN  17   19   21   23   20   25   27   29   33   26   32
    # GPIO 05   06   09   10   07   11   12   NC   15   08   14
    DIG_IO_MAPS = [ 5, 6, 9, 10, 7, 11, 12, -1, 15, 8, 14 ]

    def _dig_io_to_gpio (self, io):
        gpio = 0
        for n in range(11):
            if (io >> n) & 1 and self.DIG_IO_MAPS[n] >= 0:
                gpio |= (1 << self.DIG_IO_MAPS[n])

        return gpio

    def _spi_submit (self):
        collect, _ = ps_queue_submit(self.queue, self.channel, 0)
        self.assertFalse(collect < 0,
                         'Collect: %s' % ps_app_status_string(collect))

        while True:
            t, length, result = ps_collect_resp(collect, -1)

            if t == PS_APP_NO_MORE_CMDS_TO_COLLECT:
                break
            self.assertFalse(t < 0, ps_app_status_string(t))

    def _spi_multi_write (self, pkts, debug=False): # list of (raw pkt):
        if self.sim_mode == ESPI_SIMULATOR_MODE_NO_TRANS:
            return

        io_mode        = self.io[self.slave_id]

        single_on_dual = (io_mode == 0)
        if self.sim_mode == ESPI_SIMULATOR_MODE_MASTER:
            single_on_dual = False

        if single_on_dual:
            io_mode = 2

        ps_queue_clear(self.queue)

        adj_bits = [ 3, 2, 0 ]
        adj      = adj_bits[io_mode >> 1]

        for pkt in pkts:
            cmd, resp, _, _ = pkt
            if debug:
                debug_size = 64
                print("[>]", [ '%02x' % x for x in (cmd + resp)[:debug_size] ], end=' ')
                print("..." if len(cmd + resp) > debug_size else "")

            raw = self._espi_pack_data(*pkt, single_on_dual=single_on_dual)

            raw_len = len(raw) * 4 - adj

            ps_queue_spi_ss(self.queue, self.ss_mask)
            if self.sim_mode == ESPI_SIMULATOR_MODE_TRANS or io_mode == 0:
                ps_queue_spi_write(self.queue, io_mode, 2, raw_len, raw)
            else:
                cmd_len = (len(cmd) + 1) * 4
                ps_queue_spi_write(self.queue, io_mode, 2, cmd_len, raw)
                ps_queue_spi_read(self.queue, io_mode, 2, raw_len - cmd_len)

            ps_queue_spi_ss(self.queue, 0)

        self._spi_submit()

    def _espi_pack_cmd_for_single (self, data):
        result = [ ]
        for byte in data:
            word = 0
            for n in range(8):
                if byte & (1 << n):
                    word |= (1 << (2 * n))

            result += [ (word >> 8) & 0xFF, word & 0xFF ]

        return result

    def _espi_pack_resp_for_single (self, data):
        result = [ ]
        for byte in data:
            word = 0
            for n in range(8):
                if byte & (1 << n):
                    word |= (1 << (2 * n + 1))

            result += [ (word >> 8) & 0xFF, word & 0xFF ]
        return result

    def _espi_pack_header (self, cycle_type, tag, length, addr, addr_len):
        header = [ ]
        if cycle_type != None:
            header += [ cycle_type & 0xFF ]
        if tag != None or length != None:
            header += [ ((tag & 0xF) << 4) | ((length >> 8) & 0xF),
                        length & 0xFF ]
        if addr_len > 0:
            header += betoa(addr, addr_len)
        return header

    def _espi_pack_data (self, cmd, resp, cmd_crc=True, resp_crc=True,
                         single_on_dual=False):
        # append cmd data
        cmd_raw = cmd[:]

        # append cmd crc
        crc = calc_crc(cmd)
        if not cmd_crc:
            crc = crc ^ 0xFF
        cmd_raw.append(crc)

        if single_on_dual:
            cmd_raw = self._espi_pack_cmd_for_single(cmd_raw)
        raw = array('B', cmd_raw)

        # append tar and resp
        tar_bits = [ 2, 4, 8 ]
        tar      = tar_bits[self.io[self.slave_id] >> 1]

        resp_raw = [ ]
        # append wait_state to resp
        num_wait_cycle = random.randrange(0, 4) if self.rand_wait_enable \
            else 0

        if self.sim_mode == ESPI_SIMULATOR_MODE_MASTER:
            resp_with_wait = [ 0xFF ] * len(resp)
        else:
            resp_with_wait = ([ RESP_WAIT_STATE ] * num_wait_cycle) + resp

        tmp = 0
        for n in range(len(resp_with_wait)):
            tmp = tmp | (resp_with_wait[n] >> tar)
            resp_raw.append(tmp & 0xFF)
            tmp = (resp_with_wait[n] << (8 - tar)) & 0xFF

        # append resp crc
        crc = calc_crc(resp)
        if not resp_crc:
            crc = crc ^ 0xFF
        resp_raw.append(tmp | (crc >> tar))
        resp_raw.append((crc << (8 - tar)) & 0xFF)

        if single_on_dual:
            resp_raw = self._espi_pack_resp_for_single(resp_raw)
            resp_raw = resp_raw[:-1]
        raw += array('B', resp_raw)

        return raw

    # All I/O lines are driven to high ('1') for 16 eSPI clocks.
    def _espi_inband_reset (self):
        ps_queue_clear(self.queue)

        ps_queue_spi_ss(self.queue, self.ss_mask)
        data = array('B', [ 0xFF ] * 8)

        ps_queue_spi_write(self.queue, 4, 8, len(data), data)
        ps_queue_spi_ss(self.queue, 0)

        self._spi_submit()


    #======================================================================
    # eSPI Transaction
    #======================================================================
    #cmd, resp, cmd_crc=True, resp_crc=True = pkt
    def espi_transact (self, pkts, debug=False):
        new_pkts = [ ]
        for pkt in pkts:
            if len(pkt) == 2:
                cmd, resp, cmd_crc, resp_crc = pkt[0], pkt[1], True, True
            else:
                cmd, resp, cmd_crc, resp_crc = pkt

            new_pkts.append((cmd, resp, cmd_crc, resp_crc))
            if len(new_pkts) > 10:
                self._spi_multi_write(new_pkts, debug)

        if len(new_pkts) > 0:
            self._spi_multi_write(new_pkts, debug)


    #======================================================================
    # SIGNAL (ALERT, RESET, DIGITAL IOs)
    #======================================================================
    # Reset and alert
    def espi_toggle_reset (self, dur=0.05, reset_bus=True):
        gpio = [ 4, 13 ][self.slave_id]
        ps_gpio_direction(self.channel, self.dig_io_dir | (0x1 << gpio))
        ps_gpio_set(self.channel, self.dig_io_default)
        time.sleep(dur)
        ps_gpio_set(self.channel, self.dig_io_default | (0x1 << gpio))
        ps_gpio_direction(self.channel, self.dig_io_dir)

        if reset_bus and self.slave_id == 0:
            # reset bus to 20Mhz and single IO mode for all slaves
            for slave_id in range(NUM_OF_ESPI_SLAVE):
                self.slave_id = slave_id
                self.espi_config_bus(0, 0)

            self.slave_id = 0

    def espi_assert_alert (self):
        gpio = [ 0, 1 ][self.slave_id]
        ps_gpio_direction(self.channel,
                          self.dig_io_dir | (0x1 << gpio))
        ps_gpio_set(self.channel,
                    self.dig_io_default | (0x0 << gpio))

    def espi_deassert_alert (self):
        gpio = [ 0, 1 ][self.slave_id]
        ps_gpio_set(self.channel,
                    self.dig_io_default | (0x1 << gpio))
        ps_gpio_direction(self.channel, self.dig_io_dir)

    def espi_toggle_alert (self, dur=0.05):
        self.espi_assert_alert()
        time.sleep(dur)
        self.espi_deassert_alert()

    # Digital IOs
    def espi_config_dig_io (self, dig_ins, active_low=True):
        self.dig_io_dir      = self._dig_io_to_gpio(dig_ins)
        self.dig_io_default  = self.dig_io_dir if active_low \
            else ~self.dig_io_dir
        self.dig_io_default &= self.dig_io_dir

        ps_gpio_direction(self.channel, self.dig_io_dir)
        ps_gpio_set(self.channel, self.dig_io_default)

    def espi_toggle_dig_ins (self, dig_ins, active_low=True, dur=0.05):
        gpio = self._dig_io_to_gpio(dig_ins) & self.dig_io_dir
        ps_gpio_set(self.channel, ~gpio if active_low else gpio)
        time.sleep(dur)
        ps_gpio_set(self.channel, gpio if active_low else ~gpio)

    def espi_get_dig_outs (self):
        gpio = ps_gpio_get(self.channel) & (~self.dig_io_dir)

        dig_out = 0
        for n in range(11):
            if self.DIG_IO_MAPS[n] >= 0 and (gpio >> self.DIG_IO_MAPS[n]) & 1:
                dig_out |= (1 << n)

        return dig_out


    #======================================================================
    # BUS CONFIGURATION (DO NOT GENERATE ANY ESPI TRANSACTION)
    #======================================================================
    def espi_config_mode (self, mode):
        self.sim_mode = mode

    def espi_config_slave (self, slave_id):
        ss_bitmask    = [ 0, 2 ]
        self.ss_mask  = (1 << ss_bitmask[slave_id])
        self.slave_id = slave_id

    # insert n of wait_state response code in response
    def espi_enable_wait_state (self, enable=False):
        self.rand_wait_enable = enable

    def _espi_init_bus (self):
        self.bitrate = [ 20000 ] * NUM_OF_ESPI_SLAVE
        self.io      = [ 0 ] * NUM_OF_ESPI_SLAVE

    def espi_config_bus (self, io, frequency, debug=False):
        # actual bitrate [ 20000, 25000, 33333, 50000, 66666 ]
        bitrate_khz = [ 20000, 25000, 33400, 50000, 66700 ]
        io_spi      = [ 0, 2, 4 ]

        bitrate      = bitrate_khz[frequency]
        self.bitrate[self.slave_id] = ps_spi_bitrate(self.channel, bitrate)
        self.io[self.slave_id]      = io_spi[io]

        if debug:
           print("espi_config_bus: bitrate=%d, iospi=%d"
                 % (bitrate, io_spi[io]))


    #======================================================================
    # INDEPENDENT CHANNEL
    #======================================================================
    ### addr = address to configure
    ### data = 4-byte array for data
    def espi_get_config (self, addr, data,
                         resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        cmd  = [ GET_CONFIGURATION ] + betoa(addr, 2)
        resp = [ resp_code ] + data + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### addr = address to configure
    ### data = 4-byte array for data
    def espi_set_config (self, addr, data,
                         resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        cmd  = [ SET_CONFIGURATION ] + betoa(addr, 2) + data
        resp = [ resp_code ] + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### frequency = 0..4 = 20000, 25000, 33000, 50000, 66000
    ### io_mode   = 0..2 = single, dual, quad
    def espi_get_config_08h (self, frequency, io_mode):
        data = [ 0x0F, 0x00, 0x04 | (frequency << 4), 0x03 | (io_mode << 2) ]
        return self.espi_get_config(0x08, data)

    ### frequency = 0..4 = 20000, 25000, 33000, 50000, 66000
    ### io_mode   = 0..2 = single, dual, quad
    def espi_set_config_08h (self, frequency, io_mode, status=STAT_NORMAL):
        data = [ 0x00, 0x00, frequency << 4, 0x10 | (io_mode << 2) ]
        pkts = self.espi_set_config(0x08, data, status=status)

        # also configure bus for the following transactions
        self.espi_config_bus(io_mode, frequency)

        return pkts

    ### PERIPHERAL CHANNEL
    ### max_req_size     = 1..7 = 64,128,256,..4096 bytes
    ### max_payload_size = 1..3 = 64,128,256
    ### bus_enable       = 0..1 = disable,enable
    ### channel_enable   = 0..1 = disable,enable
    def espi_set_config_10h (self, max_req_size, max_payload_size,
                             bus_enable, ch_enable):
        data = [ ch_enable | bus_enable << 2,
                 max_payload_size | max_req_size << 4,
                 0x00, 0x00 ]
        return self.espi_set_config(0x10, data)

    ### VW CHANNEL
    ### max_vw_count = 0..63 = 0-based counter. 0 means 1
    ### ch_enable    = 0..1 = disable,enable
    def espi_set_config_20h (self, max_vw_count, ch_enable):
        data = [ ch_enable, 0x00, max_vw_count & 0x3f, 0x00 ]
        return self.espi_set_config(0x20, data)

    ### OOB CHANNEL
    ### max_payload_size = 1..3
    ### ch_enable        = 0..1 = disable,enable
    def espi_set_config_30h (self, max_payload_size, ch_enable):
        data = [ ch_enable, max_payload_size, 0x00, 0x00 ]
        return self.espi_set_config(0x30, data)

    ### FLASH CHANNEL
    ### max_req_size     = 1..7 = 64,128,256,..4096 bytes
    ### max_payload_size = 1..3 = 64,128,256
    ### block_erase_size = 1..5 = 4K, 64K, 4K/64K, 128K, 256K
    ### ch_enable        = 0..1 = disable,enable
    def espi_set_config_40h (self, max_req_size, max_payload_size,
                             block_erase_size, ch_enable):
        data = [ ch_enable | block_erase_size << 2,
                 max_payload_size | max_req_size << 4,
                 0x00, 0x00 ]
        return self.espi_set_config(0x40, data)

    ### resp_data  = array of data read
    def espi_get_status (self, resp_data=[ ],
                         resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        cmd  = [ GET_STATUS ]
        resp = [ resp_code ] + resp_data + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### tag        = 0..15 = id of series of transactions
    ### resp_cycle = cycle type when data is returned in response
    ### resp_data  = array of data read
    def espi_get_status_with_perif (self, tag, resp_cycle, resp_data,
                                    resp_code=RESP_ACCEPTED,
                                    status=STAT_NORMAL):
        header = self._espi_pack_header(
            resp_cycle, tag, len(resp_data), None, 0)
        resp_body = header + resp_data
        return self.espi_get_status(resp_body, resp_code | RESP_WITH_PERIF,
                                    status)

    ### vw_count = number of vw data
    ### data     = [ vw_index1, vw_data1, vw_index2, vw_data2, ... ]
    def espi_get_status_with_vw (self, vw_count, data,
                                 resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        resp_data = [ vw_count & 0x3F ] + data
        return self.espi_get_status(resp_data, resp_code | RESP_WITH_VW,
                                    status)

    ### tag        = 0..15 = id of series of transactions
    ### resp_cycle = cycle type when data is returned in response
    ### resp_data  = array of data read
    def espi_get_status_with_flash (self, tag, resp_cycle, resp_data,
                                    resp_code=RESP_ACCEPTED,
                                    status=STAT_NORMAL):
        header = self._espi_pack_header(
            resp_cycle, tag, len(resp_data), None, 0)
        resp_body = header + resp_data
        return self.espi_get_status(resp_body, resp_code | RESP_WITH_FLASH,
                                    status)

    # RESET command opcode is FFh (i.e. all 1's).
    # It is sent with the 20MHz speed or lower.
    # No CRC byte and thus CRC checking must be ignored.
    # The transaction has no response phase from eSPI slave.
    # All I/O lines are driven to high ('1') for 16 eSPI clocks.
    def espi_inband_reset (self, reset_bus=True):
        # quad mode to drive '1' for all I/O lines and bitrate to 20MHz
        self._espi_inband_reset()

        if reset_bus:
            # reset bus to 20Mhz and single IO mode for only that slave
            self.espi_config_bus(0, 0)


    #======================================================================
    # PERIPHERAL CHANNEL
    #======================================================================
    ### is_down    = True, False = down stream or up stream
    ### tag        = 0..15 = id of series of transactions
    ### addr       = 32 bit or 64 bit based on is_addr_32
    ### is_addr_32 = True, False = 32 bit addressing or 64 bit
    ### length     = number of bytes to read
    ### resp_cycle = cycle type when data is returned in response
    ### resp_data  = array of data read
    def espi_perif_read_mem (self, is_down, tag, addr, is_addr_32,
                             length, resp_cycle, resp_data,
                             resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        if is_addr_32:
            cycle_type = CYCLE_MEMRD32
        else:
            cycle_type = CYCLE_MEMRD64
        header = self._espi_pack_header(cycle_type, tag, length, addr,
                                        4 if is_addr_32 else 8)

        if is_down:
            cmd  = [ PUT_NP ] + header
            if resp_cycle != None: # resp_code should be also RESP_ACCEPTED
                header = self._espi_pack_header(
                    resp_cycle, tag, len(resp_data), None, 0)
                resp_body = header + resp_data
            else:
                resp_body = [ ]
            resp = [ resp_code ] + resp_body + letoa(status, 2)
        else:
            cmd  = [ GET_NP ]
            resp = [ resp_code ] + header + letoa(status, 2)
        pkts  = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### is_down    = True, False = down stream or up stream
    ### tag        = 0..15 = id of series of transactions
    ### addr       = 32 bit or 64 bit based on is_addr_32
    ### is_addr_32 = True, False = 32 bit addressing or 64 bit
    ### data       = array of data (can't be None)
    def espi_perif_write_mem (self, is_down, tag, addr, is_addr_32, data,
                              resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        if is_addr_32:
            cycle_type = CYCLE_MEMWR32
        else:
            cycle_type = CYCLE_MEMWR64
        header = self._espi_pack_header(cycle_type, tag, len(data), addr,
                                        4 if is_addr_32 else 8)

        if is_down:
            cmd  = [ PUT_PC ] + header + data
            resp = [ resp_code ] + letoa(status, 2)
        else:
            cmd  = [ GET_PC ]
            resp = [ resp_code ] + header + data + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### is_down    = True, False = down stream or up stream
    ### tag        = 0..15 = id of series of transactions
    ###            = should be 0 when it is PUT_MEMRD32_SHORT
    ### cycle_type = cycle type
    ### data       = array of data read
    def espi_perif_cmpl_mem (self, is_down, tag, cycle_type, data,
                             resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(cycle_type, tag, len(data), None, 0)

        if is_down:
            cmd  = [ GET_PC ]
            resp = [ resp_code ] + header + data + letoa(status, 2)
        else:
            cmd  = [ PUT_PC ] + header + data
            resp = [ resp_code ] + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### addr       = 32 bit
    ### data       = array of data (0, 1, 2 or 4 bytes)
    def espi_perif_read_mem_short (self, addr, data,
                                   resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(None, None, None, addr, 4)

        cmd_by_len = {
            1: PUT_MEMRD32_SHORT1,
            2: PUT_MEMRD32_SHORT2,
            4: PUT_MEMRD32_SHORT4,
        }

        cmd  = [ cmd_by_len[len(data)] ] + header
        if resp_code == RESP_DEFER:
            resp = [ resp_code ] + letoa(status, 2)
        else:
            resp = [ resp_code ] + data + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### addr       = 32 bit
    ### data       = array of data (1, 2 or 4 bytes)
    def espi_perif_write_mem_short (self, addr, data,
                                    resp_code=RESP_ACCEPTED,
                                    status=STAT_NORMAL):
        header = self._espi_pack_header(None, None, None, addr, 4)

        cmd_by_len = {
            1: PUT_MEMWR32_SHORT1,
            2: PUT_MEMWR32_SHORT2,
            4: PUT_MEMWR32_SHORT4,
        }

        cmd  = [ cmd_by_len[len(data)] ] + header + data
        resp = [ resp_code ] + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### is_down    = True, False = down stream or up stream
    ### tag        = 0..15 = id of series of transactions
    ### msg_data   = array including msg code and 4 byte of msg data
    ### data       = array of data (can't be None)
    def espi_perif_put_msg (self, is_down, tag, msg_data, data,
                            resp_code=RESP_ACCEPTED, status=STAT_NORMAL):

        if len(data) > 0:
            cycle_type = CYCLE_MSG_DATA
        else:
            cycle_type = CYCLE_MSG
        header = self._espi_pack_header(cycle_type, tag, len(data), None, 0)

        if is_down:
            cmd  = [ PUT_PC ] + header + msg_data + data
            resp = [ resp_code ] + letoa(status, 2)
        else:
            cmd  = [ GET_PC ]
            resp = [ resp_code ] + header + msg_data + data + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### addr       = 16 bit
    ### data       = array of data (0, 1, 2 or 4 bytes)
    def espi_perif_read_io (self, addr, data,
                            resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(None, None, None, addr, 2)

        cmd_by_len = {
            1: PUT_IORD_SHORT1,
            2: PUT_IORD_SHORT2,
            4: PUT_IORD_SHORT4,
        }

        cmd  = [ cmd_by_len[len(data)] ] + header
        if resp_code == RESP_DEFER:
            resp = [ resp_code ] + letoa(status, 2)
        else:
            resp = [ resp_code ] + data + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### addr       = 16 bit
    ### data       = array of data (1, 2 or 4 bytes)
    def espi_perif_write_io (self, addr, data,
                             resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(None, None, None, addr, 2)

        cmd_by_len = {
            1: PUT_IOWR_SHORT1,
            2: PUT_IOWR_SHORT2,
            4: PUT_IOWR_SHORT4,
        }

        cmd  = [ cmd_by_len[len(data)] ] + header + data
        resp = [ resp_code ] + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### is_read    = True, False = completion for io_read or io_write
    ### cycle_type = cycle type
    ### data       = array of data
    def espi_perif_cmpl_io (self, is_read, cycle_type, data,
                            resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        # if it was io_write, data part should be empty
        if not is_read:
            data = [ ]
        header = self._espi_pack_header(cycle_type, 0, len(data), None, 0)

        cmd  = [ GET_PC ]
        resp = [ resp_code ] + header + data + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts


    #======================================================================
    # VIRTUAL WIRE CHANNEL
    #======================================================================
    ### vw_count = number of vw data
    ### data     = [ vw_index1, vw_data1, vw_index2, vw_data2, ... ]
    def espi_vw_get (self, vw_count, data,
                     resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        cmd  = [ GET_VWIRE ]
        resp = [ resp_code, vw_count & 0x3F ] + data + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### vw_count = number of vw data
    ### data     = [ vw_index1, vw_data1, vw_index2, vw_data2, ... ]
    def espi_vw_put (self, vw_count, data,
                     resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        cmd  = [ PUT_VWIRE, vw_count & 0x3F ] + data
        resp = [ resp_code ] + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts


    #======================================================================
    # OOB CHANNEL
    #======================================================================
    def espi_oob_get (self, tag, data,
                      resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(CYCLE_OOB, tag, len(data), None, 0)

        cmd  = [ GET_OOB ]
        resp = [ resp_code ] + header + data + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    def espi_oob_put (self, tag, data,
                      resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(CYCLE_OOB, tag, len(data), None, 0)

        cmd  = [ PUT_OOB ] + header + data
        resp = [ resp_code ] + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts


    #======================================================================
    # FLASH CHANNEL
    #======================================================================
    ### is_down    = True, False = down stream or up stream
    ### tag        = 0..15 = id of series of transactions
    ### addr       = 32 bit
    ### length     = number of bytes to read
    ### resp_cycle = cycle type when data is returned in response
    ### resp_data  = array of data read
    def espi_flash_read (self, is_down, tag, addr, length,
                         resp_cycle, resp_data,
                         resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(CYCLE_FLASH_RD, tag, length, addr, 4)

        if is_down:
            cmd  = [ PUT_FLASH_NP ] + header
            if resp_cycle != None: # resp_code should be also RESP_ACCEPTED
                header = self._espi_pack_header(
                    resp_cycle, tag, len(resp_data), None, 0)
                resp_body = header + resp_data
            else:
                resp_body = [ ]
            resp = [ resp_code ] + resp_body + letoa(status, 2)
        else:
            cmd  = [ GET_FLASH_NP ]
            resp = [ resp_code ] + header + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### is_down    = True, False = down stream or up stream
    ### tag        = 0..15 = id of series of transactions
    ### cycle_type = cycle type
    ### data       = array of data to be written
    def espi_flash_read_cmpl (self, is_down, tag, cycle_type, data,
                              resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(cycle_type, tag, len(data), None, 0)

        if is_down:
            cmd  = [ GET_FLASH_C ]
            resp = [ resp_code ] + header + data + letoa(status, 2)
        else:
            cmd  = [ PUT_FLASH_C ] + header + data
            resp = [ resp_code ] + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### is_down    = True, False = down stream or up stream
    ### tag        = 0..15 = id of series of transactions
    ### addr       = 32 bit
    ### length     = number of bytes to read
    ### resp_cycle = cycle type when data is returned in response
    def espi_flash_erase (self, is_down, tag, addr, length, resp_cycle,
                          resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(CYCLE_FLASH_ER, tag, length, addr, 4)

        if is_down:
            cmd  = [ PUT_FLASH_NP ] + header
            if resp_cycle != None: # resp_code should be also RESP_ACCEPTED
                header = self._espi_pack_header(resp_cycle, tag, 0, None, 0)
                resp_body = header
            else:
                resp_body = [ ]
            resp = [ resp_code ] + resp_body + letoa(status, 2)
        else:
            cmd  = [ GET_FLASH_NP ]
            resp = [ resp_code ] + header + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### is_down    = True, False = down stream or up stream
    ### tag        = 0..15 = id of series of transactions
    ### cycle_type = cycle type
    def espi_flash_erase_cmpl (self, is_down, tag, cycle_type,
                               resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(cycle_type, tag, 0, None, 0)

        if is_down:
            cmd  = [ GET_FLASH_C ]
            resp = [ resp_code ] + header + letoa(status, 2)
        else:
            cmd  = [ PUT_FLASH_C ] + header
            resp = [ resp_code ] + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    ### is_down    = True, False = down stream or up stream
    ### tag        = 0..15 = id of series of transactions
    ### addr       = 32 bit
    ### data       = array of data to be written
    ### resp_cycle = cycle type when data is returned in response
    def espi_flash_write (self, is_down, tag, addr, data, resp_cycle,
                          resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        header = self._espi_pack_header(CYCLE_FLASH_WR, tag, len(data), addr, 4)

        if is_down:
            cmd  = [ PUT_FLASH_NP ] + header + data
            if resp_cycle != None: # resp_code should be also RESP_ACCEPTED
                header = self._espi_pack_header(resp_cycle, tag, 0, None, 0)
                resp_body = header
            else:
                resp_body = [ ]
            resp = [ resp_code ] + resp_body + letoa(status, 2)
        else:
            cmd  = [ GET_FLASH_NP ]
            resp = [ resp_code ] + header + data + letoa(status, 2)
        pkts = [ (cmd, resp) ]

        self.espi_transact(pkts)
        return pkts

    def espi_flash_write_cmpl (self, is_down, tag, cycle_type,
                               resp_code=RESP_ACCEPTED, status=STAT_NORMAL):
        return self.espi_flash_erase_cmpl(is_down, tag, cycle_type,
                                          resp_code, status)
