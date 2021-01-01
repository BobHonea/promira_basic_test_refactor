from __future__ import division, with_statement, print_function

import sys, os

######################################


srcpath=str(os.getcwd())
srcparent=srcpath.rsplit('//')[0]
promactpath=srcparent+"SerialPlatformAPI_Promact_IS"

#add project folders missing from system path
for folder in [ srcpath, promactpath ]:
  for sysfolder in sys.path:
    if folder==sysfolder:
      break
  print("adding %s to sys.path" % folder)
  sys.path.append(folder)

print("--------------")
print(sys.path)
print("--------------")

import TestSpiDut as spitest

#run SPI Test
TEST_I2C_NOT_SPI=False
TEST_NEW_SPITEST=True

if (TEST_NEW_SPITEST):
  test=spitest.promiraSpiTestApp()
  test.runTest()
