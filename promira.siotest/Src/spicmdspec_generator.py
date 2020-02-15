'''
Created on Feb 8, 2020

@author: Asus
'''


'''
The buildup of the command tables of a SPI EEPROM driver is tedious
and hard to protect from errors during a manual compilation.

THIS AUTOMATED COMPILATION FROM THE CSV FILE WILL:

 0: DOCUMENT INTERPRETATION OF THE SPI EEPROM COMMAND TABLE
    any errors in interpretation can be found and corrected there.
    Corrections are propagated by invocation of this Generator.
    
    ELIMINATES obscuring mis-interpretations purely within source code.
    CAVEAT: sometimes, fuller understanding of the annotations is supported
    by an understanding of the source code.
    
 a: load table information from a text representation of the CSV table
    The CSV Table can be generated from a PDF data sheet.
    Additional editing is required for cleanup into useable format.
    
 b: analyze the command, address, dummy, and data phases of all commands
 c: compile a complete set of phase descriptors
 d: generate a complete set of transaction descriptors, built up from phase descriptors
 e: generate a complete set of SPI Command Specifications, assigning supporting
    assigning transaction descriptors to each command.
    
'''
import os, sys
import csv
import collections as coll
from zlib import crc32



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



busyPhx=coll.namedtuple("busyPhx", "mode busy_bit")
wrenPhx=coll.namedtuple("wrenPhx", "mode")
cmdPhx=coll.namedtuple("cmdPhx", "mode")
addrPhx=coll.namedtuple("addrPhx", "mode length")
modePhx=coll.namedtuple("modePhx", "mode length")
dummyPhx=coll.namedtuple("dummyPhx", "mode length")
dataPhx=coll.namedtuple("dataPhx", "mode burst min_length max_length")
SpiCmdSpec=namedtupleX("SpiCmdSpec", "spec_id iowMax busy_wait send_wren cmd mode address dummy data", [None, None, None, None, None, None, None, None, None])
cmdDescriptor=coll.namedtuple('cmdDescriptor', 'index mnemonic code iotype iowidth modephase')

IOTYPE_NODATA=0
IOTYPE_READ=1
IOTYPE_WRITE=2


