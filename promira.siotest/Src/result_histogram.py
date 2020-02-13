'''
Created on Feb 10, 2020

@author: honea
'''

import test_utility
import numpy as np
from _ast import Or

class result2DHistogram(object):
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

    
    def __init__(self,  parameter_values, parameter_labels,
                        parameter_units_label, 
                        data_values, data_labels ):
        '''
        Constructor
        '''
        m_testUtil=test_utility.testUtil()
        
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
 
        s=(self.m_bucket_count,2)
        self.m_bucket_data      = np.zeros(s)


    def addData(self, parameter_value, data_value):
      bucket_ndx=self.m_bucket_values.index(parameter_value)
      data_ndx=self.m_data_values.index(data_value)
      self.m_bucket_data[bucket_ndx,data_ndx]+=1
      pass
    
    def display(self, out_string):
      test_utility.testUtil().bufferDisplayInfo(out_string)
      
    def dumpHistogram(self):
      
      s=(0,2)
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
        if self.m_bucket_data[ydx,0]!=0 or self.m_bucket_data[ydx,1]!=0:
          self.display('%s:%s at %s %s = %04d:%04d' %  (self.m_data_labels[0], self.m_data_labels[1], 
                                                 self.m_bucket_labels[ydx], 
                                                 self.m_bucket_units_label,
                                                 self.m_bucket_data[ydx,0],
                                                 self.m_bucket_data[ydx,1]))
              
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
