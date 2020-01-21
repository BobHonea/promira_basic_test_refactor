from __future__ import division, with_statement, print_function
import TestSpiDut as spitest
import TestDutSIO as dutsio

######################################

#run SPI Test
TEST_I2C_NOT_SPI=False
TEST_NEW_SPITEST=True

if (TEST_NEW_SPITEST):
  test=spitest.promiraTestApp()
  test.runTest(test.BUSTYPE_SPI)
else:
  test=spitest.promiraTestApp()
 
  if (TEST_I2C_NOT_SPI):
    test.runTest(test.BUSTYPE_I2C)
  else:
    test.runTest(test.BUSTYPE_SPI)
    