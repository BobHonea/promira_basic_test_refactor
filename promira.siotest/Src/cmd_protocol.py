from __future__ import division, with_statement, print_function
import promact_is_py as pmact
import collections
from test_utility import testUtil
import test_utility as testutil




'''
named tuples supporting command session management
'''
CmdPhaseSpec=collections.namedtuple("CmdPhaseSpec", "mode length")
AddrPhaseSpec=collections.namedtuple("AddrPhaseSpec", "mode length")
DummyPhaseSpec=collections.namedtuple("DummyPhaseSpec", "mode length")
DataPhaseSpec=collections.namedtuple("DataPhaseSpec", "mode lengthSpec")
SpiCmdType=collections.namedtuple("SpiCmdType", "max_iowidth cmd address dummy data")


LengthSpec=collections.namedtuple("LengthSpec", "fixed rangeMin rangeMax")
dlengthSpec_1=LengthSpec(fixed=1, rangeMin=None, rangeMax=None)
dlengthSpec_2=LengthSpec(fixed=2, rangeMin=None, rangeMax=None)
dlengthSpec_3=LengthSpec(fixed=3, rangeMin=None, rangeMax=None)
dlengthSpec_1plus=LengthSpec(fixed=None, rangeMin=1, rangeMax=None)
dlengthSpec_2plus=LengthSpec(fixed=None, rangeMin=2, rangeMax=None)
dlengthSpec_3plus=LengthSpec(fixed=None, rangeMin=3, rangeMax=None)
dlengthSpec_page=LengthSpec(fixed=None, rangeMin=1, rangeMax=256)
dlengthSpec_Nplus=LengthSpec(fixed=None, rangeMin=None, rangeMax=None)
dlengthSpec_reg18=LengthSpec(fixed=None, rangeMin=1, rangeMax=18)
dlengthSpec_2K=LengthSpec(fixed=None, rangeMin=1, rangeMax=2048)


SPIIO_NONE = None
SPIIO_SINGLE = pmact.PS_SPI_IO_STANDARD
SPIIO_DUAL = pmact.PS_SPI_IO_DUAL
SPIIO_QUAD = pmact.PS_SPI_IO_QUAD
SPIIO_DUMMY= 1+max([SPIIO_SINGLE, SPIIO_DUAL, SPIIO_QUAD])

'''
Cmd Phase Specs
'''
singleCmdPhase=CmdPhaseSpec(mode=SPIIO_SINGLE, length=1)
dualCmdPhase=CmdPhaseSpec(mode=SPIIO_DUAL, length=1)
quadCmdPhase=CmdPhaseSpec(mode=SPIIO_QUAD, length=1)

'''
Address Phase Specs
'''
singleAddrPhase=AddrPhaseSpec(mode=SPIIO_SINGLE, length=3)
dualAddrPhase=AddrPhaseSpec(mode=SPIIO_DUAL, length=3)
quadAddrPhase=AddrPhaseSpec(mode=SPIIO_QUAD, length=3)
single2ByteAddrPhase=AddrPhaseSpec(mode=SPIIO_SINGLE, length=2)
dual2ByteAddrPhase=AddrPhaseSpec(mode=SPIIO_DUAL, length=2)
quad2ByteAddrPhase=AddrPhaseSpec(mode=SPIIO_QUAD, length=2)

'''
Dummy Phase Specs
'''
noDummyPhase=DummyPhaseSpec(mode=SPIIO_NONE, length=0)
oneCycleDummyPhase=DummyPhaseSpec(mode=SPIIO_DUMMY, length=1)
twoCycleDummyPhase=DummyPhaseSpec(mode=SPIIO_DUMMY, length=2)
threeCycleDummyPhase=DummyPhaseSpec(mode=SPIIO_DUMMY, length=3)
eightCycleDummyPhase=DummyPhaseSpec(mode=SPIIO_DUMMY, length=8)

