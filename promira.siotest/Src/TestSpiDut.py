"""Py test that does a test function"""
from __future__ import division, with_statement, print_function
#import usertest
import promact_is_py as pmact
import promira_py as pm
import eeprom
import test_utility as utility
import spi_io
import spi_config_mgr as cfgmgr
import promactive_msg as spimsg 
import cmd_protocol as protocol
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

import array
import sys
import time



#==========================================================================
# CONSTANTS
#==========================================================================
BUFFER_SIZE = 65535
INTERVAL_TIMEOUT = 500



#==========================================================================
# FUNCTIONS
#==========================================================================



def fatalError(reason):
  print("Fatal Error : "+reason)
  sys.exit()

class promiraTestApp(usertest.SwUserTest):
  """Unit test template"""
  
    
  m_bus_type = BUSTYPE_UNKNOWN
  m_eepromStatus = None

  m_rxdata_array = pmact.array_u08(m_pkgsize)
  m_txdata_array = pmact.array_u08(m_pkgsize)

  m_random_page_array = pmact.array_u08(EEPROM_PAGE_SIZE)


      

  
  def __init__(self):
    self.m_util     = utility.testUtil()
    self.m_spi_msg  = spimsg.promact_messages()
    self.m_eeprom   = eeprom.eeprom()
    
    self.m_spiio        = spi_io.spiIO(spi_io.spiIO.spi_config_00)
    self.m_config_mgr   = spicfg.configMgr()
    self.m_spi_protocol = protocol.spi_transaction()
    
    

  def apiIfError(self, result_code):
    if result_code == pmact.PS_APP_OK or result_code>0:
      return False 
    
    for error_id in self.PROMIRA_ERRORS:
      if error_id[0] == result_code:
        print(error_id[1])
        return True
    
    print("unspecified API error")
    return True
  


#==========================================================================
# FUNCTION (APP)
#==========================================================================

    
  def eepromSpiTestJedec(self):
    id_array=pmact.array_u08(3)
    result_length = self.spiMasterMultimodeCmd(self.SPICMD_JEDEC_ID, None, 3, id_array)
    if result_length != 3:
      print("error: jedec read")
      sys.exit()

    jedec_id = [0xBF, 0x26, 0x42]
    for index in range(len(jedec_id)):
      if jedec_id[index] != id_array[index]:
        return False
    
    return True
  
  

  
  def runTest(self, busType):

    
    if not self.m_spiio.discoverDevice():
      fatalError("Primira Spi Platform Connection Failure")
    

    self.m_spiio.initSpiMaster()

    self.m_txdata_array = self.m_util.nextRandomPageArray()
      
    self.m_txdata_array = self.random_u08_array(self.m_pkgsize)
    txdata_count = self.m_pkgsize


    '''
    flags control test loop contents
    '''
    
    write_data = True
    read_single_data=False
    read_dual_data=True
    eeprom_unlocked=False
    
    while True:
      if write_data:
        self.m_txdata_array = self.next_random_packet_array()
        
      self.eepromSpiTestNOP()
      self.eepromSpiWaitUntilNotBusy()
      self.eepromSpiTestJedec()
      '''
      #self.eepromSpiTestQuadJedec()

      '''
      
      if not eeprom_unlocked:
        if self.eepromSpiReadProtectBitmap() == False:
          fatalError("Protect Bitmap Read Failed")
          
        self.printArrayHexDump("Initial Protect Bitmap Array", self.m_eeprom_protect_bitmap)
        
        if self.eepromSpiGlobalUnlock() == False:
          fatalError("Global Unlock Command Failed")
          
        if self.eepromSpiReadProtectBitmap() == False:
          fatalError("Protect Bitmap Read Failed")
  
        sum = 0
    
        for entry in self.m_eeprom_protect_bitmap:
          sum += entry
      
        eeprom_unlocked= (sum == 0)
           
        if not eeprom_unlocked:
          #fatalError("Global Unlock Failed")
          self.m_util.printArrayHexDump("Unlocked Protect Bitmap Array", self.m_eeprom_protect_bitmap)
    
          self.eeprom.m_eeprom_protect_bitmap=self.zeroed_u08_array(18)  
          self.m_util.printArrayHexDump("ZEROED Protect Bitmap Array", self.m_eeprom_protect_bitmap)
  
          if self.eeprom.eepromWriteProtectBitmap():
            self.m_util.printArrayHexDump("Post-Write Protect Bitmap Array", self.m_eeprom_protect_bitmap)
    
          protect_array = self.eeprom.eepromSpiReadProtectBitmap()
          self.m_util.printArrayHexDump("Protect Array", self.m_eeprom_protect_bitmap)
      
      



      if write_data:      
        self.m_util.printArrayHexDump("Unlocked Protect Bitmap Array", self.m_eeprom_protect_bitmap)
        
        txdata_array = self.m_util.nextRandomPageArray()
        self.m_eeprom.eepromSpiUpdateWithinPage(0x1000, self.EEPROM_PAGE_SIZE, txdata_array)
        if not ( read_dual_data or read_single_data):
          self.m_util.printArrayHexDump("EEProm Written", txdata_array)

 
            
      if read_dual_data:
        dual_rxdata_array = self.m_util.zeroedArray(self.EEPROM_PAGE_SIZE)
        self.m_eeprom.eepromSpiWaitUntilNotBusy()
        read_length = self.m_eeprom.eepromSpiReadDataDual(0x1000, self.EEPROM_PAGE_SIZE, dual_rxdata_array)

        if write_data:
          self.printArrayHexDump("EEProm Written", txdata_array)

        self.printArrayHexDump("EEProm Dual-Read", dual_rxdata_array)

        if write_data: 
          for index in range(self.EEPROM_PAGE_SIZE-4, self.EEPROM_PAGE_SIZE):
            if dual_rxdata_array[index] != txdata_array[index]:
              print("write/read/compare fault at offset %02X " % index)



      if read_single_data:      
        rxdata_array = self.m_util.zeroedArray(self.m_eeprom.EEPROM_PAGE_SIZE)
        self.m_eeprom.eepromSpiWaitUntilNotBusy()
        read_length = self.m_eeprom.eepromSpiReadData(0x1000, self.m_eeprom.EEPROM_PAGE_SIZE, rxdata_array)

        if write_data:
          self.m_util.printArrayHexDump("EEProm Written", txdata_array)

        self.m_util.printArrayHexDump("EEProm Read", rxdata_array)

        if self.m_util.cmpArray(rxdata_array, txdata_array):
          print("write/read compare failed)

      
      time.sleep(2)

#    self.run_test_core()  
    self.m_spiio.closeSpiMaster()
