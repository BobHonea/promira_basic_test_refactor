import array
import collections as coll
import test_utility as testutil
import promact_is_py as pmact

import spi_io as spiio
import cmd_protocol_2 as protocol
import eeprom_devices
import eeprom_map




PWR_3_3V = 3.3
PWR_1_8V = 1.8





class eepromAPI:
  
  EEPROM_PROTECT_BITMAP_SIZE = 18
  EEPROM_PAGE_SIZE = 0x100
  EEPROM_SECTOR_SIZE = 0x1000
  EEPROM_SIZE = 0x400000
  

 
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
  
  m_testutil        = None
  m_jedec_id        = None
  m_device_map      = None
  m_devconfig       = None
  m_spiio           = None
  m_micron_status   = None
  m_4byte_addr_mode = None

  
  def __init__(self):
    self.m_testutil     = testutil.testUtil()
    self.m_spiio        = spiio.spiIO()
    self.m_4byte_addr_mode = False



  
  def getobjectSpiIO(self):
    return self.m_spiio
  
  
  def configure(self):
    self.testJedec()

    mfgrname=self.m_devconfig.mfgr
    #chipname=self.m_devconfig.chip_type
    #memsize_MB=self.m_devconfig.memsize/(1024*1024)
    if mfgrname.upper() == 'MICRON':
      self.m_device_map=eeprom_map.deviceMap(eeprom_map.MICRON_EEPROM_BLOCKS)
    elif mfgrname.upper() == 'MICROCHIP':
      self.m_device_map=eeprom_map.deviceMap(eeprom_map.MICROCHIP_EEPROM_BLOCKS)
    else:
      self.m_testutil.fatalError("Unrecognized EEPROM")
    
    self.m_testutil.bufferDetailInfo("Block/Sector Maps for %s initialized" % mfgrname, True)  
    
      
    
      
  def doJedecTest(self, cmd_byte):  
    rxdata_array=array.ArrayType('B', [0]*3)
    spi_result = self.m_spiio.spiMasterMultimodeCmd(cmd_byte, None, 3, rxdata_array)
    if spi_result.xfer_length != 3:
      self.m_testutil.fatalError("error: jedec read")

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
  
  def nvConfigStatus(self,mask, shift, read_now=False):
    register_bytes=array.ArrayType('B', [0]*2)
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RNVCFG, None, 2, register_bytes)
    register=register_bytes[0]+ register_bytes[1]*256    
    return (register >>  shift) & mask
  
  BitField=coll.namedtuple('BitField', 'mask shift')

  nvcfg_bitfield__not_long_address  = BitField(mask=0b1,   shift=0)
  nvcfg_bitfield__not_dual_io       = BitField(mask=0b1,   shift=1)
  nvcfg_bitfield__not_quad_io       = BitField(mask=0b1,   shift=2)
  nvcfg_bitfield__hldrst_disabled   = BitField(mask=0b1,   shift=3)
  nvcfg_bitfield__dtr_disabled      = BitField(mask=0b1,   shift=4)
  nvcfg_bitfield__rsthld_disabled   = BitField(mask=0b1,   shift=5)
  nvcfg_bitfield__drv_strength      = BitField(mask=0b111, shift=6)
  nvcfg_bitfield__xip_mode          = BitField(mask=0b111, shift=9)
  nvcfg_bitfield__dummy_clock_cycles= BitField(mask=0b111, shift=12)
      
  def update_nvcfg_bitfield(self, field:BitField, field_value):
    register_bytes=array.ArrayType('B', [0]*2)
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RNVCFG, None, 2, register_bytes)
    register=register_bytes[0]+ register_bytes[1]*256
    register = register &  ~(field.mask << field.shift)
    register = register | (field_value << field.shift)
    register_bytes[0]=register&0xff
    register_bytes[1]=register//256
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_WNVCFG, None, 2, register_bytes)
    return 

  
  def setLongAddressMode(self, enable_long_addresses):
    self.update_nvcfg_bitfield(self.nvcfg_bitfield__not_long_address, 0)
    self.m_4byte_addr_mode=self.longAddressMode()
    return self.m_4byte_addr_mode
    pass
  


    
  def dualIoModeEnabled(self):
    field=self.nvcfg_bitfield__not_dual_io
    return not self.nvConfigStatus(field.mask, field.shift)
  
  def quadIoModeEnabled(self):
    field=self.nvcfg_bitfield__not_quad_io
    return not self.nvConfigStatus(field.mask, field.shift)
  
  def holdResetDisabled(self):
    field=self.nvcfg_bitfield__hldrst_disabled
    return not self.nvConfigStatus(field.mask, field.shift)
  
  def dtrIoModeEnabled(self):
    field=self.nvcfg_bitfield__dtr_disabled
    return not self.nvConfigStatus(field.mask, field.shift)
  
  def longAddressMode(self):
    field=self.nvcfg_bitfield__not_long_address
    return not self.nvConfigStatus(field.mask, field.shift)
  
  def driverStrength(self):
    field=self.nvcfg_bitfield__drv_strength
    return self.nvConfigStatus(field.mask, field.shift)
  
  def xipIoMode(self):
    field=self.nvcfg_bitfield__xip_mode
    return self.nvConfigStatus(field.mask, field.shift)
    
  def dummyCycles(self):
    field=self.nvcfg_bitfield__xip_mode
    cycle_code=self.nvConfigStatus(field.mask, field.shift)
    
    if cycle_code == 0xf:
      cycle_code = 0
    return cycle_code
    
  
  def readMicronStatusRegisters(self):
    if self.m_devconfig.mfgr!='Micron':
      self.m_testutil.fatalError("Micron Tech. Devices Only")
      
    status_val=array.ArrayType('B', [0])
    status_val2=array.ArrayType('B', [0, 0])
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RFLAG, None, 1, status_val)
    flagstatus=status_val[0]
    
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RNVCFG, None, 2, status_val2)
    nvconfig=  status_val2[0] + (status_val2[1]*256)
    
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RVCFG, None, 1, status_val)
    vconfig=status_val[0]
    
    _spi_result=self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_RENHVCFG, None, 1, status_val)
    enhvconfig=status_val[0]
    
    self.m_micron_status=eeprom_devices.micronStatus(flag_status=flagstatus, nv_config=nvconfig, v_config=vconfig, enh_v_config=enhvconfig)
    return self.m_micron_status
    
  def readData(self, read_address, read_length, read_array):
    if self.m_4byte_addr_mode:
      read_cmd=protocol.SPICMD_READ4A
    else:
      read_cmd=protocol.SPICMD_READ
  
    spi_result = self.m_spiio.spiMasterMultimodeCmd(  read_cmd,
                                                      read_address,
                                                      read_length,
                                                      read_array)
    data_in_length = spi_result.xfer_length
    
    if data_in_length==read_length:
      return True
    self.m_testutil.fatalError("SpiReadData error")
    

  def highspeedReadData(self, read_address, read_length, read_array):
    if self.m_4byte_addr_mode:
      hsread_cmd=protocol.SPICMD_HSREAD4A
    else:
      hsread_cmd=protocol.SPICMD_HSREAD
      
    spi_result = self.m_spiio.spiMasterMultimodeCmd(  hsread_cmd,
                                                      read_address,
                                                      read_length,
                                                      read_array)
    data_in_length = spi_result.xfer_length
    
    if data_in_length==read_length:
      return True
    
    self.m_testutil.fatalError("SpiReadData error")


  def readDataDual(self, read_address, read_length, read_array):