'''
Single Mode Data Phase Specs
'''
singleData_1=DataPhaseSpec(mode=SPIIO_SINGLE, lengthSpec=dlengthSpec_1)
singleData_2=DataPhaseSpec(mode=SPIIO_SINGLE, lengthSpec=dlengthSpec_2)
singleData_3=DataPhaseSpec(mode=SPIIO_SINGLE, lengthSpec=dlengthSpec_3)
singleData_1plus=DataPhaseSpec(mode=SPIIO_SINGLE, lengthSpec=dlengthSpec_1plus)
singleData_2plus=DataPhaseSpec(mode=SPIIO_SINGLE, lengthSpec=dlengthSpec_2plus)
singleData_3plus=DataPhaseSpec(mode=SPIIO_SINGLE, lengthSpec=dlengthSpec_3plus)
singleData_page=DataPhaseSpec(mode=SPIIO_SINGLE, lengthSpec=dlengthSpec_page)
singleData_Nplus=DataPhaseSpec(mode=SPIIO_SINGLE, lengthSpec=dlengthSpec_Nplus)
singleData_reg18=DataPhaseSpec(mode=SPIIO_SINGLE, lengthSpec=dlengthSpec_reg18)
singleData_2K=DataPhaseSpec(mode=SPIIO_SINGLE, lengthSpec=dlengthSpec_2K)

'''
Dual Mode Data Phase Specs
'''
dualData_1=DataPhaseSpec(mode=SPIIO_DUAL, lengthSpec=dlengthSpec_1)
dualData_2=DataPhaseSpec(mode=SPIIO_DUAL, lengthSpec=dlengthSpec_2)
dualData_3=DataPhaseSpec(mode=SPIIO_DUAL, lengthSpec=dlengthSpec_3)
dualData_1plus=DataPhaseSpec(mode=SPIIO_DUAL, lengthSpec=dlengthSpec_1plus)
dualData_2plus=DataPhaseSpec(mode=SPIIO_DUAL, lengthSpec=dlengthSpec_2plus)
dualData_3plus=DataPhaseSpec(mode=SPIIO_DUAL, lengthSpec=dlengthSpec_3plus)
dualData_page=DataPhaseSpec(mode=SPIIO_DUAL, lengthSpec=dlengthSpec_page)
dualData_Nplus=DataPhaseSpec(mode=SPIIO_DUAL, lengthSpec=dlengthSpec_Nplus)
dualData_reg18=DataPhaseSpec(mode=SPIIO_DUAL, lengthSpec=dlengthSpec_reg18)
dualData_2K=DataPhaseSpec(mode=SPIIO_DUAL, lengthSpec=dlengthSpec_2K)
'''
Quad Mode Data Phase Specs
'''
quadData_1=DataPhaseSpec(mode=SPIIO_QUAD, lengthSpec=dlengthSpec_1)
quadData_2=DataPhaseSpec(mode=SPIIO_QUAD, lengthSpec=dlengthSpec_2)
quadData_3=DataPhaseSpec(mode=SPIIO_QUAD, lengthSpec=dlengthSpec_3)
quadData_1plus=DataPhaseSpec(mode=SPIIO_QUAD, lengthSpec=dlengthSpec_1plus)
quadData_2plus=DataPhaseSpec(mode=SPIIO_QUAD, lengthSpec=dlengthSpec_2plus)
quadData_3plus=DataPhaseSpec(mode=SPIIO_QUAD, lengthSpec=dlengthSpec_3plus)
quadData_page=DataPhaseSpec(mode=SPIIO_QUAD, lengthSpec=dlengthSpec_page)
quadData_Nplus=DataPhaseSpec(mode=SPIIO_QUAD, lengthSpec=dlengthSpec_Nplus)
quadData_reg18=DataPhaseSpec(mode=SPIIO_QUAD, lengthSpec=dlengthSpec_reg18)
quadData_2K=DataPhaseSpec(mode=SPIIO_QUAD, lengthSpec=dlengthSpec_2K)  



