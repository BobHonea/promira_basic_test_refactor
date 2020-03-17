'''
Created on Feb 10, 2020

@author: honea
'''

import test_utility
import numpy as np
from _random  import Random
import collections as coll
import math
import time
import os

'''
parameterizedErrorHistorgram

  Collect pass/fail/error-count data for a parameterized range
  of test types.
  
  Build a histogram of errors for each parameter level.
  
  A single histogram of pass/fail/error-count for each parameter level.
  For each parameter lavel, a histogram of error counts.
  
  The buckets for the parameterized axis is supplied by user.
  The max-values for each error bucket is supplied by user.
  
'''

class parameterizedErrorHistogram(object):
    '''
    classdocs
    collect and publish results
    '''
    m_testUtil          = None
    m_bucket_labels     = None
    m_bucket_units_label= None
    m_bucket_values     = None
    m_bucket_data       = None
    m_data_labels       = None
    m_data_values       = None
    m_event_count       = None

    
    def __init__(self,  parameter_values,
                        parameter_labels,
                        parameter_units_label, 
                        data_values,
                        data_labels,
                        error_max_values):
        '''
        Constructor
        '''
        self.m_testUtil=test_utility.testUtil()
        
        if len(parameter_labels)!=len(parameter_values):
          self.m_testutil.fatalError("parameter values vs. labels length mismatch")
          
        if len(data_labels) != len(data_labels):
          self.m_testutil.fatalError("data values vs labels length mismatch")
          
          
        self.m_bucket_labels      = parameter_labels
        self.m_bucket_values      = parameter_values
        self.m_bucket_units_label = parameter_units_label
        self.m_data_labels        = data_labels
        self.m_data_values        = data_values
        self.m_bucket_count       = len(self.m_bucket_values)
        self.m_data_value_count   = len(self.m_data_values)
        self.m_data_value_range   = range(self.m_data_value_count)
        self.m_bucket_range       = range(self.m_bucket_count)
        self.m_error_buckets      = error_max_values
        self.m_error_bucket_labels= None
        self.m_error_bucket_count = len(self.m_error_buckets)
        self.m_event_count        = 0
 
        fault_values              = []
        self.m_fault_values       = fault_values
        self.m_fault_types        = []
        self.m_fault_events       = []
        self.m_fault_history      = []
 
        s=(self.m_bucket_count,2)
        e=(self.m_error_bucket_count,1)
        
        self.m_bucket_data      = np.zeros(s)
        self.m_errors           = [ np.zeros(e) for _bucket in self.m_bucket_range]
        

    def errorIndex(self, error_count):
      bucket_ndx=0
      for bucket in self.m_error_buckets:
        if error_count<= bucket:
          return bucket_ndx
        bucket_ndx+=1
      self.m_testutil.fatalError("input value overflow")

    '''
    addFault
    
      Flexible fault accumulation system.
      Fault types are recognized as they are reported
      New types are appended to the type list
      Fault type list index is the index for the event type count
      A list of each event is also kept
    ''' 
    def addFault(self, parameter_value, fault_code, fault_api, fault_string):

      fault_type=[fault_code, fault_api, fault_string]
      self.m_fault_history.append([parameter_value, fault_code, fault_api, self.m_event_count])
      
      if fault_type not in self.m_fault_types:
        self.m_fault_types.append(fault_type)
        self.m_fault_events.append(1)
      else:
        fault_ndx=self.m_fault_types.index(fault_type)
        self.m_fault_events[fault_ndx]+=1
        
      self.addFaultError(parameter_value)

    def dumpFaultHistory(self):
      if len(self.m_fault_history) > 0:
        self.display("******** Begin Fault History *********")
        for fault in self.m_fault_history:
          self.display(repr(fault))
        self.display("********* End Fault History **********")
      else:
        self.display("No Faults Recorded")

        
    def addFaultError(self, parameter_value):
      #self.m_event_count+=1
      bucket_ndx=self.m_bucket_values.index(parameter_value)

      try:
        error_count_array=self.m_errors[bucket_ndx]
        promira_error_ndx=self.errorIndex(258)
        error_count_array[promira_error_ndx]+=1
      except ValueError as e:
        self.m_testutil.fatalError("histogram addData ValueError:" + e) 
      
      finally:
        return

    def updateTrueParameter(self, parameter_value, actual_parameter):
      #self.m_event_count+=1
      bucket_ndx=self.m_bucket_values.index(parameter_value)

      try:
        error_count_array=self.m_errors[bucket_ndx]
        promira_error_ndx=self.errorIndex(259)
        error_count_array[promira_error_ndx]=actual_parameter
      except ValueError as e:
        self.m_testutil.fatalError("histogram addData ValueError:" + e) 
      
      finally:
        return      
      
    def addData(self, parameter_value, data_value, error_count, single_value_input):
      self.m_event_count+=1
      bucket_ndx=self.m_bucket_values.index(parameter_value)
      data_ndx=self.m_data_values.index(data_value)
      self.m_bucket_data[bucket_ndx,data_ndx]+=1

      try:
        error_ndx=self.errorIndex(error_count)
        error_count_array=self.m_errors[bucket_ndx]
        error_count_array[error_ndx]+=1
        if single_value_input:
          single_ndx=self.errorIndex(257)
          error_count_array[single_ndx]+=1
      except ValueError as e:
        self.m_testutil.fatalError("histogram addData ValueError:" + e) 
      
      finally:
        return
    
    def display(self, out_string):
      self.m_testUtil.bufferDisplayInfo(out_string)



    m_spaces="            "
    
    def centerText(self, text, field_width):
      #short side right
      spaces=int(field_width-len(text))
      space_right=int(spaces/2)
      space_left=spaces-space_right
      blank_left=self.m_spaces[-space_left:]
      blank_right=self.m_spaces[-space_right:]
      column_text=blank_left+text+blank_right
      return column_text
    
    def rightText(self, text, field_width):
      #1 space to right of text
      spaces=field_width-len(text)
      if spaces>0:
        space_right=1
      else:
        space_right=0
        
      space_left=spaces-space_right
      return( " "*(space_left)+text+" "*space_right)

    m_singval_col_hdr="1-Val"
    m_promira_error_col_hdr="Prmra"
    m_actual_clock_col_hdr="KHz"
    
    def columnWidth(self):
      minimum_width=len(self.m_singval_col_hdr)+2
      dynamic_width=self.m_number_width+2
      return max([dynamic_width, minimum_width])

    def histogramHeader(self):
      column_width=self.columnWidth()

      error_header=self.centerText("SPI-Clock", 12)
      error_header=error_header+" |"
      error_header=error_header+self.centerText("Pass",column_width)
      error_header=error_header+" : "
      error_header=error_header+self.centerText("Fail",column_width)
      
      error_header=error_header+"   ["

      for value in self.m_error_buckets:
        if value==257:
          display_value=self.centerText(self.m_singval_col_hdr, column_width)
        elif value==258:
          display_value=self.centerText(self.m_promira_error_col_hdr, column_width)
        elif value==259:
          display_value=self.centerText(self.m_actual_clock_col_hdr, column_width)
        else:
          display_value=self.centerText("%d"%value, column_width)
          
        error_header=error_header+display_value
        
      error_header=error_header+"]"
      topline= "*" * len(error_header)
      bottom=  "-" * len(error_header)
      return [ topline, error_header, bottom ]


    
    def errorCountBuckets(self, bucket_ndx):
      column_width=self.columnWidth()
      
      if bucket_ndx >= len(self.m_errors):
        self.m_testutil.fatalError("Index Out Of Range")
                                   
      error_count_array=self.m_errors[bucket_ndx]
      error_display=" ["

      for value in error_count_array:
        if value==0:
          display_value=self.centerText('-', column_width)
        else:
          display_value=self.centerText("%d"%value, column_width)
          
        error_display=error_display+display_value
        
      error_display=error_display+"]"
      return error_display
  
    def dumpHistogram(self):
      
      # width of total events is width of largest number
      self.m_number_width=len(str(self.m_event_count))
      
      #s=(0,2)
      data_max_count=np.zeros(2)
      data_min_count=np.zeros(2)
      max_count_label=['','']
      min_count_label=['','']
      data_total_count=np.zeros(2)
      
      for ndx in range(len(self.m_bucket_data)):
        for ydx in range (len(self.m_data_values)):
          if self.m_bucket_data[ndx][ydx] > data_max_count[ydx]:
            # update total count
            data_total_count[ydx]+=self.m_bucket_data[ndx,ydx]


          # test/update max count
          if self.m_bucket_data[ndx][ydx] > data_max_count[ydx]:
            data_max_count[ydx]=self.m_bucket_data[ndx][ydx]
            max_count_label.pop(ydx)
            max_count_label.insert(ydx,self.m_bucket_labels[ndx])
            pass
              
          # test/update min count
          if self.m_bucket_data[ndx][ydx] < data_min_count[ydx]:
            data_min_count[ydx]=self.m_bucket_data[ndx][ydx]
            max_count_label.pop(ydx)
            max_count_label.insert(ydx,self.m_bucket_data[ndx])
            pass
    

      '''
      display total trials
      display total events for each data value
      '''
      if False:
        total_trials=data_total_count[0]+data_total_count[1]
        self.display("Total Trials= %d" % total_trials)
        for ydx in self.m_data_value_range:
          self.display("Total %s = %d" % (self.m_data_labels[ydx],data_total_count[ydx]))
          
        '''
        display max/min for each data value
        '''  
        for ndx in self.m_data_value_range:
          self.display("Max %s = %d at %s" % (self.m_data_labels[ndx],data_max_count[ndx], max_count_label[ndx]))
          self.display("Min %s = %d at %s" % (self.m_data_labels[ndx],data_min_count[ndx], min_count_label[ndx]))
        
        
      for line in self.histogramHeader():
        self.display(line)
          
      column_width=self.columnWidth()
      
      for ydx in self.m_bucket_range:
        if self.m_bucket_data[ydx,0]!=0 or self.m_bucket_data[ydx,1]!=0:
          self.display('  %s %s | %s:%s | %s' 
                                             %  (self.m_bucket_labels[ydx], 
                                                 self.m_bucket_units_label,
                                                 self.centerText(str(int(self.m_bucket_data[ydx,0])), column_width),
                                                 self.centerText(str(int(self.m_bucket_data[ydx,1])), column_width),
                                                 self.errorCountBuckets(ydx)) )
              
      '''
      display max counts
      '''

      #for ndx in range (len(self.m_bucket_data)):
      pass
        
    def addSuccess(self, value):
      pass
       
    '''
    generate a set of bucket values and labels
    based on the success/failure of events with present buckets
    
    ALGO:
      select two highest bucket values with NO FAILURES
      select the two lowest bucket values with NO SUCCESS
      limit total buckets to 10
      range from the lowest of the two non-fail buckets ...
      ...to the highest of the two non-success buckets
      linearly assign buckets between them
      
    CAVEAT:
      this is a naive algorithm that PRESUMES that optimal
      performance will occur in the initial buckets and degrade
      with succeeding indexed buckets.
      Additional assumption that the most degraded performance
      will be in the highest indexed buckets and improve as
      the index decreases.
    '''
    def refine_buckets(self, min_bucket_value):
      
      all_fail_detection_count=0
      all_pass_detection_count=0
      all_fail_bucket_indices=[]
      all_pass_bucket_indices=[]
      bucket_margin=3
      
      for index in self.m_bucket_range:
        
        bucket_data=self.m_bucket_data[index]

        if (all_fail_detection_count<=2 or 
            all_pass_detection_count<=2):
          
          if bucket_data[0]==0 and bucket_data[1]>0:
            all_fail_detection_count+=1
            all_fail_bucket_indices.append(index)

          if bucket_data[1]==0 and bucket_data[0]>0:
            all_pass_detection_count+=1
            all_pass_bucket_indices.append(index)
            

      if (all_fail_detection_count<bucket_margin and 
          all_pass_detection_count<bucket_margin):
        return None, None

      all_fail_bucket_indices=all_fail_bucket_indices[:bucket_margin]
      all_pass_bucket_indices=all_pass_bucket_indices[-bucket_margin:]
      
      if len(all_fail_bucket_indices) == 0 or len(all_pass_bucket_indices)==0:
        # insufficient data to work
        return None, None
                        
                      
      #use highest all_fail index               
      vernier_max_index=all_fail_bucket_indices[-1]
      #use lowest all succeed index
      vernier_min_index=all_pass_bucket_indices[0]
      

      max_vernier_value = self.m_bucket_values[vernier_max_index]
      min_vernier_value = self.m_bucket_values[vernier_min_index]
      if min_vernier_value > min_bucket_value:
        min_vernier_value=min_bucket_value
      
      
      vernier_granularity=50
      
      range_buckets=15          
      range_length = float(max_vernier_value - min_vernier_value)
      range_step   = range_length / range_buckets
      range_step   = vernier_granularity*int((range_step+(vernier_granularity/2)+1)/vernier_granularity)
      
      vernier_values = [int(min_vernier_value+(range_step*index)) for index in range(range_buckets)]
      vernier_labels = [str(vernier_values[index]) for index in range(range_buckets)]
      return vernier_values, vernier_labels
      
          
      pass



