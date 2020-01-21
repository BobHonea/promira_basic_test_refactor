"""Py test that does a test function"""

import usertest
import os
import time
import subprocess


class myTestApp(usertest.DutUserTest):
  """Unit test template"""

  m_PromiraOK = False
  
  def checkPromiraAPI(self):
    pass
  
  def runTestCore(self):
    pass
  
  def runTest(self):

    self.run_test_core()  