SPICMDTYPE_00=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=None, dummy=None, data=None)
SPICMDTYPE_01=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=None, dummy=None, data=None)
SPICMDTYPE_02=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=None, dummy=None, data=singleData_1plus)
SPICMDTYPE_03=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=None, dummy=None, data=quadData_1plus)
SPICMDTYPE_04=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=None, dummy=None, data=singleData_2)
SPICMDTYPE_05=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=None, dummy=None, data=quadData_2)
SPICMDTYPE_06=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=singleAddrPhase, dummy=None, data=singleData_1plus)
SPICMDTYPE_07=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=singleAddrPhase, dummy=threeCycleDummyPhase, data=quadData_1plus)
SPICMDTYPE_08=SpiCmdType(max_iowidth=SPIIO_DUAL, cmd=singleCmdPhase, address=singleAddrPhase, dummy=oneCycleDummyPhase, data=dualData_1plus)
SPICMDTYPE_09=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=None, dummy=None, data=singleData_1)
SPICMDTYPE_0A=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=None, dummy=None, data=quadData_1)
SPICMDTYPE_0B=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=singleAddrPhase, dummy=threeCycleDummyPhase, data=singleData_Nplus)
SPICMDTYPE_0C=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=quadAddrPhase, dummy=threeCycleDummyPhase, data=quadData_Nplus)
SPICMDTYPE_0D=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=None, dummy=None, data=singleData_3plus)
SPICMDTYPE_0E=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=None, dummy=None, data=quadData_3plus)
SPICMDTYPE_0F=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=quadAddrPhase, dummy=oneCycleDummyPhase, data=quadData_1plus)
SPICMDTYPE_10=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=singleAddrPhase, dummy=oneCycleDummyPhase, data=singleData_1plus)
SPICMDTYPE_11=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=quadAddrPhase, dummy=oneCycleDummyPhase, data=quadData_1plus)
SPICMDTYPE_12=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=singleAddrPhase, dummy=None, data=None)
SPICMDTYPE_13=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=quadAddrPhase, dummy=None, data=None)
SPICMDTYPE_14=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=singleAddrPhase, dummy=None, data=singleData_page)
SPICMDTYPE_15=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=quadAddrPhase, dummy=None, data=quadData_page)  
SPICMDTYPE_16=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=None, dummy=None, data=singleData_reg18)
SPICMDTYPE_17=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=None, dummy=None, data=quadData_reg18)  
SPICMDTYPE_18=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=single2ByteAddrPhase, dummy=oneCycleDummyPhase, data=singleData_2K)
SPICMDTYPE_19=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=quad2ByteAddrPhase, dummy=oneCycleDummyPhase, data=quadData_2K)
SPICMDTYPE_1A=SpiCmdType(max_iowidth=SPIIO_SINGLE, cmd=singleCmdPhase, address=single2ByteAddrPhase, dummy=None, data=singleData_page)
SPICMDTYPE_1B=SpiCmdType(max_iowidth=SPIIO_QUAD, cmd=quadCmdPhase, address=quad2ByteAddrPhase, dummy=None, data=quadData_page)

SPICMDTYPE_1D=SpiCmdType(max_iowidth=SPIIO_DUAL, cmd=singleCmdPhase, address=singleAddrPhase, dummy=eightCycleDummyPhase, data=dualData_1plus)



'''
TODO!!!
SDIOREAD is more complicated than SDOREAD
Figure out **for sure** how it is supposed to work.
Not a priority now, so *TODO*
'''
# begin spec for SDIOREAD transaction
SPICMDTYPE_1C=SpiCmdType(max_iowidth=SPIIO_DUAL, cmd=singleCmdPhase, address=dualAddrPhase, dummy=None, data=dualData_1plus)
# end spec for SDIOREAD transaction  

PHASE_SPECS_0 = [SPICMDTYPE_00]#, SPICMDTYPE_01]
PHASE_SPECS_1 = [SPICMDTYPE_01]
PHASE_SPECS_2 = [SPICMDTYPE_02]
PHASE_SPECS_3 = [SPICMDTYPE_03]
PHASE_SPECS_4 = [SPICMDTYPE_02, SPICMDTYPE_03]
PHASE_SPECS_5 = [SPICMDTYPE_06]
PHASE_SPECS_6 = [SPICMDTYPE_07]
PHASE_SPECS_7 = [SPICMDTYPE_08]
PHASE_SPECS_8 = [SPICMDTYPE_09, SPICMDTYPE_0A]
PHASE_SPECS_9 = [SPICMDTYPE_0C]
PHASE_SPECS_A = [SPICMDTYPE_0B]
PHASE_SPECS_B = [SPICMDTYPE_0D]
PHASE_SPECS_C = [SPICMDTYPE_0E]
PHASE_SPECS_D = [SPICMDTYPE_11]
PHASE_SPECS_E = [SPICMDTYPE_12, SPICMDTYPE_13]
PHASE_SPECS_F = [SPICMDTYPE_14, SPICMDTYPE_15]
PHASE_SPECS_10 = [SPICMDTYPE_14]
PHASE_SPECS_11 = [SPICMDTYPE_16]
PHASE_SPECS_12 = [SPICMDTYPE_17]
PHASE_SPECS_13 = [SPICMDTYPE_16, SPICMDTYPE_17]
PHASE_SPECS_14 = [SPICMDTYPE_18]
PHASE_SPECS_15 = [SPICMDTYPE_19]
PHASE_SPECS_16 = [SPICMDTYPE_1A, SPICMDTYPE_1B]
PHASE_SPECS_17 = [SPICMDTYPE_1C] # SDIOREAD
PHASE_SPECS_18 = [SPICMDTYPE_1D] # SDOREADX

