import collections as coll
import sys


BUSTYPE_UNKNOWN = 0
BUSTYPE_I2C = 1
BUSTYPE_SPI = 2
'''
SPICLOCKMODE_0 = pmact.PS_SPI_MODE_0
SPICLOCKMODE_1 = pmact.PS_SPI_MODE_1
SPICLOCKMODE_2 = pmact.PS_SPI_MODE_2
SPICLOCKMODE_3 = pmact.PS_SPI_MODE_3
SPIBITORDER_MSB= pmact.PS_SPI_BITORDER_MSB
SPIBITORDER_LSB= pmact.PS_SPI_BITORDER_LSB
'''
SPICLOCKMODE_0 = 'mode0'
SPICLOCKMODE_1 = 'mode1'
SPICLOCKMODE_2 = 'mode2'
SPICLOCKMODE_3 = 'mode3'
SPIBITORDER_MSB= 'msb'
SPIBITORDER_LSB= 'lsb'

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

class spi_configure:

  clock_khz_rates = [1000, 6200, 12200, 18000, 23400, 28200, 32200, 35600]
  bit_orders      = [SPIBITORDER_MSB]
  spi_clock_modes = [SPICLOCKMODE_0, SPICLOCKMODE_3] 
#   unused_clkmodes = [SPICLOCKMODE_1, SPICLOCKMODE_2]
  address_offsets = [0, 0x1000, 0x2000, 0x30000]
  target_vdds     = [3.3]

  spi_configuration=coll.namedtuple('py', 'clk_mode bit_order clk_kHz address_offset target_vdd' )

  spi_config_ranges=spi_configuration( clk_mode=spi_clock_modes,
                                      bit_order=bit_orders,
                                      clk_kHz=clock_khz_rates,
                                      address_offset=address_offsets,
                                      target_vdd=target_vdds )



  
  spi_config_list= []
  
  def __init__(self):
    self.gen_configs()
    pass
  
  def gen_configs(self):
    
    
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
    
    
    
    
    
config=spi_configure()
print("configuration done")
