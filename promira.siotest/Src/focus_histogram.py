'''
Created on Feb 10, 2020

@author: honea
'''

import test_utility
import numpy as np
import collections as coll
from builtins import None

class result2DHistogram(object):
    '''
    classdocs
    collect and publish results
    '''
    ResultSet=coll.namedtuple('ResultSet', 'index_range bucket_count bucket_parameters bucket_data data_value_list bucket_labels bucket_label_units')

    basedata            = None
    focusdata           = None
    m_testUtil          = None
    
    m_base_set          = None
    m_focus_set         = None
    
    BKTFOCUS_UNDEFINED  = 0
    BKTFOCUS_NORMAL     = 1
    BKTFOCUS_DECIMATE   = 2
    BKTFOCUS_IN_FOCUS   = 3
    
    
    '''
    Setup Histogram by providing:
    1. parameter value_list    -  a list of histogram bucket centerpoint values
    2. parameter units string  -  such as 'MHz', "ms', 'microsecond', '10e-06 sec'
    3. data_values             -  presently only [ True, False ] accepted
                        
    '''

    def buildBuckets(self, parameter_list, parameter_units_string, data_value_list):
        if (type(parameter_units_string) != str):
          self.m_testutil.fatalError("illegal label format")

        _bucket_count       = len(parameter_list)
        _index_range        = range(_bucket_count)
        _bucket_parameters  = parameter_list
        _bucket_index_range = range(len(parameter_list))
        _label_units_string = parameter_units_string
        _label_format       = '@ %d %s'
        _data_value_list    = data_value_list
        _bucket_labels      = [ _label_format % (parameter, _label_units_string ) for parameter in _bucket_parameters]
        _bucket_data        = np.zeros(_bucket_count,2)
        return self.ResultSet(index_range=_index_range, bucket_count=_bucket_count, bucket_parameters=_bucket_parameters,
                         bucket_data=_bucket_data, data_values=_data_value_list, bucket_labels=_bucket_labels, _bucket_label_units=_label_units_string) 
        
      
      
    def __init__(self,  parameter_values, parameter_units_string, data_value_list)
        '''
        Constructor
        '''
        self.m_base_set = self.buildBuckets(parameter_values, parameter_units_string, data_value_list)
        m_testUtil=test_utility.testUtil()
        



    def addData(self, parameter_value, data_value):
      if self.m_focus_enabled:
        # update focus bucket spectrum
        bucket_ndx=self.m_focus_set.bucket_parameters.index(parameter_value)
        data_ndx=self.m_focus_set.data_value_list.index(data_value)
        self.m_focus_set.bucket_data[bucket_ndx, data_ndx]+=1
        
        # update to original bucket spectrum **also**
        base_ndx=self.m_focus_bucket_xlat[0]
        self.basedata.bucket_data[base_ndx, data_ndx]+=1
        
        self.m_bucket_events+=1

      else:
        bucket_ndx=self.m_base_set.bucket_parameters.index(parameter_value)
        data_ndx=self.m_base_set.data_value_list.index(data_value)
        self.m_base_set.bucket_data[bucket_ndx, data_ndx]+=1

        # update the bucket spectrum
        self.m_bucket_events+=1
      pass
    
    def bucketFocus(self, parameter_value):
      if parameter_value in self.m_bucket_values:
        index = self.m_bucket_values.index(parameter_value)
        return self.m_bucket_focus[index]
    
    def display(self, out_string):
      test_utility.testUtil().bufferDisplayInfo(out_string)

    '''
    Histogram Bucket Weight
    Histogram Bucket Granularity
    
    The range in the initial configuration of clock frequencies must be preserved
      ...so test coverage is not lost
      
    The focus of results desplay can be focused on buckets with "mixed' pass/fail
    results.
    
    The number of tests in buckets with unmixed pass/fail results can be reduced.
      ...since they are stable on all-pass or all-fail, they aren't interesting
      
    On a heuristic level, all-pass/all-fail buckets furthest from the mixed result
    buckets are presumed to be unlikely to fail. the testing in these buckets can
    be reduced to a level to continue to confirm their stability, and to catch 
    any new instability.
    
    heuristic:  the further a bucket is from a mixed-result bucket the less weight
                the less weight, fewer tests / greater decimation of test events
                the more equal pass and fail numbers are, the more 'lensing'
                  lensing: local increase in granularity (decrease in bucket width)
    
    
    '''
      
    m_bucket_weight           = None
    m_bucket_pfratio          = None
    m_bucket_pass_event_ratio = None
    m_bucket_focus_code       = None
    
    m_refocus_bucket_values   = None
    m_refocus_bucket_weight   = None
    m_refocus_bucket_pfratio  = None
    
    m_focus_magnification     = 3
    
    LENSE_UNDEFINED           = 0
    LENSE_DEFOCUS             = 1
    LENSE_UNCHANGED           = 2
    LENSE_FOCUS               = 3



    def dumpFocusHistogram(self):
      s=(0,2)
      data_max_count=np.zeros(2)
      data_min_count=np.zeros(2)
      max_count_label=['','']
      min_count_label=['','']
      data_total_count=np.zeros(2)
      
      for ndx in range(len(self.basedata.bucket_data)):
        for ydx in range (len(self.m_data_values)):
          if self.basedata.bucket_data[ndx][ydx] > data_max_count[ydx]:
            # update total count
            data_total_count[ydx]+=self.basedata.bucket_data[ndx,ydx]


          # test/update max count
          if self.basedata.bucket_data[ndx][ydx] > data_max_count[ydx]:
            data_max_count[ydx]=self.basedata.bucket_data[ndx][ydx]
            max_count_label.pop(ydx)
            max_count_label.insert(ydx,self.m_bucket_labels[ndx])
            pass
              
          # test/update min count
          if self.basedata.bucket_data[ndx][ydx] < data_min_count[ydx]:
            data_min_count[ydx]=self.basedata.bucket_data[ndx][ydx]
            max_count_label.pop(ydx)
            max_count_label.insert(ydx,self.basedata.bucket_data[ndx])
            pass
    

      '''
      display total trials
      display total events for each data value
      '''
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
        
        
      for ydx in self.m_bucket_range:
        if self.basedata.bucket_data[ydx,0]!=0 or self.basedata.bucket_data[ydx,1]!=0:
          self.display('%s:%s at %s %s = %04d:%04d' %  (self.m_data_labels[0], self.m_data_labels[1], 
                                                 self.m_bucket_labels[ydx], 
                                                 self.m_bucket_units_label,
                                                 self.basedata.bucket_data[ydx,0],
                                                 self.basedata.bucket_data[ydx,1]))
              
      '''
      display max counts
      '''

      #for ndx in range (len(self.basedata.bucket_data)):
      pass
      

    def genFocusHistogram(self):
      
      self.m_bucket_weight=[]
      self.m_bucket_pass_ratio=[]
      
      '''
      get continuum of pass/event ratio in .1 units
      '''
      lense_width=3

      for index in self.m_bucket_range:
        self.m_bucket_pass_ratio.append(int(10*float(self.basedata.bucket_data[0])/self.m_bucket_events))
        

      '''
      compute pf difference
      assign focus codes to base buckets
      compute total focus histogram buckets 
      '''
        
      self.m_bucket_focus_code=[]
        
      for index in self.m_bucket_range:
        lense_min_index=max[index-lense_width, 0]
        lense_max_index=min[len(self.m_bucket_range), index+lense_width]
        lensing_sum=0
        
        for lense_index in range(lense_min_index, lense_max_index)
          if self.m_bucket_pass_ratio[index]!=self.m_bucket_pass_ratio[lense_index]:
            lensing_sum+=1
            
        self.m_lensing_sum.append(lensing_sum)
        self.m_focus_display_buckets = 0
        focus_bucket_sum = 0
        
        for index in self.m_bucket_range:
          lensing_sum = self.m_lensing_sum[index]
          
          if lensing_sum < 3:
            focus_code = self.LENSE_DEFOCUS
            focus_buckets = 1
          elif lensing_sum < 5:
            focus_code = self.LENSE_UNCHANGED
            focus_buckets = 1
          else:
            focus_code = self.LENSE_FOCUS
            focus_buckets = self.m_focus_magnification

          self.m_bucket_focus_code=focus_code
          focus_bucket_sum += focus_buckets
        
        self.m_focus_buckets_range=range(focus_bucket_sum)
        self.m_focus_bucket_xlat=[]
        

        self.m_bucket_xlat = []
        
        for index in self.m_bucket_range:
          bucket_focus_code = self.m_bucket_focus_code[index]
          if bucket_focus_code==self.LENSE_DEFOCUS:
            self.m_bucket_xlat.append([index, self.LENSE_DEFOCUS])
          elif bucket_focus_code==self.LENSE_UNCHANGED:
            self.m_bucket_xlat.append([index, self.LENSE_UNCHANGED])
          else:
            focus_bucket=[index, self.LENSE_FOCUS]
            for index in range(self.m_focus_magnification):
              self.m_bucket_xlat.append(focus_bucket)
              
        

          
      
          
        
      
      pass
    def dumpHistogram(self):
      
      s=(0,2)
      data_max_count=np.zeros(2)
      data_min_count=np.zeros(2)
      max_count_label=['','']
      min_count_label=['','']
      data_total_count=np.zeros(2)
      
      for ndx in range(len(self.basedata.bucket_data)):
        for ydx in range (len(self.m_data_values)):
          if self.basedata.bucket_data[ndx][ydx] > data_max_count[ydx]:
            # update total count
            data_total_count[ydx]+=self.basedata.bucket_data[ndx,ydx]


          # test/update max count
          if self.basedata.bucket_data[ndx][ydx] > data_max_count[ydx]:
            data_max_count[ydx]=self.basedata.bucket_data[ndx][ydx]
            max_count_label.pop(ydx)
            max_count_label.insert(ydx,self.m_bucket_labels[ndx])
            pass
              
          # test/update min count
          if self.basedata.bucket_data[ndx][ydx] < data_min_count[ydx]:
            data_min_count[ydx]=self.basedata.bucket_data[ndx][ydx]
            max_count_label.pop(ydx)
            max_count_label.insert(ydx,self.basedata.bucket_data[ndx])
            pass
    

      '''
      display total trials
      display total events for each data value
      '''
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
        
        
      for ydx in self.m_bucket_range:
        if self.basedata.bucket_data[ydx,0]!=0 or self.basedata.bucket_data[ydx,1]!=0:
          self.display('%s:%s at %s %s = %04d:%04d' %  (self.m_data_labels[0], self.m_data_labels[1], 
                                                 self.m_bucket_labels[ydx], 
                                                 self.m_bucket_units_label,
                                                 self.basedata.bucket_data[ydx,0],
                                                 self.basedata.bucket_data[ydx,1]))
              
      '''
      display max counts
      '''

      #for ndx in range (len(self.basedata.bucket_data)):
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
        
        bucket_data=self.basedata.bucket_data[index]

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
      vernier_max_focus_index=all_fail_bucket_indices[-1]
      #use lowest all succeed index
      vernier_min_focus_index=all_pass_bucket_indices[0]
      
      new_bucket_values=[]
      new_bucket_focus=[]
      focus_factor=4
      focus_factor_range=range(focus_factor)
      
      max_vernier_value = self.m_bucket_values[vernier_max_focus_index]
      min_vernier_value = self.m_bucket_values[vernier_min_focus_index]


      for index in self.m_bucket_range:
        # lower focus intensity outside focus range
        if ( bucket_data[index] < vernier_min_focus_index 
              or bucket_data[index] > vernier_max_focus_index ):
          new_bucket_focus.append(self.BKTFOCUS_DECIMATE)
          new_bucket_values=self.bucket_values[index]
        else:
          # increase bucket granularity and higher intensity
          # within focus range
          if (index+1) in self.m_bucket_range:
            next_bucket_value=self.m_bucket_values[index+1]
            old_bucket_size=next_bucket_value=self.m_bucket_values[index]
          else:
            old_bucket_size=self.m_bucket_values[index]-self.m_bucket_values[index-1]
          pass 

          # increase bucket granularity within focus range
          sub_bucket_size=old_bucket_size/focus_factor

          for subindex in focus_factor_range:    
            new_bucket_focus.append(self.BKTFOCUS_IN_FOCUS)
            new_bucket_values.append(self.m_bucket_values[index]+subindex*sub_bucket_size)


      '''
      reset bucket metrics
      transfer data from old buckets to new
      '''
          self.basedata.bucket_data=
          self.m_bucket_values=
          self.m_data_labels=
          self.m_data_values=
  
        
      '''
      cast a new vernier
      buckets outside the focus area are changed to twice their width
      buckets inside the focus area are half their previous width
      focus status array is re-cast
      '''
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
