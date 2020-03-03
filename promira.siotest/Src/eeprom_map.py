
import collections as coll
import test_utility



KB4         = 0x1000
KB8         = 0x2000
KB32        = 0x8000
KB64        = 0x10000
SECTOR_SIZE = 0x00001000
PAGE_SIZE   = 0x00000100
SECTOR_MASK = 0xFFFFF000
PAGE_MASK   = 0xFFFFFF00

# 4 8KB BLOCKS FROM ADDRESS 0
# 1 32KB BLOCKS FROM ADDRESS 0x8000
# 32 64KB BLOCKS FROM ADDRESS 0x10000
# 1 32BLOCK FROM ADDRESS 0x3F0000
# 4 8KB BLOCKS FROM ADDRESS 0x3F8000

MEM_BLOCKSIZE = 0
MEM_BLOCKCOUNT = 1



MICROCHIP_EEPROM_BLOCKS = [[KB8, 2]] * 4 +\
                          [[KB32, 8]] +\
                          [[KB64, 16]] * 31 +\
                          [[KB32, 8]] +\
                          [[KB8, 2]] * 4

MICRON_EEPROM_BLOCKS = [[KB32, 8] for index in range(512)]

'''
sectorSet()
  manage data about eeprom sectors.
  1. sector addresses
  2. sector sizes
  3. sector writable
  4. sector accessibility
'''


SECSTAT_UNKNOWN       = 0
SECSTAT_UNLOCK        = 1
SECSTAT_RDLOCK        = 2
SECSTAT_WRLOCK        = 4
SECSTAT_RWLOCK        = 6

SECSTAT_CODES=[SECSTAT_UNKNOWN, SECSTAT_UNLOCK, SECSTAT_RDLOCK, SECSTAT_WRLOCK, SECSTAT_WRLOCK]

WRITESTAT_UNKNOWN     = 0
WRITESTAT_ERASED      = 1
WRITESTAT_WRITTEN     = 2
WRITESTAT_MIXED       = 3


WRITESTAT_CODES = [ WRITESTAT_UNKNOWN, WRITESTAT_WRITTEN, WRITESTAT_ERASED, WRITESTAT_MIXED]

'''
Submit Sector Map to sectorSet():
  1. address:      sectors listed in increasing address order
  2. size:         no gaps in memory space between sectors
  3. write_status: 
'''
SectorMap = coll.namedtuple('SectorMap', 'address size block_index')
BlockMap = coll.namedtuple('BlockMap', 'address size sectors base_sector_index')

