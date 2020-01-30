from __future__ import division, with_statement, print_function
import promact_is_py as pmact
import collections as coll
from test_utility import testUtil
import test_utility as testutil


'''
SPI Command Byte Codes
'''

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
RBSQI_WRAP=   0x0C
RBSPI_WRAP=   0xEC
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

'''
Command Categories
'''

IOTYPE_NONE = 0
IOTYPE_READ = 1
IOTYPE_WRITE= 2

READ_DATA_CMDS  =   [RDSR, RDCR, READ, HSREAD, SQOREAD, SQIOREAD,
                     SDOREAD, SDIOREAD, RBSQI_WRAP, RBSPI_WRAP,
                     JEDEC_ID, QUAD_JID, SFDP, RBPR, RSID ]

WRITE_DATA_CMDS =   [WRSR, SETBURST, PP, QPP, WBPR, NVWLDR, PSID]

NODATA_CMDS     =   [NOP, RSTEN, RSTMEM, ENQIO, RSTQIO, WREN, WRDI, SE, BE, CE, ULBPR]

WREN_REQUIRED   =   [ SE, BE, CE, PP, WRSR, PSID, LSID, WBPR, LBPR,
                     ULBPR, NVWLDR, QPP, WRSR]



'''
Inherit namedtuple and extend with defaults
for Python 2.7 onward
'''
def namedtupleX(typename, field_names, default_values=()):
    T = coll.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, coll.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T

'''
named tuples supporting command session management
'''
cmdPhx=coll.namedtuple("cmdPhx", "mode length")
addrPhx=coll.namedtuple("addrPhx", "mode length")
modePhx=coll.namedtuple("modePhx", "mode length")
dummyPhx=coll.namedtuple("dummyPhx", "mode length")
dataPhx=coll.namedtuple("dataPhx", "mode lengthSpec")
SpiCmdSpec=namedtupleX("SpiCmdSpec", "iowMax cmd mode address dummy data", [None, None, None, None, None, None])

LengthSpec=namedtupleX("LengthSpec", "fixed rangeMin rangeMax", [None, None, None])



dataSpec_1=LengthSpec(fixed=1)
dataSpec_2=LengthSpec(fixed=2)
dataSpec_3=LengthSpec(fixed=3)
dataSpec_1plus=LengthSpec(rangeMin=1)
dataSpec_2plus=LengthSpec(rangeMin=2)
dataSpec_3plus=LengthSpec(rangeMin=3)
dataSpec_page=LengthSpec(rangeMin=1, rangeMax=256)
dataSpec_Nplus=LengthSpec()
dataSpec_reg18=LengthSpec(rangeMin=1, rangeMax=18)
dataSpec_2K=LengthSpec(rangeMin=1, rangeMax=2048)


SPIIO_NONE = None
SPIIO_SINGLE = pmact.PS_SPI_IO_STANDARD
SPIIO_DUAL = pmact.PS_SPI_IO_DUAL
SPIIO_QUAD = pmact.PS_SPI_IO_QUAD
SPIIO_DUMMY= 1+max([SPIIO_SINGLE, SPIIO_DUAL, SPIIO_QUAD])

'''
Cmd Phase Specs
'''
w1CmdPhase=cmdPhx(mode=SPIIO_SINGLE, length=1)
w2CmdPhase=cmdPhx(mode=SPIIO_DUAL, length=1)
w4CmdPhase=cmdPhx(mode=SPIIO_QUAD, length=1)

'''
Address Phase Specs
'''
w1L3AddrPhase=addrPhx(mode=SPIIO_SINGLE, length=3)
w2L3AddrPhase=addrPhx(mode=SPIIO_DUAL, length=3)
w4L3AddrPhase=addrPhx(mode=SPIIO_QUAD, length=3)
w1L2AddrPhase=addrPhx(mode=SPIIO_SINGLE, length=2)
w2L2AddrPhase=addrPhx(mode=SPIIO_DUAL, length=2)
w4L2AddrPhase=addrPhx(mode=SPIIO_QUAD, length=2)


'''
Mode Phase Specs
'''
w1ModePhase=modePhx(mode=SPIIO_SINGLE, length=1)
w2ModePhase=modePhx(mode=SPIIO_DUAL, length=1)
w4ModePhase=modePhx(mode=SPIIO_QUAD, length=1)


'''
Dummy Phase Specs
'''
noDummyPhase=dummyPhx(mode=SPIIO_NONE, length=0)
x1DummyPhase=dummyPhx(mode=SPIIO_DUMMY, length=1)
x2DummyPhase=dummyPhx(mode=SPIIO_DUMMY, length=2)
x3DummyPhase=dummyPhx(mode=SPIIO_DUMMY, length=3)
x8DummyPhase=dummyPhx(mode=SPIIO_DUMMY, length=8)

