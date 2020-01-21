#==========================================================================
# Promira Management Interface Library
#--------------------------------------------------------------------------
# Copyright (c) 2014-2019 Total Phase, Inc.
# All rights reserved.
# www.totalphase.com
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# - Neither the name of Total Phase, Inc. nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
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
#--------------------------------------------------------------------------
# To access Promira devices through the API:
#
# 1) Use one of the following shared objects:
#      promira.so       --  Linux or macOS shared object
#      promira.dll      --  Windows dynamic link library
#
# 2) Along with one of the following language modules:
#      promira.c/h      --  C/C++ API header file and interface module
#      promira_py.py    --  Python API
#      promira.cs       --  C# .NET source
#==========================================================================


#==========================================================================
# VERSION
#==========================================================================
PM_API_VERSION    = 0x0128   # v1.40
PM_REQ_SW_VERSION = 0x0128   # v1.40


#==========================================================================
# IMPORTS
#==========================================================================
import os
import struct
import sys

from array import array, ArrayType

def import_library ():
    global api

    import platform
    ext = platform.system() == 'Windows' and '.dll' or '.so'
    dir = os.path.dirname(os.path.abspath(__file__))
    lib = os.path.join(dir, 'promira' + ext)

    try:
        if sys.version_info >= (3, 4):
            from importlib.machinery import ExtensionFileLoader
            from importlib.util import spec_from_file_location
            from importlib.util import module_from_spec

            loader = ExtensionFileLoader('promira', lib)
            spec = spec_from_file_location('promira', loader=loader)
            api = module_from_spec(spec)
            spec.loader.exec_module(api)

        else:
            import imp
            api = imp.load_dynamic('promira', lib)

    except:
        _, err, _ = sys.exc_info()
        msg = 'Error while importing promira%s:\n%s' % (ext, err)
        sys.exit(msg)

try:
    import promira as api
except ImportError:
    import_library()

del import_library

PM_SW_VERSION      = api.py_version() & 0xffff
PM_REQ_API_VERSION = (api.py_version() >> 16) & 0xffff
PM_LIBRARY_LOADED  = \
    ((PM_SW_VERSION >= PM_REQ_SW_VERSION) and \
     (PM_API_VERSION >= PM_REQ_API_VERSION))


#==========================================================================
# HELPER FUNCTIONS
#==========================================================================
def array_u08 (n):  return array('B', [0]*n)
def array_u16 (n):  return array('H', [0]*n)
def array_u32 (n):  return array('I', [0]*n)
def array_u64 (n):  return array('K', [0]*n)
def array_s08 (n):  return array('b', [0]*n)
def array_s16 (n):  return array('h', [0]*n)
def array_s32 (n):  return array('i', [0]*n)
def array_s64 (n):  return array('L', [0]*n)
def array_f32 (n):  return array('f', [0]*n)
def array_f64 (n):  return array('d', [0]*n)


#==========================================================================
# STATUS CODES
#==========================================================================
# All API functions return an integer which is the result of the
# transaction, or a status code if negative.  The status codes are
# defined as follows:
# enum PromiraStatus
# General codes (0 to -99)
PM_OK                        =    0
PM_UNABLE_TO_LOAD_LIBRARY    =   -1
PM_UNABLE_TO_LOAD_DRIVER     =   -2
PM_UNABLE_TO_LOAD_FUNCTION   =   -3
PM_INCOMPATIBLE_LIBRARY      =   -4
PM_INCOMPATIBLE_DEVICE       =   -5
PM_COMMUNICATION_ERROR       =   -6
PM_UNABLE_TO_OPEN            =   -7
PM_UNABLE_TO_CLOSE           =   -8
PM_INVALID_HANDLE            =   -9
PM_CONFIG_ERROR              =  -10
PM_SHORT_BUFFER              =  -11
PM_FUNCTION_NOT_AVAILABLE    =  -12

