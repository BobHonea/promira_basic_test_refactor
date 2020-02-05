'''
Created on Feb 3, 2020

@author: honea
'''

import collections as coll


chip_mcn25QL=0
chip_mcn25QU=1
chip_mcc26VF=2
chip_mcn25QL_XX=3
chip_mcn25QU_XX=4

devConfig=coll.namedtuple('devConfig', 'jedec vdd memsize chip_id mfgr chip_type')


mcn8MB3V3  =devConfig(jedec=[0xBF, 0x26, 0x42], vdd=3.3, memsize=0x400000, chip_id=chip_mcc26VF, mfgr='Microchip', chip_type='SST26VF032B')  
mcc1MB3V3  =devConfig(jedec=[0x20, 0xBA, 0x17], vdd=3.3, memsize=0x100000, chip_id=chip_mcn25QL, mfgr='Micron', chip_type='MT25QLxxxABA')
mcc2MB3V3  =devConfig(jedec=[0x20, 0xBA, 0x18], vdd=3.3, memsize=0x200000, chip_id=chip_mcn25QL, mfgr='Micron', chip_type='MT25QLxxxABA')
mcc4MB3V3  =devConfig(jedec=[0x20, 0xBA, 0x19], vdd=3.3, memsize=0x400000, chip_id=chip_mcn25QL, mfgr='Micron', chip_type='MT25QLxxxABA')
mcc8MB3V3  =devConfig(jedec=[0x20, 0xBA, 0x20], vdd=3.3, memsize=0x800000, chip_id=chip_mcn25QL, mfgr='Micron', chip_type='MT25QLxxxABA')
mcc16MB3V3 =devConfig(jedec=[0x20, 0xBA, 0x21], vdd=3.3, memsize=0x1000000,chip_id=chip_mcn25QL, mfgr='Micron', chip_type='MT25QLxxxABA')
mcc32MB3V3 =devConfig(jedec=[0x20, 0xBA, 0x22], vdd=3.3, memsize=0x2000000,chip_id=chip_mcn25QL, mfgr='Micron', chip_type='MT25QLxxxABA')
mcc1MB1V8  =devConfig(jedec=[0x20, 0xBB, 0x17], vdd=1.8, memsize=0x100000, chip_id=chip_mcn25QU, mfgr='Micron', chip_type='MT25QUxxxABA')
mcc2MB1V8  =devConfig(jedec=[0x20, 0xBB, 0x18], vdd=1.8, memsize=0x200000, chip_id=chip_mcn25QU, mfgr='Micron', chip_type='MT25QUxxxABA')
mcc4MB1V8  =devConfig(jedec=[0x20, 0xBB, 0x19], vdd=1.8, memsize=0x400000, chip_id=chip_mcn25QU, mfgr='Micron', chip_type='MT25QUxxxABA')
mcc8MB1V8  =devConfig(jedec=[0x20, 0xBB, 0x20], vdd=1.8, memsize=0x800000, chip_id=chip_mcn25QU, mfgr='Micron', chip_type='MT25QUxxxABA')
mcc16MB1V8 =devConfig(jedec=[0x20, 0xBB, 0x21], vdd=1.8, memsize=0x1000000,chip_id=chip_mcn25QU, mfgr='Micron', chip_type='MT25QUxxxABA')
mcc32MB1V8 =devConfig(jedec=[0x20, 0xBB, 0x22], vdd=1.8, memsize=0x2000000,chip_id=chip_mcn25QU, mfgr='Micron', chip_type='MT25QUxxxABA')
gdmcc8MB3V3=devConfig(jedec=[0xFF, 0x00, 0x01], vdd=3.3, memsize=0x800000, chip_id=chip_mcn25QL_XX, mfgr='Google', chip_type='Unknown')
gdmcc32MB1V8=devConfig(jedec=[0xFF, 0x00, 0x02], vdd=1.8, memsize=0x2000000, chip_id=chip_mcn25QL_XX, mfgr='Google', chip_type='Unknown')  
            
eepromDevices=[mcn8MB3V3,
               mcc1MB3V3, mcc2MB3V3, mcc4MB3V3, mcc8MB3V3, mcc16MB3V3, mcc32MB3V3,
               mcc1MB1V8, mcc2MB1V8, mcc4MB1V8, mcc8MB1V8, mcc16MB1V8, mcc32MB1V8,
               gdmcc8MB3V3, gdmcc32MB1V8]

'''
There are three types of EEPROMs targeted:
   MT25QU256ABA   3V Supply Single/Dual/Quad I/0 64MB->2GB EEPROM
   MT25QL128ABA 1.8V Supply Single/Dual/Quad I/0 64MB->2GB EEPROM
   
'''

micronStatus=coll.namedtuple('micronStatus', 'flag_status nv_config v_config   enh_v_config')