'''
Single Mode Data Phase Specs
'''
w1Data_1=dataPhx(mode=SPIIO_SINGLE, lengthSpec=dataSpec_1)
w1Data_2=dataPhx(mode=SPIIO_SINGLE, lengthSpec=dataSpec_2)
w1Data_3=dataPhx(mode=SPIIO_SINGLE, lengthSpec=dataSpec_3)
w1Data_1plus=dataPhx(mode=SPIIO_SINGLE, lengthSpec=dataSpec_1plus)
w1Data_2plus=dataPhx(mode=SPIIO_SINGLE, lengthSpec=dataSpec_2plus)
w1Data_3plus=dataPhx(mode=SPIIO_SINGLE, lengthSpec=dataSpec_3plus)
w1Data_page=dataPhx(mode=SPIIO_SINGLE, lengthSpec=dataSpec_page)
w1Data_Nplus=dataPhx(mode=SPIIO_SINGLE, lengthSpec=dataSpec_Nplus)
w1Data_reg18=dataPhx(mode=SPIIO_SINGLE, lengthSpec=dataSpec_reg18)
w1Data_2K=dataPhx(mode=SPIIO_SINGLE, lengthSpec=dataSpec_2K)

'''
Dual Mode Data Phase Specs
'''
w2Data_1=dataPhx(mode=SPIIO_DUAL, lengthSpec=dataSpec_1)
w2Data_2=dataPhx(mode=SPIIO_DUAL, lengthSpec=dataSpec_2)
w2Data_3=dataPhx(mode=SPIIO_DUAL, lengthSpec=dataSpec_3)
w2Data_1plus=dataPhx(mode=SPIIO_DUAL, lengthSpec=dataSpec_1plus)
w2Data_2plus=dataPhx(mode=SPIIO_DUAL, lengthSpec=dataSpec_2plus)
w2Data_3plus=dataPhx(mode=SPIIO_DUAL, lengthSpec=dataSpec_3plus)
w2Data_page=dataPhx(mode=SPIIO_DUAL, lengthSpec=dataSpec_page)
w2Data_Nplus=dataPhx(mode=SPIIO_DUAL, lengthSpec=dataSpec_Nplus)
w2Data_reg18=dataPhx(mode=SPIIO_DUAL, lengthSpec=dataSpec_reg18)
w2Data_2K=dataPhx(mode=SPIIO_DUAL, lengthSpec=dataSpec_2K)
'''
Quad Mode Data Phase Specs
'''
w4Data_1=dataPhx(mode=SPIIO_QUAD, lengthSpec=dataSpec_1)
w4Data_2=dataPhx(mode=SPIIO_QUAD, lengthSpec=dataSpec_2)
w4Data_3=dataPhx(mode=SPIIO_QUAD, lengthSpec=dataSpec_3)
w4Data_1plus=dataPhx(mode=SPIIO_QUAD, lengthSpec=dataSpec_1plus)
w4Data_2plus=dataPhx(mode=SPIIO_QUAD, lengthSpec=dataSpec_2plus)
w4Data_3plus=dataPhx(mode=SPIIO_QUAD, lengthSpec=dataSpec_3plus)
w4Data_page=dataPhx(mode=SPIIO_QUAD, lengthSpec=dataSpec_page)
w4Data_Nplus=dataPhx(mode=SPIIO_QUAD, lengthSpec=dataSpec_Nplus)
w4Data_reg18=dataPhx(mode=SPIIO_QUAD, lengthSpec=dataSpec_reg18)
w4Data_2K=dataPhx(mode=SPIIO_QUAD, lengthSpec=dataSpec_2K)  



