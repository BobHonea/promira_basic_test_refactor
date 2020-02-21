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
import collections as coll
from cmd_protocol import RVCFG
#from result_histogram import result2DHistogram
#from error_histogram import parameterizedErrorHistogram
from err_fault_histogram import parameterizedErrorHistogram












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



      
    arrays_match, errors=self.m_testutil.arraysMatch(rxdata_array, pattern_array)
    single_valued_input=False
    
    if not arrays_match:

        self.m_testutil.bufferDetailInfo("%s comparison fault" % cmd_namestring)
        single_valued_input, error_count=self.m_testutil.arraySingleValued(rxdata_array)

        if verbose:
          if single_valued_input:
            self.m_testutil.bufferDetailInfo("rxdata array is single valued")          
          self.m_testutil.bufferDetailInfo("Sector Address %x" % address)

          self.m_testutil.printArrayHexDumpWithErrors("EEProm %s" % cmd_namestring, rxdata_array, pattern_array, verbose)
          
    return arrays_match, errors, single_valued_input


  '''
  A Configuration Set test includes a test of a battery of reads command trials
  A battery of read command trials includes
    1. multiple trials of a single type of read commands
    2. (presently) 3 different types of read command
         (single, high-speed single, dual)

  Failure can be interpreted as:
    1. failure of a sub-battery: data-read-command type
    2. failure of battery:       all data-read-command types
    3. falure of a trial:        all configurations

  Failure Criteria can be:
    1. SEVERE:        any read command test within a subtest/battery fails
    2. STRICT:        most commands of a subtest/battery fail
    3. GENERAL:       all tests of a subtest/battery fail
    
  When Failure can be judged:
    1. SEVERE:        as soon as ANY test-level
    2. STRICT:        as soon as a majority of tests in a level complete
    3. GENERAL:       as soon as all tests in a level complete
  
'''
  
  
  '''
  AUTO VERNIER
  
  After a soak-in period, the initial results of testing can be assessed 
  against clock_kHz frequencies. The set of tested frequencies can be recast
  to eliminate most contiguous failure free low-frequency trials, and most
  100% failed high-frequency trials.
  
  The benefits of Auto Vernier are:
    1.  Exclusion of tests that historically DO NOT FAIL.
    2.  Exclusion of tests that historically DO NOT SUCCEED.
    3.  Retention of a bracketing set of ALWAYS-FAIL and ALWAYS SUCCEED tests.
    4.  FASTER EXECUTION of meaningful subset of Trial.
    5.  Finer granularity of meaningful trial clock frequencies.
    
  The risks of Auto Vernier are:
    1.  Device performance drifts with time/heat/etc
    2.  FAILED/SUCESSFUL frequency ranges change with trial count or temperature
    3.  Changed Results are not viewed due to exclusion from test focus
    
  '''

  CRITERIA_SEVERE=0
  CRITERIA_STRICT=1
  CRITERIA_GENERAL=3
  CRITERIA_LIBERAL=4
  
  #CRITERIA_LIBERAL=4
  
  BREAKTYPE_NONE=0
  BREAKTYPE_SUB_BATTERY=1
  BREAKTYPE_BATTERY=2
  BREAKTYPE_CONFIGURATION=4
  BREAKTYPE_TRIAL=8

  ReadTestControl=coll.namedtuple('ReadTestControl', 
                       'read_single_iowidth'
                      ' read_hispeed_single_iowidth'
                      ' read_dual_iowidth'
                      ' severe strict general liberal'
                      ' configuration_passfail_criteria'
                      ' battery_passfail_criteria'
                      ' sub_battery_passfail_criteria '
                      ' break_none '
                      ' break_sub_battery'
                      ' break_battery'
                      ' break_configuration'
                      ' break_trial'
                      ' break_on_read_fail'
                      ' break_on_sub_battery_fail'
                      ' break_on_battery_fail'
                      ' break_on_configuration_fail'
                      ' break_on_config_set_fail'
                      ' sub_battery_tests_per_battery'
                      ' battery_tests_per_configuration'
                      ' sufficient_command_tests_per_trial'
                      ' use_auto_vernier'
                      ' default_vernier_soak_cycles')
  
  SubtestControl=coll.namedtuple('SubtestControl', 'test_selected test_name command_code test_monitor')
  
  class testMonitor(object):
    def __init__(self, criteria, maximum_trials):
      self.m_testutil=testutil.testUtil()
      
      if  (criteria in [promiraSpiTestApp.CRITERIA_GENERAL, promiraSpiTestApp.CRITERIA_STRICT,
                        promiraSpiTestApp.CRITERIA_SEVERE]
          and maximum_trials>0 ):
        self.m_criteria=criteria
        self.m_maximum_trials=maximum_trials
        self.m_results=[]
      else:
        self.m_testutil.fatalError("testMonitor intiialization")
    
    def reset(self):
      self.m_results=[]
        
    def enterResult(self, pass_fail):
      self.m_results.append(pass_fail)
      
    def passCount(self):
      return(self.m_results.count(True))
    
    def failCount(self):
      return(self.m_results.count(False))
    
    def resultCount(self):
      return(len(self.m_results))
    
    def maxTrials(self):
      return self.m_maximum_trials
    
    def testComplete(self):
      return len(self.m_results) == self.m_maximum_trials
    
    def passCriteriaMet(self):
      if self.m_criteria == promiraSpiTestApp.CRITERIA_STRICT:
        if self.resultCount() > (self.m_maximum_trials+1)/2:
          proportion=float(self.failCount())/self.resultCount()
          return (proportion > 0.5)
    
      elif self.m_criteria == self.criteria_SEVERE:
        return self.resultCount() > 0 and self.failCount() == 0
        
      elif self.m_criteria == promiraSpiTestApp.CRITERIA_GENERAL:
        if self.resultCount() == self.m_maximum_trials: 
          return self.failCount() < self.resultCount()
        
      return False
    
    def failCriteriaMet(self):
      if self.m_criteria == promiraSpiTestApp.CRITERIA_STRICT:
        return self.failCount() > int(self.m_maximum_trials+1)/2
      
      elif self.m_criteria == promiraSpiTestApp.CRITERIA_GENERAL:
        if self.resultCount() == self.m_maximum_trials:
          return self.failCount() == self.resultCount()
         
      elif self.m_criteria == promiraSpiTestApp.CRITERIA_SEVERE:
          return self.failCount() > 0
        
      return False
    

  
    
  def runTest(self):
    


    enable_single_iowidth_read    = True
    enable_hs_single_iowidth_read = True
    enable_dual_iowidth_read      = True
  
    read_enables = [ enable_single_iowidth_read, enable_hs_single_iowidth_read, enable_dual_iowidth_read]

    control=self.ReadTestControl(
      read_single_iowidth             = enable_single_iowidth_read,
      read_hispeed_single_iowidth     = enable_hs_single_iowidth_read,
      read_dual_iowidth               = enable_dual_iowidth_read,
      severe                          = self.CRITERIA_SEVERE,
      strict                          = self.CRITERIA_STRICT,
      general                         = self.CRITERIA_GENERAL,
      liberal                         = self.CRITERIA_LIBERAL,
      configuration_passfail_criteria = self.CRITERIA_GENERAL,
      battery_passfail_criteria       = self.CRITERIA_STRICT,
      sub_battery_passfail_criteria   = self.CRITERIA_STRICT,
      break_none                      = self.BREAKTYPE_NONE,
      break_sub_battery               = self.BREAKTYPE_SUB_BATTERY,
      break_battery                   = self.BREAKTYPE_BATTERY,
      break_configuration             = self.BREAKTYPE_CONFIGURATION,
      break_trial                     = self.BREAKTYPE_TRIAL,
      break_on_read_fail              = [self.BREAKTYPE_NONE],
      break_on_sub_battery_fail       = [self.BREAKTYPE_NONE],
      break_on_battery_fail           = [self.BREAKTYPE_NONE],
      break_on_configuration_fail     = [self.BREAKTYPE_NONE],
      break_on_config_set_fail        = [self.BREAKTYPE_NONE],
      sub_battery_tests_per_battery   = read_enables.count(True),
      battery_tests_per_configuration = 3,
      sufficient_command_tests_per_trial = 50000,
      use_auto_vernier                = False,
      default_vernier_soak_cycles     = 10  )


    
     
    txdata_array = self.m_testutil.firstReferencePageArray()
    _txdata_count = len(txdata_array)
    
    self.m_testutil.printArrayHexDump("Reference Array", txdata_array, True)

    '''
    flags control test loop contents
    '''
    
    verbose=True
    write_data = False
    self.m_single_valued_failure=0
    
    eeprom_unlocked=False

    auto_vernier_cycle_count=0

    
    configOptions=self.m_configVal.getSpiConfigOptions()
    
    parameter_values  = configOptions.clk_kHz
    parameter_labels  = [ ("%06.3f" % (float(frequency)/1000)) for frequency in configOptions.clk_kHz ]
    parameter_units_label = "MHz"
    data_values       = [ True, False ]
    data_labels       = [ 'Pass', 'Fail']
    '''
    self.m_histogram=result2DHistogram( parameter_values, parameter_labels, 
                                        parameter_units_label, 
                                        data_values, data_labels)
    '''

    
    error_buckets=[0, 1, 4, 8, 16, 32, 64, 128, 256, 257 ]
    error_bucket_labels=[ "%03d" % error for error in error_buckets]
    error_units_label = "Error"

    self.m_histogram=parameterizedErrorHistogram(
                                        parameter_values,
                                        parameter_labels, 
                                        parameter_units_label, 
                                        data_values,
                                        data_labels,
                                        error_buckets)
    
    spi_parameters = self.m_config_mgr.firstConfig()
    self.m_spiio.initSpiMaster(spi_parameters)
    
    self.m_testutil.initTraceBuffer(200)
    self.m_testutil.traceEnabled()
    self.m_testutil.detailTraceOn()
    self.m_testutil.displayTraceOn()
    self.m_testutil.openLogfile("/usr/local/google/home/honea/results")
    self.m_testutil.initLogfileBuffer(1000)
    self.m_testutil.enableLogfile()
    #self.m_testutil.detailEchoOn()
  
    
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
    self.m_testutil.traceEchoOn()
  
  
  
  
    
    
    hispeed_control     = self.SubtestControl(test_selected=control.read_hispeed_single_iowidth,
                                              command_code=protocol.HSREAD, test_name="Highspeed Read",
                                              test_monitor=self.testMonitor(control.sub_battery_passfail_criteria,
                                              control.sub_battery_tests_per_battery))

    read_hispeed_control= self.SubtestControl(test_selected=control.read_single_iowidth,
                                              command_code=protocol.READ, test_name="Read", 
                                              test_monitor=self.testMonitor(control.sub_battery_passfail_criteria,
                                              control.sub_battery_tests_per_battery))
    
    read_dual_control   = self.SubtestControl(test_selected=control.read_dual_iowidth,
                                              command_code=protocol.SDOREAD, test_name="Dual Output Read", 
                                              test_monitor=self.testMonitor(control.sub_battery_passfail_criteria,
                                              control.sub_battery_tests_per_battery))
      
      
    '''
    pre-select command controls / command set to be tested
    '''  
    subtest_set       = [hispeed_control, read_hispeed_control, read_dual_control ]
    battery_commands  = []
    
    for subtest in subtest_set:
      if subtest.test_selected==True:
        battery_commands.append(subtest)


    trial_monitor=self.testMonitor(self.CRITERIA_GENERAL, control.sufficient_command_tests_per_trial)
    
    while not trial_monitor.testComplete():
      '''
      Test all configurations
      '''
  

      # trial inner-loop
      config_set_monitor=self.testMonitor(self.CRITERIA_GENERAL, len(self.m_config_mgr.m_spi_config_list))
      config_list=self.m_config_mgr.m_spi_config_list
      for spi_parameters in config_list:
        
        '''
        Test one configuration
        '''
        # configuration inner loop
        #self.m_testutil.bufferDisplayInfo("Testing config #%03d of %03d" % (config_list.index(spi_parameters), len(config_list)) )
        retries=2
        one_config_test_complete=False
        while not one_config_test_complete: 
          #configuration test loop       
          try:

            # configuration test try 
            self.m_testutil.traceEchoOff()