class spiDescriptorApi(object):


  m_header            = ['mnemonic','description','cmd','spimode',
                         'sqimode','addrcycles','dummycycles',
                         'datamincycles','datamaxcycles','iotype', 'variant']
  
  _skip_line          = '#'
  _manufacturer       = 'manufacturer'
  _device             = 'device'
  _jedec_id           = 'jedec_id'
  _mem_size           = 'mem_size'
  _device_vdd         = 'device_vdd'
  _cmd_count          = 'cmd_count'
  _transcriber        = 'transcriber'
  _transcription_date    = 'transcription_date'
  _transcript_version = 'transcript_version'
  _compiler_version   = 'compiler_version'
  _comment            = 'comment'
  _legend             = 'legend'

  _table_header       = 'table_header'
  _table_data         = 'table_data'
  _table_end          = 'table_end'
  _table_crc32        = 'table_crc32'
  m_table_parameter_id= [ _skip_line, _manufacturer, _device, _jedec_id, _mem_size,
                          _device_vdd, _cmd_count, _transcriber, _transcription_date,
                          _transcript_version, _compiler_version, _comment, _legend]
  
  m_table_data_id     = [ _table_header, _table_data, _table_end, _table_crc32]
  
  m_header_valid      = None
  m_descriptor_csvfile= None
  m_descriptor_header = None
  m_descriptor_data   = None
  m_cmdphx_types      = None
  m_addrphx_types     = None
  m_dummyphx_types    = None
  m_dataphx_types     = None
  m_session_types     = None
  m_mnemonic_ndx      = None
  m_description_ndx   = None
  m_cmd_ndx           = None
  m_spimode_ndx       = None
  m_sqimode_ndx       = None
  m_addrcycles_ndx    = None
  m_dummycycles_ndx   = None
  m_datamincycles_ndx = None
  m_datamaxcycles_ndx = None
  m_iotype_ndx        = None

  m_phase_descriptor_tuplets     = None
  m_command_set       = None
  m_table_crc32       = None

  
  m_command_set       = None
  
  def __init__(self):
    pass
  
  def setDescriptorCsvFileName(self,filename):
    self.m_descriptor_csvfile=filename
    


  
  def processHeaderRow(self, csvrow):
    for column in range(len(csvrow)):
      if csvrow[column]!=self.m_header[column]:
        print("csv table error")
        sys.exit(-1)


    self.m_header_valid=True
    
    self.m_mnemonic_ndx=self.m_header.index('mnemonic')
    self.m_description_ndx=self.m_header.index('description')
    self.m_cmd_ndx=self.m_header.index('cmd')
    self.m_spimode_ndx=self.m_header.index('spimode')
    self.m_sqimode_ndx=self.m_header.index('sqimode')
    self.m_addrcycles_ndx=self.m_header.index('addrcycles')
    self.m_dummycycles_ndx=self.m_header.index('dummycycles')
    self.m_datamincycles_ndx=self.m_header.index('datamincycles')
    self.m_datamaxcycles_ndx=self.m_header.index('datamaxcycles')
    self.m_iotype_ndx=self.m_header.index('iotype')
    self.m_variant_ndx=self.m_header.index('variant')
    return
    
  def processTableRow(self, csvrow):
    if len(csvrow)!=len(self.m_header):
      print("csv data row error")
      sys.exit(-1)
      
    self.m_descriptor_data.append(csvrow)
  
  '''
  Parameter Processing is for Beta Level
  Currently in pre-alpha development
  '''
    
  m_command_count   = None
  _displayable_parameters = [ _manufacturer, _device, _jedec_id, _mem_size,
                             _device_vdd, _cmd_count, _compiler_version]
  def processParameter(self, csvrow):
    
    return
  
  def sumTableRow(self, row):
    rowtext=bytes(''.join(row),'utf-8')
    self.m_table_crc32=crc32(rowtext, 0)
    
  def processSumCheck(self, csvrow):

    print("table computed crc32= %04X" % self.m_table_crc32)

    if len(csvrow[0])>0:
      read_crc32=int(csvrow[0],16)
      print("table encoded crc32= %04X" % read_crc32)
      if read_crc32==self.m_table_crc32:
        print("GOOD NEWS: signed/computed crc32 values ARE EQUAL")
      else:
        print("BAD NEWS: signed/computed crc32 values ARE NOT EQUAL")
    else:
      print("UPDATE the input file with the computed CRC32")
 
  
  def loadDescriptorCSV(self):
    if type(self.m_descriptor_csvfile)==str:
      with open(self.m_descriptor_csvfile) as csvDataFile:
        self.m_descriptor_data=[]
        rowndx=0
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
          firstcolumn=str(row[0]).lower()
          if firstcolumn in self.m_table_parameter_id:
            self.processParameter(row) 
          elif firstcolumn in self.m_table_data_id:
            if firstcolumn==self._table_header:
              self.sumTableRow(row[1:])
              self.m_descriptor_header=row[1:]
              self.processHeaderRow(row[1:])
            elif firstcolumn==self._table_data:
              self.sumTableRow(row[1:])
              self.processTableRow(row[1:])
            elif firstcolumn==self._table_end:
              self.processSumCheck(row[1:])
              print('data intake processing complete')

          rowndx+=1
    else:
      print("fatal error: csvfile undefined")
      sys.exit(-1)
      
    pass



  def getWrenDescriptor(self, iowidth):
    for descriptor in self.m_wrenphx_types:
      if (descriptor.mode==iowidth):
        return descriptor
    return None
      
  def getDataDescriptor(self, iowidth, burst, datamin, datamax):
    for descriptor in self.m_dataphx_types:
      if (descriptor.mode==iowidth and descriptor.burst==burst
          and descriptor.datamin==datamin and descriptor.datamax==datamax):
        return descriptor
    return None
  
  def getModeDescriptor(self, iowidth):
    for descriptor in self.m_modephx_types:
      if (descriptor.mode==iowidth):
        return descriptor
    return None
    
  def getAddrDescriptor(self, iowidth, length ):
    for descriptor in self.m_addrphx_types:
      if descriptor.mode==iowidth and descriptor.length==length:
        return descriptor
    return None
  
  def getCmdDescriptor(self, iowidth):
    for descriptor in self.m_cmdphx_types:
      if (descriptor.mode==iowidth):
        return descriptor
    return None
  
  def getDummyDescriptor(self,iowidth, length):
    for descriptor in self.m_dummyphx_types:
      if (descriptor.mode==iowidth and descriptor.length==length):
        return descriptor
    return None

  def getTransactionDescriptor(self, wrenPhx, cmdPhx, addrPhx, modePhx, dummyPhx, dataPhx):
    for session in self.m_session_types:
      if session.cmdPhx != cmdPhx:
        continue
      if session.addrPhx != addrPhx:
        continue
      if session.dummyPhx != dummyPhx:
        continue
      if session.dataPhx != dataPhx:
        continue
      return session
    return None
    

  _iowidth_code   = ['S', 'D', 'Q']
  _iowidth_value  = [1, 1, 2, 2, 4, 4]
  _burstread      = 'B'
  _modephase      = 'M'
  _unlimited      = 'U'
  _iotype_string  = ['nodata', 'read', 'write']
  _iotype_code    = [ IOTYPE_NODATA, IOTYPE_READ, IOTYPE_WRITE]

  class compactTypedList(object):
    
    def __init__(self, itemType):
      self.m_list=[] 
      self.m_index=None
      self.m_item_type=itemType
      
    def submitItem(self, item):
      if isinstance(item, self.m_item_type):
        if item not in self.m_list:
          self.m_list.append(item)
          return True
      return False

    def stored(self, item):
      if isinstance(item, self.m_item_type):
        return item in self.m_list
      return False

    def firstItem(self):
      self.m_index=0
      return self.nextItem()
    
    def nextItem(self):
      index=self.m_index
      self.m_index+=1
      return self.m_list[index]

    def count(self):
      return len(self.m_list)
    

  class compactKeyedLists(object):
    
    def __init__(self, key_list, type_list):
      self.m_keys=key_list
      self.m_index_range=range(len(key_list))
      self.m_compact_lists=[ self.compactList(type_list[_ndx]) for _ndx in self.m_index_range]

    def listCount(self):
      return len(self.m_compact_lists)

    def listKeyIndex(self, key):
      if key in self.m_keys:
        return self.m_keys.index(key)

    def fetchList(self, key ):
      return(self.m_compact_lists[self.listKeyIndex(key)])

    def submitItem(self, item, key):
      return(self.fetchList(key).submitItem(item))
      
    def indexSubmitItem(self, item, index):
      return(self.m_compact_lists[index].submitItem(item))
        
    def stored(self, item, key):
      return(self.fetchList(key).stored())
    
    def firstItem(self, item, key):
      return(self.fetchList(key).firstItem())
    
    def nextItem(self, key):
      return(self.fetchList(key).nextItem())

    def count(self, key):
      return(self.fetchList(key).count())

      
      
  m_phase_data_lists=None
  m_phase_descriptor_lists=None
  def analyzeDescriptorData(self):
    
    
    
    '''
    discover unique phase descriptor tuplets for each data width mode
    '''
    phase_data_columns=[self.m_cmd_ndx, self.m_addrcycles_ndx, self.m_dummycycles_ndx, self.m_datamincycles_ndx, self.m_datamaxcycles_ndx]
    phase_data_types=[ list for _ndx in phase_data_columns]
    
    phase_descriptor_columns=[self.m_cmd_ndx, self.m_addrcycles_ndx, self.m_dummycycles_ndx, self.m_datamincycles_ndx, self.m_datamaxcycles_ndx]
    phase_descriptor_types=[busyPhx, wrenPhx, cmdPhx, addrPhx, dummyPhx, dataPhx]

    self.m_phase_data_lists=self.compactTypedLists(phase_data_columns, phase_data_types)
    self.m_phase_descriptor_lists=self.compactKeyedLists(phase_descriptor_columns, phase_descriptor_types)

      
    self.m_command_set = []
    
    '''
    across each session phase element of command description
    
      store unique combinations session phase parameters in 
      - session specific lists
    '''
    row_ndx=0
    for row in self.m_descriptor_data:
      for mode in [[self.m_spimode_ndx, 1], [self.m_sqimode_ndx,4]]:
        # use the implicit io mode (single/quad)
        if row[mode[0]]=='':
          continue
        else:
          iowidth=mode[1]
        
        for value_ndx in phase_descriptor_columns:
          
          '''
          building command set
          '''
          if value_ndx == self.m_cmd_ndx:
            '''
            build command list
            build cmdPhx uniques
            '''
            if row[self.m_iotype_ndx] not in self._iotype_string:
              print("table error: iotype, row %d", row_ndx)
              sys.exit(-1)

            iowidth_list=[row[self.m_spimode_ndx]!='', row[self.m_sqimode_ndx]!='']
            has_modephase=self._modephase in row[self.m_variant_ndx]
            iotype_code_index=self._iotype_string.index(row[self.m_iotype_ndx])
            iotype_code=self._iotype_code[iotype_code_index]
            cmd_descriptor=cmdDescriptor(index=row_ndx,
                                         mnemonic=row[self.m_mnemonic_ndx],
                                         code=row[self.m_cmd_ndx],
                                         iotype=iotype_code,
                                         iowidth=iowidth_list,
                                         modephase=has_modephase)

            self.m_command_set.append(cmd_descriptor)


            for iowidth in iowidth_list:
              if [iowidth] not in self.m_phase_descriptor_tuplets[self.m_cmd_ndx]:
                self.m_phase_descriptor_tuplets[self.m_cmd_ndx].append([iowidth])

          else:
            '''
            process variant annotations for mixed iowidth commands
            '''
            row_entry=row[value_ndx]
            this_iowidth=iowidth
            burstread=False
            cycles=None
           
            '''
            cycles with overrides or augmentations
            currently: iowidth overrides, burstread specification
            '''
            if row_entry.isnumeric():
              cycles=row_entry
            else:
              # override iowidth ?
              for iowidth_code in self._iowidth_code:
                if iowidth_code in row_entry:
                  row_entry=row_entry.replace(iowidth_code,'')
                  this_iowidth=self._iowidth_value[self._iowidth_code.index(iowidth_code)]
                  break
                
              if self._burstread in row_entry:
                row_entry=row_entry.replace(self._burstread,'')
                burstread=True
                
              if row_entry==self._unlimited:
                cycles=None
              elif not row_entry.isnumeric():
                print("table syntax error")
                sys.exit(-1)
                
            
            value=[this_iowidth, cycles]
            if burstread == True:
              value.append(self._burstread)

            '''
            compact list: do not store duplicates
            '''              
            if value not in self.m_phase_descriptor_tuplets[value_ndx]:
              self.m_phase_descriptor_tuplets[value_ndx].append(row[value_ndx])
              

          row_ndx+=1

  '''
  generateTransactionSpecs
  
    compile a complete list of the transaction session specs
    that support every kind of SPI command for the EEPROM.

    compile command specifications that associate an EEPROM
    SPI command to the appropriate transaction session spec
    
    These specs are used by the multimode SPI cmd processor.
    
  '''
  def generateTransactionSpecs(self):            
    '''
    process datacycle value-pair [datamin, datamax]
    '''
    self.m_unique_dataminmax_values=[]
    
    
    for row in self.m_descriptor_data:
      dataminmax=[row[self.m_datamincycles_ndx], row[self.m_datamaxcycles_ndx]]
      if dataminmax not in self.m_unique_dataminmax_values:
        self.m_unique_dataminmax.append(dataminmax)

    
    '''
    build unique data-phase data specs tuplets
      begin by building all the unique constituient phase tuplets
      handle burstmode variant
    '''
    self.m_minmax_phases=[]
    burstmode=False
    for value in self.m_unique_dataminmax_values:
      if self._burstread in value[1]:
        # datamin carries burstmode variant note, save flag, remove from item
        burstmode=True
        value.remove(self._burstread)
      
      if burstmode:
        self.m_data_phases.append(dataPhx(mode=value[0][0], burst=True, min_length=value[0][1], max_length=value[1][1]))
      else:
        self.m_data_phases.append(dataPhx(mode=value[0][0], min_length=value[0][1], max_length=value[1][1]))


    '''
    build cmd phases
    '''
    self.m_cmd_phases=[]
    for value in self.m_phase_descriptor_tuplets[self.m_cmd_ndx]:
      self.m_cmd_phases.append(cmdPhx(mode=value[0]))

    '''
    build addr phases
    '''
    self.m_addr_phases=[]
    for value in self.m_phase_descriptor_tuplets[self.m_addrcycles_ndx]:
      self.m_addr_phases.append(addrPhx(mode=value[0], length=value[1]))
      
    '''
    build dummy phases
    '''
    self.m_dummy_phases=[]
    for value in self.m_phase_descriptor_tuplets[self.m_dummycycles_ndx]:
      self.m_dummy_phases.append(dummyPhx(mode=value[0], length=value[1]))


    '''
    build wren phases
    '''
    self.m_wren_phases=[]
    for value in self.m_phase_descriptor_tuplets[self.m_wren_cmd_ndx]:
      self.m_wren_phases.append(wrenPhx(mode=value[0]))
      
    '''
    build transaction descriptors
    '''

    '''
    assemble all phases of supported transaction sessions
    i.e. sessions specified in the command table
    if it is unique, add it to the specification store
    if not, the store will return the existing specification
    '''
    self.m_session_types=[]
    
    for transaction in self.m_descriptor_data:
      
      def getPhaseAttributes(default_mode, phase_ndx):
        entry=transaction[phase_ndx]
        burst=None
        iowidth=default_mode
        if type(entry)==list:
          cycles=entry[0]
          if entry[1] in self._iowidth_code:
            iowidth=self._iowidth_value[self._iowidth_code.index(entry[1])]
          elif entry[1]==self._burstread:
            burst=True
        return iowidth, cycles, burst


      modes=[]

      if transaction[self.m_spimode_ndx]!='':
        modes.append[1]
      if transaction[self.m_sqimode_ndx]!='':
        modes.append[4]


      '''
      note: equation between namedtuples and simple tuples work
      '''
      for mode in modes:
        
        cmdPhx=self.getCmdDescriptor(mode)
        cmd_mode=addr_mode=dummy_mode=data_mode=mode
        
        '''
        get unique cmdPhx tuple index
        '''
        
        cmd_tuple=(cmd_mode)
        cmdPhx_ndx=self.m_phase_descriptor_tuplets[self.m_cmd_ndx].index( (cmd_tuple) )
        thisCmdPhx=self.m_phase_descriptor_tuplets[self.m_cmd_ndx][cmdPhx_ndx]
        
        #_dc is 'don't care'
        iowidth, addrcycles, _dc = getPhaseAttributes(addr_mode, self.m_addrcycles_ndx)
        addrPhx_ndx=self.m_phase_descriptor_tuplets[self.m_addrcycles_ndx].index( (iowidth, addrcycles) )
        thisAddrPhx=self.m_phase_descriptor_tuplets[self.m_addrcycles_ndx][addrPhx_ndx]

        iowidth, dummycycles, _dc = getPhaseAttributes(dummy_mode, self.m_dummycycles_ndx)
        dummyPhx_ndx=self.m_phase_descriptor_tuplets[self.m_dummycycles_ndx].index( ( iowidth, dummycycles))
        thisDummyPhx=self.m_phase_descriptor_tuplets[self.m_dummycycles_ndx][dummyPhx_ndx]
        
        iowidth, datacycles, if_burst = getPhaseAttributes(dummy_mode, self.m_dummycycles_ndx)
        thisDataPhx=(iowidth, if_burst, datacycles[0], datacycles[1])
        dataPhx_ndx=self.m_phase_descriptor_tuplets[self.m_datacycles_ndx].index( thisDataPhx )
        thisDataPhx=self.m_phase_descriptor_tuplets[self.m_datacycles_ndx][dataPhx_ndx]
        
        
        transaction_tuple= (thisCmdPhx, thisAddrPhx, thisDummyPhx, thisDataPhx)
        
        '''
        process any annotated entries
        annotations can override iowidth
        '''

        addrPhx=self.getAddrDescriptor(mode, )
        dummyPhx=self.getDummyDescriptor(mode, transaction[self.m_dummycycles_ndx])
        data_entry=transaction[self.m_datacycles_ndx]
        
        dataPhx=self.getDataDescriptor(mode, transaction[self.m_datacycles_ndx])
  pass