SPICMDTYPE_00=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase)
SPICMDTYPE_01=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase)
SPICMDTYPE_02=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, data=w1Data_1plus)
SPICMDTYPE_03=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, data=w4Data_1plus)
SPICMDTYPE_04=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, data=w1Data_2)
SPICMDTYPE_05=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, data=w4Data_2)
SPICMDTYPE_06=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, address=w1L3AddrPhase, data=w1Data_1plus)
SPICMDTYPE_07=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, address=w1L3AddrPhase, dummy=x3DummyPhase, data=w4Data_1plus)
SPICMDTYPE_08=SpiCmdSpec(iowMax=SPIIO_DUAL,    cmd=w1CmdPhase, address=w1L3AddrPhase, dummy=x1DummyPhase, data=w2Data_1plus)
SPICMDTYPE_09=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, data=w1Data_1)
SPICMDTYPE_0A=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, data=w4Data_1)
SPICMDTYPE_0B=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, address=w1L3AddrPhase, dummy=x3DummyPhase, data=w1Data_Nplus)
SPICMDTYPE_0C=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, address=w4L3AddrPhase, dummy=x3DummyPhase, data=w4Data_Nplus)
SPICMDTYPE_0D=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, data=w1Data_3plus)
SPICMDTYPE_0E=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, data=w4Data_3plus)
SPICMDTYPE_0F=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, address=w4L3AddrPhase, dummy=x1DummyPhase, data=w4Data_1plus)
SPICMDTYPE_10=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, address=w1L3AddrPhase, dummy=x1DummyPhase, data=w1Data_1plus)
SPICMDTYPE_11=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, address=w4L3AddrPhase, dummy=x1DummyPhase, data=w4Data_1plus)
SPICMDTYPE_12=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, address=w1L3AddrPhase)
SPICMDTYPE_13=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, address=w4L3AddrPhase)
SPICMDTYPE_14=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, address=w1L3AddrPhase, data=w1Data_page)
SPICMDTYPE_15=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, address=w4L3AddrPhase, data=w4Data_page)  
SPICMDTYPE_16=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, data=w1Data_reg18)
SPICMDTYPE_17=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, data=w4Data_reg18)  
SPICMDTYPE_18=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, address=w1L2AddrPhase, dummy=x1DummyPhase, data=w1Data_2K)
SPICMDTYPE_19=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, address=w4L2AddrPhase, dummy=x1DummyPhase, data=w4Data_2K)
SPICMDTYPE_1A=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, address=w1L2AddrPhase, data=w1Data_page)
SPICMDTYPE_1B=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, address=w4L2AddrPhase, data=w4Data_page)
SPICMDTYPE_1C=SpiCmdSpec(iowMax=SPIIO_DUAL,    cmd=w1CmdPhase, address=w2L3AddrPhase, data=w2Data_1plus)
SPICMDTYPE_1D=SpiCmdSpec(iowMax=SPIIO_DUAL,    cmd=w1CmdPhase, address=w1L3AddrPhase, dummy=x8DummyPhase, data=w2Data_1plus)
SPICMDTYPE_1E=SpiCmdSpec(iowMax=SPIIO_QUAD,    cmd=w4CmdPhase, mode=w1ModePhase,      dummy=x1DummyPhase, data=w4Data_2)





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
PHASE_SPECS_19 = [SPICMDTYPE_1E]
PHASE_SPECS_1A = [SPICMDTYPE_10]




SPICMD_NOP        = [NOP,       0,            IOTYPE_NONE]
SPICMD_RSTEN      = [RSTEN,     0,            IOTYPE_NONE]
SPICMD_RSTMEM     = [RSTMEM,    0,            IOTYPE_NONE]
SPICMD_ENQIO      = [ENQIO,     1,            IOTYPE_NONE]
SPICMD_RSTQIO     = [RSTQIO,    0,            IOTYPE_NONE]
SPICMD_RDSR       = [RDSR,      [2, 3],       IOTYPE_READ]
SPICMD_WRSR       = [WRSR,      4,            IOTYPE_WRITE]
SPICMD_RDCR       = [RDCR,      [2, 3],       IOTYPE_READ]
SPICMD_READ       = [READ,      5,            IOTYPE_READ]
SPICMD_HSREAD     = [HSREAD,    [0x1A, 0x19],    IOTYPE_READ]
SPICMD_SQOREAD    = [SQOREAD,   7,            IOTYPE_READ]
SPICMD_SQIOREAD   = [SQIOREAD,  6,            IOTYPE_READ]
SPICMD_SDOREAD    = [SDOREAD,   7,            IOTYPE_READ]
SPICMD_SDOREADX   = [SDOREAD,   0x18,         IOTYPE_READ]
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


PHASE_SPECS = [ PHASE_SPECS_0, PHASE_SPECS_1, PHASE_SPECS_2, PHASE_SPECS_3, PHASE_SPECS_4,
              PHASE_SPECS_5, PHASE_SPECS_6, PHASE_SPECS_7, PHASE_SPECS_8, PHASE_SPECS_9,
              PHASE_SPECS_A, PHASE_SPECS_B, PHASE_SPECS_C, PHASE_SPECS_D, PHASE_SPECS_E,
              PHASE_SPECS_F, PHASE_SPECS_10, PHASE_SPECS_11, PHASE_SPECS_12,
              PHASE_SPECS_13, PHASE_SPECS_14, PHASE_SPECS_15, PHASE_SPECS_16, PHASE_SPECS_17,
              PHASE_SPECS_18, PHASE_SPECS_19, PHASE_SPECS_1A]


  
  
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
    # ->SpiCmdSpec
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
    return self.m_descriptor.iowMax
  
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
      if cmdspec.iowMax==iomode:
        return cmdspec
  
  testUtil().fatalError("io mode forbidden")

