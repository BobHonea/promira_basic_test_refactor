import random
import sys
import promact_is_py as pmact

import array
import math
from _random import Random

class testUtil:
  m_instantiated=False
  m_random=Random()
  m_randarray_count = 16  # arbitrary number
  m_random_page_array_index = 0
  m_random_page_array_list = []
  m_page_size=256  # eeprom page size (universal)

  _instance=None
  
  def __new__(cls):
      if cls._instance is None:
          print('Creating the testUtil object')
          cls._instance = super(testUtil, cls).__new__(cls)
          cls.m_random=random.Random()
          cls.m_random.seed(1)
          cls.buildPageArrays(cls)
      return cls._instance
  
  def __singleton_init__(self, page_size=256):
    self.m_random.seed(0)
    self.m_page_size=page_size
    self.buildRandomPageArrays()
  
  def fatalError(self, reason):
    print("Fatal : "+reason)
    sys.exit()

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
      zero_array = pmact.array_u08(array_size)
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
  

  
  def generatePatternedArray(self, array_size):
    patterned_array=pmact.array_u08(array_size)
    for index in range(array_size):
      patterned_array[index] =int(256*math.sin(index*3.141579/256))
    return patterned_array
  
      
  def generateRandomArray(self, array_size):
      rand_array = pmact.array_u08(array_size)
      for index in range(array_size):
        rand_array[index] = random.randint(0, 255)
        
      return rand_array
  
  PATTERNED_ARRAYS=True
  
  def buildPageArrays(self):
      self.m_random_page_array_list = []
      for _index in range(self.m_randarray_count):
        if self.PATTERNED_ARRAYS:
          this_array=self.generatePatternedArray(self.m_page_size, self.m_page_size)
        else:  
          this_array=self.generateRandomArray(self.m_page_size, self.m_page_size)
             
        self.m_random_page_array_list.append(this_array)
        # array_label = "Random Page Array #%02X:" % index
        # self.printArrayHexDump(array_label, self.m_random_page_array_list[index])
          
  def firstRandomPageArray(self):
    self.m_random_page_array_index=0
    return self.m_random_page_array_list[0]
    
  def nextRandomPageArray(self):
      self.m_random_page_array_index = (self.m_random_page_array_index + 1) % self.m_randarray_count
      return self.m_random_page_array_list[self.m_random_page_array_index]


  def printArrayHexDump(self, label, data_array=None):
    
    if not type(data_array)==array.ArrayType or len(data_array)==0:
      print("Hexdump:  array is empty")
      return
    
    bytes_per_line = 32
    array_size = len(data_array)
    array_lines = (array_size + bytes_per_line - 1) // bytes_per_line
    dump_bytes = array_size
    dump_index = 0
    print("%s [ 0x%x bytes ]" % (label, array_size))
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
      print(linestring)
 
 
 
  '''
  printArrayHexDumpWithErrors
    Dump an array in rows of fixed length.
    Include between rows of array_a, annotated values
    of array_b where they differ with array_a.
  '''  

  def printArrayHexDumpWithErrors(self, label, data_array, pattern_array):

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
          
        print('      '+''.join(diff_text))
        return False
      
      else:
        return True, ''
    
    
    if not type(data_array)==array.ArrayType or len(data_array)==0:
      print("Hexdump:  array is empty")
      return
    
    bytes_per_line = 32
    array_size = len(data_array)
    array_lines = (array_size + bytes_per_line - 1) // bytes_per_line
    dump_bytes = array_size
    dump_index = 0
    print("%s [ 0x%x bytes ]" % (label, array_size))
    
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
      pattern_match=self.arraysMatch(data_sub_array, pattern_sub_array)

      if not pattern_match:
        print("")
        
      for dump_index in range(dump_index, dump_index + line_bytes):
        value = data_array[dump_index]
        line_string = line_string + " %02X" % value
      
      print(line_string)
      if not pattern_match:
        printDiffLine(data_array[line_start:line_end], pattern_array[line_start:line_end])
        
  pass
 
  def arraysMatch(self, array_a, array_b):
    match=False
    if len(array_a) == len(array_b):
      for index in range (len(array_a)):
        if array_a[index]==array_b[index]:
          continue
        else:
          return False
    return True
  pass