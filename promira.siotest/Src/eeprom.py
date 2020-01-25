import array
import test_utility as testutil
import sys
import promact_is_py as pmact
import collections as coll
import spi_io as spiio

import spi_cfg_mgr as spicfg
import cmd_protocol as protocol

class eeprom:
  
  EEPROM_PROTECT_BITMAP_SIZE = 18
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
    self.m_testutil     = testutil.testUtil()
    self.m_spiio        = spiio.spiIO()
    self.enumerateBlocks()

  
  def getobjectSpiIO(self):
    return self.m_spiio
  
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
  
  def doJedecTest(self, cmd_byte):  
    rxdata_array=array.ArrayType('B', [0]*3)
    spi_result = self.m_spiio.spiMasterMultimodeCmd(cmd_byte, None, 3, rxdata_array)
    if spi_result.xfer_length != 3:
      print("error: jedec read")
      sys.exit()

    jedec_id = [0xBF, 0x26, 0x42]
    for index in range(len(jedec_id)):
      if jedec_id[index] != rxdata_array[index]:
        return False
    
    return True

  
  def testQuadJedec(self):
    return self.doJedecTest(protocol.SPICMD_QUAD_JID)
  
  def testJedec(self):
    return self.doJedecTest(protocol.SPICMD_JEDEC_ID)
  

            
  def testNOP(self):
    result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_NOP)
    return result==0
  
  EESTATUS_BUSY1 = 0x1
  EESTATUS_W_ENABLE_LATCH = 0x2
  EESTATUS_W_SUSPEND_ERASE = 0x4
  EESTATUS_W_SUSPEND_PROGRAM = 0x8
  EESTATUS_W_PROTECT_LOCKDOWN = 0x10
  EESTATUS_SECURITY_ID = 0x20
  EESTATUS_RESERVED = 0x40
  EESTATUS_BUSY80 = 0x80
  EESTATUS_READ_ERROR = 0x8000
  
  def statusBusy(self):
    self.readStatusRegister()
    return ((self.m_eepromStatus & self.EESTATUS_BUSY1) != 0)
  
  def waitUntilNotBusy(self):
    while self.statusBusy():
      continue
    return
  
  def readStatusRegister(self):
    data_array = pmact.array_u08(1)
    
    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RDSR,
                                                            None,
                                                            len(data_array),
                                                            data_array)
    self.m_eepromStatus = None
    data_in_length=spi_result.xfer_length
    
    if data_in_length>=1:
      #offset=len(data_array)-data_in_length
      self.m_eepromStatus = data_array[0]
      return self.m_eepromStatus
    
    self.m_testutil.fatalError("ReadStatusRegister error")
    return self.EESTATUS_READ_ERROR
    
  def readData(self, read_address, read_length, read_array):

    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_READ,
                                                            read_address, read_length, read_array)
    data_in_length = spi_result.xfer_length
    
    if data_in_length==read_length:
      return True
    self.m_testutil.fatalError("SpiReadData error")

  def readDataDual(self, read_address, read_length, read_array):

#    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_SDOREAD,
    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_SDOREADX,
                                                           read_address,
                                                           read_length,
                                                           read_array)

    result_length = spi_result.xfer_length
    
    if result_length==read_length:
      return True
    self.m_testutil.fatalError("SpiReadDual error")    



  def writeEnable(self):
    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_WREN)
    return spi_result.success

  
  def readBlockProtectBitmap(self):
    self.m_block_protect_bitmap = pmact.array_u08(18)
    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RBPR,
                                                            None, len(self.m_block_protect_bitmap),
                                                            self.m_block_protect_bitmap)
    data_in_length=spi_result.xfer_length
    if data_in_length==18:
      return True
    else:
      self.m_testutil.fatalError("Protect Bitmap Read fail")

  
  def getBlockProtectBitmap(self):
    return self.m_block_protect_bitmap

  def setBlockProtectBitmap(self, bitmap):
    if type(bitmap)==array.ArrayType and len(bitmap) == self.EEPROM_PROTECT_BITMAP_SIZE:
      self.m_block_protect_bitmap=bitmap
    else:
      self.m_testutil.fatalError("Unsupported Bitmap Array Size")

  def eraseSector(self, sector_address):
    if (sector_address & ~(self.EEPROM_SECTOR_SIZE-1)) != sector_address:
      self.m_testutil.fatalError("sector address error")

    self.waitUntilNotBusy()
          

    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_SE, sector_address)
    return spi_result.success

      
  def updateWithinPage(self, write_address, write_length, write_array):
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
    
    if self.eraseSector(sector_address) == False:
      return False
    
    if self.writeWithinPage(write_address, write_length, write_array) == False:
      return False
    
    return True

  
  def writeWithinPage(self, write_address, write_length, write_array):
    # Update one page per function use
    start_page = write_address // self.EEPROM_PAGE_SIZE
    end_page = (write_address + (write_length - 1)) // self.EEPROM_PAGE_SIZE
    if start_page != end_page:
      self.m_testutil.fatalError("Page Write Spans Pages")

    self.waitUntilNotBusy()
    
    spi_result =self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_PP,
                                                         write_address, write_length, write_array)
    result_length=spi_result.xfer_length
    return (result_length == write_length)


  def globalUnlock(self):
    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_ULBPR)
    return spi_result.success
    
    self.m_testutil.fatalError("SpiGlobalUnlock error")
  
  
  def writeBlockProtectBitmap(self):
    if ( type(self.m_block_protect_bitmap) == array.ArrayType and 
              len(self.m_block_protect_bitmap)==18):
      spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_WBPR,
                                                             None, len(self.m_block_protect_bitmap),
                                                             self.m_block_protect_bitmap)
      if spi_result.xfer_length>=len(self.m_block_protect_bitmap):
        return True
      
    self.m_testutil.fatalError("protect bitmap write failure")
  
  
  '''
  setTargetPowerVoltages
     Promira supplies two distinct power rails.
     pins 2 and 4 (vtgt1, vtgt2) supply either 3.3 or 5.0 v
     pins 22, and 24 (vtgt3, vtgt4) supply a voltage in the range 0.9 to 3.45 v
     the latter takes a 32bit float, instead of an integer setting code.
  '''

    
