import array
import test_utility as testutil
import sys
import promact_is_py as pmact

class eeprom:
  
  EEPROM_PAGE_SIZE = 0x100
  EEPROM_SECTOR_SIZE = 0x1000
  EEPROM_SIZE = 0x400000
  
  KB8 = 0x2000
  KB32 = 0x8000
  KB64 = 0x10000
  # 4 8KB BLOCKS FROM ADDRESS 0
  # 1 32KB BLOCKS FROM ADDRESS 0x8000
  # 32 64KB BLOCKS FROM ADDRESS 0x10000
  # 1 32BLOCK FROM ADDRESS 0x3F0000
  # 4 8KB BLOCKS FROM ADDRESS 0x3F8000
  
  MEM_ADDRESS = 0
  MEM_BLOCKSIZE = 1
  MEM_BLOCKCOUNT = 2
  
  EEPROM_BLOCKS = [[0x0, KB8, 4],
                 [0x8000, KB32, 1],
                 [0x10000, KB64, 31],
                 [0x3F0000, KB32, 1],
                 [0x3F8000, KB8, 4],
                 [0x400000, 0, 0]]
  
  ENUMERATED_BLOCKS = []
  
  m_testutil=None
  
  def __init__(self):
    self.m_instantiator = testutil.singletonInstantiator()
    self.m_testutil     = self.m_instantiator.getTestUtil()

    self.enumerateBlocks()

  
  def enumerateBlocks(self):
    for blockset in self.EEPROM_BLOCKS:
      address = blockset[0]
      if address == self.EEPROM_SIZE:
        break;
      blocksize = blockset[1]
      blockcount = blockset[2]
      enumeration_address = address
      
      for _index in range(blockcount):
        self.ENUMERATED_BLOCKS.append([enumeration_address, blocksize])
        enumeration_address += blocksize
        pass
      pass
    return
  
  
  
  def eepromSpiTestQuadJedec(self):
    result_tuple = self.spi_master_multimode_cmd(self.SPICMD_QUAD_JID, None, 3, self.m_rxdata_array)
    if result_tuple[0] < 3:
      print("error: jedec read")
      sys.exit()

    self.m_rxdata_array = result_tuple[1][1:]
      
    jedec_id = [0xBF, 0x26, 0x42]
    for index in range(len(jedec_id)):
      if jedec_id[index] != self.m_rxdata_array[index]:
        return False
    
    return True

          
  def eepromSpiTestNOP(self):
    result = self.spi_master_multimode_cmd(self.SPICMD_NOP)
    return result==1
  
  EESTATUS_BUSY1 = 0x1
  EESTATUS_W_ENABLE_LATCH = 0x2
  EESTATUS_W_SUSPEND_ERASE = 0x4
  EESTATUS_W_SUSPEND_PROGRAM = 0x8
  EESTATUS_W_PROTECT_LOCKDOWN = 0x10
  EESTATUS_SECURITY_ID = 0x20
  EESTATUS_RESERVED = 0x40
  EESTATUS_BUSY80 = 0x80
  EESTATUS_READ_ERROR = 0x8000
  
  def eepromSpiStatusBusy(self):
    self.eepromSpiStatusReadStatusRegister()
    return ((self.m_eepromStatus & self.EESTATUS_BUSY1) != 0)
  
  def eepromSpiWaitUntilNotBusy(self):
    while self.eepromSpiStatusBusy():
      print(",")
      continue
    return
  
  def eepromSpiStatusReadStatusRegister(self):
    data_array = pmact.array_u08(1)
    
    data_in_length = self.spi_master_multimode_cmd(self.SPICMD_RDSR, None, len(data_array), data_array)
    self.m_eepromStatus = None
    if data_in_length>=1:
      #offset=len(data_array)-data_in_length
      self.m_eepromStatus = data_array[0]
      return self.m_eepromStatus
    
    self.m_testutil.fatalError("ReadStatusRegister error")
    return self.EESTATUS_READ_ERROR
    
  def eepromSpiReadData(self, read_address, read_length, read_array):

    data_in_length = self.spi_master_multimode_cmd(self.SPICMD_READ, read_address, read_length, read_array)
    if data_in_length==read_length:
      return True
    self.m_testutil.fatalError("SpiReadData error")

  def eepromSpiReadDataDual(self, read_address, read_length, read_array):

    result_length = self.spi_master_multimode_cmd(self.SPICMD_SDOREAD, read_address, read_length, read_array)

    if result_length==read_length:
      return True
    self.m_testutil.fatalError("SpiReadDual error")    



  def eepromSpiWriteEnable(self):
    result_tuple = self.spi_master_multimode_cmd(self.SPICMD_WREN)
    return (result_tuple == 1)

  
  def eepromSpiReadProtectBitmap(self):
    self.m_eeprom_protect_bitmap = pmact.array_u08(18)
    data_in_length = self.spi_master_multimode_cmd(self.SPICMD_RBPR, None, len(self.m_eeprom_protect_bitmap), self.m_eeprom_protect_bitmap)
    if data_in_length==18:
      return True
    else:
      self.m_testutil.fatalError("Protect Bitmap Read fail")
  
  def eepromSpiEraseSector(self, sector_address):
    if (sector_address & ~(self.EEPROM_SECTOR_SIZE-1)) != sector_address:
      self.m_testutil.fatalError("sector address error")

    self.eepromSpiWaitUntilNotBusy()
          

    result_length = self.spi_master_multimode_cmd(self.SPICMD_SE, sector_address)
    return True

      
  def eepromSpiUpdateWithinPage(self, write_address, write_length, write_array):
    # Update one page per function use
    # This function erases a sector EVERY TIME it is used
    # Proves erase-before-write works, but NOT EFFICIENT
    
    # Page level checks
    start_page = write_address // self.EEPROM_PAGE_SIZE
    end_page = (write_address + (write_length - 1)) // self.EEPROM_PAGE_SIZE
    if start_page != end_page:
      self.m_testutil.fatalError("Page Write Spans Pages")
      
    # Sector level check & Sector Erase + Page Write
    sector_size_mask = self.EEPROM_SECTOR_SIZE - 1
    sector_address = write_address & ~sector_size_mask
    sector_offset = write_address & sector_size_mask
    
    if self.eepromSpiEraseSector(sector_address) == False:
      return False
    
    if self.eepromSpiWriteWithinPage(write_address, write_length, write_array) == False:
      return False
    
    return True

  
  def eepromSpiWriteWithinPage(self, write_address, write_length, write_array):
    # Update one page per function use
    start_page = write_address // self.EEPROM_PAGE_SIZE
    end_page = (write_address + (write_length - 1)) // self.EEPROM_PAGE_SIZE
    if start_page != end_page:
      self.m_testutil.fatalError("Page Write Spans Pages")

    self.eepromSpiWaitUntilNotBusy()
    
    result_length =self.spi_master_multimode_cmd(self.SPICMD_PP, write_address, write_length, write_array)
    return (result_length == write_length)


  def eepromSpiGlobalUnlock(self):
    result_length = self.spi_master_multimode_cmd(self.SPICMD_ULBPR)
    if result_length==1:
      return True
    
    self.m_testutil.fatalError("SpiGlobalUnlock error")
  
  
  def eepromWriteProtectBitmap(self):
    if ( type(self.m_eeprom_protect_bitmap) == array.ArrayType and 
              len(self.m_eeprom_protect_bitmap)==18):
      result_length = self.spi_master_multimode_cmd(self.SPICMD_WBPR, None, len(self.m_eeprom_protect_bitmap), self.m_eeprom_protect_bitmap)
      if result_length>=len(self.m_eeprom_protect_bitmap):
        return True
      
    self.m_testutil.fatalError("protect bitmap write failure")
  
