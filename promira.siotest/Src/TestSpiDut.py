"""Py test that does a test function"""
from __future__ import division, with_statement, print_function


#import os
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
import usertest
import promact_is_py as pmact
import eeprom
import cmd_protocol as protocol
import test_utility as testutil
import spi_io as spiio
import spi_cfg_mgr as spicfg
import promactive_msg as pmmsg 
import sys
import time
from _ast import Or
from cmd_protocol import SPICMD_READ, SPICMD_HSREAD
from cairo._cairo import Pattern






#==========================================================================
# CONSTANTS
#==========================================================================
BUFFER_SIZE = 65535
INTERVAL_TIMEOUT = 500



#==========================================================================
# FUNCTIONS
#==========================================================================

  

class promiraSpiTestApp(usertest.SwUserTest):
  """Unit test template"""
  
    
  m_eepromStatus  = None
  m_testutil          = None
  m_spi_msg       = None
  m_config_mgr    = None
  m_rxdata_array  = None
  m_txdata_array  = None
  m_random_page_array = None
  m_pagesize      = None
  m_eeprom        = None
  m_instantiator  = None

  
  def __init__(self):
    self.m_testutil     = testutil.testUtil()
    self.m_config_mgr   = spicfg.configMgr()
    self.m_spi_msg      = pmmsg.promactMessages()
    self.m_eeprom       = eeprom.eeprom()
    self.m_spiio       = self.m_eeprom.getobjectSpiIO()

    self.m_pagesize     = eeprom.eeprom.EEPROM_PAGE_SIZE

    block_protect_bitmap  = pmact.array_u08(18)
    self.m_rxdata_array           = pmact.array_u08(self.m_pagesize)
    self.m_txdata_array           = pmact.array_u08(self.m_pagesize)
    self.m_random_page_array      = pmact.array_u08(self.m_pagesize)
    return
    


  


#==========================================================================
# FUNCTION (APP)
#==========================================================================
  
  def voltageOK(self, var, fixed, eeprom_vdd):

    if fixed!=None:
      print("Promira DUT voltage supply (VTGT1,2) is not allowed")
      return True

    elif var==None:
        print("Bench "+str(eeprom_vdd)+"V power supply required for eeprom")
        return True
      
    elif var==3.3:
      if eeprom_vdd==3.3:
        print("EEPROM vdd="+str(var)+"V supplied by Promira")
        return True
      
      else:
        print("EEPROM vdd="+str(eeprom_vdd)+"V, supply by Promira is "+str(var)+"V: MISMATCH")
        return False

    elif eeprom_vdd==1.8:
        if var>=1.6 and var<=1.8:
          print("EEPROM vdd="+str(eeprom_vdd)+"V, supply by Promira is "+str(var)+"V: OK")
          return True
          
    print("Promira Supply and EEPROM vdd mismatch")
    return False
  
  
  def writeDevicePattern(self, start_page_address, length, device_byte_size, pattern_array):
    if start_page_address % self.m_eeprom.EEPROM_PAGE_SIZE != 0:
      self.m_testutil.fatalError("illegal page address")
    
    if length % self.m_eeprom.EEPROM_PAGE_SIZE != 0:
      self.m_testutil.fatalError("illegal page fill length")
      
    start_page=start_page_address/self.m_eeprom.EEPROM_PAGE_SIZE
    page_count=length/self.m_eeprom.EEPROM_PAGE_SIZE
    
    if start_page+page_count > (device_byte_size/self.m_eeprom.EEPROM_PAGE_SIZE):
      self.m_testutil.fatalError("write request too large")
      
    for page in range(page_count):
      page_address=start_page_address+(page * self.m_eeprom.EEPROM_PAGE_SIZE)
      self.m_eeprom.updateWithinPage(page_address, eeprom.eeprom.EEPROM_PAGE_SIZE, pattern_array)

  
  def readTest(self, read_cmd_byte, cmd_namestring, address, length, pattern_array, verbose):
    rxdata_array = self.m_testutil.zeroedArray(self.m_eeprom.EEPROM_PAGE_SIZE)
    self.m_eeprom.waitUntilNotBusy()

    if read_cmd_byte==protocol.READ:
      _read_length = self.m_eeprom.readData(address, length, rxdata_array)

    if read_cmd_byte==protocol.HSREAD:
      _read_length = self.m_eeprom.highspeedReadData(address, length, rxdata_array)

    if read_cmd_byte==protocol.SDOREAD:
      _read_length = self.m_eeprom.readDataDual(address, length, rxdata_array)



      
    if not self.m_testutil.arraysMatch(rxdata_array, pattern_array):
        print("%s comparison fault" % cmd_namestring)
        if verbose:
          print("Sector Address %x" % address)

          self.m_testutil.printArrayHexDumpWithErrors("EEProm %s" % cmd_namestring, rxdata_array, pattern_array)
          
        return False
    return True
  
  def runTest(self):


    txdata_array = self.m_testutil.firstRandomPageArray()
    _txdata_count = len(txdata_array)
    

    '''
    flags control test loop contents
    '''
    
    verbose=True
    write_data = False
    read_single_data=True
    read_dual_data=True
    read_hispeed_data=True
    eeprom_unlocked=False

    first_loop=True
    spi_parameters = self.m_config_mgr.firstConfig()
    self.m_spiio.initSpiMaster(spi_parameters)
    '''
    testJedec() forces device recognition
    '''
    
    self.m_eeprom.testJedec()
    eepromConfig= self.m_eeprom.m_devconfig
    
    mfgrname=eepromConfig.mfgr
    chipname=eepromConfig.chip_type
    memsize_MB=eepromConfig.memsize/(1024*1024)
    print("EEPROM Type: "+ mfgrname + " "+ chipname  )
    print("Memory Size = " + str(memsize_MB) +"   Voltage= "+ str(eepromConfig.vdd)+"V")