#    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_SDOREAD,
    if self.m_4byte_addr_mode:
      dual_read_cmd=protocol.SPICMD_SDOREAD4A
    else:
      dual_read_cmd=protocol.SPICMD_SDOREAD
      
    spi_result = self.m_spiio.spiMasterMultimodeCmd(dual_read_cmd,
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

  def eraseSector(self, address):
    if self.m_device_map.sectorWriteStatus(address) == eeprom_map.WRITESTAT_ERASED:
      return True
    
    self.waitUntilNotBusy()
    sector_address=self.m_device_map.sectorAddress(address)
    if self.m_4byte_addr_mode:
      se_cmd=protocol.SPICMD_SE4A
    else:
      se_cmd=protocol.SPICMD_SE
      
    spi_result = self.m_spiio.spiMasterMultimodeCmd(se_cmd, sector_address)

    if spi_result.success:
      self.m_device_map.setSectorWriteStatus(sector_address, eeprom_map.WRITESTAT_ERASED)
      
    return spi_result.success


  def eraseBlock(self, address):
    if self.m_device_map.blockWriteStatus(address) == eeprom_map.WRITESTAT_ERASED:
      return True
    
    block_address = self.m_device_map.blockAddress(address)
    self.waitUntilNotBusy()
          
    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_BE, block_address)
    if spi_result.success:
      self.m_device_map.setBlockWriteStatus(block_address, eeprom_map.WRITESTAT_ERASED)
      
    return spi_result.success
      
      
  '''
  Write Data, Erasing as we go.
  Sector Oriented Algorithm: smallest universally avialble size is 4Kbytes (sector)
  
    Split write array into slices of array along sector boundaries
    Per slice, verify the pages affected are writable
    When not writable - erase the sector bearing the data
    
    CAVEAT: pre-existing sector data that is not addressed by the slice
    will be lost to the erasure!
      example 1: a gap exists between the sector start and the slice start.
      example 2: a gap exists between the sector end, and the slice end.
      outcome1: data written in that gap is lost: written gap pages.
      outcome2: the gap is unwritten, no data is lost: gap pages were unwritten.
      
  Efficiency ?:
    the deviceMap keeps track of data status on a page granularity, even though
    pages cannot be singly erased.
    when a write ends in the middle of a sector, and a later writes are limited
    to unwritten pages in that sector, the full sector need not be erased.
    
    this permits writing to the eeprom with contiguous commands WITHOUT minding
    whether the boundaries of the write commands is on sector boundaries.
  '''    

  '''
  Algorithm:
    catalog write segments along sector boundaries
    for each sub-sector: 
        verify pages-to-be-written are writable
          if fractional-write of sector
               verify sectors-to-be-written are writable
        else flag the sector for erasure
        
    erase flagged sub-sectors
    
    write entire data bloc
  '''
  SectorSlice=coll.namedtuple('SectorSlice', 'sector_address write_offset array_offset length')
  
  def writePages(self, write_address, write_length, write_array):
    # pre-erase any sectors, as needed


    sector_slices=[]
    erase_sectors=[]
    start_write_address=write_address
    end_write_address=write_address+write_length-1
    
    while start_write_address <= end_write_address:
      sectr_address= self.m_device_map.sectorAddress(start_write_address)
      sectr_offset = start_write_address-sectr_address
      
      slice_length  = min([ eeprom_map.SECTOR_SIZE-sectr_offset,
                            end_write_address-start_write_address+1 ])

      sector_slices.append(self.SectorSlice(
        sector_address = sectr_address,
        write_offset  = sectr_offset,
        array_offset   = start_write_address-write_address,
        length         = slice_length))

      start_write_address+=slice_length

    # what sectors to erase
    for sector_slice in sector_slices:
      start_address=write_address+sector_slice.array_offset
      end_address=start_address+sector_slice.length-1

      if sector_slice.length != eeprom_map.SECTOR_SIZE:
        writestatus=self.m_device_map.subSectorWriteStatus(start_address, end_address)
      else:
        writestatus=self.m_device_map.sectorWriteStatus(sector_slice.sector_address)

      if writestatus!=eeprom_map.WRITESTAT_ERASED:
        erase_sectors.append(sector_slice.sector_address)
        
    # erase WRITTEN sectors
    for sector_address in erase_sectors:
      if self.eraseSector(sector_address):
        continue
      else:
        return False


    '''
    All erasure is complete
    Write data out page-by-page
    '''
    written_length=0
    for sector_slice in sector_slices:
      sector_write_address=sector_slice.sector_address+sector_slice.write_offset
      sector_write_length=sector_slice.length
      sector_array=write_array[written_length:written_length+sector_write_length]
      
      if self.writeWithinSector(sector_write_address, sector_write_length, sector_array):
        return False
      
      written_length+=sector_write_length

    return True

  
  def writeWithinSector(self, write_address, write_length, write_array):
    # Update one page per function use
    page_address = self.m_device_map.pageAddress(write_address)
    end_page_address = self.m_device_map.pageAddress(write_address+write_length-1)
    
    while page_address <= end_page_address:
      self.m_device_map.setPageDirty(write_address)      
      page_address+=eeprom_map.PAGE_SIZE
      
    self.waitUntilNotBusy()
    if self.m_4byte_addr_mode:
      page_program_cmd=protocol.SPICMD_PP4A
    else:
      page_program_cmd=protocol.SPICMD_PP
      
    spi_result =self.m_spiio.spiMasterMultimodeCmd(page_program_cmd,
                                                   write_address,
                                                   write_length,
                                                   write_array)

    result_length=spi_result.xfer_length
    return (result_length == write_length)

  
  
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

  def globalUnlock(self):
    spi_result = self.m_spiio.spiMasterMultimodeCmd(protocol.SPICMD_ULBPR)
    return spi_result.success
    
    self.m_testutil.fatalError("SpiGlobalUnlock error")
  
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

    
