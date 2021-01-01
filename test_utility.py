import random
import sys

import array
import math
import time
import os
from _random import Random



#==========================================================================
# HELPER FUNCTIONS
#==========================================================================
def array_u08 (n):  return array.ArrayType('B', [0]*n)
def array_u16 (n):  return array.ArrayType('H', [0]*n)
def array_u32 (n):  return array.ArrayType('I', [0]*n)
def array_u64 (n):  return array.ArrayType('K', [0]*n)
def array_s08 (n):  return array.ArrayType('b', [0]*n)
def array_s16 (n):  return array.ArrayType('h', [0]*n)
def array_s32 (n):  return array.ArrayType('i', [0]*n)
def array_s64 (n):  return array.ArrayType('L', [0]*n)
def array_f32 (n):  return array.ArrayType('f', [0]*n)
def array_f64 (n):  return array.ArrayType('d', [0]*n)

# A python program to create user-defined exception 
  
# class MyError is derived from super class Exception 
class TestError(Exception): 
  
    # Constructor or Initializer 
    def __init__(self, value): 
        self.value = value 
  
    # __str__ is to print() the value 
    def __str__(self): 
        return(repr(self.value)) 
  

  

  
  


class testUtil:
  m_instantiated=False
  m_random=Random()
  m_ref_array_count = 16  # arbitrary number
  m_ref_array_index = 0
  m_ref_array_list = []
  m_patterned_not_random_arrays = True
  m_page_size=256  # eeprom page size (universal)
  m_trace_buffer=[]
  m_trace_protect_index=0
  m_detail_trace  = False
  m_display_trace = False
  m_detail_echo   = False
  m_display_echo  = False
  m_trace_echo    = False
  m_log_file      = None
  m_log_to_file   = False
  m_log_to_file = False
  m_file_log_buffer_depth = 0
  m_file_log_buffer_lines = 0
  m_trace_enabled = False
  m_page_arrays_built = False
  _instance=None
  
  def __new__(cls):
      if cls._instance is None:
          print('Creating the testUtil object')
          cls._instance = super(testUtil, cls).__new__(cls)
          cls.m_random=random.Random()
          cls.m_random.seed(2000)
          cls.m_page_arrays_built=False
      return cls._instance
  
  
  def fatalError(self, reason):
    
    fatal_msg="Fatal : "+reason
    if self.traceEnabled():
      self.bufferTraceInfo(fatal_msg)
      self.dumpTraceBuffer()
    else:
      print(fatal_msg)
    sys.exit(-1)
    
  def flushLogfileBuffer(self):
    if len(self.m_file_log_buffer) > 0:
      for line in self.m_file_log_buffer:
        self.m_log_file.write(line+"\n")
        
      self.m_file_log_buffer=[]
      self.m_file_log_buffer_lines=0
    
    
  '''
  Create Log Files in N MB Segments
  when flushing a file, check its size.
  when file size is at limit, close and
  reopen with incremented name
  '''  
  m_log_file_rootname = None
  m_log_file_path     = None
  m_log_file_index    = None
  MAX_LOGFILE_SIZE    = 1024*1024*10
    
  def openLogfile(self, file_path):
    self.m_log_file_path=file_path
    datetime_string=time.strftime("%Y%m%d-%H%M%S")
    self.m_log_file_rootname="SpiReadTest_%s" % datetime_string
    self.m_log_file_index=0
    return self.openNthLogfile()
  
  def openNthLogfile(self):
    self.m_log_file_pathname=("%s/%s.%002d.log" % ( self.m_log_file_path,
                                                self.m_log_file_rootname,
                                                self.m_log_file_index) )
    
    self.m_log_file=open(self.m_log_file_pathname,"w+")
    self.m_file_log_buffer_depth = 200
    self.m_file_log_buffer_lines = 0
    self.initLogfileBuffer(200)
    self.bufferLogfileLine("SPI EEPROM Read Test Log: "+self.m_log_file_pathname)
    self.flushLogfileBuffer()
    return self.m_log_file
  
  def reopenLogFile(self):
    self.closeLogFile()
    self.m_log_file_index+=1
    return self.openNthLogfile()
    
  def logFileSize(self):
    log_statinfo=os.stat(self.m_log_file_pathname)
    return log_statinfo.st_size
  
  def logFileCheck(self):
    if self.logFileSize() >= self.MAX_LOGFILE_SIZE:

       self.reopenLogFile()
  
    '''  
    except IOError as e:
      print("Open or Write Failure to %s: %s" %(file_pathname, e))
      self.fatalError("File I/O Error")
      
    finally:
      return
    '''
  
  def closeLogFile(self):
    self.flushLogfileBuffer()
    self.m_log_file.close()

  def enableLogfile(self):
    if self.m_log_file!=None:
      self.m_log_to_file = True
    
  def disableLogfile(self):
    if self.m_log_file!=None:
      self.m_log_to_file = False
    
  def initLogfileBuffer(self, buffer_depth=None):
    if buffer_depth!=None:
      self.m_file_log_buffer_depth=buffer_depth
    self.m_file_log_buffer=[]

  def bufferLogfileLine(self, string_info):
    self.m_file_log_buffer.append(string_info)
    self.m_file_log_buffer_lines+=1
    if self.m_file_log_buffer_lines==self.m_file_log_buffer_depth:
      self.flushLogfileBuffer()
      self.m_file_log_buffer_lines=0
  

  

  def traceEnabled(self):
    return self.m_trace_enabled
  
  def setTraceBufferDepth(self, trace_depth):
    self.m_trace_depth=trace_depth
    
    
  def initTraceBuffer(self, trace_depth=0):
    self.m_trace_buffer=[]
    self.m_trace_enabled=True
    self.m_trace_depth=trace_depth
    self.m_trace_protect_depth=0
    
  '''
  protectTraceBuffer
      locks the initial contents into the Trace Buffer
      sets the flush index
      data in the trace buffer when this function is called
      will NEVER be flushed until initTraceBuffer.
  
    The Trace Depth is measured from the end of the protect
    index.
  '''
  def protectTraceBuffer(self):
    if self.m_trace_enabled:
      self.m_trace_protect_depth=self.m_trace_depth
    
  def disableTrace(self):
    self.m_trace_enabled=False

  
  def detailTraceOff(self):
    if self.m_trace_enabled:
      self.m_detail_trace=False
    
  def displayTraceOff(self):
    if self.m_trace_enabled:
      self.m_display_trace=False

  def detailTraceOn(self):
    if self.m_trace_enabled:
      self.m_detail_trace=True
    
  def displayTraceOn(self):
    if self.m_trace_enabled:
      self.m_display_trace=True
      
  def bufferDisplayInfo(self, string_info, echo=True):
    if self.m_display_trace:
      self.bufferTraceInfo(string_info, echo or self.m_display_echo)

      
  def bufferDetailInfo(self, string_info, echo=False):
    if self.m_detail_trace:
      self.bufferTraceInfo(string_info, echo or self.m_detail_echo)
    
  def bufferTraceInfo(self, string_info, echo=False):
    if self.m_trace_enabled:
      if self.m_trace_depth>0:
        if len(self.m_trace_buffer) >= (self.m_trace_depth+self.m_trace_protect_depth):
          self.m_trace_buffer.pop(self.m_trace_protect_depth)
      if self.m_trace_echo or echo:
        print(string_info)
      self.m_trace_buffer.append(string_info)
      if self.m_log_to_file:
        self.bufferLogfileLine(string_info)
  
  def flushTraceBuffer(self):
    if self.m_trace_enabled:
      self.m_trace_buffer = self.m_trace_buffer[:self.m_trace_protect_depth]

  def traceEchoOn(self):
    self.m_trace_echo=True

  def traceEchoOff(self):
    self.m_trace_echo=False
    
  def detailEchoOn(self):
    self.m_detail_echo=True
    
  def detailEchoOff(self):
    self.m_detail_echo=False

  def dumpTraceBuffer(self):
    if self.m_trace_enabled:
      if len(self.m_trace_buffer) > 0:
        print("******TRACE BUFFER DUMP ******")
        index=0
        for entry in self.m_trace_buffer:
          print("%04d %s" % (index,entry))
          index+=1
        return True
    return False
    
  def ipString(self, ip_integer):
    integer=ip_integer
    ipString_buf=""
    
    for index in range (0,4):
      if index>0:
        ipString_buf="."+ipString_buf
      octet=int((ip_integer>>((3-index)*8))&0xff) 
      integer>>=8
      octet_string=format(octet, "d")
      ipString_buf=octet_string+ipString_buf
    return ipString_buf

  
  def zeroedArray(self, array_size):
      zero_array = array_u08(array_size)
      return zero_array
  
  def randomizeList(self, reference_list):
    element_count=len(reference_list)
    if element_count<=1:
      # NULL and Single Item List already Randomized
      return reference_list
    
    ordinals=[None]*element_count
    reorder_indices=[]
    
    for index in range(element_count):
      test_index=self.m_random.randint(0,element_count)
      if ordinals[test_index]==test_index:
        continue
      else:
        ordinals[test_index]=test_index
        reorder_indices.append[test_index]
        
      if len(reorder_indices)==element_count:
        break
      
      
      reordered_list=[None]*element_count
      for index in reordered_list:
        reordered_list[index]=reference_list[reorder_indices[index]]
        
      return reordered_list
    pass
  

  class pagePatternGenerator(object):
    m_index             = None
    m_recurrence_page   = None
    m_page_size         = None
    m_max_value         = None
    m_max_index         = None
    m_frequency_1       = None
    m_frequency_2       = None
        
    def __init__(self, recurrence_page, page_size, max_value):
      self.m_index=0
      self.m_recurrence_page=recurrence_page
      self.m_page_size=page_size
      self.m_max_value=max_value
      self.m_max_index=page_size*recurrence_page
      self.m_frequency_1=1/self.m_max_index
      self.m_frequency_2=10/page_size
      
    def initPatternNumber(self):
      self.m_pattern_index=0
    
    def incrementIndex(self):
      self.m_index+=1
      if self.m_index==self.m_max_index:
        self.m_index=0
        
    def nextPatternNumber(self):
      sin_1=math.sin(2*self.m_index*math.pi*self.m_frequency_1)
      sin_2=math.sin(2*self.m_index*math.pi*self.m_frequency_2)
      self.incrementIndex()

      num = math.sqrt(math.fabs(sin_1+sin_2)/2)
      num = num*self.m_max_value
      return int(num)
  m_pattern_generator = None


  class referenceArraySequence(object):
    
    def __init__(self, array_list):
      self.m_max_index=len(array_list)-1
      self.m_base_index=0
      self.m_reference_index=0
      self.m_array_size=len(array_list[0])
      self.m_array_count=len(array_list)
      self.m_array_list=array_list
      self.m_sequence_byte_length=self.m_array_size*self.m_array_count
      
      
    def firstIndex(self):
      self.m_reference_index=self.m_base_index
      return self.m_reference_index

    def currentIndex(self):
      return self.m_reference_index

    def nextIndex(self):
      self.m_reference_index+=1
      if self.m_reference_index>self.m_max_index:
        self.m_reference_index=self.m_base_index
        
    def pageSize(self):
      return self.m_array_size
        
    def firstAddress(self):
      return self.m_array_size*self.firstIndex()

    def currentAddress(self):
      return self.m_reference_index*self.m_array_size
    
    def nextAddress(self):
      return self.m_array_size*self.nextIndex()
        
    def indexOfAddress(self, array_address):
      return array_address//self.m_array_size
      
    def arrayAtIndex(self, index):
      return self.m_array_list[index]
      
    def arrayAtAddress(self, array_address):
      modaddress=array_address%self.m_sequence_byte_length
      return self.m_array_list[self.indexOfAddress(modaddress)]
      
    def firstArray(self):
      return self.arrayAtIndex(self.firstIndex())
    
    def currentArray(self):
      return self.arrayAtIndex(self.currentIndex())
    
    def nextArray(self):
      return self.arrayAtIndex(self.nextIndex())
    
    def addressForArrayIndex(self, index):
      modindex=index%self.m_array_count
      return modindex*self.m_array_size

    def setIndex(self, index):
      self.m_reference_index=index
      
    def setIndexByAddress(self, address):
      self.m_reference_index=self.indexOfAddress(address)

  '''
  referenceArrayIndex()
  the reference array set is finite in page-array length
  it is written recurrently throughout the memory space
  compute the page array index matching a memory page start address
  '''
  
  def referenceArrayIndex(self, start_address):
    if start_address % 256 != 0:
      self.fatalError("referenceArrayIndex: start_address not on page boundary")
    return (start_address//256)%self.m_ref_array_count
    
  def generatePatternedArray(self, array_size):
    if self.m_pattern_generator == None:
      self.m_pattern_generator=self.pagePatternGenerator(self.m_ref_array_count, 256, 255)

    patterned_array=array_u08(array_size)
    for index in range(array_size):
      patterned_array[index] = self.m_pattern_generator.nextPatternNumber()
    return patterned_array
  
      
  def generateRandomArray(self, array_size):
      rand_array = array_u08(array_size)
      for index in range(array_size):
        rand_array[index] = random.randint(0, 255)
        
      return rand_array
  
  
  
  def refArrayCount(self):
    return self.m_ref_array_count
  
  def buildPageArrays(self):
      self.m_ref_array_list = []
      for _index in range(self.m_ref_array_count):
        if self.m_patterned_not_random_arrays:
          this_array=self.generatePatternedArray(self.m_page_size)
        else:  
          this_array=self.generateRandomArray(self.m_page_size, self.m_page_size)
             
        self.m_ref_array_list.append(this_array)
      self.m_page_arrays_built=True
        # array_label = "Reference Page Array #%02X:" % index
        # self.printArrayHexDump(array_label, self.m_ref_array_list[index])
  
  def nthReferencePageArray(self, index):
    index=index % self.m_ref_array_count
    return self.m_ref_array_list[index]
  
  def firstReferencePageArray(self):
    self.m_ref_array_index=0
    return self.m_ref_array_list[0]
    
  def nextReferencePageArray(self):
      self.m_ref_array_index = (self.m_ref_array_index + 1) % self.m_ref_array_count
      return self.m_ref_array_list[self.m_ref_array_index]


  def printArrayHexDump(self, label, data_array=None, echo_to_display=False):
    
    if not type(data_array)==array.ArrayType or len(data_array)==0:
      self.bufferDetailInfo("Hexdump:  array is empty")
      return
    
    bytes_per_line = 32
    array_size = len(data_array)
    array_lines = (array_size + bytes_per_line - 1) // bytes_per_line
    dump_bytes = array_size
    dump_index = 0
    self.bufferDetailInfo("%s [ 0x%x bytes ]" % (label, array_size), echo_to_display)
    for line in range(array_lines):
      linestart = line * bytes_per_line
      linestring = " %02X : " % linestart
      if dump_bytes >= bytes_per_line:
        line_bytes = bytes_per_line
      else:
        line_bytes = dump_bytes
        
      for dump_index in range(dump_index, dump_index + line_bytes):
        value = data_array[dump_index]
        linestring = linestring + " %02X" % value
      self.bufferDetailInfo(linestring, echo_to_display)
 
 
 
  '''
  printArrayHexDumpWithErrors
    Dump an array in rows of fixed length.
    Include between rows of array_a, annotated values
    of array_b where they differ with array_a.
  '''  

  def printArrayHexDumpWithErrors(self, label, data_array, pattern_array, echo_to_display=False):

    '''
    diffLine
      compares two arrays
      if equal, returns True and Null String
      else, returns False and Text with Annotated differing hex values
    '''
    def printDiffLine(array_a, array_b):
      diff_indices=[]
      if len(array_a) == len(array_b):
        for index in range (len(array_a)):
          if array_a[index]==array_b[index]:
            continue
          else:
            diff_indices.append(index)

      if len(diff_indices)>0:
        diff_text=['   ',]*len(array_a)
        last_index=-2
        for index in diff_indices:
          reference=array_b[index]
          if index==last_index+1:
            diff_text[index]="-%02x"%reference
          else:
            diff_text[index]=">%02x"%reference
          last_index=index
          
        self.bufferDetailInfo('      '+''.join(diff_text), echo_to_display)
        return False
      
      else:
        return True, ''
    
    
    if not type(data_array)==array.ArrayType or len(data_array)==0:
      self.bufferDetailInfo("Hexdump:  array is empty", echo_to_display)
      return
    
    bytes_per_line = 32
    array_size = len(data_array)
    array_lines = (array_size + bytes_per_line - 1) // bytes_per_line
    dump_bytes = array_size
    dump_index = 0
    self.bufferDetailInfo("%s [ 0x%x bytes ]" % (label, array_size), echo_to_display)
    
    for line in range(array_lines):
      line_start = line * bytes_per_line
      line_string = " %02X : " % line_start
      if dump_bytes >= bytes_per_line:
        line_bytes = bytes_per_line
      else:
        line_bytes = dump_bytes
      
      line_end=line_start+bytes_per_line
      data_sub_array=data_array[line_start:line_end]
      pattern_sub_array=pattern_array[line_start:line_end]
      pattern_match, _errors =self.arraysMatch(data_sub_array, pattern_sub_array)

      if not pattern_match:
        self.bufferDetailInfo("", echo_to_display)
        
      for dump_index in range(dump_index, dump_index + line_bytes):
        value = data_array[dump_index]
        line_string = line_string + " %02X" % value
      
      self.bufferDetailInfo(line_string, echo_to_display)
      if not pattern_match:
        printDiffLine(data_array[line_start:line_end], pattern_array[line_start:line_end])
        
  pass
 
  def arraySingleValued(self, array_a, value=None):
    
    if value!=None and array_a[0]!=value:
        return False
      
    byte_0=array_a[0]
    match_count=0
    
    for item in array_a:
      if item!= byte_0:
        break
      match_count+=1
      
    return match_count==len(array_a), match_count
      
  def arraysMatch(self, array_a, array_b):
    errors=0
    if len(array_a) == len(array_b):
      for index in range (len(array_a)):
        if array_a[index]==array_b[index]:
          continue
        else:
          errors+=1
          continue

    if errors >= 250:
      errors+=0        
      
    return errors==0, errors
  pass


  def logReferenceArrays(self):
    for index in range(self.refArrayCount()):
      this_array=self.nthReferencePageArray(index)
      label="Reference Array %02d" % index
      self.printArrayHexDump(label, this_array, True)
      
    