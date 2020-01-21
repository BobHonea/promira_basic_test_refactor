
import sys
 
import collections as coll
import promact_is_py as pmact
import promira_py as pm

 
class spi_io:
  
  
  BUSTYPE_UNKNOWN = 0
  BUSTYPE_I2C = 1
  BUSTYPE_SPI = 2
  SPICLOCKMODE_0 = pmact.PS_SPI_MODE_0
  SPICLOCKMODE_1 = pmact.PS_SPI_MODE_1
  SPICLOCKMODE_2 = pmact.PS_SPI_MODE_2
  SPICLOCKMODE_3 = pmact.PS_SPI_MODE_3
  SPIBITORDER_MSB= pmact.PS_SPI_BITORDER_MSB
  SPIBITORDER_LSB= pmact.PS_SPI_BITORDER_LSB
  
  '''
  Chip Select Polarity Vector
    one bit for each of 4 chip selects
    1 = active high
    0 = active low
    bits 0..3 comprise the vector bits
  '''
  SPI_SS_ALL_ACTIVE_HIGH = 0x0F
  SPI_SS_ALL_ACTIVE_LOW = 0x00
  SPI_SS0_ACTIVE_HIGH=0x01
  
  class spi_configuration:


    spi_configuration=coll.namedtuple('spi_configuration', 'clk_mode bit_order ss_polarity clk_kHz address_offset target_vdd' )

    spi_config_ranges=spi_configuration( 
      clk_mode      = [SPICLOCKMODE_0, SPICLOCKMODE_3],
      #   unused_clkmodes = [SPICLOCKMODE_1, SPICLOCKMODE_2]
      bit_order     = [SPIBITORDER_MSB],
      ss_polarity   = [SPI_SS_ALL_ACTIVE_HIGH, SPI_SS_ALL_ACTIVE_LOW],
      clk_kHz       = [1000, 6200, 12200, 18000, 23400, 28200, 32200, 35600],
      address_offset= [0, 0x1000, 0x2000, 0x3000],
      target_vdd    = [3.3])
      #   unused vdd: 1.8

    spi_config_list=[]
    
  
    '''
    traverse config list:
      getconfig(index)
      firstConfig()
      nextConfig()
          Config functions return spi_configuration namedtuple, or None if end of list
         
      configCount()  : valid after firstConfig()
          Count of valid configurations
    '''

    def __init__(self):
      self.spi_config_list=[]
      self.genConfigs()


    def getConfig(self, index):
      if self.m_config_ndx<self.m_config_count:
        return(self.spi_config_list[self.m_config_ndx])
      else:
        return None
          
    def firstConfig(self):
      self.m_config_ndx=0
      self.m_config_count=len(self.spi_config_list)
      return self.getConfig(self.m_config_ndx)


    def nextConfig(self):
      self.m_config_ndx+=1
      return self.getConfig(self.m_config_ndx)
      
    
    def configCount(self):
      return self.m_config_count
  
    def genConfigs(self):
      
      def fill_config_level(attrib_index):
        
        if attrib_index==-1:
          self.config_item_list=[]
          attrib_index+=1
          fill_config_level(attrib_index)
          return
          
        elif attrib_index==max_config_ndx:
          # spi_config is defined, store it
          spi_config_list.append(self.spi_configuration._make(self.config_item_list))
          
        else:
          config_items=getattr(self.spi_config_ranges, self.spi_configuration._fields[attrib_index])
          config_item_count=len(config_items)
          for item_index in range(config_item_count):
            this_value=config_items[item_index]
            # begin recurse
            self.config_item_list.append(this_value)    
            fill_config_level(attrib_index+1) 
            self.config_item_list=self.config_item_list[:-1]
            # recurse end
            
      spi_config_list=[]
      max_config_ndx=len(self.spi_configuration._fields)
      fill_config_level(-1)
    
      

  m_ss_mask         = None
  m_device          = None
  m_spi_bitorder    = None
  m_devices         = None
  m_device_ids      = None
  m_device_ips      = None
  m_device_status   = None

  
  m_spi_bitrate_khz = None
  m_spi_clock_mode  = None
  m_spi_ss_polarity = None
  
  
  m_spi_configuration = None
  
  m_queue           = None
  m_channel_handle  = None
  m_app_conn_handle = None
  m_pm              = None
  m_app_name        = "com.totalphase.promact_is"
  
  def __init__(self):
    self.m_ss_mask = 0x1
    self.m_device = None
    self.m_devices    = pmact.array_u16(4)
    self.m_device_ids = pmact.array_u32(4)
    self.m_device_ips = pmact.array_u32(4)
    self.m_device_status = pmact.array_u32(4)

    self.m_spiconfig = self.spi_configuration()
    self.m_spi_configuration=self.m_spiconfig.firstConfig()
    self.m_timeout_ms = 1000  # arbitrary 10 second value 

    self.initSpiMaster(self.m_device_ipString, self.m_spi_configuration )

  
  
  def selectSpiConfig(self, index=0):
    pass
 
  def ipString(self, ip_integer):
    integer=ip_integer
    ipString_buf=""
    
    for index in range (0,4):
      if index>0:
        ipString_buf="."+ipString_buf
      octet=int((ip_integer>>((3-index)*8))&0xff) 
      integer>>=8
      octet_string=format(octet, "d")
      ipString_buf=octet_string+ipString_buf
  
  
    return ipString_buf
 
  def discoverDevice(self, serial_number=None):
    self.m_port = 0  # default port for a single promira device

    return_tuple = pm.pm_find_devices_ext(self.m_device_ips, self.m_device_ids, self.m_device_status)
    device_count = return_tuple[0]
    self.m_device_ips = return_tuple[1]
    self.m_devices = return_tuple[2]
    self.m_device_ids = return_tuple[3]
    print("device_count:" + str(device_count))
    self.m_device_ipString=self.ipString(self.m_device_ips[0])

 
  '''
  init_spi_master()
  
    creates a connection and connection handle for session with
    Promira Serial Platform.
    
    intializes static SPI parameters (rarely change during session)
  
  '''
  
  
  def initSpiMaster(self, net_ipString, bitrate_kHz, clock_mode, ss_polarity):
    
    self.m_spi_bitrate_kHz  = bitrate_kHz
    self.m_spi_clock_mode   = clock_mode
    self.m_spi_ss_polarity  = ss_polarity
    self.m_device_ipString = net_ipString
    
    self.devOpen(self.m_device_ipString)
    
    pmact.ps_app_configure(self.m_channel_handle, pmact.PS_APP_CONFIG_SPI)
    # Power the EEPROM using one of the VTGT supply pins
    
    pmact.ps_phy_target_power(self.m_channel_handle, pmact.PS_PHY_TARGET_POWER_TARGET1_3V)  
      
    pmact.ps_spi_bitrate(self.m_channel_handle, self.m_spi_bitrate_kHz)
    
    #configure static spi parameters

    pmact.ps_spi_configure( self.m_channel_handle,
                            self.m_spi_clock_mode, 
                            self.m_spi_bitorder, 
                            self.m_spi_ss_polarity)
    

    return
  
  '''
  closeSpiMaster()
  
    release the SPI connection and app handles.
    release any other app/connection resource reservations
    
  '''
  def closeSpiMaster(self):
    pmact.ps_app_disconnect(self.m_app_conn_handle)
    pmact.ps_channel_close(self.m_channel_handle)
     
   
  
  
  
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
  
  def devClose (self):
      pm.ps_channel_close(self.m_channel_handle)
      pm.ps_app_disconnect(self.m_app_conn_handle)
      pm.pm_close(self.m_pm)

  def closeSpiMaster(self):
    devClose()


  
  def devCollect (self, collect):

    def showCollectResponseMsg(self, response):
      message=promact_msg.getResponseMessage(response)
      if message==None:
        fatalError("unknown collect response")
      print("Collect Response: "+message)
    
    if collect < 0:
        print(pmact.ps_app_status_string(collect))
        return
  
    collection_count=0
    response_length=0
    response_buf=pmact.array_u08(0)

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
        self.showCollectResponseMsg(t)
        if t == pmact.PS_APP_NO_MORE_CMDS_TO_COLLECT:
            break
        elif t < 0:
            print(pmact.ps_app_status_string(t))
            continue
          
        if t == pmact.PS_SPI_CMD_READ:
            _ret, _word_size, buf = pmact.ps_collect_spi_read(collect, result)
            print("PS_SPI_CMD_READ len: "+str(_ret)+"  "+str(type(buf)))            #response_buf += buf
            #response_length+= len(buf)
    
