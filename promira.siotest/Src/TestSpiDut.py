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
      print("Promira fixed voltage (VTGT1,2) is not allowed")
      return True

    elif var==None:
        print("bench supply for eeprom and DUT")
        return True
    elif var==3.3 or (var >= 1.6 and var <=1.8):
      print("eeprom vdd=%fv supplied by Promira" % var)
      return True

    print("configuration and eeprom vdd mismatch")
    return False
  
  def runTest(self):


    txdata_array = self.m_testutil.firstRandomPageArray()
    txdata_count = len(txdata_array)
    

    '''
    flags control test loop contents
    '''
    
    verbose=True
    write_data = False
    read_single_data=False
    read_dual_data=True
    eeprom_unlocked=False

    first_loop=True
    spi_parameters = self.m_config_mgr.firstConfig()

    page_address=spi_parameters.address_base+0x1000
    
    for spi_config in self.m_config_mgr.m_spi_config_list:
    
      self.m_spiio.initSpiMaster(spi_config)
      print(repr(spi_config))
      '''
      testJedec() forces device recognition
      '''
      
      self.m_eeprom.testJedec()
      eepromConfig= self.m_eeprom.m_devconfig
      '''
      check to see that power is appropriate for the target
      the variable voltage supplies the eeprom, which
      can have a voltage range of 3.3v only, or 1.6 to 1.8V
      '''
      fixed=spi_config.tgt_v1_fixed
      var=spi_config.tgt_v2_variable
      

      if not self.voltageOK(var, fixed, eepromConfig.vdd):
        continue
       
      if write_data:
        self.m_eeprom.testNOP()
      
        self.m_eeprom.readStatusRegister()
        
        self.m_eeprom.waitUntilNotBusy()
        
        self.m_eeprom.testJedec()
      

      if write_data and not eeprom_unlocked:
        
        if self.m_eeprom.readBlockProtectBitmap() == False:
          self.m_testutil.fatalError("Protect Bitmap Read Failed")
    
        block_protect_bitmap=self.m_eeprom.getBlockProtectBitmap()
              
        if verbose:
          self.m_testutil.printArrayHexDump("Initial Protect Bitmap Array", block_protect_bitmap)


      
        if self.m_eeprom.globalUnlock() == False:
          self.m_testutil.fatalError("Global Unlock Command Failed")
          
        if self.m_eeprom.readBlockProtectBitmap() == False:
          self.m_testutil.fatalError("Protect Bitmap Read Failed")
          
        self.m_eeprom.getBlockProtectBitmap()
        sum = 0
    
        for entry in block_protect_bitmap:
          sum += entry
      
        eeprom_unlocked= (sum == 0)
           
        if not eeprom_unlocked:
          #self.m_testutil.fatalError("Global Unlock Failed")
          if verbose:
            self.m_testutil.printArrayHexDump("Unlocked Protect Bitmap Array", block_protect_bitmap)
    
          self.m_eeprom.setBlockProtectBitmap(self.m_testutil.zeroedArray(self.m_eeprom.EEPROM_PROTECT_BITMAP_SIZE))
          if verbose:
            self.m_testutil.printArrayHexDump("ZEROED Protect Bitmap Array", block_protect_bitmap)
  
          if ( self.m_eeprom.writeBlockProtectBitmap()
            and self.m_eeprom.readBlockProtectBitmap() ):
            block_protect_bitmap = self.m_eeprom.getBlockProtectBitmap()
            if verbose:
              self.m_testutil.printArrayHexDump("Post Update Protect Bitmap Array", block_protect_bitmap)
          else:
            self.m_testutil.fatalError("block protect bitmap acquisition failed")



      if write_data:
        if verbose:      
          self.m_testutil.printArrayHexDump("Unlocked Protect Bitmap Array", block_protect_bitmap)
        
        self.m_eeprom.updateWithinPage(page_address, eeprom.eeprom.EEPROM_PAGE_SIZE, txdata_array)
        if verbose and not ( read_dual_data or read_single_data):
          self.m_testutil.printArrayHexDump("EEProm Written", txdata_array)

 
            
      if read_dual_data:
        dual_rxdata_array = self.m_testutil.zeroedArray(self.m_eeprom.EEPROM_PAGE_SIZE)
        
        self.m_eeprom.waitUntilNotBusy()
        
        read_length = self.m_eeprom.readDataDual(page_address, self.m_eeprom.EEPROM_PAGE_SIZE, dual_rxdata_array)

        if verbose:
          print("Sector Address %x" % page_address)
          self.m_testutil.printArrayHexDump("EEProm Written", txdata_array)
          self.m_testutil.printArrayHexDump("EEProm Dual-Read", dual_rxdata_array)
          
        if not self.m_testutil.arraysMatch(txdata_array, dual_rxdata_array):
            print("Dual Mode Read comparison fault")



      if read_single_data:      
        rxdata_array = self.m_testutil.zeroedArray(self.m_eeprom.EEPROM_PAGE_SIZE)
        self.m_eeprom.waitUntilNotBusy()
        read_length = self.m_eeprom.readData(page_address, self.m_eeprom.EEPROM_PAGE_SIZE, rxdata_array)


        if verbose:
          print("Sector Address %x" % page_address)
          self.m_testutil.printArrayHexDump("EEProm Written", txdata_array)
          self.m_testutil.printArrayHexDump("EEProm Read", rxdata_array)

        if not self.m_testutil.arraysMatch(rxdata_array, txdata_array):
          print("Single Mode Read compare failed")

      #txdata_array = self.m_testutil.nextRandomPageArray()
      #page_address+=self.m_eeprom.EEPROM_PAGE_SIZE
      time.sleep(2)

    print("Configuration Looptest Complete!")