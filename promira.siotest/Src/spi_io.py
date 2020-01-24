
import sys
import collections as coll
import promact_is_py as pmact
import promira_py as pm
import promactive_msg as pm_msg
import array
import test_utility as testutil
from spi_cfg_mgr import configMgr
import spi_cfg_mgr as spicfg
import cmd_protocol as protocol




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
  m_pm              = None
  m_app_name        = "com.totalphase.promact_is"
  m_promira_open    = None
  def __init__(self):
    self.m_pm_msg   = pm_msg.promactMessages()
    self.m_test_util= testutil.testUtil()    
    self.m_cfg_mgr  = configMgr()
    
    self.m_ss_mask = 0x1
    self.m_device = None
    self.m_devices    = pmact.array_u16(4)
    self.m_device_ids = pmact.array_u32(4)
    self.m_device_ips = pmact.array_u32(4)
    self.m_device_status = pmact.array_u32(4)

    self.m_spi_configuration = self.m_cfg_mgr.firstConfig()
    self.m_timeout_ms = 1000  # arbitrary 10 second value 

    self.discoverDevice()
    self.m_spi_initialized = False
    

  
  
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
      self.m_device_ipString=self.m_test_util.ipString(self.m_device_ips[0])
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
  
  
  def initSpiMaster(self, parameters):
    
    self.m_spi_parameters   = parameters
    self.m_spi_clk_kHz      = self.m_spi_parameters.clk_kHz
    self.m_spi_clk_mode     = parameters.clk_mode
    self.m_spi_ss_polarity  = parameters.ss_polarity
    self.m_spi_target_vdd   = parameters.target_vdd
    self.m_spi_bit_order    = parameters.bit_order
    self.m_spi_address_base = parameters.address_base

    if self.m_promira_open != True:    
      self.devOpen(self.m_device_ipString)
      self.m_promira_open=True
      
    pmact.ps_app_configure(self.m_channel_handle, pmact.PS_APP_CONFIG_SPI)
    
    # Power the EEPROM using one of the VTGT supply pins
    pmact.ps_phy_target_power(self.m_channel_handle, pmact.PS_PHY_TARGET_POWER_TARGET1_3V)  

    pmact.ps_spi_bitrate(self.m_channel_handle, self.m_spi_clk_kHz)
    
    #configure static spi parameters
    retval=pmact.ps_spi_configure( self.m_channel_handle,
                            self.m_spi_clk_mode, 
                            self.m_spi_bit_order, 
                            self.m_spi_ss_polarity)
    
    self.m_spi_initialized=True
    
    return
  

  def setTargetpower(self, vtgt_setting, variable_voltage_level):
    
    if type(variable_voltage_level)==float:
      if 0.9 <= variable_voltage_level and 3.45>=variable_voltage_level:
        # supported variable level
        if vtgt_setting not in [pmact.PS_PHY_TARGET_POWER_TARGET2, pmact.PS_PHY_TARGET_POWER_BOTH]:
          self.m_testutil.fatalError("unsupported target power settings")
      pass
    
    if vtgt_setting==pmact.PS_PHY_TARGET_POWER_NONE:
          # set no power and return
      pass
    elif ( vtgt_setting==pmact.PS_PHY_TARGET_POWER_TARGET1_3V
          or vtgt_setting==pmact.PS_PHY_TARGET_POWER_TARGET1_5V):
          # set fixed power and return
      pass
    elif vtgt_setting==pmact.PS_PHY_TARGET_POWER_TARGET2:
          # set variable power only and return
      pass
    elif vtgt_setting==pmact.PS_PHY_TARGET_POWER_BOTH:
        # set fixed and variable power and return
      pass
    else:
      self.m_testutil.fatalError("unsupported power setting")
 
 
      