NOP       =   0x00
RSTEN     =   0x66
RSTMEM    =   0x99
ENQIO     =   0x38
RSTQIO    =   0xFF
RDSR      =   0x05
WRSR      =   0x01
RDCR      =   0x35
READ      =   0x03
HSREAD    =   0x0B
SQOREAD   =   0x6B
SQIOREAD  =   0xEB
SDOREAD   =   0x3B
SDIOREAD  =   0xBB
SETBURST  =   0xC0
RBSQI_WRAP = 0x0C
RBSPI_WRAP = 0xEC
JEDEC_ID  =   0x9F
QUAD_JID  =   0xAF
SFDP      =   0x5A
WREN      =   0x06
WRDI      =   0x04
SE        =   0x20
BE        =   0xD8
CE        =   0xC7
PP        =   0x02
QPP       =   0x32
WRSU      =   0xB0
WRRE      =   0x30
RBPR      =   0x72
WBPR      =   0x42
LBPR      =   0x8D
NVWLDR    =   0xE8
ULBPR     =   0x98
RSID      =   0x88
PSID      =   0xA5
LSID      =   0x85

READ_DATA_CMDS =  [RDSR, RDCR, READ, HSREAD, SQOREAD, SQIOREAD,
                  SDOREAD, SDIOREAD, RBSQI_WRAP, RBSPI_WRAP,
                  JEDEC_ID, QUAD_JID, SFDP, RBPR, RSID ]
WRITE_DATA_CMDS=  [WRSR, SETBURST, PP, QPP, WBPR, NVWLDR, PSID]
NODATA_CMDS    =  [NOP, RSTEN, RSTMEM, ENQIO, RSTQIO, WREN, WRDI, SE, BE, CE, ULBPR]


IOTYPE_NONE = 0
IOTYPE_READ = 1
IOTYPE_WRITE= 2


SPICMD_NOP        = [NOP,       0,            IOTYPE_NONE]
SPICMD_RSTEN      = [RSTEN,     0,            IOTYPE_NONE]
SPICMD_RSTMEM     = [RSTMEM,    0,            IOTYPE_NONE]
SPICMD_ENQIO      = [ENQIO,     1,            IOTYPE_NONE]
SPICMD_RSTQIO     = [RSTQIO,    0,            IOTYPE_NONE]
SPICMD_RDSR       = [RDSR,      [2, 3],       IOTYPE_READ]
SPICMD_WRSR       = [WRSR,      4,            IOTYPE_WRITE]
SPICMD_RDCR       = [RDCR,      [2, 3],       IOTYPE_READ]
SPICMD_READ       = [READ,      5,            IOTYPE_READ]
SPICMD_HSREAD     = [HSREAD,    [6, 7],       IOTYPE_READ]
SPICMD_SQOREAD    = [SQOREAD,   7,            IOTYPE_READ]
SPICMD_SQIOREAD   = [SQIOREAD,  6,            IOTYPE_READ]
SPICMD_SDOREAD    = [SDOREAD,   7,            IOTYPE_READ]
SPICMD_SDOREADX   = [SDOREAD,   0x18,           IOTYPE_READ]
SPICMD_SDIOREAD   = [SDIOREAD,  7,            IOTYPE_READ]
SPICMD_SETBURST   = [SETBURST,  8,            IOTYPE_WRITE]
SPICMD_RBSQI_WRAP = [RBSQI_WRAP,9,            IOTYPE_READ]
SPICMD_RBSPI_WRAP = [RBSPI_WRAP,0x0A,         IOTYPE_READ]
SPICMD_JEDEC_ID   = [JEDEC_ID,  0x0B,         IOTYPE_READ]
SPICMD_QUAD_JID   = [QUAD_JID,  0x0C,         IOTYPE_READ]
SPICMD_SFDP       = [SFDP,      0x0D,         IOTYPE_READ ]
SPICMD_WREN       = [WREN,      0,            IOTYPE_NONE]
SPICMD_WRDI       = [WRDI,      0,            IOTYPE_NONE]
SPICMD_SE         = [SE,        0x0E,         IOTYPE_NONE]
SPICMD_BE         = [BE,        0x0E,         IOTYPE_NONE]
SPICMD_CE         = [CE,        0,            IOTYPE_NONE]
SPICMD_PP         = [PP,        0x0F,         IOTYPE_WRITE]
SPICMD_QPP        = [QPP,       0x10,         IOTYPE_WRITE]
SPICMD_WRSU       = [WRSU,      0,            IOTYPE_NONE]
SPICMD_WRRE       = [WRRE,      0,            IOTYPE_NONE]
SPICMD_RBPR       = [RBPR,      [0x11, 0x12], IOTYPE_READ]
SPICMD_WBPR       = [WBPR,      0x13,         IOTYPE_WRITE]
SPICMD_LBPR       = [LBPR,      0,            IOTYPE_NONE]
SPICMD_NVWLDR     = [NVWLDR,    0x13,         IOTYPE_WRITE]
SPICMD_ULBPR      = [ULBPR,     0,            IOTYPE_NONE]
SPICMD_RSID       = [RSID,      [0x14, 0x15], IOTYPE_READ]
SPICMD_PSID       = [PSID,      0x16,         IOTYPE_WRITE]
SPICMD_LSID       = [LSID,      0,            IOTYPE_NONE]