# Load command error codes (-100 to -199)
PM_APP_NOT_FOUND             = -101
PM_INVALID_LICENSE           = -102
PM_UNABLE_TO_LOAD_APP        = -103
PM_INVALID_DEVICE            = -104
PM_INVALID_DATE              = -105
PM_NOT_LICENSED              = -106
PM_INVALID_APP               = -107
PM_INVALID_FEATURE           = -108
PM_UNLICENSED_APP            = -109
PM_APP_ALREADY_LOADED        = -110

# Network info error codes (-200 to -299)
PM_NETCONFIG_ERROR           = -201
PM_INVALID_IPADDR            = -202
PM_INVALID_NETMASK           = -203
PM_INVALID_SUBNET            = -204
PM_NETCONFIG_UNSUPPORTED     = -205
PM_NETCONFIG_LOST_CONNECTION = -206


#==========================================================================
# GENERAL TYPE DEFINITIONS
#==========================================================================
# Promira handle type definition
# typedef Promira => integer

# Promira version matrix.
#
# This matrix describes the various version dependencies
# of Promira components.  It can be used to determine
# which component caused an incompatibility error.
#
# All version numbers are of the format:
#   (major << 8) | minor
#
# ex. v1.20 would be encoded as:  0x0114
class PromiraVersion:
    def __init__ (self):
        # Software and firmware versions.
        self.software      = 0
        self.firmware      = 0
        self.hardware      = 0

        # Firmware requires that software must be >= this version.
        self.sw_req_by_fw  = 0

        # Software requires that firmware must be >= this version.
        self.fw_req_by_sw  = 0

        # Software requires that the API interface must be >= this version.
        self.api_req_by_sw = 0

        # (year << 24) | (month << 16) | (day << 8) | build
        self.build         = 0


#==========================================================================
# MANAGEMENT API
#==========================================================================
# Get a list of Promira devices on the network.
#
# nelem   = maximum number of elements to return
# devices = array into which the IP addresses are returned
#
# Each element of the array is written with the IP address.
#
# If the array is NULL, it is not filled with any values.
# If there are more devices than the array size, only the
# first nmemb IP addresses will be written into the array.
#
# Returns the number of devices found, regardless of the
# array size.
def pm_find_devices (devices):
    """usage: (int return, u32[] devices) = pm_find_devices(u32[] devices)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # devices pre-processing
    __devices = isinstance(devices, int)
    if __devices:
        (devices, num_devices) = (array_u32(devices), devices)
    else:
        (devices, num_devices) = isinstance(devices, ArrayType) and (devices, len(devices)) or (devices[0], min(len(devices[0]), int(devices[1])))
        if devices.typecode != 'I':
            raise TypeError("type for 'devices' must be array('I')")
    # Call API function
    (_ret_) = api.py_pm_find_devices(num_devices, devices)
    # devices post-processing
    if __devices: del devices[max(0, min(_ret_, len(devices))):]
    return (_ret_, devices)


# Get a list of Promira devices on the network.
#
# This function is the same as pm_find_devices() except that
# it returns the unique ID and status of each Promira device.
# The IDs are guaranteed to be non-zero if valid.
#
# The IDs are the unsigned integer representation of the 10-digit
# serial numbers.
#
# If status is PM_DEVICE_NOT_FREE, the device is in-use by
# another host and is not ready for connection.
PM_DEVICE_NOT_FREE = 1
def pm_find_devices_ext (devices, unique_ids, statuses):
    """usage: (int return, u32[] devices, u32[] unique_ids, u32[] statuses) = pm_find_devices_ext(u32[] devices, u32[] unique_ids, u32[] statuses)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # devices pre-processing
    __devices = isinstance(devices, int)
    if __devices:
        (devices, num_devices) = (array_u32(devices), devices)
    else:
        (devices, num_devices) = isinstance(devices, ArrayType) and (devices, len(devices)) or (devices[0], min(len(devices[0]), int(devices[1])))
        if devices.typecode != 'I':
            raise TypeError("type for 'devices' must be array('I')")
    # unique_ids pre-processing
    __unique_ids = isinstance(unique_ids, int)
    if __unique_ids:
        (unique_ids, num_ids) = (array_u32(unique_ids), unique_ids)
    else:
        (unique_ids, num_ids) = isinstance(unique_ids, ArrayType) and (unique_ids, len(unique_ids)) or (unique_ids[0], min(len(unique_ids[0]), int(unique_ids[1])))
        if unique_ids.typecode != 'I':
            raise TypeError("type for 'unique_ids' must be array('I')")
    # statuses pre-processing
    __statuses = isinstance(statuses, int)
    if __statuses:
        (statuses, num_statuses) = (array_u32(statuses), statuses)
    else:
        (statuses, num_statuses) = isinstance(statuses, ArrayType) and (statuses, len(statuses)) or (statuses[0], min(len(statuses[0]), int(statuses[1])))
        if statuses.typecode != 'I':
            raise TypeError("type for 'statuses' must be array('I')")
    # Call API function
    (_ret_) = api.py_pm_find_devices_ext(num_devices, num_ids, num_statuses, devices, unique_ids, statuses)
    # devices post-processing
    if __devices: del devices[max(0, min(_ret_, len(devices))):]
    # unique_ids post-processing
    if __unique_ids: del unique_ids[max(0, min(_ret_, len(unique_ids))):]
    # statuses post-processing
    if __statuses: del statuses[max(0, min(_ret_, len(statuses))):]
    return (_ret_, devices, unique_ids, statuses)


