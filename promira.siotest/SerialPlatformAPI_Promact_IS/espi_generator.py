#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : espi_generator.py
#--------------------------------------------------------------------------
# Generate eSPI transactions using the SPI active application.
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

from espi_simulator import *


#==========================================================================
# eSPI FUNCTIONS
#==========================================================================
def espi_reset(simulator):
    """ Send a RESET """
    simulator.espi_config_slave(0)
    simulator.espi_toggle_reset()

def espi_alert(simulator):
    """ Send an ALERT """
    simulator.espi_config_slave(0)
    simulator.espi_toggle_alert()

def espi_inband_reset(simulator):
    """ Send an INBAND RESET """
    simulator.espi_config_slave(0)
    simulator.espi_inband_reset()

def espi_set_config_io(simulator, io_mode=0):
    simulator.espi_config_slave(0)
    # set config, 50Mhz
    simulator.espi_set_config_08h(3, io_mode)

def espi_set_config_io_single(simulator):
    """ Send a SET_CONFIGURATION command to configure IO MODE as SINGLE """
    espi_set_config_io(simulator, 0)

def espi_set_config_io_dual(simulator):
    """ Send a SET_CONFIGURATION command to configure IO MODE as DUAL """
    espi_set_config_io(simulator, 1)

def espi_set_config_io_quad(simulator):
    """ Send a SET_CONFIGURATION command to configure IO MODE as QUAD """
    espi_set_config_io(simulator, 2)

def espi_set_config_10h(simulator):
    """ Send a SET_CONFIGURATION command to configure the peripheral channel \
operating mode. Maximum Read Request Size: 4096 bytes, Maximum Payload Size: 256 bytes """
    simulator.espi_config_slave(0)
    # max_req_size : 4096, max_payload_size : 256, bus_enable, ch_enable
    simulator.espi_set_config_10h(7, 3, 1, 1)

def espi_put_msg(simulator):
    """ Send multiple down stream messages on Slave 0 and Slave 1 """
    msg_data = [ 1, 2, 3, 4, 5 ]

    # put msg on slave 0
    simulator.espi_config_slave(0)
    for _ in range(1):
        tag = random.randrange(0, 15)
        data = random.sample(range(0, 0xff), random.randrange(0, 32))

        simulator.espi_perif_put_msg(
            True, tag, msg_data, data,
            status=STAT_PC_FREE|STAT_PC_AVAIL)

    # put msg on slave 1
    msg_data = [ 5, 4, 3, 2, 1 ]
    simulator.espi_config_slave(1)
    for _ in range(2):
        tag = random.randrange(0, 15)
        data = random.sample(range(0, 0xff), random.randrange(0, 32))

        simulator.espi_perif_put_msg(
            True, tag, msg_data, data,
            status=STAT_PC_FREE|STAT_PC_AVAIL)

def espi_get_status(simulator):
    """ Send a GET_STATUS command """
    resp_data  = []
    simulator.espi_config_slave(0)
    # Send a get_status command indicating that the
    # slave has a posted/completion rx queue free
    simulator.espi_get_status(resp_data, RESP_ACCEPTED, STAT_NORMAL)

def espi_get_status_pc_free(simulator):
    """ Send a GET_STATUS command indicating a free posted/completion RX queue"""
    resp_data  = []
    simulator.espi_config_slave(0)
    # Send a get_status command indicating that the
    # slave has a posted/completion rx queue free
    simulator.espi_get_status(resp_data, RESP_ACCEPTED, STAT_PC_FREE)

def espi_get_status_np_free(simulator):
    """ Send a GET_STATUS command indicating a free non-posted RX queue"""
    resp_data  = []
    simulator.espi_config_slave(0)
    # Send a get_status command indicating that the
    # slave has a non-posted rx queue free
    simulator.espi_get_status(resp_data, RESP_ACCEPTED, STAT_NP_FREE)