'''
eventTimeLine()
   an animated character based Event Timeline
   the 'time' variable is the advancing count/sequence of events
   animation is driven by evolution as events accumulate
   
   an additional mechanic is a replay scroll through the display
   
   linear, exponential, polynomial, logarithmic scales are available
   to provide views to focus attention on different time periods
   of the event generation and evolution.
   
   in evolutionary mode:
     the display animates as events accumulate

   in replay mode:
     the evolutionary display, events are sequentially displayed from
     the accumulated event data-set.
     
   in review mode:
     subsets of the evolutionioray sequence can be displayed in detail
     with lensing interval metrics, expanding display in areas.

   manages event-sequence data display
   display is on a horizontal axis sorted by event
   events occurring at the same sequence interval display in the same
   horizontal position on the sequence (horizontal) axis
   
   the axis shifts in one direction with sequence-advance/time.
   the represented width of sequence intervals narrows with sequence-time
   as sequence intervals shift away from 'NOW', they will be combined with
   previous sequence intervals until they are bunched in the single interval
   furthest from 'NOW'.
   
   the sequence-time scale can be linear, or nonlinear.
   
'''

DisplayedEvent=coll.namedtuple('DisplayedEvent', 'event_type event_mhz sequence_number event_count')
  
class eventTimeLine(object):


  EVT_ORIGIN          = 0
  EVT_LOWFREQ_ERROR   = 1
  EVT_LOWFREQ_1VAL    = 2
  EVT_PROMIRA_ERR     = 3
  
  m_event_type_list   = [EVT_LOWFREQ_ERROR, EVT_LOWFREQ_1VAL, EVT_PROMIRA_ERR, EVT_ORIGIN]
  m_event_type_symbol = ["e", "s", "p", '|']
  
  EVTSCALE_LINEAR     = 1
  EVTSCALE_EXP        = 2
  EVTSCALE_LOG        = 3
  EVTSCALE_ROOT       = 4
  EVTSCALE_LENSE      = 5
  EVTSCALE_ROTATE     = 6

  m_interval_table    = None
  m_interval_buckets  = None
  m_event_buckets     = None
  m_rotate_event_buckets = None
  m_display_events    = None
  m_display_range     = None
  m_max_display_column= None
  m_rev_display_range = None
  m_interval_index    = None
  m_event_list        = None
  
  def __init__(self, display_width, max_sequence_number,  scale_type):
    self.m_max_display_column = display_width-1
    self.m_max_sequence_number= max_sequence_number
    self.m_event_buckets= [ [] for bucket in range(display_width)]
    self.m_display_range=range(len(self.m_event_buckets))
    self.m_rev_display_range=range(len(self.m_event_buckets)-1, -1, -1)
    self.m_display_events=[]
    self.build_intervals()
    self.m_scale_type=scale_type


  def computeIntervals(self, interval_endpoints):
    last_endpoint=0
    interval=[]
    for index in range (len(interval_endpoints)):
      this_endpoint=interval_endpoints[index]
      interval.append([last_endpoint, this_endpoint])
      last_endpoint=this_endpoint
    return interval
  
  def buildRuler(self, interval_endpoints):
    ruler=str('#')
    hash_interval=self.m_max_sequence_number//10
    next_hash=hash_interval
    for index in range(len(interval_endpoints)):
      if interval_endpoints[index]>next_hash:
        ruler+='#'
        next_hash+=hash_interval
      else:
        ruler+='-'
        
    return ruler
  
  def build_intervals(self):
    self.m_interval_table = []
    end_index=self.m_display_range[-1]
    start_index=self.m_display_range[0]
    final_dwell_time=self.m_max_sequence_number
    
    '''
    Linear Interval
    '''
    # y=mx; x(end_index)=10000
    interval_endpoints=[]
    slope=float(final_dwell_time/end_index)
    for index in self.m_display_range:
      interval_endpoints.append(int(slope*index))
      
    linear_interval=self.computeIntervals(interval_endpoints)
    ruler=self.buildRuler(interval_endpoints)
    self.m_interval_table.append([self.EVTSCALE_LINEAR, linear_interval, ruler])

    '''
    exponential interval
    '''
    # y(x)=k^x; ln(y(x))=x*ln(k); e^(ln(y(x))/x)=k
    interval_endpoints=[]
    k=math.exp(math.log(final_dwell_time)/end_index)
    for index in self.m_display_range:
      interval_endpoints.append(int(k**index))
      
    exp_interval=self.computeIntervals(interval_endpoints)
    ruler=self.buildRuler(interval_endpoints)
    self.m_interval_table.append([self.EVTSCALE_EXP, exp_interval, ruler])

    '''
    log interval
    '''
    #y(x)=k*log(2+x); y(x)/log(2+x)=k
    interval_endpoints=[]
    k=final_dwell_time/math.log(2+end_index)
    for index in self.m_display_range:
      interval_endpoints.append(int(k*math.log(2+index)))
      
    log_interval=self.computeIntervals(interval_endpoints)
    ruler=self.buildRuler(interval_endpoints)
    self.m_interval_table.append([self.EVTSCALE_LOG, log_interval, ruler])

    '''
    polynomial interval
    '''
    poly_power=2
    #y(x)=k*x^poly_power;y(x)/x^poly_power=k  
    interval_endpoints=[]
    k=final_dwell_time/(end_index**poly_power)
    for index in self.m_display_range:
      interval_endpoints.append(int(k*(index**poly_power)))
      
    poly_interval=self.computeIntervals(interval_endpoints)
    ruler=self.buildRuler(interval_endpoints)
    self.m_interval_table.append([self.EVTSCALE_ROOT, poly_interval, ruler])
    
    '''
    lense interval
    --------------------------
    # Y(x) = poly(x) = k (x-xmid)^n ; n=2 
    #--------------------------------------------------
    # Sum k * int(poly(x)) over (0, Xmax) == Smax
    # 
    #--------------------------------------------------
    '''
    
    display_columns=self.m_max_display_column+1
    poly_list=[]
    
    degree=2
    
    def polyInt(x):
      p=math.fabs(math.pow((x-self.m_max_display_column/2),degree))
      return int(0.5+p)
    
    def sumPolyInt(start, end):
      poly_sum=0
      for x in range(start, end):
        poly_int=polyInt(x)
        poly_list.append(poly_int)
        poly_sum+=poly_int
        
      return poly_sum
    
    interval_endpoints=[]
    k=self.m_max_sequence_number/sumPolyInt(0, self.m_max_display_column)
    
    for index in self.m_display_range:
      endpoint=k*polyInt(index)
      if index>0:
        endpoint+=interval_endpoints[-1]
      interval_endpoints.append(int(endpoint+.5))

    lense_interval=self.computeIntervals(interval_endpoints)
    ruler=self.buildRuler(interval_endpoints)
    self.m_interval_table.append([self.EVTSCALE_LENSE, lense_interval, ruler])
        
  def selectInterval(self, scale_type):
    entry=list(filter( lambda x:scale_type == x[0], self.m_interval_table))
    return entry[0][1]
  
  def selectRuler(self, scale_type):
    entry=list(filter( lambda x:scale_type == x[0], self.m_interval_table))
    return entry[0][2]
  
  
  def addOrigin(self):
    self.addEvent(self.EVT_ORIGIN, None, 0)
    
  def addEvent(self, event__type, event__mhz, sequence__number ):
    event=DisplayedEvent(  event_type=event__type,
                           event_mhz=event__mhz,
                           sequence_number=sequence__number,
                           event_count=1)
    
    self.m_display_events.append(event)
    self.m_event_buckets[0].append(event)
  

  
  '''
  ageEvents
      ... from timeline start towards timeline end
      move events to 'next' bucket when its age exceeds the bucket limit
      
  '''


  
  def ageEvents(self, current_sequence_number, interval):
    
    for index in self.m_rev_display_range:
      prev_index=index-1
      #TODO  ?is this next line OK?
      if prev_index<0:
        break

      '''
      assumption: items appended in sequence
      promote events to next bucket as they 'age out'
      promote from end of list toward beginning
       - prevents out-of-range exception
      stop promoting once an event is 'too young' to promote
       - prevents wasting time and effort
       - pleases users and saves the planet!!
      '''
      
      for event in self.m_event_buckets[prev_index]:
        event_entry_time=event.sequence_number
        event_age=current_sequence_number-event_entry_time
        if event_age > interval[prev_index][1]:
          #item will always be oldest, last one
          pop_event=self.m_event_buckets[prev_index].pop(-1)
          self.m_event_buckets[index].insert(0, pop_event)



  '''
  rotateIntervals()
  ... the dataset is complete when this is used
      each 'rotation' is a rotation of the display intervals.
      events are populated into buckets corresponding to fixed display intervals.
      rotating the non-linear intervals causes the displayed events to pack
      more or less tightly together, as the interval metric is rotated.
  '''
  def rotateEvents(self, sequence_step, ):
    
    pass

  '''
  'lensing' event display metric
       each distribution has sparse and dense regions of display
       these regions are reflected in the display intervals
       rotating the sequence_number width of the buckets, then
       redistributing the events among the buckets effects a
       lensing effect, which can move the focus of the display.
  '''
  def distributeEvents(self, interval):
    for event in self.m_display_events:
      for interval in self.m_interval_buckets:
        pass
      
    for index in self.m_rev_display_range:
      prev_index=index-1
      if prev_index<0:
        break

      for evt_index in range(len(self.m_event_buckets[prev_index])):
        event=self.m_event_buckets[prev_index][evt_index]
        event_entry_time=event.sequence_number
        event_age=current_sequence_number-event_entry_time
        if event_age > interval[prev_index][1]:
          pop_event=self.m_event_buckets[prev_index].pop(evt_index)
          self.m_event_buckets[index].insert(0, pop_event)    
    pass
  
    
  '''
  rotateDisplay
      incrementally offset the event display with wrap-at-boundaries
      method 1:
        a. create a relative_intervals list
        b. assign the sequence_start_number to the zeroeth interval of the list
        c. evaluate the interval for each bucket as offsets from the
        d. wrap the sequence numbering around the interval list boundaries 
        c. populate a rotated_display_buckets iist with events
        d.   display the events
        e.   increment/decrement the sequence_number of interval 0
        f.   promote events forwards/backwards per direction variable
        g.   continue at d until break
        
  '''
  '''
  rotateInterval
    scale_type              -  scale_type to be projected
    origin_sequence_number  -  sequence_number aligned with scale origin
    sequence_steps          -  sequence counts to rotate (+ = right; - = left)
    pause                   -  ms to pause between steps
  '''  
  
  def relativeInterval(self, intervals):
    relative=[]
    for bucket in intervals:
      relative.append([0, bucket[1]-bucket[0]])
    return relative
  
  '''
  populateRelativeIntervals
    intervals  -  a zero-origin interval set
    
        
  '''
  def populateOffsetIntervals(self, intervals, origin_sequence_number):
    sequence_number_ptr=origin_sequence_number
    
    display_buckets=[[] for _ndx in range(self.m_display_range)]
    display_bucket_count=self.m_max_display_column+1
    
    interval_index=0
    interval_start=origin_sequence_number

    buckets = filter( self.m_event_buckets )
    
    # reorder events, starting with events at or
    # just above origin_sequence_number
    high_buckets = list(filter(lambda x: x.sequence_number >=origin_sequence_number, self.m_display_events)) 
    low_buckets = list(filter(lambda x: x.sequence_number < origin_sequence_number, self.m_display_events))
    events=high_events+low_events

    # only one pass through events and intervals    
    for interval_index in range(len(intervals)):
      interval=intervals[interval_index]
      
      # computes bucket sequence number boundaries, wraps at max value
      bucket_start=(interval_start+interval[0]) % self.m_max_sequence_number
      bucket_end=(interval_start+interval[1]) % self.m_max_sequence_number

      for event in events:
        if ( event.sequence_number >= bucket_start
             and bucket_end <= event.sequence_number ):
              display_buckets[interval_index].append(event)
        else:
          break
      
      
    # all display events are populated
    return display_events
    
  def initializeIntervalRotation(self, scale_type, origin_sequence_number, sequence_steps, pause_seconds):
    # get interval and data
    interval_info=self.m_interval_table[scale_type]
    # rotate the initial bucket distribution of the event data
    # the interval buckets and ruler hash marks are unchanged
    self.m_rotate_event_buckets=self.populateOffsetIntervals(interval_info[1], origin_sequence_number)
    self.m_rotate_sequence_offset=0
    self.m_rotate_sequence_steps=sequence_steps
    self.m_rotate_pause_seconds=pause_seconds


  def stepEventRotation(self):
    self.rotateEvents()
  
    for display_pass in self.m_event_type_list:
      event_symbol=str(self.m_event_type_symbol[self.m_event_type_list.index(display_pass)])
      timeline=""
          
      for event_list in self.m_event_buckets:
        count=0
        if len(event_list) > 0:
          for event in event_list:
            if event.event_type==display_pass:
              count+=1
        if count==0:
          sym_str=(" ")
        elif count==1:
          sym_str=event_symbol.lower()
        else:
          sym_str=event_symbol.upper()
        timeline=timeline+sym_str
        
      print(timeline)    
    pass
    
  def displayEvents(self, scale_type, current_sequence_number):
    interval=self.selectInterval(scale_type)
    self.ageEvents(current_sequence_number, interval)
    
  
    for display_pass in self.m_event_type_list:
      event_symbol=str(self.m_event_type_symbol[self.m_event_type_list.index(display_pass)])
      timeline=""
          
      for event_list in self.m_event_buckets:
        count=0
        if len(event_list) > 0:
          for event in event_list:
            if event.event_type==display_pass:
              count+=1
        if count==0:
          sym_str=(" ")
        elif count==1:
          sym_str=event_symbol.lower()
        else:
          sym_str=event_symbol.upper()
        timeline=timeline+sym_str
        
      print(timeline)
  
    
    
randobj=Random()
randobj.seed(3)
display_events=180
max_sequence_number=1000000
event_scale=eventTimeLine.EVTSCALE_LINEAR
timeline=eventTimeLine(display_events, max_sequence_number, event_scale)

ruler=timeline.selectRuler(event_scale)

for sequence in range(max_sequence_number*2):
  rand_int=randobj.getrandbits(16)
  
  if rand_int==0:
    timeline.addEvent(eventTimeLine.EVT_LOWFREQ_1VAL, 15, sequence)
  elif rand_int==32:
    timeline.addEvent(eventTimeLine.EVT_LOWFREQ_ERROR, 15, sequence)
  elif rand_int==66:
    timeline.addEvent(eventTimeLine.EVT_PROMIRA_ERR, 15, sequence)
  
  if sequence % 10 == 0:
    print(ruler)
    timeline.displayEvents(event_scale, sequence)
    time.sleep(.001)

      

  