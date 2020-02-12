
import sys
import collections as coll
import promact_is_py as pmact
import promira_py as pm
import promactive_msg as pm_msg
import array

import cmd_protocol as protocol
import test_utility as testutil



#from spi_cfg_mgr import configMgr





class spiIO:
  
    
  m_ss_mask         = None
  m_device          = None
  m_spi_bitorder    = None
  m_devices         = None
  m_device_ids      = None
  m_device_ips      = None
  m_device_status   = None

  
  m_spi_clock_khz   = None
  m_spi_clock_mode  = None
  m_spi_ss_polarity = None
  
  
  m_spi_configuration = None
  m_spi_transaction = None
  m_queue           = None
  m_channel_handle  = None
  m_app_conn_handle = None
  m_app_selection   = None
  m_psp_handle              = None
  m_app_name        = "com.totalphase.promact_is"
  m_promira_open    = None
  m_device_ipstring = None
  _instance         = None
  
  
  '''
  Custom Exception for Promira Serial Platform Errors
  '''  
  class PromiraError(Exception): 
    
      # Constructor or Initializer 
      def __init__(self, value): 
          self.value = value 
    
      # __str__ is to print() the value 
      def __str__(self): 
          return(repr(self.value)) 
      
  
  def __new__(cls):
    if cls._instance is None:
        print('Creating the SpiIO object')
        cls._instance = super(spiIO, cls).__new__(cls)        
        cls.m_pm_msg   = pm_msg.promactMessages()
        cls.m_testutil= testutil.testUtil()    
        #self.m_configMgr  = configMgr()
        
        cls.m_ss_mask = 0x1
        cls.m_device = None
        cls.m_devices    = pmact.array_u16(4)
        cls.m_device_ids = pmact.array_u32(4)
        cls.m_device_ips = pmact.array_u32(4)
        cls.m_device_status = pmact.array_u32(4)
    
        cls.m_spi_configuration = None #cls.m_configMgr.firstConfig()
        cls.m_timeout_ms = 1000  # arbitrary 10 second value 
    
        cls.discoverDevice(cls)
        cls.m_spi_initialized = False
        return cls._instance

    
  def selectSpiConfig(self, index=0):
    pass

 
 
  def discoverDevice(self, serial_number=None):
    self.m_port = 0  # default port for a single promira device

    return_tuple = pm.pm_find_devices_ext(self.m_device_ips, self.m_device_ids, self.m_device_status)
    device_count = return_tuple[0]
    if (device_count >= 1):
      self.m_device_ips = return_tuple[1]
      self.m_devices = return_tuple[2]
      self.m_device_ids = return_tuple[3]
      print("device_count:" + str(device_count))
      self.m_device_ipString=self.m_testutil.ipString(self.m_device_ips[0])
      return True
    
    return False
    

 
  '''
  init_spi_master()
  
    creates a connection and connection handle for session with
    Promira Serial Platform.
    
    intializes static SPI parameters (rarely change during session)
  
  '''
  
  def getAdapterIP(self):
    return self.m_device_ipString
  
  '''
  signalEvent() 
  .............causes a unique event to occur on the SPI Bus
  this event is one that WILL NOT occur during normal operation
  this event can be interpreted by test equipment as a synchronization
  point to perform a test or display operation (dump trace, etc).
  '''
 
  m_in_signal_event=False
  
  def signalEvent(self):
    if self.m_in_signal_event:
      return
    
    #signal_ss_polarity  = (self.m_spi_ss_polarity) &0xf    
    data_out=pmact.array_u08(1)
    data_out[0]=0xAA
    #invert chip select polarity, send a byte
    retval=pmact.ps_spi_configure( self.m_channel_handle,
                                   self.m_spi_clk_mode, 
                                   self.m_spi_bit_order, 
                                   self.m_spi_ss_polarity)

    signal_queue = pmact.ps_queue_create( self.m_app_conn_handle,
                                                  pmact.PS_MODULE_ID_SPI_ACTIVE)
    pmact.ps_queue_clear(signal_queue)
    pmact.ps_queue_spi_oe(signal_queue, 0x01)
    pmact.ps_queue_spi_write_word(signal_queue, protocol.SPIIO_SINGLE, 8, 10, 0xAA)
    pmact.ps_queue_spi_oe(signal_queue, 0x00)

        
    status_collect, _dc = pmact.ps_queue_submit(signal_queue, self.m_channel_handle, pmact.PS_MODULE_ID_SPI_ACTIVE)
    self.m_in_signal_event=True
    collect_length, collect_buf, _fatal_error = self.procDevCollect(status_collect)
    pmact.ps_queue_destroy(signal_queue)
    self.m_in_signal_event=False
    

          
  def initSpiMaster(self, parameters):
    # (configVal.spiConfiguration)
    self.m_spi_parameters   = parameters
    self.m_spi_clk_kHz      = self.m_spi_parameters.clk_kHz
    self.m_spi_clk_mode     = parameters.clk_mode
    self.m_spi_ss_polarity  = parameters.ss_polarity
    self.m_spi_bit_order    = parameters.bit_order
    self.m_spi_address_base = parameters.address_base
    self.m_spi_tgt_v1_fixed = parameters.tgt_v1_fixed
    self.m_spi_tgt_v2_var   = parameters.tgt_v2_variable

    if self.m_promira_open != True:    
      self.devOpen(self.m_device_ipString)
      self.m_promira_open=True
      
    self.m_app_selection = pmact.ps_app_configure(self.m_channel_handle, pmact.PS_APP_CONFIG_SPI)
    
    self.m_testutil.bufferDetailInfo("Promira channel_handle = %d" % self.m_channel_handle)
        
    if (self.m_app_selection != pmact.PS_APP_CONFIG_SPI):
      self.m_testutil.bufferDisplayInfo("promira app selection fail: should be=%d   was=%d" % 
                                        (pmact.PS_APP_CONFIG_SPI, self.m_app_selection))
      raise self.PromiraError("Promira App configuration Fault")
    
    # Power the target device with none, one or two power sources
    self.setTargetpower(self.m_spi_tgt_v1_fixed, self.m_spi_tgt_v2_var)

    pmact.ps_spi_bitrate(self.m_channel_handle, self.m_spi_clk_kHz)
    
    #configure static spi parameters
    retval=pmact.ps_spi_configure( self.m_channel_handle,
                            self.m_spi_clk_mode, 
                            self.m_spi_bit_order, 
                            self.m_spi_ss_polarity)
    
    self.m_spi_initialized=True
    

 
    return
  
  '''
  setTargetPower
  
    The Promira Serial Platform Adapter permits setting two different
    power sources:
      fixed (pins 2, 4)
      variable (level-shift-able) (pins 22, and 24).
      
    The fixed pins may be set to either 3.3 or 5.0 volts.
    the variable source may be set to a single voltage in the range between
    0.9 and 3.45 volts.
    
    based on the expressed power requirements, program the Adapter.
  '''

  def setTargetpower(self, vtgt1_setting, vtgt2_variable_setting):
    values=[3.3, 5.0]
    fixed_codes=[pmact.PS_PHY_TARGET_POWER_TARGET1_3V, pmact.PS_PHY_TARGET_POWER_TARGET1_5V]
    fixed_code=variable_voltage=None
    
    if vtgt1_setting==None and vtgt2_variable_setting==None:
      # No power supplied
      pmact.ps_phy_target_power(self.m_channel_handle, pmact.PS_PHY_TARGET_POWER_NONE)
      return
    
    else:
      if vtgt1_setting!=None:
        # validate 
        if vtgt1_setting in values:
          index=values.index(vtgt1_setting)
          fixed_code=fixed_codes[index]
        else:
          self.m_testutil.fatalError("unsupported tgt1 voltage")

      if vtgt2_variable_setting!=None:
        if (type(vtgt2_variable_setting)!=float  or
          vtgt2_variable_setting < 0.9 or
          vtgt2_variable_setting > 3.45 ):
          self.m_testutil.fatalError("unsupported variable voltage setting")
        else:
          variable_voltage=vtgt2_variable_setting
          
      if variable_voltage != None: 
        pmact.ps_phy_level_shift(self.m_channel_handle, variable_voltage)
        pmact.ps_phy_target_power(self.m_channel_handle, pmact.PS_PHY_TARGET_POWER_TARGET2)
        
      if fixed_code != None:
        pmact.ps_phy_target_power(self.m_channel_handle, fixed_code)
        
      
      if fixed_code!=None and variable_voltage!=None:
        pmact.ps_phy_target_power(self.m_channel_handle, pmact.PS_PHY_TARGET_POWER_BOTH)
        pass

      return
 
  
  
  
  def devOpen (self, ip):
      self.m_psp_handle = pm.pm_open(ip)
      if self.m_psp_handle <= 0:
          print("Unable to open Promira platform on %s" % ip)
          print("Error code = %d" % self.m_psp_handle)
          sys.exit()
  
      ret = pm.pm_load(self.m_psp_handle, self.m_app_name)
      if ret < 0:
          print("Unable to load the application(%s)" % self.m_app_name)
          print("Error code = %d" % ret)
          sys.exit()
  
      self.m_app_conn_handle = pmact.ps_app_connect(ip)
      if self.m_app_conn_handle <= 0:
          print("Unable to open the application on %s" % ip)
          print("Error code = %d" % self.m_app_conn_handle)
          sys.exit()
  
      self.m_channel_handle = pmact.ps_channel_open(self.m_app_conn_handle)
      if self.m_channel_handle <= 0:
          print("Unable to open the channel")
          print("Error code = %d" % self.m_channel_handle)
          sys.exit()
  
      return self.m_psp_handle, self.m_app_conn_handle, self.m_channel_handle
  
  
  '''
  closeSpiMaster()
  
    release the SPI connection and app handles.
    release any other app/connection resource reservations
    
  '''
     
  def devClose (self):
      pmact.ps_channel_close(self.m_channel_handle)
      pmact.ps_app_disconnect(self.m_app_conn_handle)
      pm.pm_close(self.m_psp_handle)

  def devResetOpen(self):
    self.devClose()
    self.devOpen(self.m_device_ipString)
    
  def closeSpiMaster(self):
    self.devClose()


  debug_devCollect = True
  def procDevCollect (self, collect):

    response_length=0
    fatal_error=False
    fatal_errmsg=None
    fatal_t=None
    
    '''
    collect intermediate results until:
      No More Cmds Uncollected
      
      response array is a catenation of an input length byte,
      and all received input bytes from queued command reads
      '[n, byte0, byte1, ..., byte n-1]
      
      if nothing received, response is 1 byte array '[0]'
      
    '''
    while True:
        t, _length, result = pmact.ps_collect_resp(collect, 1000)

        if self.debug_devCollect:
          #****DEBUG****
          found, resp_msg=self.m_pm_msg.getResponseMessage(t)
          if found:
            self.m_testutil.bufferDetailInfo("in devCollect(): %s" % resp_msg)
          else:
            result_msg=self.m_pm_msg.getResultString(t)
            self.m_testutil.bufferDetailInfo("in devCollect(): %s" % result_msg )
        
        if t == pmact.PS_APP_NO_MORE_CMDS_TO_COLLECT:
          break
        
        if t < 0:
          fatal_error=True
          return None, None, fatal_error
          
        if t == pmact.PS_SPI_CMD_READ:
            _ret, _word_size, buf = pmact.ps_collect_spi_read(collect, result)
            if self.debug_devCollect:
              input_msg="PS_SPI_CMD_READ len: "+str(_ret)+"  "+str(type(buf))
              self.m_testutil.bufferDetailInfo(input_msg)
            response_length+= len(buf)
            #response_buf += buf
    
