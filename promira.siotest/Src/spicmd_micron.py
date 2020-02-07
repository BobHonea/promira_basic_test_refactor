'''
Created on Feb 5, 2020

@author: Asus
'''

class MyClass(object):
    '''
    classdocs
    '''




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
  '''
  Microchip LSID conflicts with Micron RVCFG
  TODO: Fix This Conflict!!
  '''
  LSID      =   0x85
  
  '''
  Micron Instructions
  '''  
  RNVCFG    =   0xB5
  RFLAG     =   0x70
  RVCFG     =   0x85
  RENHVCFG  =   0x65
  
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
  
  WREN_REQUIRED   =   [ SE, BE, CE, PP, WRSR, PSID, WBPR, LBPR,
                     ULBPR, NVWLDR, QPP] #LSID, removed for convflict with RNVCFG
  
  

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
  PHASE_SPECS_1B = [SPICMDTYPE_1F]
  
  
  
  
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
  #SPICMD_LSID       = [LSID,      0,            IOTYPE_NONE]
  SPICMD_RFLAG      = [RFLAG,     2,            IOTYPE_READ]
  SPICMD_RNVCFG     = [RNVCFG,    0x1B,         IOTYPE_READ]
  SPICMD_RVCFG      = [RVCFG,     2,            IOTYPE_READ]
  SPICMD_RENHVCFG   = [RENHVCFG,  2,            IOTYPE_READ]
  
  
  #READ FLAG STATUS REGISTER 70h 1-0-1 2-0-2 4-0-4 0 0 0 0 1 to ∞ –
  #READ NONVOLATILE CONFIGURATION REGISTER B5h 1-0-1 2-0-2 4-0-4 0 0 0 0 2 to ∞ –
  #READ VOLATILE CONFIGURATION REGISTER 85h 1-0-1 2-0-2 4-0-4 0 0 0 0 1 to ∞ –
  #READ ENHANCED VOLATILE CONFIGURATION REGISTER 65h 1-0-1 2-0-2 4-0-4 0 0 0 0 1 to ∞ –
  
  
  
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
                   SPICMD_PSID,
                   #SPICMD_LSID,  conflicts with R
                   SPICMD_SDOREADX, SPICMD_RNVCFG, SPICMD_RVCFG, SPICMD_RFLAG, SPICMD_RENHVCFG ] 
  
  
  PHASE_SPECS = [ PHASE_SPECS_0, PHASE_SPECS_1, PHASE_SPECS_2, PHASE_SPECS_3, PHASE_SPECS_4,
                PHASE_SPECS_5, PHASE_SPECS_6, PHASE_SPECS_7, PHASE_SPECS_8, PHASE_SPECS_9,
                PHASE_SPECS_A, PHASE_SPECS_B, PHASE_SPECS_C, PHASE_SPECS_D, PHASE_SPECS_E,
                PHASE_SPECS_F, PHASE_SPECS_10, PHASE_SPECS_11, PHASE_SPECS_12,
                PHASE_SPECS_13, PHASE_SPECS_14, PHASE_SPECS_15, PHASE_SPECS_16, PHASE_SPECS_17,
                PHASE_SPECS_18, PHASE_SPECS_19, PHASE_SPECS_1A, PHASE_SPECS_1B]




    def __init__(self, params):
        '''
        Constructor
        '''
        