# Open the Promira device
#
# Returns a Promira handle, which is guaranteed to be
# greater than zero if it is valid.
#
# This function is recommended for use in simple applications
# where extended information is not required.  For more complex
# applications, the use of pm_open_ext() is recommended.
#   str net_addr
def pm_open (net_addr):
    """usage: Promira return = pm_open(str net_addr)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_open(net_addr)


# Return the version matrix for the device attached to the
# given handle.  If the handle is 0 or invalid, only the
# software and required api versions are set.
def pm_version (promira):
    """usage: (int return, PromiraVersion version) = pm_version(Promira promira)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_version) = api.py_pm_version(promira)
    # version post-processing
    version = PromiraVersion()
    (version.software, version.firmware, version.hardware, version.sw_req_by_fw, version.fw_req_by_sw, version.api_req_by_sw, version.build) = c_version
    return (_ret_, version)


# Return the version matrix for the application to the
# given application name. Only firmware is valid and other
# will be set to 0.
def pm_app_version (promira, app_name):
    """usage: (int return, PromiraVersion app_version) = pm_app_version(Promira promira, str app_name)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_app_version) = api.py_pm_app_version(promira, app_name)
    # app_version post-processing
    app_version = PromiraVersion()
    (app_version.software, app_version.firmware, app_version.hardware, app_version.sw_req_by_fw, app_version.fw_req_by_sw, app_version.api_req_by_sw, app_version.build) = c_app_version
    return (_ret_, app_version)


# Sleep for the specified number of milliseconds
def pm_sleep_ms (milliseconds):
    """usage: int return = pm_sleep_ms(u32 milliseconds)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_sleep_ms(milliseconds)


# Network related commands
# enum PromiraNetCommand
PM_NET_ETH_ENABLE      = 0
PM_NET_ETH_IP          = 1
PM_NET_ETH_NETMASK     = 2
PM_NET_ETH_MAC         = 3
PM_NET_ETH_DHCP_ENABLE = 4
PM_NET_ETH_DHCP_RENEW  = 5
PM_NET_USB_IP          = 6
PM_NET_USB_NETMASK     = 7
PM_NET_USB_MAC         = 8

# Configure the network settings
def pm_query_net (promira, cmd, buf):
    """usage: (int return, u08[] buf) = pm_query_net(Promira promira, PromiraNetCommand cmd, u08[] buf)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # buf pre-processing
    __buf = isinstance(buf, int)
    if __buf:
        (buf, buf_size) = (array_u08(buf), buf)
    else:
        (buf, buf_size) = isinstance(buf, ArrayType) and (buf, len(buf)) or (buf[0], min(len(buf[0]), int(buf[1])))
        if buf.typecode != 'B':
            raise TypeError("type for 'buf' must be array('B')")
    # Call API function
    (_ret_) = api.py_pm_query_net(promira, cmd, buf_size, buf)
    # buf post-processing
    if __buf: del buf[max(0, min(_ret_, len(buf))):]
    return (_ret_, buf)


def pm_config_net (promira, cmd, data):
    """usage: int return = pm_config_net(Promira promira, PromiraNetCommand cmd, str data)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_config_net(promira, cmd, data)


