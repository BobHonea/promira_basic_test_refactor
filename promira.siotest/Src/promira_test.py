from __future__ import division, with_statement, print_function
import TestSpiDut as spitest
import TestDutSIO as dutsio

######################################

#run SPI Test
TEST_I2C_NOT_SPI=False
TEST_NEW_SPITEST=True

if (TEST_NEW_SPITEST):
  test=spitest.promiraSpiTestApp()
  test.runTest()