#    ps_phy_level_shift (PromiraChannelHandle channel,
#                              f32                  level);
    
    if vtgt_22_24==   
  
  
  
  def devOpen (self, ip):
      self.m_pm = pm.pm_open(ip)
      if self.m_pm <= 0:
          print("Unable to open Promira platform on %s" % ip)
          print("Error code = %d" % self.m_pm)
          sys.exit()
  
      ret = pm.pm_load(self.m_pm, self.m_app_name)
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
  
      return self.m_pm, self.m_app_conn_handle, self.m_channel_handle
  
  
  '''
  closeSpiMaster()
  
    release the SPI connection and app handles.
    release any other app/connection resource reservations
    
  '''
     
  def devClose (self):
      self.m_pm.ps_channel_close(self.m_channel_handle)
      self.m_pm.ps_app_disconnect(self.m_app_conn_handle)
      self.m_pm.pm_close(self.m_pm)

  def closeSpiMaster(self):
    self.devClose()


  
  def devCollect (self, collect):


    '''
    collect intermediate results until:
      No More Cmds Uncollected
      
      response array is a catenation of an input length byte,
      and all received input bytes from queued command reads
      '[n, byte0, byte1, ..., byte n-1]
      
      if nothing received, response is 1 byte array '[0]'
      
    '''
    while True:
        t, _length, result = pmact.ps_collect_resp(collect, -1)
        # self.m_pm_msg.showCollectResponseMsg(t)
        if t == pmact.PS_APP_NO_MORE_CMDS_TO_COLLECT:
            break
        elif t < 0:
            print(pmact.ps_app_status_string(t))
            continue
          
        if t == pmact.PS_SPI_CMD_READ:
            _ret, _word_size, buf = pmact.ps_collect_spi_read(collect, result)
            #print("PS_SPI_CMD_READ len: "+str(_ret)+"  "+str(type(buf)))            #response_buf += buf
            #response_length+= len(buf)
    
#    return response_length, response_buf
    if buf==None:
      return _ret, buf


    return _ret, buf
  

  '''
  spiMasterMultlimodeCmd( spi_cmd, address, data_length, data_buffer )
    on read commands, the buffer presented will be returned with (any) received data
    
  RETURN
    tuplet:  ( Success(T/F), data transfer length/None, data transfer array/None)
  '''
 
  SpiResult=coll.namedtuple('SpiResult', 'success xfer_length xfer_array')
  
  def spiMasterMultimodeCmd(self,
                                spi_cmd,
                                address=None,
                                data_length=None,
                                data_buffer=None): 
    # -> self.SpiResult


    if self.m_spi_initialized != True:
      self.m_test_util.fatalError("attempt to transact on uninitialized SPI bus")
        
    cmd_byte=spi_cmd[0]
    cmd_spec=protocol.precedentCmdSpec(spi_cmd)
    spi_session=protocol.spiTransaction(spi_cmd, cmd_spec)
    collect = None
    
    '''
    if cmd_byte in self.NODATA_CMDS:
      dataphase_readNotWrite=None
    else:
      dataphase_readNotWrite=cmd_byte in self.READ_DATA_CMDS
    '''
    
    #print("cmd_byte= ", hex(cmd_byte))
    
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
    
    if cmd_byte in protocol.WREN_REQUIRED:
      wren_cmd=array.ArrayType('B', [protocol.WREN])
      pmact.ps_queue_spi_write(session_queue, protocol.SPIIO_SINGLE, 8, 1, wren_cmd )
      pmact.ps_queue_spi_ss(session_queue, 0)
      pmact.ps_queue_spi_ss(session_queue, self.m_ss_mask)





        
    
    '''
    cmd_phase
    ''' 
    spi_session.setInitialPhase()
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

        collect_handle, _dc = pmact.ps_queue_submit(session_queue, self.m_channel_handle, 0)
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

      #self.m_test_util.printArrayHexDump("addr: ", data_out)

        #pmact.ps_queue_spi_ss(session_queue, 0)
        
      if spi_session.endOfSession():
        pmact.ps_queue_spi_ss(session_queue, 0)
        pmact.ps_queue_spi_oe(session_queue, 0)        
        collect, _dc = pmact.ps_queue_submit(session_queue, self.m_channel_handle, 0)
        collect_length, collect_buf = self.devCollect(collect)
        pmact.ps_queue_destroy(session_queue)
        return self.SpiResult(True, collect_length, _dc)
        
      spi_session.nextSpiPhase()

    '''
    dummy phase
    '''
    if spi_session.isDummyPhase()==True:
      use_dummy_array=False
      phase=spi_session.currentSpiPhase()
      prev_phase=spi_session.prevSpiPhase()
      
      if use_dummy_array:
        dummy_array=pmact.array_u08(phase.length)
        pmact.ps_queue_spi_write( session_queue,
                                  prev_phase.mode,
                                  8,
                                  phase.length,
                                  dummy_array)
      else:
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
          
        collect, _dc = pmact.ps_queue_submit(session_queue, self.m_channel_handle, 0)
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
        
        collect, _dc = pmact.ps_queue_submit(session_queue, self.m_channel_handle, 0)
        

          
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
      


