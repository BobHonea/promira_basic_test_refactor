#!/usr/bin/env python3
#==========================================================================
# (c) 2014-2019 Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Promira Sample Code
# File    : detect.py
#--------------------------------------------------------------------------
# Auto-detection test routine
#--------------------------------------------------------------------------
# Redistribution and use of this file in source and binary forms, with
# or without modification, are permitted.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
from __future__ import division, with_statement, print_function
from promira_py import *


#==========================================================================
# FUNCTION
#==========================================================================
def array_to_str (arr):
    string = arr.tostring()
    return string if isinstance(string, str) else string.decode('utf-8')


#==========================================================================
# MAIN PROGRAM
#==========================================================================
print("Detecting the Promira platforms...")

# Find all the attached devices
try:
    (num, ips, unique_ids, statuses) = pm_find_devices_ext(16, 16, 16)
except:
    num = 0

if num > 0:
    print("%d device(s) found:" % num)

    # Print the information on each device
    for i in range(num):
        ip        = ips[i]
        unique_id = unique_ids[i]
        status    = statuses[i]

        # Determine if the device is in-use
        if status & PM_DEVICE_NOT_FREE:
            inuse = "(in-use)"
        else:
            inuse = "(avail)"

        # Display device ip address, in-use status, and serial number
        ipstr = "%u.%u.%u.%u" \
            % (ip & 0xff, ip >> 8 & 0xff, ip >> 16 & 0xff, ip >> 24 & 0xff)
        print("    ip = %s   %s  (%04d-%06d)"
              % (ipstr, inuse, unique_id // 1000000, unique_id % 1000000))

        if not status & PM_DEVICE_NOT_FREE:
            pm = pm_open(ipstr)
            try:
                apps = array_to_str(pm_apps(pm, 1024)[1])
                print("    - apps = %s" % apps)
            except:
                print("    - apps = unable to retreive")
            pm_close(pm)

else:
    print("No devices found.")