#            self.m_testutil.flushTraceBuffer()
#            self.m_testutil.detailTraceOn()
#            self.m_testutil.displayTraceOn()   
      
            self.m_testutil.bufferDetailInfo(repr(spi_parameters))
            
            self.m_spiio.initSpiMaster(spi_parameters)
            time.sleep(.01)
            clock_kHz=spi_parameters.clk_kHz
      
      
      
                  
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
      
                        
            '''
            Test Battery of Read Commands @ Configuration
            '''
            test_battery_monitor=self.testMonitor(control.battery_passfail_criteria, control.battery_tests_per_configuration)
            while not test_battery_monitor.testComplete():
              
              #battery test level
              for sub_battery in battery_commands:

                # sub-battery test level
                subtest_command=sub_battery.command_code
                subtest_monitor=sub_battery.test_monitor
                subtest_monitor.reset()
                subtest_name=sub_battery.test_name
                '''
                Test Sub-Battery of Read Commands
                '''
                
                while not subtest_monitor.testComplete():
                  #sub-battery subtest test level
                  test_pass, errors, single_valued =self.readTest( subtest_command,
                                                                   subtest_name,
                                                                   page_address,
                                                                   self.m_eepromAPI.EEPROM_PAGE_SIZE,
                                                                   txdata_array,
                                                                   False)
                  
                  subtest_monitor.enterResult(test_pass)
                  self.m_histogram.addData(spi_parameters.clk_kHz, test_pass, errors, single_valued)
                  
                  self.m_testutil.bufferDetailInfo("FAILURE @ %d KHz" % (spi_parameters.clk_kHz), False)
                  self.m_testutil.bufferDetailInfo("subtest iteration #"+str(subtest_monitor.resultCount())+" of " +
                                                   str(subtest_monitor.maxTrials())+" failed")
  
                  
                  if subtest_monitor.failCriteriaMet():
                    self.m_testutil.bufferDetailInfo("break on Sub-Battery test failure: %s " % sub_battery.test_name)
                    break
    
                  #time.sleep(.001)  #10 ms sleep

              # battery test level
                test_battery_monitor.enterResult(subtest_monitor.passCriteriaMet())
                if test_battery_monitor.failCriteriaMet():
                  self.m_testutil.bufferDetailInfo("Break on Battery Test Fail")
                  break
      
              #time.sleep(.001)
  
            one_config_test_complete=True
            #first_loop=False
            

            config_set_monitor.enterResult(test_battery_monitor.passCriteriaMet())
            if config_set_monitor.failCriteriaMet():
              self.m_testutil.bufferDetailInfo("Break On Configuration Test Fail")
              break

            

          except self.m_spiio.PromiraError as e:
            print(e)
            self.m_histogram.addFault(spi_parameters.clk_kHz, e[0], e[1])
            self.m_testutil.dumpTraceBuffer()
            self.m_spiio.devResetOpen()
            retries-=1
            one_config_test_complete= retries == 0

              
        if config_set_monitor.failCriteriaMet():
          self.m_testutil.bufferDetailInfo("Break on Configuration Set Test Fail")    
     
      self.m_testutil.bufferDetailInfo("Configuration Looptest Complete!")

      if self.m_single_valued_failure>0:
        self.m_testutil.bufferDetailInfo("Total Single Valued Failures = %s" % self.m_single_valued_failure, True)

      self.m_histogram.dumpHistogram()


      if control.use_auto_vernier and auto_vernier_cycle_count>control.auto_vernier_soak_cycles:
        auto_vernier_cycle_count+=1
        if control.auto_vernier_soak_cycles==auto_vernier_cycle_count:
          min_kHz_vernier_value=25000
          vernier_bucket_values, vernier_bucket_labels=self.m_histogram.refine_buckets(min_kHz_vernier_value)
          if vernier_bucket_values != None:
            self.m_testutil.bufferDisplayInfo("Restarting TestRun / Resetting Bucket Definitions")
            self.m_histogram=parameterizedErrorHistogram(
                                               vernier_bucket_values,
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
            self.m_config_mgr.genConfigs(True)
          
          else:
            # retry in cycle counts, try again much later
            auto_vernier_cycle_count=0
            
    self.m_testutil.closeLogFile()
          
          
          