class deviceMap(object):
  m_sector_map    = None
  m_block_map     = None
  m_sector_count  = None
  m_byte_size    = None
  m_valid         = None
  m_base_address  = None
  m_testutil      = None
  
  def fatalError(self, reason):
    self.m_testutil.fatalError(reason)
    
  def __init__(self, block_map:BlockMap):
    
    self.m_testutil = test_utility.testUtil()
    if ( type(block_map) == list
         and block_map[0][0] in [ KB8, KB32, KB64]
         and len(block_map)>0 ):
         
      self.m_byte_size      = 0
      self.m_sector_count   = 0
      self.m_block_map      = []
      self.m_sector_map     = []
      self.m_sector_status  = []
      sector_count          = 0
      block_address         = 0
      
      for block_ndx in range(len(block_map)):
        blockinfo=block_map[block_ndx]
        block_size = blockinfo[0]
        sector_count = blockinfo[1]
        
        blockmap=BlockMap(address=block_address,
                          size=block_size, 
                          sectors=sector_count,
                          base_sector_index=self.m_sector_count)
        
        self.m_block_map.append(blockmap)
        
        sector_address = block_address
        
        for _sec_ndx in range(sector_count):
         
          sector_map=SectorMap(address=sector_address, size=KB4, block_index=block_ndx)

          self.m_sector_map.append(sector_map)
          self.m_sector_status.append(self._sectorStatusVector(SECSTAT_UNKNOWN))

          sector_address=sector_map.address+sector_map.size
  
        self.m_byte_size+=block_size
        self.m_sector_count+=sector_count
        block_address=self.m_byte_size

        
      self.m_valid=self.m_byte_size>0 and self.m_sector_count>0
      
      if self.m_valid!=True:
        self.m_testutil.fatalError("invalid sector_map")

  def valid(self):
    return self.m_valid
  
  def totalSectors(self):
    return self.m_sector_count
  
  def totalBlocks(self):
    return len(self.m_block_map)
  
  def deviceBytes(self):
    return self.m_byte_size
  
  def devicePages(self):
    return int (self.m_sector_count * (SECTOR_SIZE/PAGE_SIZE))
  
  def sectorIndex(self, address):
    index = address//SECTOR_SIZE
    if index > self.m_sector_count:
      return None
    return index

  def blockIndex(self, address):
    sector_index=self.sectorIndex(address)
    if sector_index==None:
      return None
    
    sector_map=self.m_sector_map[sector_index]
    return(sector_map.block_index)
  



  def pageAddress(self, address):
    return address & PAGE_MASK
    
  def pageWriteStatus(self, address):
    sector_status=self.sectorWriteStatus(address)
    if sector_status in [WRITESTAT_MIXED]:
      page_address=self.pageAddress(address)
      sector_address=self.sectorAddress(page_address)  
      page_index=(page_address-sector_address)//PAGE_SIZE
      page_bit_mask=1<<page_index
      written=(self.m_sector_status[1]&page_bit_mask)==page_bit_mask
      if written:
        return WRITESTAT_WRITTEN
      else:
        return WRITESTAT_ERASED
    else:
      return sector_status
  
    
  m_left_bits = [ 0x0001, 0x0003, 0x0007, 0x000f, 0x001f, 0x003f,
                  0x007F, 0x00FF, 0x01ff, 0x03ff, 0x07ff, 0x0fff,
                  0x1fff, 0x3fff, 0x7fff, 0xffff ]
  m_right_bits= [ 0xffff, 0xfffe, 0xfffc, 0xfff8, 0xfff0, 0xffe0,
                  0xffc0, 0xff80, 0xff00, 0xfe00, 0xfc00, 0xf800,
                  0xf000, 0xe000, 0xc000, 0x8000 ]
  
  def _bitsMask(self, start_bit, end_bit):
    bits= self.m_right_bits[start_bit]&self.m_left_bits[end_bit]
    return bits
  
  def subSectorWriteStatus(self, start_address, end_address):
    sector_writestatus=self.sectorWriteStatus(start_address)
    if sector_writestatus==WRITESTAT_MIXED:
      
      sector_index=self.sectorIndex(start_address)
      sector_address=self.sectorAddress(start_address)
      start_page_index=(start_address-sector_address)//PAGE_SIZE
      end_page_index=(end_address-sector_address)//PAGE_SIZE
      page_bits=self._bitsMask(start_page_index, end_page_index)
      
      page_status_vector=(self.m_sector_status[sector_index][1]&page_bits)
      if page_status_vector == 0:
        return WRITESTAT_ERASED
      elif page_status_vector != page_bits:
        return WRITESTAT_MIXED
      else:
        return WRITESTAT_WRITTEN

    else:
      return sector_writestatus
    

  def addressedSectorMap(self, address):
    return self.m_sector_map[self.sectorIndex(address)]
  
  def indexedSectorMap(self, sector_index):
    if sector_index >= 0 and sector_index < self.m_sector_count:
      return self.m_sector_map[sector_index]
    
  def addressedBlockMap(self, address):
    return self.m_block_map[self.blockIndex(address)]
  
  def indexedBlockMap(self, block_index):
    if block_index >= 0 and block_index < len(self.m_block_map):
      return self.m_block_map[block_index]
  
  def sectorAddress(self, address):
    return(address & SECTOR_MASK)
    #return self.m_sector_map[self.sectorIndex(address)].address
  
  def sectorSize(self, address):
    return self.m_sector_map[self.sectorIndex(address)].size
  
  def _sectorStatusVector(self, write_status):
    if write_status==WRITESTAT_ERASED:
      return [WRITESTAT_ERASED, 0]
    else:
      return [write_status, 0xffff]
    
    
  '''
  setPageDirty
    is usable only when the SECTOR status is NOT 'Unknown'
    SECTOR STATUS must be WRITTEN, ERASED, or MIXED
  '''
     
  def setPageDirty(self, address):
    
    page_address=self.pageAddress(address)
    sector_address=self.sectorAddress(page_address)  

    sector_index=self.sectorIndex(page_address)
    page_index=(page_address-sector_address)//PAGE_SIZE
    page_bit_mask=1<<page_index
    
    sector_status=self.m_sector_status[sector_index]
    sector_status[1] = sector_status[1] | page_bit_mask
    
    if sector_status[1]==0xffff:
      sector_status[0]=WRITESTAT_WRITTEN
    else:
      sector_status[0]=WRITESTAT_MIXED
          
    self.m_sector_status[sector_index]=sector_status
    
    
  def sectorWriteStatus(self, address):
    if self.sectorIndex(address) >= len(self.m_sector_status):
      self.m_testutil.fatalError("eeprom_map.sectorWriteStatus(): index out of bounds")
    return self.m_sector_status[self.sectorIndex(address)][0]

  def setSectorWriteStatus(self, address, write_status):
    if write_status in WRITESTAT_CODES:
      self.m_sector_status[self.sectorIndex(address)]=self._sectorStatusVector(write_status)
  
  def blockAddress(self, address):
    block_map=self.addressedBlockMap(address)
    return block_map.address
  
  def setBlockWriteStatus(self, address, write_status):
    if write_status in WRITESTAT_CODES:
      block_map=self.addressedBlockMap(address)
      sector_range=range(block_map.base_sector_index, block_map.base_sector_index+block_map.sectors)
      '''
      page bits are zeroed ONLY with ERASED status
      else the page bits '1' for written/un-erased
      '''
      for sector_index in sector_range:
        self.m_sector_status[sector_index]=self._sectorStatusVector(write_status)
      

  def blockWriteStatus(self, address):
    block_map=self.addressedBlockMap(address)
    '''
    slice the block's status values together
    if the sorted slice is all one value, return it as block status.
    else... return 'undefined'
    '''
    block_sector_status=self.m_sector_status[block_map.base_sector_index:block_map.base_sector_index+block_map.sectors]
    status_val=[]
    for status_entry in block_sector_status:
      status_val.append(status_entry[0])
      
    sorted_status=sorted(status_val)
    if sorted_status[0]==sorted_status[-1]:
      # all sector status' in block match
      return sorted_status[0]
    else:
      return WRITESTAT_MIXED
    
    
  def setDeviceWriteStatus(self, write_status):
    for block_index in range(len(self.m_block_map)):
      self.setBlockWriteStatus(self.m_block_map[block_index].address, write_status)

