def espi_perif_downstream_wr32(simulator):
    """ Send a downstream memory write to a 32-bit address. Address: 0xFF008000, Tag: 0xA, Data: 8 bytes """
    write_data = [10, 11, 12, 13, 14, 15, 16 , 17]
    simulator.espi_config_slave(0)
    # Send downstream posted write command with 8 bytes of data
    # to address 0xFF008000, Tag value: 0xA
    # Command   : PUT_PC
    # Cycle type: MEMORY WRITE 32
    # Tag value : 0xA
    # Address   : 0xFF008000
    simulator.espi_perif_write_mem(True, 10, 0xFF008000, True, write_data,
                                   RESP_ACCEPTED, STAT_NORMAL)

def espi_perif_downstream_rd32(simulator):
    """ Send a downstream memory read request to a 32-bit address with a connected completion (successful with data, only). Address: 0x80800000, Tag: 0xA, Data: 16 bytes """
    cmpl_data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    simulator.espi_config_slave(0)
    # Send a downstream non posted read request with an ACCEPT
    # response to a 32 bit address 0x80800000, Tag value: 0xA
    # Command   : PUT_NP
    # Cycle type: MEMORY READ 32
    # Tag value : 0xA
    # Address   : 0x80800000
    simulator.espi_perif_read_mem(True, 10, 0x80800000, True,
                                  16, CYCLE_SC_DATA_11, cmpl_data,
                                  RESP_ACCEPTED, STAT_NORMAL)

def espi_perif_downstream_rd64(simulator):
    """ Send a downstream memory read request to a 64-bit address with a connected completion (successful with data, only). Address: 0xFFFFC00080800000, Tag: 0xA, Data: 16 bytes """
    cmpl_data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    simulator.espi_config_slave(0)
    # Send a downstream non posted read request with an ACCEPT response
    # to a 64 bit address 0xFFFFC00080800000, Tag value: 0xA
    # Command   : PUT_NP
    # Cycle type: MEMORY READ 64
    # Tag value : 0xA
    # Address   : 0xFFFFC00080800000
    simulator.espi_perif_read_mem(True, 10, 0xFFFFC00080800000, False,
                                  16, CYCLE_SC_DATA_11, cmpl_data,
                                  RESP_ACCEPTED, STAT_NORMAL)


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 3):
    print("usage: espi_generator IP sim_mode command1 command2 ... commnadn")
    print("- sim_mode 0 : transaction mode that generates eSPI transaction")
    print("  sim_mode 1 : master mode that generates eSPI command phase " +
          "and clock only for TAR and response phase")
    print("\n")
    print("Available commands are ")
    func_names = [ f[5:] for f in dir(sys.modules[__name__])
                   if f.startswith('espi_') ]
    for f in func_names:
       doc = eval('espi_%s.__doc__'%f)
       if doc:
          print('%-25s : %s' % (f, eval('espi_%s.__doc__' % f)))
    print("\n")
    print("- To generate a sequence of espi packets that satisfy the condition")
    print("  for advance trigger mode 1 example 'capture_espi_trig1.py' using")
    print("  Promira espi analyzer, use the following command:")
    print("  espi_generator.py IP 0 set_config_10h get_status_pc_free perif_downstream_wr32")
    print("\n")
    print("- To generate a sequence of espi packets that satisfy the condition")
    print("  for advance trigger mode 2 example 'capture_espi_trig2.py' using")
    print("  Promira espi analyzer, use the following command:")
    print("  espi_generator.py IP 0 set_config_10h get_status_np_free perif_downstream_rd64")
    print("\n")
    print("- To generate a sequence of espi packets that satisfy the condition")
    print("  for advance trigger eerror code mode example 'capture_espi_trig_err.py' using")
    print("  Promira espi analyzer, use the following command:")
    print("  espi_generator.py IP 0 set_config_10h get_status perif_downstream_rd32")
    sys.exit()

ip       = sys.argv[1]
sim_mode = int(sys.argv[2])
cmds     = sys.argv[3:]

# Open the device
simulator = EspiSimulator(ip)
simulator.espi_config_mode(sim_mode)

for cmd in cmds:
    try:
        print('simulating %s' % cmd)
        eval('espi_%s(simulator)' % cmd)
    except:
        print('unknown command or failed: %s' % cmd)

# Close the device
simulator.close()

