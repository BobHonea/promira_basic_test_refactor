'''
Created on Feb 10, 2020

@author: honea
'''

import test_utility
import numpy as np

class result2DHistogram(object):
    '''
    classdocs
    collect and publish results
    '''

    m_bucket_labels     = None
    m_bucket_units_label= None
    m_bucket_values     = None
    m_bucket_data       = None
    m_data_labels       = None
    m_data_values       = None
    m_testUtil          = None
    
    def __init__(self, parameter_values, parameter_labels, parameter_units_label, data_values, data_labels ):
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
      print("Total Trials= %d" % total_trials)
      for ydx in self.m_data_value_range:
        print("Total %s = %d" % (self.m_data_labels[ydx],data_total_count[ydx]))
        
      '''
      display max/min for each data value
      '''  
      for ndx in self.m_data_value_range:
        print("Max %s = %d at %s" % (self.m_data_labels[ndx],data_max_count[ndx], max_count_label[ndx]))
        print("Min %s = %d at %s" % (self.m_data_labels[ndx],data_min_count[ndx], min_count_label[ndx]))
        
        
      for ydx in self.m_bucket_range:
        if self.m_bucket_data[ydx,0]!=0 or self.m_bucket_data[ydx,1]!=0:
          print('%s:%s at %s %s = %04d:%04d' %  (self.m_data_labels[0], self.m_data_labels[1], 
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
       

