'''
Created on Feb 6, 2020

@author: honea
'''

import promact_is_py as pmact
import promira_py as pm
  
 
from __future__ import division, with_statement, print_function
import sys
import time

from promira_py import *
from promact_is_py import *


#==========================================================================
# FUNCTION (APP)
#==========================================================================
APP_NAME = "com.totalphase.promact_is"
def dev_open (ip):
    pm = pm_open(ip)
    if pm <= 0:
         print("Unable to open Promira platform on %s" % ip)
         print("Error code = %d" % pm)
         sys.exit()

    ret = pm_load(pm, APP_NAME)
    if ret < 0:
         print("Unable to load the application(%s)" % APP_NAME)
         print("Error code = %d" % ret)
         sys.exit()

    conn = ps_app_connect(ip)
    if conn <= 0:
         print("Unable to open the application on %s" % ip)
         print("Error code = %d" % conn)
         sys.exit()

    channel = ps_channel_open(conn)
    if channel <= 0:
         print("Unable to open the channel")
         print("Error code = %d" % channel)
         sys.exit()

    return pm, conn, channel

def dev_close (pm, app, channel):
    ps_channel_close(channel)
    ps_app_disconnect(conn)
    pm_close(pm)


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 2):
    print("usage: gpio IP")
    sys.exit()

ip = sys.argv[1]

# Open the device
pm, conn, channel = dev_open(ip)

# Configure the Promira adapter so all pins
# are now controlled by the GPIO subsystem
ps_app_configure(channel, PS_APP_CONFIG_GPIO)

# Turn off the external I2C line pullups
ps_i2c_pullup(channel, PS_I2C_PULLUP_NONE)

# Make sure the charge has dissipated on those lines
ps_gpio_set(channel, 0x0)
ps_gpio_direction(channel, 0xffff)

# By default all GPIO pins are inputs.  Writing 1 to the
# bit position corresponding to the appropriate line will
# configure that line as an output
ps_gpio_direction(channel, 0x1 | 0x8)

# By default all GPIO outputs are logic low.  Writing a 1
# to the appropriate bit position will force that line
# high provided it is configured as an output.  If it is
# not configured as an output the line state will be
# cached such that if the direction later changed, the
# latest output value for the line will be enforced.
ps_gpio_set(channel, 0x1)
print("Setting GPIO0 to logic low")

# The get method will return the line states of all inputs.
# If a line is not configured as an input the value of
# that particular bit position in the mask will be 0.
val = ps_gpio_get(channel)

# Check the state of GPIO1
if (val & 0x2):
    print("Read the GPIO1 line as logic high")
else:
    print("Read the GPIO1 line as logic low")

# Now reading the MISO line should give a logic high,
# provided there is nothing attached to the Promira
# adapter that is driving the pin low.
val = ps_gpio_get(channel)
if (val & 0x4):
    print("Read the GPIO2 line as logic high (passive pullup)")
else:
    print("Read the GPIO2 line as logic low (is pin driven low?)")

# Now do a 1000 gets from the GPIO to test performance
for i in range(1000):
    ps_gpio_get(channel)

# Demonstrate use of ps_gpio_change
ps_gpio_direction(channel, 0x00)
oldval = ps_gpio_get(channel)
print("Calling ps_gpio_change for 2 seconds...")
newval = ps_gpio_change(channel, 2000)
if (newval != oldval):
    print("  GPIO inputs changed.")
else:
    print("  GPIO inputs did not change.")

# Turn on the I2C line pullups since we are done
ps_i2c_pullup(channel, PS_I2C_PULLUP_BOTH)

# Configure the Promira adapter back to SPI/I2C mode.
ps_app_configure(channel, PS_APP_CONFIG_SPI | PS_APP_CONFIG_I2C)

# Close the device and exit
dev_close(pm, conn, channel)



class gpioUtil():

  _instance=None
  
  def __new__(cls):
      if cls._instance is None:
          print('Creating the testUtil object')
          cls._instance = super(gpioUtil, cls).__new__(cls)
      return cls._instance
  
  
  '''
  initGPIOPulse -
  
      build the queue to emit/toggle a signal via GPIO on demand.
      
  '''
  def initGPIO(self, gpio_pin):
    
    gpio_task_queue = pmact.ps_queue_create(self.m_app_conn_handle,
                                          pmact.PS_MODULE_ID_GPIO)
    
  
  pass