"""Py test that does a test function"""
from __future__ import division, with_statement, print_function
import usertest
# import os
# import time
# import subprocess

# Test Serial IO of DUT
# Monitor DUT Serial IO with Promira Serial Platform
# Articulate DUT with Nucleo64.ate
# DUT Specified as Nucleo64.dut

# DUT Interface
# 2 GPIO Output
#   1 Bit: DUT Select
#
# 2 GPIO Input
#   1 Bit: DUT Busy
#   1 Bit: DUT ReadDataRdy
#   1 Bit: DUT WriteDataRdy
#
# 8 bits command register
# COMMANDS:
#     INIT
#     DUT transition to initial/ready state
#
#     START
#     DUT transiton to execute tests state
#
#     CONTINUE
#     DUT transition to execute next subtest
#
#   DUT Behavior
#     DUT initialized
#     At start of each test, DUT performs test function read cycle
#     DUT then performs the testfunction specified by contents
#     of the command register
#     
#
#   Manifest of tests
#   - basic SIO tests
#   - parameter setting for SIO Output Corruption/Dropout
#         this helps verify PROMIRA Platform failure detection
# 
#     1. I2C Write Packet
#     2. I2C Read Packet
#     3. I2C Repeat Write Packet
#     4. I2C Repeat Read Packet
#     5. I2C Set Corruption Modulus
#     6. I2C Set Char Dropout Modulus
#     7. I2C Set Packet Dropout Modulus
#

#==========================================================================
# IMPORTS
#==========================================================================

import array
import sys

import aa_pm_py as promira
# from smtpd import program

import time
import random
# from __builtin__ import None
import collections
import builtins
from _ast import Or


#==========================================================================
# CONSTANTS
#==========================================================================
BUFFER_SIZE = 65535
SLAVE_RESP_SIZE = 5  # 26
INTERVAL_TIMEOUT = 500

#==========================================================================
# FUNCTIONS
#==========================================================================

# SPI COMMANDS
# CMD LIST: [ [ CMD_LENGTH, DATA_TRANSFER_TYPE, DATA_ARRAY_LENGTH ], [CMD_BYTES]]
# 
#


