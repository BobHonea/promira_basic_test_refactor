import array
import test_utility as testutil
import sys
import promact_is_py as pmact

import spi_io as spiio
from spi_protocol import py as protocol
import eeprom_devices

class eepromAPI:
  
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


  
  PWR_3_3V = 3.3
  PWR_1_8V = 1.8

  


            
               
  EEPROM_BLOCKS = [[0x0, KB8, 4],
                 [0x8000, KB32, 1],
                 [0x10000, KB64, 31],
                 [0x3F0000, KB32, 1],
                 [0x3F8000, KB8, 4],
                 [0x400000, 0, 0]]
  
  ENUMERATED_BLOCKS = []

  
 
  '''
  EESTATUS_BUSY1 and EESTATUS_W_ENABLE_LATCH are the same
  status register bits for both Microchip and Micron devices.
  '''
  
  EESTATUS_BUSY1 = 0x1
  EESTATUS_W_ENABLE_LATCH = 0x2
  '''
  EESTATUS_W_SUSPEND_ERASE = 0x4
  EESTATUS_W_SUSPEND_PROGRAM = 0x8
  EESTATUS_W_PROTECT_LOCKDOWN = 0x10
  EESTATUS_SECURITY_ID = 0x20
  EESTATUS_RESERVED = 0x40
  EESTATUS_BUSY80 = 0x80
  '''
  EESTATUS_READ_ERROR = 0x8000
  
  m_testutil  = None
  m_jedec_id  = None
  m_devconfig = None
  m_spiio     = None
  m_micron_status = None

  
  def __init__(self):
    self.m_testutil     = testutil.testUtil()
    self.m_spiio        = spiio.spiIO()
    self.enumerateBlocks()


  
  def getobjectSpiIO(self):
    return self.m_spiio
  
  
  def configure(self):
    self.testJedec()
    
    
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

    return self.devConfigDefined(rxdata_array.tolist())
  
  '''
  verify the JEDEC ID of the device is in the targeted
  set of devices
  SAVE recognized JEDEC ID
  predefine the target eeprom + configuration if the jedec 
  id cannot be read.
  '''
  m_hard_code_eeprom_config = False
  
  def hardSetTgtEEPROM(self, eeprom_configuration):
    if eeprom_configuration != None:
      self.m_hard_code_eeprom_config = True
      self.m_devconfig = eeprom_configuration
    

  def devConfigDefined(self, jedec_id):
    if self.m_hard_code_eeprom_config:
      self.m_jedec_id=self.m_devconfig.jedec
      return True

    for devconfig in eeprom_devices.eepromDevices:
      dev_jedec=devconfig.jedec
      
      for index in range(3):
        if dev_jedec[index]!=jedec_id[index]:
          break
        elif index==2:
          self.m_devconfig=devconfig
          self.m_jedec_id=devconfig.jedec
          return True

    self.m_jedec_id=None
    return False
  
  def testQuadJedec(self):
    return self.doJedecTest(protocol.SPICMD_QUAD_JID)
  
  def testJedec(self):
    return self.doJedecTest(protocol.SPICMD_JEDEC_ID)
  
            
  def testNOP(self):
    result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_NOP)
    return result==0
  
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
  
  def nvConfigStatus(self,mask, shift):
    if self.m_micron_status==None:
      self.readMicronStatusRegisters()
    return (self.m_micron_status.nv_config & mask) >> shift
    
  
  def dtrStatus(self):
    return not self.nvConfigStatus(0b100000, 5)
  
  def dualStatus(self):
    return not self.nvConfigStatus(0b10, 1)
  
  def quadStatus(self):
    return not self.nvConfigStatus(0b1, 0)
  
  def readMicronStatusRegisters(self):
    if self.m_devconfig.mfgr!='Micron':
      self.m_testutil.fatalError("Micron Tech. Devices Only")
      
    status_val=array.ArrayType('B', [0])
    status_val2=array.ArrayType('B', [0, 0])
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RFLAG, None, 1, status_val)
    flagstatus=status_val[0]
    
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RNVCFG, None, 2, status_val2)
    nvconfig=  status_val2[0] + (int(status_val2[1])>>8)
    
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RVCFG, None, 1, status_val)
    vconfig=status_val[0]
    
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RENHVCFG, None, 1, status_val)
    enhvconfig=status_val[0]
    
    self.m_micron_status=eeprom_devices.micronStatus(flag_status=flagstatus, nv_config=nvconfig, v_config=vconfig, enh_v_config=enhvconfig)
    return self.m_micron_status
    
  def readData(self, read_address, read_length, read_array):

    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_READ,
                                                            read_address, read_length, read_array)
    data_in_length = spi_result.xfer_length
    
    if data_in_length==read_length:
      return True
    self.m_testutil.fatalError("SpiReadData error")
    

  def highspeedReadData(self, read_address, read_length, read_array):

    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_HSREAD,
                                                            read_address, read_length, read_array)
    data_in_length = spi_result.xfer_length
    
    if data_in_length==read_length:
      return True
    
    self.m_testutil.fatalError("SpiReadData error")


  def readDataDual(self, read_address, read_length, read_array):