class eepromTest(object): 
  
  m_device_map  = None 
  m_testutil    = None
  page_index_subset=[1, 14, 3, 5, 7, 8, 10, 12]
  

  def __init__(self, eeprom_blocks_definition):
    self.m_device_map=deviceMap(eeprom_blocks_definition)
    self.m_testutil=test_utility.testUtil()
    pass
        
      
  def doMapTest(self):
    
    '''
    doMapTest
      1. Set Status to Erased
    '''  
    
    # 1. Set Status to Erased
    self.m_device_map.setDeviceWriteStatus(WRITESTAT_ERASED)
    
    # 2. Test Erased Status
    address=0
    while address < self.m_device_map.deviceBytes():
      block_map=self.m_device_map.addressedBlockMap(address)
      if self.m_device_map.blockWriteStatus(address)==WRITESTAT_ERASED:
        address=block_map.address+block_map.size
        continue
      
      self.m_testutil.fatalError("doMapTest() Fail - ERASED status test")
      
      
    #3. Make status MIXED
    block_address=0
    while block_address < self.m_device_map.deviceBytes():
      block_map=self.m_device_map.addressedBlockMap(block_address)
      sector_range=range(block_map.base_sector_index, block_map.base_sector_index+block_map.sectors)
  
      for sector_index in sector_range:
        sector_map=self.m_device_map.indexedSectorMap(sector_index)
        sector_address=sector_map.address
        
        for page_index in self.page_index_subset:
          page_address=sector_address+(page_index*PAGE_SIZE)
          self.m_device_map.setPageDirty(page_address)
          
  
      if self.m_device_map.blockWriteStatus(block_address)==WRITESTAT_MIXED:
        block_address=block_map.address+block_map.size
      else:
        self.m_testutil.fatalError("doMapTest() Fail - MIXED status test")
  
    #4. make status WRITTEN
    block_address=0
    while block_address < self.m_device_map.deviceBytes():
      block_map=self.m_device_map.addressedBlockMap(block_address)
      for sector_subindex in range(block_map.sectors):
        sector_index=block_map.base_sector_index+sector_subindex
        sector_map=self.m_device_map.indexedSectorMap(sector_index)
        sector_address=sector_map.address
        
        for page_index in range(16):
          if page_index not in self.page_index_subset:
            page_address=sector_address+(page_index*PAGE_SIZE)
            self.m_device_map.setPageDirty(page_address)
            
        if self.m_device_map.sectorWriteStatus(sector_address)!=WRITESTAT_WRITTEN:
          self.m_testutil.fatalError("doMapTest Fail - Sector WRITTEN status Test")
          
  
      if self.m_device_map.blockWriteStatus(block_address)==WRITESTAT_WRITTEN:
        block_address=block_map.address+block_map.size
      else:
        self.m_testutil.fatalError("doMapTest() Fail - Block WRITTEN status test")
    
    #5. Check Sector Status as Written
  
    sector_address=0  
    while sector_address < self.m_device_map.deviceBytes():
      sector_map=self.m_device_map.addressedSectorMap(sector_address)
      
      if self.m_device_map.sectorWriteStatus(sector_address)==WRITESTAT_WRITTEN:
        sector_address=sector_map.address+sector_map.size
        continue
      
      self.m_testutil.fatalError("doMapTest() Fail - Sector WRITTEN status test")
    return


#eeprom_test=eepromTest(MICRON_EEPROM_BLOCKS)
#eeprom_test.doMapTest()
#print ("MICRON MAP Test Success")

#eeprom_test=eepromTest(MICROCHIP_EEPROM_BLOCKS)
#eeprom_test.doMapTest()
#print ("MICROCHIP MAP Test Success")



    