#      if mfgrname=='Micron':
    micronstatus=self.m_eeprom.readMicronStatusRegisters()
    print(repr(micronstatus))
    
    dtr_status=not self.m_eeprom.dtrStatus()
    dual_status=not self.m_eeprom.dualStatus()
    quad_status=not self.m_eeprom.quadStatus()
    
    print("DTR: "+str(dtr_status)+"   Dual I/O: "+str(dual_status)+ "   Quad: "+str(quad_status))
    
    
    page_address=spi_parameters.address_base+0x1000
    
    for spi_parameters in self.m_config_mgr.m_spi_config_list:
      print(repr(spi_parameters))
      self.m_spiio.initSpiMaster(spi_parameters)

            
      '''
      check to see that power is appropriate for the target
      the variable voltage supplies the eeprom, which
      can have a voltage range of 3.3v only, or 1.6 to 1.8V
      '''
      fixed=spi_parameters.tgt_v1_fixed
      var=spi_parameters.tgt_v2_variable

      if not self.voltageOK(var, fixed, eepromConfig.vdd):
        print("CONFIGURATION SKIPPED/NOT TESTED")
        continue
      

      if write_data and (not eeprom_unlocked):
        eeprom_unlocked=self.m_eeprom.unlockDevice()
        
      if write_data:
        self.m_eeprom.updateWithinPage(page_address, eeprom.eeprom.EEPROM_PAGE_SIZE, txdata_array)

      if verbose and first_loop:
        self.m_testutil.printArrayHexDump("EEProm (Written) Pattern", txdata_array)

            
      read_commands=[[read_hispeed_data, protocol.HSREAD, "High Speed Read"],
                     [read_single_data, protocol.READ, "Read"],
                     [read_dual_data, protocol.SDOREAD, "Dual Output Read"]]
      
      test_failed=False
      maxloop=4
      for command in read_commands:
      
        for loop in range(maxloop):
          if command[0]==True:
            test_failed=not self.readTest(command[1], command[2], page_address, self.m_eeprom.EEPROM_PAGE_SIZE, txdata_array, verbose)
            if test_failed:
              print("subtest iteration #"+str(loop+1)+" of "+str(maxloop)+" failed")
              break
            elif loop==(maxloop-1):
              print("success: subtest (0x%02x) %s" % (command[1], command[2]))
              
            time.sleep(.5)  #10 ms sleep

        if test_failed:
          break                                                                                 

      if test_failed:
        break

      first_loop=False
    print("Configuration Looptest Complete!")