#    return response_length, response_buf
    if buf==None:
      return _ret, buf, fatal_error


    return _ret, buf, fatal_error
  
  def devCollect(self, collect):
    self.m_testutil.bufferDetailInfo("in devCollect(): collect handle = %d" % collect)
    
    _ret, buf, fatal_error = self.procDevCollect(collect)
    
    if fatal_error:
      #self.signalEvent()
      #self.m_testutil.fatalError("Error In DevCollect")
      raise self.PromiraError("Error In DevCollect")
    return _ret, buf
  

  '''
  spiMasterMultlimodeCmd( spi_cmd, address, data_length, data_buffer )
    on read commands, the buffer presented will be returned with (any) received data
    
  RETURN
    tuplet:  ( Success(T/F), data transfer length/None, data transfer array/None)
  '''
 
  m_start_busytest_queue=None
  m_continue_busytest_queue=None
  
  def buildBusyTestQueues(self, read_status_cmd):
    
      read_status=pm.array_u08(1)
      read_status[1]=read_status_cmd
      
      '''
      Start Busy Test
        this instruction queue request the status register
      '''
      start_busytest_queue = pmact.ps_queue_create(self.m_app_conn_handle,
                                          pmact.PS_MODULE_ID_SPI_ACTIVE)
      pmact.ps_queue_clear(start_busytest_queue)
      pmact.ps_queue_spi_oe(start_busytest_queue, self.m_ss_mask)
      pmact.ps_queue_spi_write(start_busytest_queue, protocol.SPIIO_SINGLE, 8, 1, read_status )
      pmact.ps_queue_spi_write_word(start_busytest_queue, protocol.SPIIO_SINGLE, 8, 1, 0)
      
      '''
      continue_busytest_queue
        this instruction queue re-reads the status register
        it MUST be committed AFTER a start_busytest_queue queue
      '''
      cont_busytest_queue = pmact.ps_queue_create(self.m_app_conn_handle,
                                          pmact.PS_MODULE_ID_SPI_ACTIVE)
      pmact.ps_queue_clear(cont_busytest_queue)
      pmact.ps_queue_spi_oe(cont_busytest_queue, 1)
      pmact.ps_queue_spi_write(cont_busytest_queue, protocol.SPIIO_SINGLE, 8, 1, read_status )
      
 
  SpiResult=coll.namedtuple('SpiResult', 'success xfer_length xfer_array')
  
  def getBusyTestQueues(self, read_status_cmd):
    if self.m_start_busytest_queue==None or self.m_continue_busytest_queue==None:
      self.buildBusyTestQueues(read_status_cmd)


  def spiMasterMultimodeCmd(self,
                                spi_cmd,
                                address=None,
                                data_length=None,
                                data_buffer=None): 
    # -> self.SpiResult


    def submitQueue(queue_handle, channel_handle, ctrlID):
      self.m_testutil.bufferDetailInfo(" queue_handle %d ; channel_handle %d ; ctrlID %d" 
                                        % (queue_handle, channel_handle, ctrlID))
      collect, _dc = pmact.ps_queue_submit(queue_handle, channel_handle, ctrlID)
      if collect < 0:
        errmsg="SubmitQueue Error %d: %s" % (collect, self.m_pm_msg.apiIfError(collect))
        raise self.PromiraError(errmsg)

      return collect


      
    if self.m_spi_initialized != True:
      self.m_testutil.fatalError("attempt to transact on uninitialized SPI bus")
        
    cmd_byte=spi_cmd[0]
    cmd_spec=protocol.precedentCmdSpec(spi_cmd)
    spi_session=protocol.spiTransaction(spi_cmd, cmd_spec)
    spi_session.setInitialPhase()
    collect = None
    toggle_select_after_wren=True
    
    
    #****DEBUG****
    if self.debug_devCollect:
      cmd_msg="cmd_byte= %02x" % cmd_byte
      if self.m_testutil.traceEnabled():
        self.m_testutil.bufferDetailInfo(cmd_msg)
        self.m_testutil.bufferDetailInfo(repr(spi_session.m_spi_phases))
      else:
        print(cmd_msg)
    #****DEBUG****
    '''
    Initialize the session queue for all phases of this SPI Command.
    '''
    session_queue = pmact.ps_queue_create(self.m_app_conn_handle,
                                          pmact.PS_MODULE_ID_SPI_ACTIVE)
    pmact.ps_queue_clear(session_queue)
    pmact.ps_queue_spi_oe(session_queue, 1)
    pmact.ps_queue_spi_ss(session_queue, self.m_ss_mask)


    '''
    enqueue WREN (write enable)
    ...when WREN is required for data and register write operations
    TODO: this is expedient, but should be in the eeprom application
    layer of code, rather than in the spi transaction layer.

    toggle chip select after wren send to enact it for the following
    of the enqueued writes
    '''
    
    

    
    
    '''
    process fast busy_wait if intrinsic
      instructions for initial status read and follow-on reads
      are in built-once and cached queues
    '''
    
    if spi_session.isBusyPhase():
      slave_busy=True
      read_status = array.array('B', [protocol.RDSR])
      first_pass=True
      
      start_queue, continue_queue=self.getBusyTestQueues(read_status)
      
      while slave_busy:
        if first_pass:
          status_collect = submitQueue(start_queue, self.m_channel_handle, pmact.PS_MODULE_ID_SPI_ACTIVE)
          collect_length, collect_buf = self.devCollect(status_collect)
        else:
          status_collect = submitQueue(continue_queue, self.m_channel_handle, pmact.PS_MODULE_ID_SPI_ACTIVE)
          collect_length, collect_buf = self.devCollect(status_collect)
          
        status=collect_buf[0]
        slave_busy = (status & 1 == 1)
      
      spi_session.nextSpiPhase()  
    
    '''
    process write enable command if intrinsic
      instructions are emitted into the general session queue
    '''
    
    if spi_session.isWrenPhase()==True:
      data_out = array.array('B', [protocol.WREN])
      pmact.ps_queue_spi_write(session_queue, protocol.SPIIO_SINGLE, 8, 1, data_out )

      
      if toggle_select_after_wren:
        '''
        optionally toggle chip select after wren
        spend some clock cycles to permit the slave to process WREN cmd
        before continuing with re-select
        '''
        pmact.ps_queue_spi_ss(session_queue, 0)
        #pmact.ps_queue_spi_delay_ns(session_queue, 1)
        pmact.ps_queue_spi_ss(session_queue, self.m_ss_mask)

      spi_session.nextSpiPhase()


        
    
    '''
    cmd_phase
    ''' 
    if spi_session.isCmdPhase()==True:
      data_out = array.array('B', [cmd_byte])
      
      '''
      look ahead to see if the next phase has same io_mode
      if yes, then delay sending bytes till next phase (at least)
      '''
      
      pmact.ps_queue_spi_write(session_queue, 
                                spi_session.phaseSpec().mode,
                                8,
                                1,
                                data_out)
      #pmact.ps_queue_spi_ss(session_queue, 0)

      '''
      Finish up if no data exchange
      '''
      if spi_session.endOfSession()==True:
        pmact.ps_queue_spi_ss(session_queue, 0)
        pmact.ps_queue_spi_oe(session_queue, 0)        

        collect_handle = submitQueue(session_queue, self.m_channel_handle, pmact.PS_MODULE_ID_SPI_ACTIVE)
        if collect_handle==None:
          self.m_testutil.fatalError("NoneType collected")

          
        result_length, _dc = self.devCollect(collect_handle)
        pmact.ps_queue_destroy(session_queue)
        return self.SpiResult(True, None, None)
      else:
        spi_session.nextSpiPhase()

    
    '''
    address phase
    '''
    if (spi_session.isAddressPhase()==True):
      # Assemble write command and address
      phase=spi_session.currentSpiPhase()
      
      data_out=pmact.array_u08(phase.length)
      if phase.length==3:
        data_out[-3]=(address>>16)&0xff
      data_out[-2]=(address>>8)&0xff
      data_out[-1]=address&0xff
        #pmact.ps_queue_spi_ss(session_queue, self.m_ss_mask)
      pmact.ps_queue_spi_write(session_queue,
                               phase.mode,
                               8,
                               phase.length,
                               data_out)

      #self.m_testutil.printArrayHexDump("addr: ", data_out)

        #pmact.ps_queue_spi_ss(session_queue, 0)
        
      if spi_session.endOfSession():
        pmact.ps_queue_spi_ss(session_queue, 0)
        pmact.ps_queue_spi_oe(session_queue, 0)        
        collect = submitQueue(session_queue, self.m_channel_handle, pmact.PS_MODULE_ID_SPI_ACTIVE)
        collect_length, collect_buf = self.devCollect(collect)
        pmact.ps_queue_destroy(session_queue)
        return self.SpiResult(True, collect_length, _dc)
        
      spi_session.nextSpiPhase()

    '''
    dummy phase
    '''
    if spi_session.isDummyPhase()==True:

      phase=spi_session.currentSpiPhase()
      prev_phase=spi_session.prevSpiPhase()
      
      pmact.ps_queue_spi_write_word( session_queue,
                                     prev_phase.mode,
                                     8,
                                     phase.length,
                                     0)
      spi_session.nextSpiPhase()


    '''
    data (read or write) phase
    
      sanity check the buffer and length
      if data_read: flush pending writes
    '''
    if spi_session.isDataPhase()==True:
      phase=spi_session.currentSpiPhase()
      length_spec=spi_session.currentSpiPhase().lengthSpec
      data_length_bad=False

      '''
      verify the data length is 'sane'
      '''
          
      if data_length > len(data_buffer):
        data_length_bad
      else:
        if length_spec.fixed == None:
          #depend on range check
          if (data_length<length_spec.rangeMin):
            data_length_bad=True
          elif length_spec.rangeMax!=None:
            if length_spec.rangeMax<data_length:
              data_length_bad=True
        else:      
          if data_length!=length_spec.fixed:
            data_length_bad=True

      if data_length_bad:  
        self.m_testutil.fatalError("cmd data spec error")

      # data_length is valid
      iotype=spi_session.readNotWrite()
      if iotype==protocol.IOTYPE_NONE:
        self.m_testutil.fatalError("illegal data phase spec")


      '''
      write to complete data_write phase
      -or-
      write to complete data_read don't care/read phase
      
      data_out contains either the final segments of bytes ot output including data payload
      or don't chare bytes to stimulate data input from the slave.
      data_out contains only the final non-payload segments of bytes to output
      '''

      if iotype==protocol.IOTYPE_WRITE:
        # append valid buffer bytes to pending data_out
        pmact.ps_queue_spi_write(session_queue,
                                 phase.mode,
                                 8,
                                 data_length,
                                 data_buffer)

        pmact.ps_queue_spi_ss(session_queue, 0)
        pmact.ps_queue_spi_oe(session_queue, 0)
        #pmact.ps_queue_delay_ms(session_queue, 1)
          
        collect = submitQueue(session_queue, self.m_channel_handle, pmact.PS_MODULE_ID_SPI_ACTIVE)
        self.m_testutil.bufferDetailInfo("Write collect handle = %d" % collect)
        _in_length, _in_buf = self.devCollect(collect)
        pmact.ps_queue_destroy(session_queue)
        
        return self.SpiResult(True, data_length, data_buffer)

      else:
        '''
        complete the read phase
        '''
        pmact.ps_queue_spi_read(session_queue,
                                phase.mode,
                                8,
                                data_length)
        
        pmact.ps_queue_spi_ss(session_queue, 0)
        pmact.ps_queue_spi_oe(session_queue, 0)
        
        
        collect = submitQueue(session_queue, self.m_channel_handle, pmact.PS_MODULE_ID_SPI_ACTIVE)        
        self.m_testutil.bufferDetailInfo("Read collect handle = %d" % collect)
        if collect < 0:
          self.m_testutil.fatalError("Failed Read Queue Submission: collect handle = %d" % collect)

          
        collect_length, collect_buf = self.devCollect(collect)
        
        if not isinstance(collect_buf, coll.Iterable):
          self.m_testutil.fatalError("return buf not 'iterable'")

        if data_length > len(data_buffer) or data_length > len(collect_buf):
          self.m_testutil.fatalError("buffer, size out of sync")
                      
        for index in range(data_length):
          data_buffer[index]=collect_buf[index]

        pmact.ps_queue_destroy(session_queue)
        return self.SpiResult(True, collect_length, data_buffer)
    else:
      self.m_testutil.fatalError("corrupt session/session_spec")  
    self.m_testutil.fatalError("how did I get here?")
    
  pass
      


