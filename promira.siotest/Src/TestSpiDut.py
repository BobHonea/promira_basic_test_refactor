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
from eeprom import eepromAPI
import cmd_protocol as protocol
import spi_cfg_mgr as spicfg
import test_utility as testutil
import promactive_msg as pmmsg 
import time
from cmd_protocol import RVCFG
from vernier_histogram import result2DHistogram










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
  m_eepromAPI        = None
  m_instantiator  = None

  
  def __init__(self):
    self.m_testutil     = testutil.testUtil()
    self.m_config_mgr   = spicfg.configMgr()
    self.m_spi_msg      = pmmsg.promactMessages()
    self.m_eepromAPI    = eepromAPI()
    self.m_spiio        = self.m_eepromAPI.getobjectSpiIO()

    self.m_pagesize     = eepromAPI.EEPROM_PAGE_SIZE

    block_protect_bitmap  = pmact.array_u08(18)
    self.m_rxdata_array           = pmact.array_u08(self.m_pagesize)
    self.m_txdata_array           = pmact.array_u08(self.m_pagesize)
    self.m_random_page_array      = pmact.array_u08(self.m_pagesize)
    
    self.m_configVal      = spicfg.configVal()
    return
    


  


#==========================================================================
# FUNCTION (APP)
#==========================================================================
  
  def voltageOK(self, var, fixed, eeprom_vdd):

    if fixed!=None:
      self.m_testutil.bufferDetailInfo("Promira DUT voltage supply (VTGT1,2) is not allowed")
      return True

    elif var==None:
        self.m_testutil.bufferDetailInfo("Bench "+str(eeprom_vdd)+"V power supply required for eeprom")
        return True
      
    elif var==3.3:
      if eeprom_vdd==3.3:
        self.m_testutil.bufferDetailInfo("EEPROM vdd="+str(var)+"V supplied by Promira")
        return True
      
      else:
        self.m_testutil.bufferDetailInfo("EEPROM vdd="+str(eeprom_vdd)+"V, supply by Promira is "+str(var)+"V: MISMATCH")
        return False

    elif eeprom_vdd==1.8:
        if var>=1.6 and var<=1.8:
          self.m_testutil.bufferDetailInfo("EEPROM vdd="+str(eeprom_vdd)+"V, supply by Promira is "+str(var)+"V: OK")
          return True
          
    self.m_testutil.bufferDetailInfo("Promira Supply and EEPROM vdd mismatch")
    return False
  
  
  def writeDevicePattern(self, start_page_address, length, device_byte_size, pattern_array):
    if start_page_address % self.m_eepromAPI.EEPROM_PAGE_SIZE != 0:
      self.m_testutil.fatalError("illegal page address")
    
    if length % self.m_eepromAPI.EEPROM_PAGE_SIZE != 0:
      self.m_testutil.fatalError("illegal page fill length")
      
    start_page=start_page_address/self.m_eepromAPI.EEPROM_PAGE_SIZE
    page_count=length/self.m_eepromAPI.EEPROM_PAGE_SIZE
    
    if start_page+page_count > (device_byte_size/self.m_eepromAPI.EEPROM_PAGE_SIZE):
      self.m_testutil.fatalError("write request too large")
      
    for page in range(page_count):
      page_address=start_page_address+(page * self.m_eepromAPI.EEPROM_PAGE_SIZE)
      self.m_eepromAPI.updateWithinPage(page_address, eepromAPI.EEPROM_PAGE_SIZE, pattern_array)

  
  def readTest(self, read_cmd_byte, cmd_namestring, address, length, pattern_array, verbose):
    rxdata_array = self.m_testutil.zeroedArray(self.m_eepromAPI.EEPROM_PAGE_SIZE)
    self.m_eepromAPI.waitUntilNotBusy()

    if read_cmd_byte==protocol.READ:
      _read_length = self.m_eepromAPI.readData(address, length, rxdata_array)

    if read_cmd_byte==protocol.HSREAD:
      _read_length = self.m_eepromAPI.highspeedReadData(address, length, rxdata_array)

    if read_cmd_byte==protocol.SDOREAD:
      _read_length = self.m_eepromAPI.readDataDual(address, length, rxdata_array)



      
    if not self.m_testutil.arraysMatch(rxdata_array, pattern_array):
        self.m_testutil.bufferDetailInfo("%s comparison fault" % cmd_namestring)
        if verbose:
          self.m_testutil.bufferDetailInfo("Sector Address %x" % address)

          self.m_testutil.printArrayHexDumpWithErrors("EEProm %s" % cmd_namestring, rxdata_array, pattern_array)
          
        return False
    return True
  
  def runTest(self):


    txdata_array = self.m_testutil.firstReferencePageArray()
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
    break_subtest_on_single_read_fail=False
    break_frequency_test_on_subtest_fail=True
    break_trial_on_nopass_frequency=True
    use_auto_vernier=True
    auto_vernier_cycle=5
    auto_vernier_cycle_count=0

    sector_read_count=0
    #first_loop=True
    subtest_loops=10
    
    configOptions=self.m_configVal.getSpiConfigOptions()
    parameter_values  = configOptions.clk_kHz
    parameter_labels  = [ ("%02.3f" % (float(frequency)/1000)) for frequency in configOptions.clk_kHz ]
    parameter_units_label = "MHz"
    data_values       = [ True, False ]
    data_labels       = [ 'Pass', 'Fail'
                         ]
    self.m_histogram=result2DHistogram( parameter_values, parameter_labels, 
                                        parameter_units_label, 
                                        data_values, data_labels)
    
    spi_parameters = self.m_config_mgr.firstConfig()
    self.m_spiio.initSpiMaster(spi_parameters)
    
    

    self.m_testutil.initTraceBuffer(200)
    self.m_testutil.detailTraceOff()
    self.m_testutil.displayTraceOn()
    
    #self.m_spiio.signalEvent()
    #self.m_testutil.fatalError("just because")
          
    '''
    if the test configuration specifies an eeprom configuration,
    set the eeprom configuration to the eeprom api.
    
    the configuration provides configuration in cases that the
    jedec id is unreadable.
    
    '''
    
    if spi_parameters.eeprom_config!=None:
      self.m_eepromAPI.hardSetTgtEEPROM(spi_parameters.eeprom_config)
    
    '''
    testJedec() forces device recognition
    when hard set, this will use the configuration set by
    hardsetTgtEEPROM().    
    '''
    
    self.m_eepromAPI.testJedec()
    eepromConfig= self.m_eepromAPI.m_devconfig
    if self.m_testutil.traceEnabled():
      self.m_testutil.bufferTraceInfo(repr(eepromConfig), True)
    
    mfgrname=eepromConfig.mfgr
    chipname=eepromConfig.chip_type
    memsize_MB=eepromConfig.memsize/(1024*1024)
    self.m_testutil.bufferDetailInfo("EEPROM Type: "+ mfgrname + " "+ chipname, True )
    self.m_testutil.bufferDetailInfo("Memory Size = " + str(memsize_MB) +"   Voltage= "+ str(eepromConfig.vdd)+"V", True)

    if mfgrname=='Micron':
      micronstatus=self.m_eepromAPI.readMicronStatusRegisters()
      self.m_testutil.bufferTraceInfo(repr(micronstatus), True)
      
      dtr_status=not self.m_eepromAPI.dtrStatus()
      dual_status=not self.m_eepromAPI.dualStatus()
      quad_status=not self.m_eepromAPI.quadStatus()
    
      self.m_testutil.bufferDetailInfo("DTR: "+str(dtr_status)+"   Dual I/O: "+str(dual_status)+ "   Quad: "+str(quad_status))
    
    page_address=spi_parameters.address_base+0x1000
    
    '''
    lock printed data up to this point into Trace Buffer
    it will never be flushed.
    '''
    self.m_testutil.protectTraceBuffer()
    #self.m_testutil.traceEchoOn()
    
    read_commands_header=['flag', 'spi_cmd', 'description', 'pass_count','fail_count' ]      
    rdcmds_passndx=3
    rdcmds_failndx=4
    read_commands=[[read_hispeed_data, protocol.HSREAD, "High Speed Read", 0, 0],
                   [read_single_data, protocol.READ, "Read", 0, 0],
                   [read_dual_data, protocol.SDOREAD, "Dual Output Read", 0, 0]]

    while True:
      for spi_parameters in self.m_config_mgr.m_spi_config_list:
        retries=2
        complete=False
        while not complete:        
          try:

            self.m_testutil.traceEchoOff()
            self.m_testutil.flushTraceBuffer()
            self.m_testutil.detailTraceOn()
            self.m_testutil.displayTraceOn()   
      
            self.m_testutil.bufferDetailInfo(repr(spi_parameters))
            
            self.m_spiio.initSpiMaster(spi_parameters)
      
      
      
                  
            '''
            check to see that power is appropriate for the target
            the variable voltage supplies the eeprom, which
            can have a voltage range of 3.3v only, or 1.6 to 1.8V
            '''
            fixed=spi_parameters.tgt_v1_fixed
            var=spi_parameters.tgt_v2_variable
      
            if not self.voltageOK(var, fixed, eepromConfig.vdd):
              self.m_testutil.bufferTraceInfo("CONFIGURATION SKIPPED/NOT TESTED", True)
              continue
            
            self.m_testutil.traceEchoOff()
      
            if write_data and (not eeprom_unlocked):
              eeprom_unlocked=self.m_eepromAPI.unlockDevice()
              
            if write_data:
              self.m_eepromAPI.updateWithinPage(page_address, eepromAPI.EEPROM_PAGE_SIZE, txdata_array)
      
            #if verbose and first_loop:
            #  self.m_testutil.printArrayHexDump("EEProm (Written) Pattern", txdata_array)
      
            
            test_failed=False
            subtest_loops=4
            loop_pass=loop_fail=0
            
            for command in read_commands:
              command[rdcmds_failndx]=command[rdcmds_passndx]=0
            
            for command_ndx in range(len(read_commands)):
              command=read_commands[command_ndx]
              
              for loop in range(subtest_loops):
                if command[0]==True:
                  test_pass=self.readTest(command[1], command[2], page_address, self.m_eepromAPI.EEPROM_PAGE_SIZE, txdata_array, verbose)
    
                  self.m_histogram.addData(spi_parameters.clk_kHz, test_pass)
    
                  if test_pass:
                    command[rdcmds_passndx]+=1
                    loop_pass+=1
                    command[3]+=1
                    
                  if not test_pass:
                    loop_fail+=1
                    command[4]+=1
                    
                    self.m_testutil.bufferDetailInfo("FAILURE @ %d KHz" % (spi_parameters.clk_kHz), False)
                    self.m_testutil.bufferDetailInfo("subtest iteration #"+str(loop+1)+" of "+str(subtest_loops)+" failed")
    
                    if break_subtest_on_single_read_fail:
                      self.m_testutil.bufferDetailInfo("break on test fail")
                      break
    
                  #time.sleep(.001)  #10 ms sleep
      
              if break_subtest_on_single_read_fail or (break_frequency_test_on_subtest_fail and loop_pass==0):
                self.m_testutil.bufferDetailInfo("break on all/single fail")
                break
      
              #time.sleep(.1)

            complete=True
            #first_loop=False
            if break_trial_on_nopass_frequency and loop_pass==0:
              self.m_testutil.bufferDetailInfo("break on all/single fail")
              break

            

          except self.m_spiio.PromiraError as e:
            print(e)
            self.m_testutil.dumpTraceBuffer()
            self.m_spiio.devResetOpen()
            retries-=1
            complete= retries == 0

              
            
      total_pass=0
      total_fail=0
      
      for command in read_commands:
        command_result=" %04d/%04d Pass/Fail %s" %( command[3], command[4], command[2])
        total_pass+=command[3]
        total_fail+=command[4]
        
      run_result="Total Pass Reads = %d     Total Fail Reads = %d" % (total_pass, total_fail)
      
      self.m_testutil.bufferDetailInfo(run_result)  
      self.m_testutil.bufferDetailInfo("Configuration Looptest Complete!")
      
      self.m_histogram.dumpHistogram()

      if use_auto_vernier and auto_vernier_cycle>auto_vernier_cycle_count:
        auto_vernier_cycle_count+=1
        if auto_vernier_cycle==auto_vernier_cycle_count:
          vernier_bucket_values, vernier_bucket_labels=self.m_histogram.refine_buckets()
          if vernier_bucket_values != None:
            self.m_testutil.bufferDisplayInfo("Restarting TestRun / Resetting Bucket Definitions")
            self.m_histogram=result2DHistogram(vernier_bucket_values,
                                               vernier_bucket_labels,
                                               parameter_units_label,
                                               data_values,
                                               data_labels)
            '''
            New Frequency Vernier is determined
            Update the default configuration for frequency vernier
            Regenerate the Spi Parameters Configuration Sets List
            ...continue testing
            '''
            configVal=spicfg.configVal()
            configVal.updateClkKhzList(vernier_bucket_values)
            self.m_config_mgr.genConfigs()
          
          else:
            # retry in cycle counts, try again much later
            auto_vernier_cycle_count=0
          
          
          