class promiraTestApp(usertest.SwUserTest):
  """Unit test template"""
  BUSTYPE_UNKNOWN = 0
  BUSTYPE_I2C = 1
  BUSTYPE_SPI = 2
  
  m_bus_type = BUSTYPE_UNKNOWN
  m_eepromStatus = None
  m_pkgsize = 32
  m_rxdata_array = promira.array_u08(m_pkgsize)
  m_txdata_array = promira.array_u08(m_pkgsize)
  
  m_slaveAddress = 0x55
  m_Aardvark = 0
  m_device = m_slaveAddress
  m_bitrate_khz = 400
  m_devices = promira.array_u16(4)
  m_device_ids = promira.array_u32(4)
  m_device_ips = promira.array_u32(4)
  m_device_status = promira.array_u32(4)
  m_spi_bitrate_khz = 125

  EEPROM_PAGE_SIZE = 0x100
  EEPROM_SECTOR_SIZE = 0x1000
  EEPROM_SIZE = 0x400000

  m_random_page_array = promira.array_u08(EEPROM_PAGE_SIZE)

  KB8 = 0x2000
  KB32 = 0x8000
  KB64 = 0x10000
  # 4 8KB BLOCKS FROM ADDRESS 0
  # 1 32KB BLOCKS FROM ADDRESS 0x8000
  # 32 64KB BLOCKS FROM ADDRESS 0x10000
  # 1 32BLOCK FROM ADDRESS 0x3F0000
  # 4 8KB BLOCKS FROM ADDRESS 0x3F8000
  
  MEM_ADDRESS = 0
  MEM_BLOCKSIZE = 1
  MEM_BLOCKCOUNT = 2
  
  EEPROM_BLOCKS = [[0x0, KB8, 4],
                 [0x8000, KB32, 1],
                 [0x10000, KB64, 31],
                 [0x3F0000, KB32, 1],
                 [0x3F8000, KB8, 4],
                 [0x400000, 0, 0]]
  
  ENUMERATED_BLOCKS = []
  
  m_randarray_count = 16  # arbitrary number
  m_random_page_array_list = []
  m_random_packet_array_list = []

  def __init__(self):
    self.enumerate_blocks()

  def enumerate_blocks(self):
    for blockset in self.EEPROM_BLOCKS:
      address = blockset[0]
      if address == self.EEPROM_SIZE:
        break;
      blocksize = blockset[1]
      blockcount = blockset[2]
      enumeration_address = address
      
      for index in range(blockcount):
        self.ENUMERATED_BLOCKS.append([enumeration_address, blocksize])
        enumeration_address += blocksize
        pass
      pass
    return
  
  # SPI PREFERRED MODE
  SPIIO_SINGLE = 0
  SPIIO_DUAL = 1
  SPIIO_QUAD = 2
  m_preferred_spiio_mode = SPIIO_SINGLE
  
  # SPISPEC ENTRIES
  SPI_CMDSPEC_CMDBYTE = 0
  SPI_CMDSPEC_MODE_INDEX = 1
  
  SPISPEC_MODES_SUBITEM = 2
  SPISPEC_XFERARRAY = 2

  # SPIMODE_
  # [SPIMODES, ADDRCY, DUMMYCY, DATACY]
  MODE_ID = 0
  MODE_ADDRCY = 1
  MODE_DUMMYCY = 2
  MODE_DATACY = 3
  
  MODE_SPI = 1
  MODE_SQI = 2
  MODE_SXI = 3
  SPIMODE_MODEITEM = 0
  SPIMODE_ADDRCY_ITEM = 1
  SPIMODE_DUMMYCY_ITEM = 2
  SPIMODE_DATACY_ITEM = 3
  
  ADCY_0 = 0
  ADCY_1 = 1
  ADCY_2 = 2
  ADCY_3 = 3
  DCY_0 = 0
  DCY_1 = 1
  DCY_2 = 2
  DCY_3 = 3
  DCY_1_INF = 0x8001
  DCY_2_INF = 0x8002
  DCY_3_INF = 0x8003
  DCY_1_256 = 0x8100
  DCY_N_INF = 0xFFFF
  DCY_1_18 = 0x8012
  DCY_1_2048 = 0x8800
  DMY_0 = 0
  DMY_1 = 1
  DMY_2 = 2
  DMY_3 = 3

  SPISPEC_XFERTYPE_OUTPUT = 1
  SPISPEC_XFERTYPE_INPUT = 2
  SPISPEC_XFERTYPE_NONE = 0
  
  SPIMODE_0 = [ MODE_SXI, ADCY_0, DMY_0, DCY_0]
  SPIMODE_1 = [ MODE_SPI, ADCY_0, DMY_0, DCY_0]
  SPIMODE_2 = [ MODE_SPI, ADCY_0, DMY_0, DCY_1_INF]
  SPIMODE_3 = [ MODE_SQI, ADCY_0, DMY_1, DCY_1_INF]
  SPIMODE_4 = [ MODE_SXI, ADCY_0, DMY_0, DCY_2]
  SPIMODE_5 = [ MODE_SPI, ADCY_3, DMY_0, DCY_1_INF]
  SPIMODE_6 = [ MODE_SQI, ADCY_3, DMY_3, DCY_1_INF]
  SPIMODE_7 = [ MODE_SPI, ADCY_3, DMY_1, DCY_1_INF]
  SPIMODE_8 = [ MODE_SXI, ADCY_0, DMY_0, DCY_1]
  SPIMODE_9 = [ MODE_SQI, ADCY_3, DMY_3, DCY_N_INF]
  SPIMODE_A = [ MODE_SPI, ADCY_3, DMY_3, DCY_N_INF]
  SPIMODE_B = [ MODE_SPI, ADCY_0, DMY_0, DCY_3_INF]
  SPIMODE_C = [ MODE_SQI, ADCY_0, DMY_1, DCY_3_INF]
  SPIMODE_D = [ MODE_SQI, ADCY_3, DMY_1, DCY_1_INF]
  SPIMODE_E = [ MODE_SXI, ADCY_3, DMY_0, DCY_0]
  SPIMODE_F = [ MODE_SXI, ADCY_3, DMY_0, DCY_1_256]
  SPIMODE_10 = [MODE_SPI, ADCY_3, DMY_0, DCY_1_256 ]
  SPIMODE_11 = [MODE_SPI, ADCY_0, DMY_0, DCY_1_18]
  SPIMODE_12 = [MODE_SQI, ADCY_0, DMY_0, DCY_1_18]
  SPIMODE_13 = [MODE_SXI, ADCY_0, DMY_0, DCY_1_18]
  SPIMODE_14 = [MODE_SPI, ADCY_2, DMY_1, DCY_1_2048]
  SPIMODE_15 = [MODE_SQI, ADCY_2, DMY_3, DCY_1_2048]
  SPIMODE_16 = [MODE_SXI, ADCY_2, DMY_0, DCY_1_256]
  
  NOP = 0x00
  RSTEN = 0x66
  RSTMEM = 0x99
  ENQIO = 0x38
  RSTQIO = 0xFF
  RDSR = 0x05
  WRSR = 0x01
  RDCR = 0x35
  READ = 0x03
  HSREAD = 0x0B
  SQOREAD = 0x6B
  SQIOREAD = 0xEB
  SDOREAD = 0x3B
  SDIOREAD = 0xBB
  SETBURST = 0xC0
  RBSQI_WRAP = 0x0C
  RBSPI_WRAP = 0xEC
  JEDEC_ID = 0x9F
  QUAD_JID = 0xAF
  SFDP = 0x5A
  WREN = 0x06
  WRDI = 0x04
  SE = 0x20
  BE = 0xD8
  CE = 0xC7
  PP = 0x02
  QPP = 0x32
  WRSU = 0xB0
  WRRE = 0x30
  RBPR = 0x72
  WBPR = 0x42
  LBPR = 0x8D
  NVWLDR = 0xE8
  ULBPR = 0x98
  RSID = 0x88
  PSID = 0xA5
  LSID = 0x85

  READ_DATA_CMDS = [RDSR, RDCR, READ, HSREAD, SQOREAD, SQIOREAD,
                    SDOREAD, SDIOREAD, RBSQI_WRAP, RBSPI_WRAP,
                    JEDEC_ID, QUAD_JID, SFDP, RBPR, RSID ]
  WRITE_DATA_CMDS = [WRSR, SETBURST, PP, QPP, WBPR, NVWLDR, PSID]
  NODATA_CMDS = [NOP, RSTEN, RSTMEM, ENQIO, RSTQIO, WREN, WRDI, SE, BE, CE, ULBPR]
  
  SPICMD_NOP = [NOP, 0]
  SPICMD_RSTEN = [RSTEN, 0]
  SPICMD_RSTMEM = [RSTMEM, 0]
  SPICMD_ENQIO = [ENQIO, 1]
  SPICMD_RSTQIO = [RSTQIO, 0]
  SPICMD_RDSR = [RDSR, [2, 3]]
  SPICMD_WRSR = [WRSR, 4]
  SPICMD_RDCR = [RDCR, [2, 3]]
  SPICMD_READ = [READ, 5]
  SPICMD_HSREAD = [HSREAD, [6, 7]]
  SPICMD_SQOREAD = [SQOREAD, 7]
  SPICMD_SQIOREAD = [SQIOREAD, 6]
  SPICMD_SDOREAD = [SDOREAD, 7]
  SPICMD_SDIOREAD = [SDIOREAD, 7]
  SPICMD_SETBURST = [SETBURST, 8]
  SPICMD_RBSQI_WRAP = [RBSQI_WRAP, 9]
  SPICMD_RBSPI_WRAP = [RBSPI_WRAP, 0x0A]
  SPICMD_JEDEC_ID = [JEDEC_ID, 0x0B]
  SPICMD_QUAD_JID = [QUAD_JID, 0x0C]
  SPICMD_SFDP = [SFDP, 0x0D]
  SPICMD_WREN = [WREN, 0]
  SPICMD_WRDI = [WRDI, 0]
  SPICMD_SE = [SE, 0x0E]
  SPICMD_BE = [BE, 0x0E]
  SPICMD_CE = [CE, 0]
  SPICMD_PP = [PP, 0x0F]
  SPICMD_QPP = [QPP, 0x10]
  SPICMD_WRSU = [WRSU, 0]
  SPICMD_WRRE = [WRRE, 0]
  SPICMD_RBPR = [RBPR, [0x11, 0x12]]
  SPICMD_WBPR = [WBPR, 0x13]
  SPICMD_LBPR = [LBPR, 0]
  SPICMD_NVWLDR = [NVWLDR, 0x13]
  SPICMD_ULBPR = [ULBPR, 0]
  SPICMD_RSID = [RSID, [0x14, 0x15]]
  SPICMD_PSID = [PSID, 0x16]
  SPICMD_LSID = [LSID, 0]
  
  SPI_CMDSPECS = [ SPICMD_NOP, SPICMD_RSTEN, SPICMD_RSTMEM,
                   SPICMD_ENQIO, SPICMD_RSTQIO, SPICMD_RDSR,
                   SPICMD_WRSR, SPICMD_RDCR, SPICMD_READ,
                   SPICMD_HSREAD, SPICMD_SQOREAD, SPICMD_SQIOREAD,
                   SPICMD_SDOREAD, SPICMD_SDIOREAD, SPICMD_SETBURST,
                   SPICMD_RBSQI_WRAP, SPICMD_RBSPI_WRAP,
                   SPICMD_JEDEC_ID, SPICMD_QUAD_JID, SPICMD_SFDP,
                   SPICMD_WREN, SPICMD_WRDI, SPICMD_SE, SPICMD_BE,
                   SPICMD_CE, SPICMD_PP, SPICMD_QPP, SPICMD_WRSU,
                   SPICMD_WRRE, SPICMD_RBPR, SPICMD_WBPR, SPICMD_LBPR,
                   SPICMD_NVWLDR, SPICMD_ULBPR, SPICMD_RSID,
                   SPICMD_PSID, SPICMD_LSID ] 
  
  WREN_REQUIRED = [ SE, BE, CE, PP, WRSR, PSID, LSID, WBPR, LBPR,
                    ULBPR, NVWLDR, QPP, WRSR]
  
  SPI_MODES = [ SPIMODE_0, SPIMODE_1, SPIMODE_2, SPIMODE_3, SPIMODE_4,
                SPIMODE_5, SPIMODE_6, SPIMODE_7, SPIMODE_8, SPIMODE_9,
                SPIMODE_A, SPIMODE_B, SPIMODE_C, SPIMODE_D, SPIMODE_E,
                SPIMODE_F, SPIMODE_10, SPIMODE_11, SPIMODE_12,
                SPIMODE_13, SPIMODE_14, SPIMODE_15, SPIMODE_16]
  
  SPIMODE_0 = promira.AA_SPI_PHASE_SAMPLE_SETUP + (promira.AA_SPI_SS_ACTIVE_LOW << 1)
  SPIMODE_1 = promira.AA_SPI_PHASE_SAMPLE_SETUP + (promira.AA_SPI_SS_ACTIVE_HIGH << 1)
  SPIMODE_2 = promira.AA_SPI_PHASE_SETUP_SAMPLE + (promira.AA_SPI_SS_ACTIVE_LOW << 1)
  SPIMODE_3 = promira.AA_SPI_PHASE_SETUP_SAMPLE + (promira.AA_SPI_SS_ACTIVE_HIGH << 1)
  
  def fatalError(self, label):
    print("Fatal Error:" + label)
    sys.exit()
    
  def printArrayHexDump(self, label, data_array=None):
    
    if data_array == None or len(data_array) == 0:
      print("Hexdump:  array is empty")
      return
    
    bytes_per_line = 32
    print(label + " [ %03X bytes ]")
    array_size = len(data_array)
    array_lines = (array_size + bytes_per_line - 1) // bytes_per_line
    dump_bytes = array_size
    dump_index = 0
    for line in range(array_lines):
      linestart = line * bytes_per_line
      linestring = " %02X : " % linestart
      if dump_bytes >= bytes_per_line:
        line_bytes = bytes_per_line
      else:
        line_bytes = dump_bytes
        
      for dump_index in range(dump_index, dump_index + line_bytes):
        value = data_array[dump_index]
        linestring = linestring + " %02X" % value
      print(linestring)
      
  def cmdN64(self, command): 
      pass
  
  PROMIRA_ERRORS=[ 
    (promira.AA_OK, "OK"),
    (promira.AA_UNABLE_TO_LOAD_LIBRARY, "unable to load library"),
    (promira.AA_UNABLE_TO_LOAD_DRIVER, "unable to load USB driver"),
    (promira.AA_UNABLE_TO_LOAD_FUNCTION, "unable to load binding function"),
    (promira.AA_INCOMPATIBLE_LIBRARY, "incompatible library version"),
    (promira.AA_INCOMPATIBLE_DEVICE, "incompatible device version"),
    (promira.AA_COMMUNICATION_ERROR, "communication error"),
    (promira.AA_UNABLE_TO_OPEN, "unable to open device"),
    (promira.AA_UNABLE_TO_CLOSE, "unable to close device"),
    (promira.AA_INVALID_HANDLE, "invalid device handle"),
    (promira.AA_CONFIG_ERROR, "configuration error"),
    (promira.AA_I2C_NOT_AVAILABLE, "i2c feature not available"),
    (promira.AA_I2C_NOT_ENABLED, "i2c not enabled"),
    (promira.AA_I2C_READ_ERROR, "i2c read error"),
    (promira.AA_I2C_WRITE_ERROR, "i2c write error"),
    (promira.AA_I2C_SLAVE_BAD_CONFIG, "i2c slave enable bad config"),
    (promira.AA_I2C_SLAVE_READ_ERROR, "i2c slave read error"),
    (promira.AA_I2C_SLAVE_TIMEOUT, "i2c slave timeout"),
    (promira.AA_I2C_DROPPED_EXCESS_BYTES, "i2c slave dropped excess bytes"),
    (promira.AA_I2C_BUS_ALREADY_FREE, "i2c bus already free"),
    (promira.AA_SPI_NOT_AVAILABLE, "spi feature not available"),
    (promira.AA_SPI_NOT_ENABLED, "spi not enabled"),
    (promira.AA_SPI_WRITE_ERROR, "spi write error"),
    (promira.AA_SPI_SLAVE_READ_ERROR, "spi slave read error"),
    (promira.AA_SPI_SLAVE_TIMEOUT, "spi slave timeout"),
    (promira.AA_SPI_DROPPED_EXCESS_BYTES, "spi slave dropped excess bytes"),
    (promira.AA_GPIO_NOT_AVAILABLE, "gpio feature not available") ]

  def apiIfError(self, result_code):
    if result_code == promira.AA_OK or result_code>0:
      return False 
    
    for error_id in self.PROMIRA_ERRORS:
      if error_id[0] == result_code:
        print(error_id[1])
        return True
    
    print("unspecified API error")
    return True
  
  def spi_master_cmd (self, cmd_spec, xfer_bytescount=None, xfer_array=None, address=None):
    if xfer_array != None:
      if xfer_bytescount == None or len(xfer_array) < xfer_bytescount:
        raise(ValueError)
    
    # SPI COMMAND MODE DATA HAS THESE ELEMENTS
    # SPI/SQI/SQX(BOTH) MODE
    # COUNT OF ADDRESS TRANSACTION CYCLES (ADDRESS BYTES WRITTEN TO DEVICE)
    # COUNT OF DUMMY TRANSACTION CYCLES (DON'T CARE BYTE WRITTEN TO DEVICE)
    # COUNT OF DATA TRANSACTION CYCLES (DATA EXCHANGED WITH DEVICE) ***
    # *** ON READ COMMANDS THE INCOMING DATA IS RELEVANT, OUTGOING IS DON'T CARE
    # *** ON WRITE COMMANDS THE OUTGOING DATA IS RELEVANT, INCOMING IS DON'T CARE
    # *** COMMANDS WHERE MEANINGFUL DATA IS OUTPUT *AND* INPUT IS POSSIBLE, BUT 
    #     NOT DEFINED FOR THIS EEPROM COMMAND SET

  # SPISPEC ENTRIES
  # SPI_CMDSPEC_CMDBYTE=0
  # SPI_CMDSPEC_MODE_INDEX=1

    # get cmd_spec mode matching preferred spi io mode
    cmd_byte = cmd_spec[self.SPI_CMDSPEC_CMDBYTE]
    cmd_mode_spec_index = cmd_spec[self.SPI_CMDSPEC_MODE_INDEX]
    if type(cmd_mode_spec_index) == list:
      for mode_spec_index in cmd_mode_spec_index:
        cmd_mode_spec = self.SPI_MODES[mode_spec_index]
        if cmd_mode_spec[self.MODE_ID] in [self.MODE_SPI, self.MODE_SXI] and self.m_preferred_spiio_mode == self.SPIIO_SINGLE:
          break
        
        elif cmd_mode_spec[self.MODE_ID] in [self.MODE_SQI, self.MODE_SXI] and self.m_preferred_spiio_mode == self.SPIIO_QUAD:
          break
    else:
      cmd_mode_spec = self.SPI_MODES[cmd_mode_spec_index]
      
      
    # obtain spi transfer characteristics
    addr_cycles = cmd_mode_spec[self.MODE_ADDRCY]
    dummy_cycles = cmd_mode_spec[self.MODE_DUMMYCY]
    data_cycles_code = cmd_mode_spec[self.MODE_DATACY]
 
    if addr_cycles > 0 and address == None: # and payload_length!=0:
      self.fatalError("spi read/write address error")
    
    # obtain transfer direction and payload type
    read_cmd=cmd_byte in self.READ_DATA_CMDS
    write_cmd=cmd_byte in self.WRITE_DATA_CMDS
    nodata_cmd=cmd_byte in self.NODATA_CMDS

    # assert orthogonality of types
    if ( ( read_cmd and (write_cmd or nodata_cmd) )
         or ( write_cmd and (read_cmd or nodata_cmd) )
         or ( nodata_cmd and (write_cmd or read_cmd))
         ):
      self.fatalError("broken cmd categories")

    # assert correct parameter usage
    if nodata_cmd:
      if (xfer_bytescount not in [None, 0]) or xfer_array!=None:
        self.fatalError("parameter error 1")
    else:
        # bytescount must be nonzero
      if type(xfer_bytescount)!=int or xfer_bytescount<0:
        self.fatalError("parameter error 2")
      
      if read_cmd:
        # optionally specified array must be equal or greater length
        if xfer_array!=None and xfer_bytescount>len(xfer_array):
          self.fatalError("parameter error 3")
      elif write_cmd:
          if xfer_array==None or xfer_bytescount > len(xfer_array):
            self.fatalError("parameter error 4")


    # compute command / payload size
    # begin with generic cmd mode data cycle spec
    if data_cycles_code == self.DCY_0:
        payload_length = 0
    elif data_cycles_code == self.DCY_1:
        payload_length = 1
    elif data_cycles_code == self.DCY_2:
      payload_length = 2
    elif data_cycles_code == self.DCY_3:
      payload_length = 3
    elif data_cycles_code == self.DCY_1_INF:
      payload_length = max([1, xfer_bytescount])
    elif data_cycles_code == self.DCY_2_INF:
      payload_length = max([2, xfer_bytescount])
    elif data_cycles_code == self.DCY_3_INF:
      payload_length = max([3, xfer_bytescount])
    elif data_cycles_code == self.DCY_1_INF:
        payload_length = max([1, xfer_bytescount])
    elif data_cycles_code == self.DCY_N_INF:
      payload_length = xfer_bytescount
    elif data_cycles_code == self.DCY_1_18:
        payload_length=max([xfer_bytescount, 18])
    elif data_cycles_code == self.DCY_1_2048:
        payload_length=max([xfer_bytescount, 2048])
    elif data_cycles_code == self.DCY_1_256:
        payload_length=max([xfer_bytescount, 256])
        

    # begin build of command (non-payload) array
    # command; address; dummy cycle placeholders;[payload]
    cmd_array = promira.array_u08(0)
    cmd_array.append(cmd_byte)

    if addr_cycles > 0:
      address_bytes = address

      for index in range(3):
        cmd_array.append(address_bytes & 0xff)
        address_bytes = address_bytes >> 8

    if dummy_cycles > 0:
      for index in range(dummy_cycles):
        cmd_array.append(0)
        
    # at this point:
    #   cmd_array is defined
    #   read: destination input array is optionally defined
    #   write: payload array is defined
    #   nodata: no payload is a constraint
    
    if read_cmd:
      cmd_array_len=len(cmd_array)
      data_in = promira.array_u08(payload_length+cmd_array_len)
      cmd_array=cmd_array+data_in[cmd_array_len:]
      transaction_length=len(cmd_array)
      xfer_retcode = promira.aa_spi_write(self.m_Aardvark, (cmd_array, transaction_length), (data_in, transaction_length))

      if self.apiIfError(xfer_retcode[0]):
        self.fatalError("")
      
      if xfer_array != None:
        xfer_array=data_in[cmd_array_len:]
        return (xfer_retcode[0]-cmd_array_len, xfer_array)
      else:
        return (xfer_retcode[0]-cmd_array_len, data_in[cmd_array_len:])

    else:
      if cmd_byte in self.WREN_REQUIRED:
        wren_array = array.array('B', [self.WREN])
        xfer_retcode = promira.aa_spi_write(self.m_Aardvark, wren_array, 1)
        if self.apiIfError(xfer_retcode[0]):
          self.fatalError("")

      if write_cmd:
        cmd_array = cmd_array + xfer_array
        
      self.m_rxdata_array = promira.array_u08(len(cmd_array))
      xfer_retcode = promira.aa_spi_write(self.m_Aardvark, cmd_array, self.m_rxdata_array)
      if self.apiIfError(xfer_retcode[0]):
        self.fatalError("")
        
      return xfer_retcode
    
  def init_spi(self, port, bitrate):
    pass
  
  def init_spi_slave(self):
    pass

  def init_spi_master(self, port, bitrate, mode):
  # Open the device
    self.m_Aardvark = promira.aa_open(port)
    if (self.m_Aardvark <= 0):
        print("Unable to open Aardvark device on port %d" % self.m_device)
        print("Error code = %d" % self.m_Aardvark)
        sys.exit()

    # Ensure that the SPI subsystem is enabled
    promira.aa_configure(self.m_Aardvark, promira.AA_CONFIG_SPI_I2C)
    
    # Power the EEPROM using the Aardvark adapter's power supply.
    # This command is only effective on v2.0 hardware or greater.
    # The power pins on the v1.02 hardware are not enabled by default.
    promira.aa_target_power(self.m_Aardvark, promira.AA_TARGET_POWER_TGT1_3V)
    
    # Setup the clock phase
    promira.aa_spi_configure(self.m_Aardvark, mode >> 1, mode & 1, promira.AA_SPI_BITORDER_MSB)
    
    # Set the bitrate
    bitrate = promira.aa_spi_bitrate(self.m_Aardvark, bitrate)
    print("Bitrate set to %d kHz" % bitrate)
    return
  
  def eepromSpiTestJedec(self):
    result_tuple = self.spi_master_cmd(self.SPICMD_JEDEC_ID, 3)
    if result_tuple[0] < 3:
      print("error: jedec read")
      sys.exit()

    self.m_rxdata_array = result_tuple[1][1:]
      
    jedec_id = [0xBF, 0x26, 0x42]
    for index in range(len(jedec_id)):
      if jedec_id[index] != self.m_rxdata_array[index]:
        return False
    
    return True
  
  def eepromSpiTestNOP(self):
    result_tuple = self.spi_master_cmd(self.SPICMD_NOP)
    return (result_tuple == 1)
  
  EESTATUS_BUSY1 = 0x1
  EESTATUS_W_ENABLE_LATCH = 0x2
  EESTATUS_W_SUSPEND_ERASE = 0x4
  EESTATUS_W_SUSPEND_PROGRAM = 0x8
  EESTATUS_W_PROTECT_LOCKDOWN = 0x10
  EESTATUS_SECURITY_ID = 0x20
  EESTATUS_RESERVED = 0x40
  EESTATUS_BUSY80 = 0x80
  
  def eepromSpiStatusBusy(self):
    if self.eepromSpiStatusReadStatusRegister() == None:
      self.fatalError("Status Read Fail")
    return ((self.m_eepromStatus & self.EESTATUS_BUSY1) != 0)
  
  def eepromSpiWaitUntilNotBusy(self):
    while self.eepromSpiStatusBusy():
      print(",")
      continue
  
  def eepromSpiStatusReadStatusRegister(self):
    cmd_array = promira.array_s08(2)
    cmd_array[0] = self.SPICMD_RDSR[0]
    cmd_array[1] = 0
    
    result_tuple = self.spi_master_cmd(self.SPICMD_RDSR, 1)
    self.m_eepromStatus = None
    if (result_tuple[0] == 1):
      self.m_eepromStatus = result_tuple[1][0]
    
    return self.m_eepromStatus
  
  def eepromSpiReadData(self, read_address, read_length, read_array):

    result_tuple = self.spi_master_cmd(self.SPICMD_READ, read_length, None, read_address)
    data_in = result_tuple[1]
    data_in_length = len(data_in)
    data_offset = data_in_length - read_length
    
    if data_offset >= 0:
      for index in range(read_length):
        read_array[index] = result_tuple[1][data_offset + index]
      return True
    
    return False

  def eepromSpiWriteEnable(self):
    result_tuple = self.spi_master_cmd(self.SPICMD_WREN)
    return (result_tuple == 1)
  
  def eepromSpiReadProtectBitmap(self):
    self.m_eeprom_protect_bitmap = promira.array_u08(18)
    result_tuple = self.spi_master_cmd(self.SPICMD_RBPR, 18, self.m_eeprom_protect_bitmap)
    if result_tuple[0] == 18:
      self.m_eeprom_protect_bitmap = result_tuple[1][1:]
      return True
    else:
      self.fatalError("Protect Bitmap Read fail")
  
  def eepromSpiEraseSector(self, sector_address):
    if (sector_address & ~(self.EEPROM_SECTOR_SIZE-1)) != sector_address:
      self.fatalError("sector address error")

    self.eepromSpiWaitUntilNotBusy()
          

    result_tuple = self.spi_master_cmd(self.SPICMD_SE, None, None, sector_address)
    #return(result_tuple[0] == 1)
    return True
      
  def eepromSpiUpdateWithinPage(self, write_address, write_length, write_array):
    # Update one page per function use
    # This function erases a sector EVERY TIME it is used
    # Proves erase-before-write works, but NOT EFFICIENT
    
    # Page level checks
    start_page = write_address // self.EEPROM_PAGE_SIZE
    end_page = (write_address + (write_length - 1)) // self.EEPROM_PAGE_SIZE
    if start_page != end_page:
      self.fatalError("Page Write Spans Pages")
      
    # Sector level check & Sector Erase + Page Write
    sector_size_mask = self.EEPROM_SECTOR_SIZE - 1
    sector_address = write_address & ~sector_size_mask
    sector_offset = write_address & sector_size_mask
    
    if self.eepromSpiEraseSector(sector_address) == False:
      return False
    
    if self.eepromSpiWriteWithinPage(write_address, write_length, write_array) == False:
      return False
    
    return True
  
  def eepromSpiWriteWithinPage(self, write_address, write_length, write_array):
    # Update one page per function use
    start_page = write_address // self.EEPROM_PAGE_SIZE
    end_page = (write_address + (write_length - 1)) // self.EEPROM_PAGE_SIZE
    if start_page != end_page:
      self.fatalError("Page Write Spans Pages")

    self.eepromSpiWaitUntilNotBusy()
    
    result_tuple = self.spi_master_cmd(self.SPICMD_PP, write_length, write_array, write_address)
    return (result_tuple[0] == 1)

  def eepromSpiGlobalUnlock(self):
    result_tuple = self.spi_master_cmd(self.SPICMD_ULBPR)
    return (result_tuple[0] == 1)
  
  def eepromWriteProtectBitmap(self):
    result_tuple = self.spi_master_cmd(self.SPICMD_WBPR, len(self.m_eeprom_protect_bitmap), self.m_eeprom_protect_bitmap)
    return (result_tuple[0] == 19)
  
  def close_session(self, handle):    
    # Close the device
    promira.aa_close(handle)
     
  def cmdPromira(self, command):
    pass
  
  def i2c_slave_read(self, maxcount, rxdata_array):
    promira.aa_i2c_slave_read(self.m_Aardvark, rxdata_array)
    pass
  
  def i2c_slave_write(self, count, txdata_array):
    pass
      
  def i2c_master_read(self, maxcount, rxdata_array):
      # prepare N64 to Read
      # command Promira to Write
      # get results
    (rx_count, rxdata_array) = promira.aa_i2c_read(self.m_Aardvark, self.m_device,
                                   promira.AA_I2C_NO_FLAGS, maxcount)    
    if (rx_count < 0):
        print("error: %s" % promira.aa_status_string(rx_count))

    elif (rx_count == 0):
        print("error: no bytes read")
        print("  are you sure you have the right slave address?")

    self.m_rxdata_array = rxdata_array
    return rx_count
  
  def i2c_master_write(self, txdata_count, txdata_array):
    
    count_txd = promira.aa_i2c_write(self.m_Aardvark, self.m_slaveAddress, promira.AA_I2C_NO_FLAGS, (txdata_array, txdata_count))

    if (count_txd < 0):
        print("error: %s" % promira.aa_status_string(count_txd))

    elif (count_txd == 0):
        print("error: no bytes written")
        print("  are you sure you have the right slave address?")

    elif (count_txd != len(txdata_array)):
        print("error: only a partial number of bytes written")
        print("  (%d) instead of full (%d)" % (count_txd, txdata_count))
    
    return(count_txd)
    
  def init_i2c(self, port, addr, timeout_ms):
    # Open the device
    self.m_Aardvark = promira.aa_open(port)
    if (self.m_Aardvark <= 0):
        print("Unable to open Aardvark device on port %d" % port)
        print("Error code = %d" % self.m_Aardvark_Aardvark)
        sys.exit()
    
    # Ensure that the I2C subsystem is enabled
    promira.aa_configure(self.m_Aardvark, promira.AA_CONFIG_SPI_I2C)
    
    # Enable the I2C bus pullup resistors (2.2k resistors).
    # This command is only effective on v2.0 hardware or greater.
    # The pullup resistors on the v1.02 hardware are enabled by default.
    promira.aa_i2c_pullup(self.m_Aardvark, promira.AA_I2C_PULLUP_BOTH)
    
    # Power the EEPROM using the Aardvark adapter's power supply.
    # This command is only effective on v2.0 hardware or greater.
    # The power pins on the v1.02 hardware are not enabled by default.
    promira.aa_target_power(self.m_Aardvark, promira.AA_TARGET_POWER_NONE)
    # Set the bitrate
    bitrate_khz = promira.aa_i2c_bitrate(self.m_Aardvark, self.m_bitrate_khz)
    print("Bitrate set to %d kHz" % bitrate_khz)
    pass
  
  def init_i2c_master(self):
    # hard code these in prototype
    # elegantly discover them in deliverable
    
    self.m_port = self.m_device_ips[0]  # default port for a single promira device
    self.m_slaveAddress = 0x55  # default for Arduino Nano TestSlave
    self.m_timeout_ms = 10000  # arbitrary 10 second value
    self.m_bitrate_khz = 400
    self.m_Aardvark = promira.aa_open(self.m_port)
    if (self.m_Aardvark <= 0):
        print("Unable to open Aardvark device on port %d" % self.m_port)
        print("Error code = %d" % self.m_Aardvark)
        sys.exit()
    
    # Set the slave response
    self.m_slave_resp_array = self.zeroed_u08_packet(self.m_pkgsize)

    promira.aa_i2c_slave_set_response(self.m_Aardvark, self.m_slave_resp_array)
    
    # Enable the slave
    promira.aa_i2c_slave_enable(self.m_Aardvark, self.m_slaveAddress, 0, 0)
    
    # Disable the slave and close the device
    promira.aa_i2c_slave_disable(self.m_Aardvark)
    promira.aa_close(self.m_Aardvark)
       
  def init_i2c_slave(self):
    # hard code these in prototype
    # elegantly discover them in deliverable
    
    # Open the device
    self.m_Aardvark = promira.aa_open(self.m_port)
    if (self.m_Aardvark <= 0):
        print("Unable to open Aardvark device on port %d" % self.m_port)
        print("Error code = %d" % self.m_Aardvark)
        sys.exit()
    
    # Set the slave response
    self.m_slave_resp = self.zeroed_u08_packet(self.m_pkgsize)

    promira.aa_i2c_slave_set_response(self.m_Aardvark, self.m_slave_resp)
    
    # Enable the slave
    promira.aa_i2c_slave_enable(self.m_Aardvark, self.m_slaveAddress, 0, 0)
    
    # Write to slave
    
    # Read from slave
    
    # Compare written to read data, show result
    
    # Disable the slave and close the device
    promira.aa_i2c_slave_disable(self.m_Aardvark)
    promira.aa_close(self.m_Aardvark)
  
  def zeroed_u08_array(self, array_size):
      zero_array = promira.array_u08(array_size)
      for index in range(array_size):
        zero_array[index] = 0
        
      return zero_array
  
  def random_u08_array(self, array_size):
      rand_array = promira.array_u08(array_size)
      for index in range(1, array_size):
        rand_array[index] = random.randint(0, 255)
        
      return rand_array
    
  def build_random_packet_arrays(self):
      self.m_random_packet_array_list = []
      for index in range(self.m_randarray_count):
          self.m_random_packet_array_list.append(self.random_u08_array(self.m_pkgsize))
          array_label = "Random Packet Array #%02X:" % index
          # self.printArrayHexDump(array_label, self.m_random_packet_array_list[index])

  def build_random_page_arrays(self):
      self.m_random_page_array_list = []
      for index in range(self.m_randarray_count):
          self.m_random_page_array_list.append(self.random_u08_array(self.EEPROM_PAGE_SIZE))
          array_label = "Random Page Array #%02X:" % index
          # self.printArrayHexDump(array_label, self.m_random_page_array_list[index])
          
  m_random_page_array_index = 0
  m_random_packet_array_index = 0
  
  def next_random_page_array(self):
      self.m_random_page_array_index = (self.m_random_page_array_index + 1) % self.m_randarray_count
      return self.m_random_page_array_list[self.m_random_page_array_index]

  def next_random_packet_array(self):
      self.m_random_packet_array_index = (self.m_random_packet_array_index + 1) % self.m_randarray_count
      return self.m_random_packet_array_list[self.m_random_packet_array_index]
    
  def runTest(self, busType):
    if busType in [self.BUSTYPE_I2C, self.BUSTYPE_SPI]:
      self.m_bus_type = busType
    else:
      print("error: illegal bus type")
      sys.exit()
    
    self.m_port = 0  # default port for a single promira device
    self.m_slaveAddress = 0x55  # default for Arduino Nano TestSlave
    self.m_timeout_ms = 1000  # arbitrary 10 second value 
    self.m_bitrate_khz = 400  # 100khz bus clock
    self.m_device = self.m_slaveAddress
    return_tuple = promira.aa_find_devices_pm(self.m_device_ips, self.m_device_ids, self.m_device_status)
    device_count = return_tuple[0]
    self.m_device_ips = return_tuple[1]
    self.m_devices = return_tuple[2]
    self.m_device_ids = return_tuple[3]
    print("device_count:" + str(device_count))

    random.seed(0)
    self.build_random_packet_arrays()
    self.build_random_page_arrays()
    
    if self.m_bus_type == self.BUSTYPE_I2C:
      self.init_i2c_master()
      self.init_i2c(self.m_device_ips[0], 0, self.m_timeout_ms);
    else:
      self.m_bus_mode = self.SPIMODE_0
      self.init_spi_master(self.m_device_ips[0], self.m_bitrate_khz, self.m_bus_mode)
      # self.init_spi(self.m_device_ips[0], self.m_bitrate_khz)
      
    self.m_txdata_array = self.random_u08_array(self.m_pkgsize)
    txdata_count = self.m_pkgsize
    read_packets = True
    write_packets = True
    
    while True:
      if write_packets:
        self.m_txdata_array = self.next_random_packet_array()
        
        if self.m_bus_type == self.BUSTYPE_I2C:
          writecount = self.i2c_master_write(txdata_count, self.m_txdata_array)
          if writecount < len(self.m_txdata_array):
            print ("Bad TxData Write %d instead of %d bytes", writecount, txdata_count)

          if read_packets:  
            readcount = self.i2c_master_read(txdata_count, self.m_rxdata_array)
            if readcount != txdata_count:
              print ("Bad RxData Read %d instead of %d bytes", readcount, txdata_count)
        
        if self.m_bus_type == self.BUSTYPE_SPI:
          self.eepromSpiTestNOP()
          self.eepromSpiTestJedec()
          self.eepromSpiWaitUntilNotBusy()
          
          if self.eepromSpiReadProtectBitmap() == False:
            self.fatalError("Protect Bitmap Read Failed")
            
            # self.printArrayHexDump("Initial Protect Bitmap Array", self.m_eeprom_protect_bitmap)
 
          if self.eepromSpiGlobalUnlock() == False:
            self.fatalError("Global Unlock Command Failed")
            
          if self.eepromSpiReadProtectBitmap() == False:
            self.fatalError("Protect Bitmap Read Failed")
          else:  
            sum = 0
            for entry in self.m_eeprom_protect_bitmap:
              sum += entry
            
            if entry != 0:
              self.fatalError("Global Unlock Failed")
              