SPI_CMDSPECS = [ SPICMD_NOP, SPICMD_RSTEN, SPICMD_RSTMEM,
                 SPICMD_ENQIO, SPICMD_RSTQIO, SPICMD_RDSR,
                 SPICMD_WRSR, SPICMD_RDCR, SPICMD_READ,
                 SPICMD_HSREAD, SPICMD_SQOREAD, SPICMD_SQIOREAD,
                 SPICMD_SDOREAD, SPICMD_SDIOREAD, SPICMD_SETBURST,
                 SPICMD_RBSQI_WRAP, SPICMD_RBSPI_WRAP,
                 SPICMD_JEDEC_ID, SPICMD_QUAD_JID, SPICMD_SFDP,
                 SPICMD_WREN, SPICMD_WRDI, SPICMD_SE, SPICMD_BE,
                 SPICMD_CE, SPICMD_PP, SPICMD_QPP, SPICMD_WRSU,
                 SPICMD_WRRE, SPICMD_RBPR, SPICMD_WBPR, SPICMD_LBPR,
                 SPICMD_NVWLDR, SPICMD_ULBPR, SPICMD_RSID,
                 SPICMD_PSID, SPICMD_LSID, SPICMD_SDOREADX ] 

WREN_REQUIRED = [ SE, BE, CE, PP, WRSR, PSID, LSID, WBPR, LBPR,
                  ULBPR, NVWLDR, QPP, WRSR]

PHASE_SPECS = [ PHASE_SPECS_0, PHASE_SPECS_1, PHASE_SPECS_2, PHASE_SPECS_3, PHASE_SPECS_4,
              PHASE_SPECS_5, PHASE_SPECS_6, PHASE_SPECS_7, PHASE_SPECS_8, PHASE_SPECS_9,
              PHASE_SPECS_A, PHASE_SPECS_B, PHASE_SPECS_C, PHASE_SPECS_D, PHASE_SPECS_E,
              PHASE_SPECS_F, PHASE_SPECS_10, PHASE_SPECS_11, PHASE_SPECS_12,
              PHASE_SPECS_13, PHASE_SPECS_14, PHASE_SPECS_15, PHASE_SPECS_16, PHASE_SPECS_17, PHASE_SPECS_18]


 