# Configure the preferences
def pm_query_pref (promira, key, buf):
    """usage: (int return, u08[] buf) = pm_query_pref(Promira promira, str key, u08[] buf)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # buf pre-processing
    __buf = isinstance(buf, int)
    if __buf:
        (buf, buf_size) = (array_u08(buf), buf)
    else:
        (buf, buf_size) = isinstance(buf, ArrayType) and (buf, len(buf)) or (buf[0], min(len(buf[0]), int(buf[1])))
        if buf.typecode != 'B':
            raise TypeError("type for 'buf' must be array('B')")
    # Call API function
    (_ret_) = api.py_pm_query_pref(promira, key, buf_size, buf)
    # buf post-processing
    if __buf: del buf[max(0, min(_ret_, len(buf))):]
    return (_ret_, buf)


def pm_config_pref (promira, key, data):
    """usage: int return = pm_config_pref(Promira promira, str key, str data)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_config_pref(promira, key, data)


# Get a list of apps installed on the device.
def pm_apps (promira, apps):
    """usage: (int return, u08[] apps) = pm_apps(Promira promira, u08[] apps)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # apps pre-processing
    __apps = isinstance(apps, int)
    if __apps:
        (apps, apps_size) = (array_u08(apps), apps)
    else:
        (apps, apps_size) = isinstance(apps, ArrayType) and (apps, len(apps)) or (apps[0], min(len(apps[0]), int(apps[1])))
        if apps.typecode != 'B':
            raise TypeError("type for 'apps' must be array('B')")
    # Call API function
    (_ret_) = api.py_pm_apps(promira, apps_size, apps)
    # apps post-processing
    if __apps: del apps[max(0, min(_ret_, len(apps))):]
    return (_ret_, apps)


# Get a list of licensed apps installed on the device.
def pm_licensed_apps (promira, apps):
    """usage: (int return, u08[] apps) = pm_licensed_apps(Promira promira, u08[] apps)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # apps pre-processing
    __apps = isinstance(apps, int)
    if __apps:
        (apps, apps_size) = (array_u08(apps), apps)
    else:
        (apps, apps_size) = isinstance(apps, ArrayType) and (apps, len(apps)) or (apps[0], min(len(apps[0]), int(apps[1])))
        if apps.typecode != 'B':
            raise TypeError("type for 'apps' must be array('B')")
    # Call API function
    (_ret_) = api.py_pm_licensed_apps(promira, apps_size, apps)
    # apps post-processing
    if __apps: del apps[max(0, min(_ret_, len(apps))):]
    return (_ret_, apps)


# Launch an app
def pm_load (promira, app_name):
    """usage: int return = pm_load(Promira promira, str app_name)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_load(promira, app_name)


# enum PromiraLoadFlags
PM_LOAD_NO_FLAGS = 0x00
PM_LOAD_UNLOAD   = 0x01

# Launch an app with the flags
def pm_load_ext (promira, app_name, flags):
    """usage: int return = pm_load_ext(Promira promira, str app_name, PromiraLoadFlags flags)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_load_ext(promira, app_name, flags)


# Retrieve the network address that was used to open the device.
# Return NULL if the handle is invalid.
#
# C programmers should not free the string returned.  It should be
# valid for as long as the device remains opens, but C callers are
# advised to reference the value as soon as they can and not cache
# it for later use.
def pm_get_net_addr (promira):
    """usage: str return = pm_get_net_addr(Promira promira)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_get_net_addr(promira)


# Close the Promira device
def pm_close (promira):
    """usage: int return = pm_close(Promira promira)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_close(promira)