#            self.printArrayHexDump("Unlocked Protect Bitmap Array", self.m_eeprom_protect_bitmap)

#          self.m_eeprom_protect_bitmap=self.zeroed_u08_array(18)  
#          if self.eepromWriteProtectBitmap():
#            self.printArrayHexDump("Post-Write Protect Bitmap Array", self.m_eeprom_protect_bitmap)
            
#          protect_array = self.eepromReadProtectBitmap()
#          self.printArrayHexDump("Protect Array", protect_array)
          txdata_array = self.next_random_page_array()
          self.printArrayHexDump("EEProm Write", txdata_array)
          self.eepromSpiUpdateWithinPage(0x1000, self.EEPROM_PAGE_SIZE, txdata_array)
                      
          rxdata_array = self.zeroed_u08_array(self.EEPROM_PAGE_SIZE)
          self.eepromSpiWaitUntilNotBusy()
          return_tuple = self.eepromSpiReadData(0x1000, self.EEPROM_PAGE_SIZE, rxdata_array)
          
          self.printArrayHexDump("Unlocked Protect Bitmap Array", self.m_eeprom_protect_bitmap)
          self.printArrayHexDump("EEProm Read", rxdata_array)
          for index in range(0xFC, self.EEPROM_PAGE_SIZE):
            if rxdata_array[index] != txdata_array[index]:
              print("write/read/compare fault at offset %02X " % index)
          
        time.sleep(2)

#    self.run_test_core()  

