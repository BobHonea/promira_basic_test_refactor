import collections as coll
import promact_is_py as pmact

class configVal:
  
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
  
  

      

class configMgr:


  spi_configuration=coll.namedtuple('spi_configuration', 'clk_mode bit_order ss_polarity clk_kHz address_base target_vdd' )

  spi_config_ranges=spi_configuration( 
    clk_mode      = [configVal.SPICLOCKMODE_0, configVal.SPICLOCKMODE_3],
    bit_order     = [configVal.SPIBITORDER_MSB],
    ss_polarity   = [configVal.SPI_SS_ALL_ACTIVE_LOW],
    clk_kHz       = [1000, 6200, 12200, 18000, 23400, 28200, 32200, 35600],
    address_base  = [0, 0x1000, 0x2000, 0x3000],
    target_vdd    = [3.3])  #  alternative: [1.6, 1.8]

  m_spi_config_list=None
  

  '''
  traverse config list:
    getconfig(index)
    firstConfig()
    nextConfig()
        Config functions return spi_configuration namedtuple, or None if end of list
       
    configCount()  : valid after firstConfig()
        Count of valid configurations
  '''
  _instance=None
  
  def __new__(cls):
      if cls._instance is None:
          print('Creating the configMgr object')
          cls._instance = super(configMgr, cls).__new__(cls)
          #cls._instance = object.__new__(cls)
          cls._instance.__singleton_init__()
      return cls._instance
  
  def __singleton_init__(self):
    self.m_spi_config_list=None
    self.m_config_list_complete=False
    self.genConfigs()
  
  '''
  class Core(object):
  
      def __new__(cls, *args, **kwargs):
          obj = object.__new__(cls, *args, **kwargs)
          return obj
      ...
  '''

  def getConfig(self, index):
    if self.m_config_ndx<self.m_config_count:
      return(self.m_spi_config_list[self.m_config_ndx])
    else:
      return None
        
  def firstConfig(self):
    self.m_config_ndx=0
    self.m_config_count=len(self.m_spi_config_list)
    return self.getConfig(self.m_config_ndx)


  def nextConfig(self):
    self.m_config_ndx+=1
    return self.getConfig(self.m_config_ndx)
    
  
  def configCount(self):
    return self.m_config_count
  
  def configIndex(self):
    return self.m_config_ndx
  
  def configsGenerated(self):
    return self.m_spi_config_list!=None

  '''
  genConfigs()
      ACTIVITY:  creates list of configuration tuples
      RETURN:    the count of tuples
  '''
  def genConfigs(self):
    
    def fill_config_level(attrib_index):
      '''
      This is a RECURSION algorithm for generating all combinations
      of configuration parameters. Modestly subtle Python techniques
      are employed.
      
      ***CAVEAT***
      First call to this function MUST be with attrib_index == -1
      '''
      
      if attrib_index==-1:
        self.config_item_list=[]
        attrib_index+=1
        fill_config_level(attrib_index)
        return
        
      elif attrib_index==max_config_ndx:
        # spi_config is defined, store it
        self.m_spi_config_list.append(self.spi_configuration._make(self.config_item_list))
        
      else:
        '''
        Modest Subtlety follows....
        '''
        config_items=getattr(self.spi_config_ranges, self.spi_configuration._fields[attrib_index])
        config_item_count=len(config_items)
        for item_index in range(config_item_count):
          this_value=config_items[item_index]
          '''
          recurse here
          '''
          self.config_item_list.append(this_value)    
          fill_config_level(attrib_index+1) 
          self.config_item_list=self.config_item_list[:-1]

    
    if not self.configsGenerated():
      # PREVENT repeated initialization
      # It is possible to generate ZERO configurations (however unlikely)    
      self.m_spi_config_list=[]
      max_config_ndx=len(self.spi_configuration._fields)
      fill_config_level(-1)

    return len(self.m_spi_config_list) > 0
    
  pass