#    return response_length, response_buf
    if buf==None:
      return _ret, buf


    return _ret, buf
  

    

  
  
  
    


  def spiMasterMultimodeCmd(self,
                                spi_cmd,
                                address:int=None,
                                data_length=None,
                                data_buffer=None):



        
    cmd_byte=spi_cmd[0]
    #cmd_spec=self.precedent_cmdspec(spi_cmd)
    spi_session=self.spiTransaction(spi_cmd, self.precedent_cmdspec(spi_cmd))
    collect = None
    
    if cmd_byte in self.NODATA_CMDS:
      dataphase_readNotWrite=None
    else:
      dataphase_readNotWrite=cmd_byte in self.READ_DATA_CMDS
    
    print("cmd_byte= ", hex(cmd_byte))
    
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
    
    if cmd_byte in self.WREN_REQUIRED:
      wren_cmd=array.ArrayType('B', [self.WREN])
      pmact.ps_queue_spi_write(session_queue, self.SPIIO_SINGLE, 8, 1, wren_cmd )
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
          fatalError("NoneType collected")
          
        result_length, _dc = self.devCollect(collect_handle)
        pmact.ps_queue_destroy(session_queue)
        return result_length
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

      self.printArrayHexDump("addr: ", data_out)

        #pmact.ps_queue_spi_ss(session_queue, 0)
        
      if spi_session.endOfSession():
        pmact.ps_queue_spi_ss(session_queue, 0)
        pmact.ps_queue_spi_oe(session_queue, 0)        
        collect, _dc = pmact.ps_queue_submit(session_queue, self.m_channel_handle, 0)
        collect_length, collect_buf = self.devCollect(collect)
        pmact.ps_queue_destroy(session_queue)
        return collect_length
        
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
        fatalError("cmd data spec error")

      # data_length is valid
      iotype=spi_session.readNotWrite()
      if iotype==self.IOTYPE_NONE:
        fatalError("illegal data phase spec")


      '''
      write to complete data_write phase
      -or-
      write to complete data_read don't care/read phase
      
      data_out contains either the final segments of bytes ot output including data payload
      or don't chare bytes to stimulate data input from the slave.
      data_out contains only the final non-payload segments of bytes to output
      '''

      if iotype==self.IOTYPE_WRITE:
        # append valid buffer bytes to pending data_out
        pmact.ps_queue_spi_write(session_queue,
                                 phase.mode,
                                 8,
                                 data_length,
                                 data_buffer)

        pmact.ps_queue_spi_ss(session_queue, 0)
        pmact.ps_queue_spi_oe(session_queue, 0)
        pmact.ps_queue_delay_ms(session_queue, 1)
          
        collect, _dc = pmact.ps_queue_submit(session_queue, self.m_channel_handle, 0)
        _in_length, _in_buf = self.devCollect(collect)
        pmact.ps_queue_destroy(session_queue)
        return len(data_out)

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
        
        if not isinstance(collect_buf, collections.Iterable):
          fatalError("return buf not 'iterable'")

        if data_length > len(data_buffer) or data_length > len(collect_buf):
          fatalError("buffer, size out of sync")
                      
        for index in range(data_length):
          data_buffer[index]=collect_buf[index]

        pmact.ps_queue_destroy(session_queue)
        return collect_length
    else:
      fatalError("corrupt session/session_spec")  
    fatalError("how did I get here?")
    
      