class SpiCmdTableGenerator(object):
  
  '''
  0. Generate cmd specs
  1. Generate data length specs
  2. Generate addr specs
  3. Generate dummy specs
  4. Generate wren specs
  5. Generate fastbusy specs
  
  '''
    
  def __init__(self, module_pathname):
    self.m_module_pathname=module_pathname
    if '//' in self.m_module_pathname:
      self.m_module_drive, self.m_module_path=os.path.splitdrive(module_pathname)
      self.m_module_path, self.m_module_name=os.path.split(self.m_module_path)
      self.m_module_rootname=self.m_module_name.rsplit('.',1)
      self.m_module_pyname=self.m_module_rootname+'.py'
      
      self.m_protocol_table_pathname=self.m_module_drive+self.m_module_path+self.m_module_pyname
    pass

  
  def genCmdSpecs(self):  
    pass
  
  def genDataSpecs(self):
    pass
    
  def genAddrSpecs(self):
    pass
  
  def genDummySpecs(self):
    pass
  
  def genWrenSpecs(self):
    pass
  
  def genFastBusySpecs(self):
    pass
  
  
  
  
  
  
  
  
  
  
    '''
    classdocs
    Load and provide a checked representation of the Command Structure Table
    of a Device SPI EEPROM device.
    
    1. SPI transactions can have SPI, Dual-SPI, or Quad-SPI variants.
    2. User generates a CSV file per the following header:
    header:   CommandName, TextDescription, iobitsPerCycle, CommandCode,
              AddressCycles, DummyCycles, MinimumDataCycles, MaximumDataCycles
      x) CommandName is a CAPITALIZED character mnemonic
      x) Text Description is terse
      x) iobits per cycle is 1, 2, or 4
          xx) if more than one value is expressed for a command, use brackets around
              veritcal bar seperated valuese.g.: [1|4]  for iowidths 1 -or- 4
          xx) if transaction cycle can have multiple iobitsPerCycle, add a bracket with the
              single or multiple iobitsPerCycle for each cycle
          xx) if this is confusing, break up a single line with variant iobitsPerCycle into
              multiple lines each with specific iobitsPercycle for each transaction cycle
              
      x) Command Codebyte is a single hex byte
      x) Address Cycles is 0, 2, 3, or 4
      x) Dummy Cycles is 0, 1, ... N
      x) Data Cycles:
        xx) Minimum Data Cycles is  None, 0,1,...N
        xx) Maximum Data Cycles is None, 0,1,....N
        xx) Data length is fixed if Max=Min and Max in {1,...}
        xx) Use 0 for No Data, and None for Unlimited Data
    '''


