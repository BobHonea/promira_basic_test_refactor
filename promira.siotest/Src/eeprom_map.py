
import collections as coll
from psutil.tests.test_linux import SECTOR_SIZE


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



MICROCHIP_EEPROM_BLOCKS = [
              [KB8, 4],
              [KB32, 1],
              [KB64, 31],
              [KB32, 1],
              [KB8, 4] ]

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
  
  
  def fatalError(self, reason):
    self.m_testutil.fatalError(reason)
    
  def __init__(self, block_map:BlockMap):
    
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
          self.m_sector_status.append(SECSTAT_UNKNOWN)

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
  
  def _sectorStatusSetting(self, write_status):
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
    return self.m_sector_status[self.sectorIndex(address)]

  def setSectorWriteStatus(self, address, write_status):
    if write_status in WRITESTAT_CODES:
      self.m_sector_status[self.sectorIndex(address)]=self._sectorStatusSetting(write_status)
  
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
        self.m_sector_status[sector_index]=self._sectorStatusSetting(write_status)
      

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
    
    