# Return the unique ID for this Promira host adapter.
# IDs are guaranteed to be non-zero if valid.
# The ID is the unsigned integer representation of the
# 10-digit serial number.
def pm_unique_id (promira):
    """usage: u32 return = pm_unique_id(Promira promira)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_unique_id(promira)


# Return the status string for the given status code.
# If the code is not valid or the library function cannot
# be loaded, return a NULL string.
def pm_status_string (status):
    """usage: str return = pm_status_string(int status)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_status_string(status)


# Wipe the device in preparation for an OS update
#
# Use with caution!!!
def pm_init_device (promira):
    """usage: int return = pm_init_device(Promira promira)"""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pm_init_device(promira)


# Read currently installed license
# Pass 0 as buf_size to get the required size of the buffer
def pm_read_license (promira, buf):
    """usage: (int return, u08[] buf) = pm_read_license(Promira promira, u08[] buf)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # buf pre-processing
    __buf = isinstance(buf, int)
    if __buf:
        (buf, buf_size) = (array_u08(buf), buf)
    else:
        (buf, buf_size) = isinstance(buf, ArrayType) and (buf, len(buf)) or (buf[0], min(len(buf[0]), int(buf[1])))
        if buf.typecode != 'B':
            raise TypeError("type for 'buf' must be array('B')")
    # Call API function
    (_ret_) = api.py_pm_read_license(promira, buf_size, buf)
    # buf post-processing
    if __buf: del buf[max(0, min(_ret_, len(buf))):]
    return (_ret_, buf)


# Generate a colon separated string containig the names of features
# that are licensed for the supplied app.
def pm_features (promira, app, features):
    """usage: (int return, u08[] features) = pm_features(Promira promira, str app, u08[] features)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # features pre-processing
    __features = isinstance(features, int)
    if __features:
        (features, features_size) = (array_u08(features), features)
    else:
        (features, features_size) = isinstance(features, ArrayType) and (features, len(features)) or (features[0], min(len(features[0]), int(features[1])))
        if features.typecode != 'B':
            raise TypeError("type for 'features' must be array('B')")
    # Call API function
    (_ret_) = api.py_pm_features(promira, app, features_size, features)
    # features post-processing
    if __features: del features[max(0, min(_ret_, len(features))):]
    return (_ret_, features)


# Return the value for the specified feature.  The value returned is
# the string representation of the value.
def pm_feature_value (promira, app, feature, value):
    """usage: (int return, u08[] value) = pm_feature_value(Promira promira, str app, str feature, u08[] value)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # value pre-processing
    __value = isinstance(value, int)
    if __value:
        (value, value_size) = (array_u08(value), value)
    else:
        (value, value_size) = isinstance(value, ArrayType) and (value, len(value)) or (value[0], min(len(value[0]), int(value[1])))
        if value.typecode != 'B':
            raise TypeError("type for 'value' must be array('B')")
    # Call API function
    (_ret_) = api.py_pm_feature_value(promira, app, feature, value_size, value)
    # value post-processing
    if __value: del value[max(0, min(_ret_, len(value))):]
    return (_ret_, value)


# Return the description for the specified feature.  The description
# returned is a string.
def pm_feature_description (promira, app, feature, desc):
    """usage: (int return, u08[] desc) = pm_feature_description(Promira promira, str app, str feature, u08[] desc)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function.

    Additionally, for arrays that are filled by the API function, an
    integer can be passed in place of the array argument and the API
    will automatically create an array of that length.  All output
    arrays, whether passed in or generated, are passed back in the
    returned tuple."""

    if not PM_LIBRARY_LOADED: return PM_INCOMPATIBLE_LIBRARY
    # desc pre-processing
    __desc = isinstance(desc, int)
    if __desc:
        (desc, desc_size) = (array_u08(desc), desc)
    else:
        (desc, desc_size) = isinstance(desc, ArrayType) and (desc, len(desc)) or (desc[0], min(len(desc[0]), int(desc[1])))
        if desc.typecode != 'B':
            raise TypeError("type for 'desc' must be array('B')")
    # Call API function
    (_ret_) = api.py_pm_feature_description(promira, app, feature, desc_size, desc)
    # desc post-processing
    if __desc: del desc[max(0, min(_ret_, len(desc))):]
    return (_ret_, desc)


