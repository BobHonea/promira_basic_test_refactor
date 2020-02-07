from __future__ import division, with_statement, print_function
import promact_is_py as pmact
import collections as coll
from test_utility import testUtil
import test_utility as testutil


'''
Command Categories
'''

IOTYPE_NONE = 0
IOTYPE_READ = 1
IOTYPE_WRITE= 2


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
busyPhx=coll.namedtuple("busyPhx", "mode busy_bit")
wrenPhx=coll.namedtuple("wrenPhx", "mode")
cmdPhx=coll.namedtuple("cmdPhx", "mode")
addrPhx=coll.namedtuple("addrPhx", "mode length")
modePhx=coll.namedtuple("modePhx", "mode length")
dummyPhx=coll.namedtuple("dummyPhx", "mode length")
dataPhx=coll.namedtuple("dataPhx", "mode lengthSpec")

SpiCmdSpec=namedtupleX("SpiCmdSpec", "iowMax busy_wait send_wren cmd mode address dummy data", [None, None, None, None, None, None, None, None])


LengthSpec=namedtupleX("LengthSpec", "fixed burstMode rangeMin rangeMax", [None, False, None, None])
dataSpec_1=LengthSpec(fixed=1)
dataSpec_2=LengthSpec(fixed=2)
dataSpec_3=LengthSpec(fixed=3)
dataSpec_1plus=LengthSpec(rangeMin=1)
dataSpec_2plus=LengthSpec(rangeMin=2)
dataSpec_3plus=LengthSpec(rangeMin=3)
dataSpec_page=LengthSpec(rangeMin=1, rangeMax=256)
dataSpec_Nplus=LengthSpec(burstMode=True)
dataSpec_reg18=LengthSpec(rangeMin=1, rangeMax=18)
dataSpec_2K=LengthSpec(rangeMin=1, rangeMax=2048)


SPIIO_NONE = None
SPIIO_SINGLE = pmact.PS_SPI_IO_STANDARD
SPIIO_DUAL = pmact.PS_SPI_IO_DUAL
SPIIO_QUAD = pmact.PS_SPI_IO_QUAD
SPIIO_DUMMY= 1+max([SPIIO_SINGLE, SPIIO_DUAL, SPIIO_QUAD])


'''
BusyWait Phase Specs
'''
w1BusyWait=busyPhx(mode=SPIIO_SINGLE, busy_bit=0b00000001)
w2BusyWait=busyPhx(mode=SPIIO_DUAL, busy_bit=0b00000001)
w4BusyWait=busyPhx(mode=SPIIO_QUAD, busy_bit=0b00000001)



'''
Wren Phase Specs
'''

w1WrenPhase=wrenPhx(mode=SPIIO_SINGLE)
w2WrenPhase=wrenPhx(mode=SPIIO_DUAL)
w4WrenPhase=wrenPhx(mode=SPIIO_QUAD)

OPTIONAL_PHASES = [ [SPIIO_SINGLE, w1BusyWait, w1WrenPhase],
                    [SPIIO_DUAL, w2BusyWait, w2WrenPhase],
                    [SPIIO_QUAD, w4BusyWait, w4WrenPhase]]


'''
Cmd Phase Specs
'''
w1CmdPhase=cmdPhx(mode=SPIIO_SINGLE)
w2CmdPhase=cmdPhx(mode=SPIIO_DUAL)
w4CmdPhase=cmdPhx(mode=SPIIO_QUAD)

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
SPICMDTYPE_1F=SpiCmdSpec(iowMax=SPIIO_SINGLE,  cmd=w1CmdPhase, data=w1Data_2plus)