#    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_SDOREAD,
    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_SDOREAD,
                                                           read_address,
                                                           read_length,
                                                           read_array)

    result_length = spi_result.xfer_length
    
    if result_length==read_length:
      return True
    self.m_testutil.fatalError("SpiReadDual error")    


  '''
  def writeEnable(self):
    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_WREN)
    return spi_result.success
  '''
  
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
  

  def unlockDevice(self):
    if self.m_devconfig.mfgr=='Micron':
      return self.unlockMicronDevice()
    
    if self.m_devconfig.mfgr=='Microchip':
      return self.unlockMicrochipDevice()
    
    self.m_testutil.fatalError('unrecognized device')
  
  def unlockMicronDevice(self):

    if self.globalUnlock() == False:
      self.m_testutil.fatalError("Global Unlock Command Failed")
      
    return True

  def unlockMicrochipDevice(self):

    debug=False
  
    if self.readBlockProtectBitmap() == False:
      self.m_testutil.fatalError("Protect Bitmap Read Failed")

    block_protect_bitmap=self.getBlockProtectBitmap()
          
    if debug:
      self.m_testutil.printArrayHexDump("Initial Protect Bitmap Array", block_protect_bitmap)

    if self.globalUnlock() == False:
      self.m_testutil.fatalError("Global Unlock Command Failed")
      
    if self.readBlockProtectBitmap() == False:
      self.m_testutil.fatalError("Protect Bitmap Read Failed")
      
    self.getBlockProtectBitmap()
    bitmap_sum = 0

    for entry in block_protect_bitmap:
      bitmap_sum += entry
  
    eeprom_unlocked= (bitmap_sum == 0)
       
    if not eeprom_unlocked:
      #self.m_testutil.fatalError("Global Unlock Failed")
      if debug:
        self.m_testutil.printArrayHexDump("Unlocked Protect Bitmap Array", block_protect_bitmap)

      self.setBlockProtectBitmap(self.m_testutil.zeroedArray(self.EEPROM_PROTECT_BITMAP_SIZE))
      if debug:
        self.m_testutil.printArrayHexDump("ZEROED Protect Bitmap Array", block_protect_bitmap)

      if ( self.writeBlockProtectBitmap()
        and self.readBlockProtectBitmap() ):
        block_protect_bitmap = self.getBlockProtectBitmap()
        if debug:
          self.m_testutil.printArrayHexDump("Post Update Protect Bitmap Array", block_protect_bitmap)
      else:
        self.m_testutil.fatalError("block protect bitmap acquisition failed")

        return True
  
  '''
  setTargetPowerVoltages
     Promira supplies two distinct power rails.
     pins 2 and 4 (vtgt1, vtgt2) supply either 3.3 or 5.0 v
     pins 22, and 24 (vtgt3, vtgt4) supply a voltage in the range 0.9 to 3.45 v
     the latter takes a 32bit float, instead of an integer setting code.
  '''

    