'''
spi_master_multimode_cmd()

  perform single-byte commands, data writing commands, data reading commands
  up to 1 to 3 of 4 different transaction phases are implemented in a call
'''
  
  
class spiTransaction:

  m_descriptor    = None
  m_phase_index   = None
  m_spi_phases    = None
  m_spi_phase     = None
  m_phase_count   = None
  m_phase         = None
  m_dummy_mode    = None
  m_prev_spi_phase= None
  m_testutil      = None
      
  def __init__(self, spi_cmd, spi_cmd_descriptor):
    # ->SpiCmdType
    self.m_spi_read_not_write=spi_cmd[2]
    self.m_descriptor=spi_cmd_descriptor
    self.m_testutil=testutil.testUtil()
    return
  
  def readNotWrite(self):
    return self.m_spi_read_not_write
  
  def setInitialPhase(self):
    self.m_spi_phases=[]
    for phase in [self.m_descriptor.cmd,
                  self.m_descriptor.address,
                  self.m_descriptor.dummy,
                  self.m_descriptor.data]:
      
      if phase!=None:
        self.m_spi_phases.append(phase)      
  
    if len(self.m_spi_phases)==0:
      self.m_testutil.fatalError("null command phase specification")
      
    self.m_spi_phase=self.m_spi_phases[0]
    self.m_phase_index=0
    self.m_phase_count=len(self.m_spi_phases)
    return True
    
  def nextSpiPhase(self):
    if not self.endOfSession():
      self.m_phase_index+=1
      self.m_prev_spi_phase=self.m_spi_phase
      self.m_spi_phase=self.m_spi_phases[self.m_phase_index]
      return True
    return False
  
  def currentSpiPhase(self):
    return self.m_spi_phase
  
  def prevSpiPhase(self):
    return self.m_prev_spi_phase
  
  def endOfSession(self):
    return self.m_phase_index+1 >= self.m_phase_count
  
  def ioModeContinues(self):
    next_phase_index=self.m_phase_index+1
    if next_phase_index<self.m_phase_count:
      nextphase=self.m_spi_phases[next_phase_index]
      '''
      dummy io mode always matches previous mode (ad hoc)
      dummy mode continues IFF previous mode matches nextmode
      '''
      if nextphase.mode == self.m_spi_phase.mode:
          return True
      elif nextphase.mode ==  self.m_protocol.promiraTestApp.SPIIO_DUMMY:
          self.m_dummy_mode=self.m_spi_phase.mode
          return True
      elif self.m_spi_phase.mode == self.m_protocol.promiraTestApp.SPIIO_DUMMY:
        return self.m_dummy_mode == nextphase.mode
    return False    
  
  def isCmdPhase(self):
    return self.m_spi_phase == self.m_descriptor.cmd
  
  def isAddressPhase(self):
    return self.m_spi_phase == self.m_descriptor.address
  
  def isDummyPhase(self):
    return self.m_spi_phase == self.m_descriptor.dummy
  
  def isDataPhase(self):
    return self.m_spi_phase == self.m_descriptor.data
  
  def peakIoWidth(self):
    return self.m_descriptor.max_iowidth
  
  def phaseSpec(self):
    return self.m_spi_phases[self.m_phase_index]



''' 
SPI IOMODE RESTRICTIONS AND PRECEDENCE

Some SPI Commands can be performed in more than one
io mode. Precedence/Restriction is used to select the
appropriate option.

This list of io modes establishes the preference order
of io modes. If an io mode is not listed, then it is 
forbidden.

the 0th item in the list is most preferred, and subsequent
items increasingly less preferred.
'''

IOMODES_SLOWER      = [SPIIO_SINGLE, SPIIO_DUAL, SPIIO_QUAD]
IOMODES_FASTER      = [SPIIO_QUAD, SPIIO_DUAL, SPIIO_SINGLE]
IOMODES_SINGLE      = [SPIIO_SINGLE]
IOMODES_SINGLE_DUAL = [SPIIO_SINGLE, SPIIO_DUAL]
IOMODES_DUAL_SINGLE = [SPIIO_DUAL, SPIIO_SINGLE]

m_spiio_mode_precedence = IOMODES_SLOWER


'''
precedent_cmdspec()
   based on the precedent io_mode list, select the cmd from
   the cmdspec list that is most preferred.
   beware! the precedent list may have not have the mode
   of ANY of the available cmdspec options.
   RETURN: preferred command, or NONE.
'''


def precedentCmdSpec(spi_cmd):
  
  # identify cmdspec list
  cmdspecs=[]
  if type(spi_cmd[1])==int:
    cmdspec_indices=[spi_cmd[1]]
  else:
    cmdspec_indices=spi_cmd[1]
  
  for index in cmdspec_indices:
    for cmdspec in PHASE_SPECS[index]:
      cmdspecs.append(cmdspec)
  
  # select cmdspec with most preferred iomode
  # cmdspec without a mode listed in precedence
  # is forbidden and rejected
  
  for iomode in m_spiio_mode_precedence:
    for cmdspec in cmdspecs:
      if cmdspec.max_iowidth==iomode:
        return cmdspec
  
  testUtil().fatalError("io mode forbidden")