class spiCmdTableGenerator(object):
  
    _header_columns=[ 'mnemonic', 'description', 'cmd','spimode','sqimode', 'addrcycles'
                      'dummycycles', 'datamincycles', 'datamaxcycles', 'iotype' ]
    
    m_descriptor_table=None
    m_header_processed=False
    m_descriptor_spec_filename=None
    
    COLMN_CMDNAME       = 0
    COLMN_DESCRIPTION   = 1
    COLMN_IOBITPERCYCLE = 2
    COLMN_CMDCODE       = 3
    COLMN_ADDRCYCLES    = 4
    COLMN_DUMMYCYCLES   = 5
    COLMN_MINDATACYCLES = 6
    COLMN_MAXDATACYCLES = 7
     

    def __init__(self, transaction_spec_filename, device_name):
      self.m_descriptor_table=None
      self.m_header_processed=False
      self.m_transaction_spec_filename
      

      
    def loadDescriptorTable(self):
      description_table=open(self.m_descriptor_spec_filename, "r")
      if description_table <0:
        print("file open error")
        sys.exit(-1)
        
      for line in description_table:
        line_items=line.split(',')

        if len(line_items) != len(self._header_columns):
          print("items per line error")
          sys.exit(-1)
                  
        if not self.m_header_processed:
          for index in range(len(self._header_columns)):
            if line_items[index] != self._header_columns[index]:
              print("line header error")
              sys.exit(-1)
              
          self.m_descriptor_table=[]
          self.m_header_processed=True
          
        else:
          transaction_descriptor=[]
          for index in range(len(line_items)):
            line_item=line_items[index]

            if index==self.COLMN_CMDNAME:
              '''
              process command name
              '''
              cmd_name=str(line_item)
              for c in cmd_name:
                if c.isalpha() and (c).isupper():
                  continue
                else:
                  print("cmd name syntax error")
                  sys.exit(-1)
                  
              transaction_descriptor.append(cmd_name)


            if index==self.COLMN_DESCRIPTION:
              description=str(line_item)
              transaction_descriptor.append(description)

              
            if index==self.COLMN_IOBITPERCYCLE:
              line_item.replace(' ','')
              iobits=str(line_item).split('|')
              multivalue_open=False
              value_parsed=False
              iowidth_list=[]
              
              for c in iobits:
                if c=='[' and not multivalue_open and not value_parsed:
                  multivalue_open=True
                  continue
                  
                elif c==']' and multivalue_open and value_parsed:
                  multivalue_open=False
                  transaction_descriptor.append(iowidth_list)
                  continue
                
                elif c.isnumeric():
                  int_c=int(c)
                  if int_c in [0,2,4]:
                    iowidth_list.append(int_c)
                    continue

                print("iowidth syntax error")
                sys.exit(-1)

            cycle_count=str(line_item).replace(' ','')
            if not line_item.isnumeric():
              print("cycle count syntax error")
              sys.exit(-1)
            
            if index==self.COLMN_ADDRCYCLES:
                transaction_descriptor.append(cycle_count)
              
            if index==self.COLMN_DUMMYCYCLES:
                transaction_descriptor.append(cycle_count)
    
              
            if index==self.COLMN_MINDATACYCLES:
                transaction_descriptor.append(cycle_count)
              
            if index==self.COLMN_MAXDATACYCLES:
                transaction_descriptor.append(cycle_count)





api=spiDescriptorApi()
api.setDescriptorCsvFileName('c:\\users\\asus\\documents\\software\\SST26VF032-spicmd-description.csv')
api.loadDescriptorCSV()
api.analyzeDescriptorData()
