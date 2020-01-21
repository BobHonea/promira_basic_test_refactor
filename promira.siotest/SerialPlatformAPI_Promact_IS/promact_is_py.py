#==========================================================================
# promact_is Interface Library
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
# To access promact_is through the API:
#
# 1) Use one of the following shared objects:
#      promact_is.so      --  Linux or macOS shared object
#      promact_is.dll     --  Windows dynamic link library
#
# 2) Along with one of the following language modules:
#      promact_is.c/h     --  C/C++ API header file and interface module
#      promact_is_py.py   --  Python API
#      promact_is.cs      --  C# .NET source
#==========================================================================


#==========================================================================
# VERSION
#==========================================================================
PS_APP_API_VERSION    = 0x0128   # v1.40
PS_APP_REQ_SW_VERSION = 0x0128   # v1.40


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
    lib = os.path.join(dir, 'promact_is' + ext)

    try:
        if sys.version_info >= (3, 4):
            from importlib.machinery import ExtensionFileLoader
            from importlib.util import spec_from_file_location
            from importlib.util import module_from_spec

            loader = ExtensionFileLoader('promact_is', lib)
            spec = spec_from_file_location('promact_is', loader=loader)
            api = module_from_spec(spec)
            spec.loader.exec_module(api)

        else:
            import imp
            api = imp.load_dynamic('promact_is', lib)

    except:
        _, err, _ = sys.exc_info()
        msg = 'Error while importing promact_is%s:\n%s' % (ext, err)
        sys.exit(msg)

try:
    import promact_is as api
except ImportError:
    import_library()

del import_library

PS_APP_SW_VERSION      = api.py_version() & 0xffff
PS_APP_REQ_API_VERSION = (api.py_version() >> 16) & 0xffff
PS_APP_LIBRARY_LOADED  = \
    ((PS_APP_SW_VERSION >= PS_APP_REQ_SW_VERSION) and \
     (PS_APP_API_VERSION >= PS_APP_REQ_API_VERSION))


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
# enum PromiraAppStatus
# General codes (0 to -99)
PS_APP_OK                        =    0
PS_APP_UNABLE_TO_LOAD_LIBRARY    =   -1
PS_APP_UNABLE_TO_LOAD_DRIVER     =   -2
PS_APP_UNABLE_TO_LOAD_FUNCTION   =   -3
PS_APP_INCOMPATIBLE_LIBRARY      =   -4
PS_APP_INCOMPATIBLE_DEVICE       =   -5
PS_APP_COMMUNICATION_ERROR       =   -6
PS_APP_UNABLE_TO_OPEN            =   -7
PS_APP_UNABLE_TO_CLOSE           =   -8
PS_APP_INVALID_HANDLE            =   -9
PS_APP_CONFIG_ERROR              =  -10
PS_APP_MEMORY_ALLOC_ERROR        =  -11
PS_APP_UNABLE_TO_INIT_SUBSYSTEM  =  -12
PS_APP_INVALID_LICENSE           =  -13

# Channel related code
PS_APP_PENDING_ASYNC_CMD         =  -30
PS_APP_TIMEOUT                   =  -31
PS_APP_CONNECTION_LOST           =  -32
PS_APP_CONNECTION_FULL           =  -33

# Queue related code
PS_APP_QUEUE_FULL                =  -50
PS_APP_QUEUE_INVALID_CMD_TYPE    =  -51
PS_APP_QUEUE_EMPTY               =  -52

# Collect related code
PS_APP_NO_MORE_CMDS_TO_COLLECT   =  -80
PS_APP_NO_MORE_QUEUES_TO_COLLECT =  -81
PS_APP_MISMATCHED_CMD            =  -82
PS_APP_UNKNOWN_CMD               =  -83
PS_APP_LOST_RESPONSE             =  -84



# I2C codes (-100 to -199)
PS_I2C_NOT_AVAILABLE             = -100
PS_I2C_NOT_ENABLED               = -101
PS_I2C_READ_ERROR                = -102
PS_I2C_WRITE_ERROR               = -103
PS_I2C_SLAVE_BAD_CONFIG          = -104
PS_I2C_SLAVE_READ_ERROR          = -105
PS_I2C_SLAVE_TIMEOUT             = -106
PS_I2C_DROPPED_EXCESS_BYTES      = -107
PS_I2C_BUS_ALREADY_FREE          = -108

# SPI codes (-200 to -299)
PS_SPI_NOT_AVAILABLE             = -200
PS_SPI_NOT_ENABLED               = -201
PS_SPI_WRITE_0_BYTES             = -202
PS_SPI_SLAVE_READ_ERROR          = -203
PS_SPI_SLAVE_TIMEOUT             = -204
PS_SPI_DROPPED_EXCESS_BYTES      = -205
PS_SPI_SLAVE_CMD_ERROR           = -206
PS_SPI_SLAVE_3WIRE               = -207

# SPI code from Promira
PS_SPI_OUTPUT_NOT_ENABLED        = -250
PS_SPI_SLAVE_ENABLED             = -251
PS_SPI_OUTPUT_ENABLED            = -252
# GPIO codes (-300 to -399)


# PHY Serial codes (-1000 to -1099)



#==========================================================================
# GENERAL TYPE DEFINITIONS
#==========================================================================
# Connection handle type definition
# typedef PromiraConnectionHandle => integer

# Channel handle type definition
# typedef PromiraChannelHandle => integer

# Queue handle type definition
# typedef PromiraQueueHandle => integer

# Collect handle type definition
# typedef PromiraCollectHandle => integer

# Version matrix.
#
# This matrix describes the various version dependencies
# of Promira components.  It can be used to determine
# which component caused an incompatibility error.
#
# All version numbers are of the format:
#   (major << 8) | minor
#
# ex. v1.20 would be encoded as:  0x0114
class PromiraAppVersion:
    def __init__ (self):
        # Software, firmware, and hardware versions.
        self.software      = 0
        self.firmware      = 0
        self.hardware      = 0

        # Firmware requires that software must be >= this version.
        self.sw_req_by_fw  = 0

        # Software requires that firmware must be >= this version.
        self.fw_req_by_sw  = 0

        # Software requires that the API interface must be >= this version.
        self.api_req_by_sw = 0


#==========================================================================
# GENERAL API
#==========================================================================
# Connect to the application
#
# Returns a connection handle, which is guaranteed to be
# greater than zero if it is valid.
def ps_app_connect (net_addr):
    """usage: PromiraConnectionHandle return = ps_app_connect(str net_addr)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_app_connect(net_addr)


# Disconnect from the application
def ps_app_disconnect (conn):
    """usage: int return = ps_app_disconnect(PromiraConnectionHandle conn)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_app_disconnect(conn)


# Return the version matrix for the device attached to the
# given handle.  If the handle is 0 or invalid, only the
# software and required api versions are set.
def ps_app_version (channel):
    """usage: (int return, PromiraAppVersion version) = ps_app_version(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_version) = api.py_ps_app_version(channel)
    # version post-processing
    version = PromiraAppVersion()
    (version.software, version.firmware, version.hardware, version.sw_req_by_fw, version.fw_req_by_sw, version.api_req_by_sw) = c_version
    return (_ret_, version)


# Sleep for the specified number of milliseconds
def ps_app_sleep_ms (milliseconds):
    """usage: int return = ps_app_sleep_ms(u32 milliseconds)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_app_sleep_ms(milliseconds)


# Return the status string for the given status code.
# If the code is not valid or the library function cannot
# be loaded, return a NULL string.
def ps_app_status_string (status):
    """usage: str return = ps_app_status_string(int status)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_app_status_string(status)



#==========================================================================
# CHANNEL API
#==========================================================================
# Channel is a logical communication layer that talks to the application.
#
# Open a logical channel to communicate with the application.
#
# Returns a connection handle, which is guaranteed to be
# greater than zero if it is valid.
def ps_channel_open (conn):
    """usage: PromiraChannelHandle return = ps_channel_open(PromiraConnectionHandle conn)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_channel_open(conn)


# Close a logical channel.
def ps_channel_close (channel):
    """usage: int return = ps_channel_close(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_channel_close(channel)


# Get the number of queues submitted, but not collected through the channel
def ps_channel_submitted_count (channel):
    """usage: int return = ps_channel_submitted_count(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_channel_submitted_count(channel)


# Get the number of queues completed and uncollected through the channel
def ps_channel_uncollected_count (channel):
    """usage: int return = ps_channel_uncollected_count(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_channel_uncollected_count(channel)



#==========================================================================
# QUEUE API
#==========================================================================
# In order to use the Promira to send data across the bus at high
# speed, commands are accumulated in a queue until a call is made to
# submit all of the queued commands.  A queue can contain only commands
# with same type. For instance, any SPI command cannot be appended to
# I2C queue.
#
# Create the queue.  queue_type is one of the PS_MODULE_ID_* values.
def ps_queue_create (conn, queue_type):
    """usage: PromiraQueueHandle return = ps_queue_create(PromiraConnectionHandle conn, u08 queue_type)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_create(conn, queue_type)


# Destroy the queue.
def ps_queue_destroy (queue):
    """usage: int return = ps_queue_destroy(PromiraQueueHandle queue)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_destroy(queue)


# Clear all commands in the queue.
# Please note that the queue is not cleared after it has been submitted.
def ps_queue_clear (queue):
    """usage: int return = ps_queue_clear(PromiraQueueHandle queue)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_clear(queue)


# Append a delay commmand into the queue.
def ps_queue_delay_ms (queue, milliseconds):
    """usage: int return = ps_queue_delay_ms(PromiraQueueHandle queue, int milliseconds)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_delay_ms(queue, milliseconds)


# Append a sync command into the queue.  Waits for all previous
# commands to compelte entirely.
def ps_queue_sync (queue):
    """usage: int return = ps_queue_sync(PromiraQueueHandle queue)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_sync(queue)


# Return the number of commands in the queue.
def ps_queue_size (queue):
    """usage: int return = ps_queue_size(PromiraQueueHandle queue)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_size(queue)


# Submit the queue.
#
# After the operation completes, the queue is untouched.  Therefore,
# this function may be called repeatedly in rapid succession.  Waits
# for the first command in the queue to complete.  Returns a
# PromiraCollectHandle.
def ps_queue_submit (queue, channel, ctrl_id):
    """usage: (PromiraCollectHandle return, u08 queue_type) = ps_queue_submit(PromiraQueueHandle queue, PromiraChannelHandle channel, u08 ctrl_id)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_submit(queue, channel, ctrl_id)


# Submit the queue asynchronously.
#
# After the operation completes, the queue is untouched.  Therefore,
# this function may be called repeatedly in rapid succession.
def ps_queue_async_submit (queue, channel, ctrl_id):
    """usage: int return = ps_queue_async_submit(PromiraQueueHandle queue, PromiraChannelHandle channel, u08 ctrl_id)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_async_submit(queue, channel, ctrl_id)


# Collect the next queue that was previously submitted asynchronously.
# Waits for the first command in the queue to complete.  queue_type is
# one of the PS_MODULE_ID_* values.  Returns a PromiraCollectHandle.
def ps_queue_async_collect (channel):
    """usage: (PromiraCollectHandle return, u08 queue_type) = ps_queue_async_collect(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_async_collect(channel)



#==========================================================================
# Collect API
#==========================================================================
# Collect the next command response.  Waits for the next command to
# complete or timeout. Returns the command type.  Get the result of
# the command and the length of data to be returned when the command
# specific collect function is called.
def ps_collect_resp (collect, timeout):
    """usage: (int return, int length, int result) = ps_collect_resp(PromiraCollectHandle collect, int timeout)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_collect_resp(collect, timeout)



#==========================================================================
# I2C Active API
#==========================================================================
PS_MODULE_ID_I2C_ACTIVE = 0x00000001
# enum PromiraI2cCommand
PS_I2C_CMD_WRITE    = 100
PS_I2C_CMD_READ     = 101
PS_I2C_CMD_DELAY_MS = 102

# Free the I2C bus.
def ps_i2c_free_bus (channel):
    """usage: int return = ps_i2c_free_bus(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_i2c_free_bus(channel)


# Set the bus lock timeout.  If a zero is passed as the timeout,
# the timeout is unchanged and the current timeout is returned.
def ps_i2c_bus_timeout (channel, timeout_ms):
    """usage: int return = ps_i2c_bus_timeout(PromiraChannelHandle channel, u16 timeout_ms)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_i2c_bus_timeout(channel, timeout_ms)


# Set the I2C bit rate in kilohertz.  If a zero is passed as the
# bitrate, the bitrate is unchanged and the current bitrate is
# returned.
def ps_i2c_bitrate (channel, bitrate_khz):
    """usage: int return = ps_i2c_bitrate(PromiraChannelHandle channel, u16 bitrate_khz)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_i2c_bitrate(channel, bitrate_khz)


# enum PromiraI2cFlags
PS_I2C_NO_FLAGS          = 0x00
PS_I2C_10_BIT_ADDR       = 0x01
PS_I2C_COMBINED_FMT      = 0x02
PS_I2C_NO_STOP           = 0x04
PS_I2C_SIZED_READ        = 0x10
PS_I2C_SIZED_READ_EXTRA1 = 0x20

# enum PromiraI2cStatus
PS_I2C_STATUS_OK            = 0
PS_I2C_STATUS_BUS_ERROR     = 1
PS_I2C_STATUS_SLAVE_ACK     = 2
PS_I2C_STATUS_SLAVE_NACK    = 3
PS_I2C_STATUS_DATA_NACK     = 4
PS_I2C_STATUS_ARB_LOST      = 5
PS_I2C_STATUS_BUS_LOCKED    = 6
PS_I2C_STATUS_LAST_DATA_ACK = 7

# Read a stream of bytes from the I2C slave device.  Fills the number
# of bytes read into the num_read variable.  The return value of the
# function is a status code.
def ps_i2c_read (channel, slave_addr, flags, data_in):
    """usage: (int return, u08[] data_in, u16 num_read) = ps_i2c_read(PromiraChannelHandle channel, u16 slave_addr, PromiraI2cFlags flags, u08[] data_in)

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

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # data_in pre-processing
    __data_in = isinstance(data_in, int)
    if __data_in:
        (data_in, num_bytes) = (array_u08(data_in), data_in)
    else:
        (data_in, num_bytes) = isinstance(data_in, ArrayType) and (data_in, len(data_in)) or (data_in[0], min(len(data_in[0]), int(data_in[1])))
        if data_in.typecode != 'B':
            raise TypeError("type for 'data_in' must be array('B')")
    # Call API function
    (_ret_, num_read) = api.py_ps_i2c_read(channel, slave_addr, flags, num_bytes, data_in)
    # data_in post-processing
    if __data_in: del data_in[max(0, min(num_read, len(data_in))):]
    return (_ret_, data_in, num_read)


# Queue I2C read.
def ps_queue_i2c_read (queue, slave_addr, flags, num_bytes):
    """usage: int return = ps_queue_i2c_read(PromiraQueueHandle queue, u16 slave_addr, PromiraI2cFlags flags, u16 num_bytes)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_i2c_read(queue, slave_addr, flags, num_bytes)


# Collect I2C read.
def ps_collect_i2c_read (collect, data_in):
    """usage: (int return, u08[] data_in, u16 num_read) = ps_collect_i2c_read(PromiraCollectHandle collect, u08[] data_in)

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

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # data_in pre-processing
    __data_in = isinstance(data_in, int)
    if __data_in:
        (data_in, num_bytes) = (array_u08(data_in), data_in)
    else:
        (data_in, num_bytes) = isinstance(data_in, ArrayType) and (data_in, len(data_in)) or (data_in[0], min(len(data_in[0]), int(data_in[1])))
        if data_in.typecode != 'B':
            raise TypeError("type for 'data_in' must be array('B')")
    # Call API function
    (_ret_, num_read) = api.py_ps_collect_i2c_read(collect, num_bytes, data_in)
    # data_in post-processing
    if __data_in: del data_in[max(0, min(num_read, len(data_in))):]
    return (_ret_, data_in, num_read)


# Write a stream of bytes to the I2C slave device.  Fills the number
# of bytes written into the num_written variable.  The return value of
# the function is a status code.
def ps_i2c_write (channel, slave_addr, flags, data_out):
    """usage: (int return, u16 num_written) = ps_i2c_write(PromiraChannelHandle channel, u16 slave_addr, PromiraI2cFlags flags, u08[] data_out)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function."""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # data_out pre-processing
    (data_out, num_bytes) = isinstance(data_out, ArrayType) and (data_out, len(data_out)) or (data_out[0], min(len(data_out[0]), int(data_out[1])))
    if data_out.typecode != 'B':
        raise TypeError("type for 'data_out' must be array('B')")
    # Call API function
    return api.py_ps_i2c_write(channel, slave_addr, flags, num_bytes, data_out)


# Queue I2C write.
def ps_queue_i2c_write (queue, slave_addr, flags, data_out):
    """usage: int return = ps_queue_i2c_write(PromiraQueueHandle queue, u16 slave_addr, PromiraI2cFlags flags, u08[] data_out)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function."""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # data_out pre-processing
    (data_out, num_bytes) = isinstance(data_out, ArrayType) and (data_out, len(data_out)) or (data_out[0], min(len(data_out[0]), int(data_out[1])))
    if data_out.typecode != 'B':
        raise TypeError("type for 'data_out' must be array('B')")
    # Call API function
    return api.py_ps_queue_i2c_write(queue, slave_addr, flags, num_bytes, data_out)


# Collect I2C write.
def ps_collect_i2c_write (collect):
    """usage: (int return, u16 num_written) = ps_collect_i2c_write(PromiraCollectHandle collect)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_collect_i2c_write(collect)


# Enable the Promira as an I2C slave
def ps_i2c_slave_enable (channel, addr, maxTxBytes, maxRxBytes):
    """usage: int return = ps_i2c_slave_enable(PromiraChannelHandle channel, u16 addr, u16 maxTxBytes, u16 maxRxBytes)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_i2c_slave_enable(channel, addr, maxTxBytes, maxRxBytes)


# Disable the Promira as an I2C slave
def ps_i2c_slave_disable (channel):
    """usage: int return = ps_i2c_slave_disable(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_i2c_slave_disable(channel)


# Set the slave response.
def ps_i2c_slave_set_resp (channel, data_out):
    """usage: int return = ps_i2c_slave_set_resp(PromiraChannelHandle channel, u08[] data_out)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function."""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # data_out pre-processing
    (data_out, num_bytes) = isinstance(data_out, ArrayType) and (data_out, len(data_out)) or (data_out[0], min(len(data_out[0]), int(data_out[1])))
    if data_out.typecode != 'B':
        raise TypeError("type for 'data_out' must be array('B')")
    # Call API function
    return api.py_ps_i2c_slave_set_resp(channel, num_bytes, data_out)


# Polling function to check if there are any asynchronous
# messages pending for processing.  The function takes a timeout
# value in units of milliseconds.  If the timeout is < 0, the
# function will block until data is received.  If the timeout is 0,
# the function will perform a non-blocking check.
# enum PromiraI2cSlaveStatus
PS_I2C_SLAVE_NO_DATA   = 0x00
PS_I2C_SLAVE_READ      = 0x01
PS_I2C_SLAVE_WRITE     = 0x02
PS_I2C_SLAVE_DATA_LOST = 0x80

def ps_i2c_slave_poll (channel, timeout):
    """usage: int return = ps_i2c_slave_poll(PromiraChannelHandle channel, int timeout)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_i2c_slave_poll(channel, timeout)


# Return number of bytes written and status code from a previous
# Promira->I2C_master transmission.  Since the transmission is
# happening asynchronously with respect to the PC host software, there
# could be responses queued up from many previous write transactions.
def ps_i2c_slave_write_stats (channel):
    """usage: (int return, u08 addr, u16 num_written) = ps_i2c_slave_write_stats(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_i2c_slave_write_stats(channel)


# Read the bytes from an I2C slave reception
def ps_i2c_slave_read (channel, data_in):
    """usage: (int return, u08 addr, u08[] data_in, u16 num_read) = ps_i2c_slave_read(PromiraChannelHandle channel, u08[] data_in)

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

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # data_in pre-processing
    __data_in = isinstance(data_in, int)
    if __data_in:
        (data_in, num_bytes) = (array_u08(data_in), data_in)
    else:
        (data_in, num_bytes) = isinstance(data_in, ArrayType) and (data_in, len(data_in)) or (data_in[0], min(len(data_in[0]), int(data_in[1])))
        if data_in.typecode != 'B':
            raise TypeError("type for 'data_in' must be array('B')")
    # Call API function
    (_ret_, addr, num_read) = api.py_ps_i2c_slave_read(channel, num_bytes, data_in)
    # data_in post-processing
    if __data_in: del data_in[max(0, min(num_read, len(data_in))):]
    return (_ret_, addr, data_in, num_read)


# Return number of I2C transactions lost due to the overflow of the
# internal Promira buffer.
def ps_i2c_slave_data_lost_stats (channel):
    """usage: int return = ps_i2c_slave_data_lost_stats(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_i2c_slave_data_lost_stats(channel)



#==========================================================================
# SPI Active API
#==========================================================================
PS_MODULE_ID_SPI_ACTIVE = 0x00000002
# enum PromiraSpiCommand
PS_SPI_CMD_OE           = 200
PS_SPI_CMD_SS           = 201
PS_SPI_CMD_DELAY_MS     = 202
PS_SPI_CMD_DELAY_CYCLES = 203
PS_SPI_CMD_DELAY_NS     = 204
PS_SPI_CMD_READ         = 205

# Set the SPI bitrate in kilohertz.  If a zero is passed as the
# bitrate, the bitrate is unchanged and the current bitrate is
# returned.
def ps_spi_bitrate (channel, bitrate_khz):
    """usage: int return = ps_spi_bitrate(PromiraChannelHandle channel, u32 bitrate_khz)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_bitrate(channel, bitrate_khz)


# These configuration parameters specify how to clock the bits that
# are sent and received on SPI interface.  See the the Promira User
# Manual for more details.
# enum PromiraSpiMode
PS_SPI_MODE_0 = 0
PS_SPI_MODE_1 = 1
PS_SPI_MODE_2 = 2
PS_SPI_MODE_3 = 3

# enum PromiraSpiBitorder
PS_SPI_BITORDER_MSB = 0
PS_SPI_BITORDER_LSB = 1

# Configure the SPI master and slave interface.  Each of bits of
# ss_polarity corresponds to each of the SS lines.
def ps_spi_configure (channel, mode, bitorder, ss_polarity):
    """usage: int return = ps_spi_configure(PromiraChannelHandle channel, PromiraSpiMode mode, PromiraSpiBitorder bitorder, u08 ss_polarity)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_configure(channel, mode, bitorder, ss_polarity)


# Configure the delays. word_delay is the the number of clock cycles
# between words.  word_delay can not be 1.  There is no gap after the
# last word.
def ps_spi_configure_delays (channel, word_delay):
    """usage: int return = ps_spi_configure_delays(PromiraChannelHandle channel, u08 word_delay)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_configure_delays(channel, word_delay)


# Enable/disable slave select lines.  When a slave select line is
# enabled, the corresponding GPIO is disabled.
def ps_spi_enable_ss (channel, ss_enable):
    """usage: int return = ps_spi_enable_ss(PromiraChannelHandle channel, u08 ss_enable)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_enable_ss(channel, ss_enable)


# Enable/disable driving the SPI data and clock signals
def ps_queue_spi_oe (queue, oe):
    """usage: int return = ps_queue_spi_oe(PromiraQueueHandle queue, u08 oe)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_spi_oe(queue, oe)


# Assert the slave select lines.  Set the bit value for a given SS
# line to 1 to assert the line or 0 to deassert the line.  The
# polarity is determined by ps_spi_configure.
def ps_queue_spi_ss (queue, ss_assert):
    """usage: int return = ps_queue_spi_ss(PromiraQueueHandle queue, u08 ss_assert)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_spi_ss(queue, ss_assert)


# Queue a delay in clock cycles.
def ps_queue_spi_delay_cycles (queue, cycles):
    """usage: int return = ps_queue_spi_delay_cycles(PromiraQueueHandle queue, u32 cycles)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_spi_delay_cycles(queue, cycles)


# Queue a delay in nanoseconds. Maximum delay is 2 secs.
def ps_queue_spi_delay_ns (queue, nanoseconds):
    """usage: int return = ps_queue_spi_delay_ns(PromiraQueueHandle queue, u32 nanoseconds)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_spi_delay_ns(queue, nanoseconds)


# enum PromiraSpiIOMode
PS_SPI_IO_STANDARD = 0
PS_SPI_IO_DUAL     = 2
PS_SPI_IO_QUAD     = 4

# Queue an array to be shifted.  data_out is a byte array containing
# packed words.  word_size is the number of bits in a word and is
# between 2 and 32.
def ps_queue_spi_write (queue, io, word_size, out_num_words, data_out):
    """usage: int return = ps_queue_spi_write(PromiraQueueHandle queue, PromiraSpiIOMode io, u08 word_size, u32 out_num_words, u08[] data_out)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function."""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # data_out pre-processing
    (data_out, _) = isinstance(data_out, ArrayType) and (data_out, len(data_out)) or (data_out[0], min(len(data_out[0]), int(data_out[1])))
    if data_out.typecode != 'B':
        raise TypeError("type for 'data_out' must be array('B')")
    # Call API function
    return api.py_ps_queue_spi_write(queue, io, word_size, out_num_words, data_out)


# Queue a single word out_num_word times.  word_size is the number of
# bits in a word and is between 2 and 32.
def ps_queue_spi_write_word (queue, io, word_size, out_num_words, word):
    """usage: int return = ps_queue_spi_write_word(PromiraQueueHandle queue, PromiraSpiIOMode io, u08 word_size, u32 out_num_words, u32 word)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_spi_write_word(queue, io, word_size, out_num_words, word)


# Queue an SPI read command.  Equivalent to ps_queue_spi_write_word
# with word equal to 0 when io is PS_SPI_IO_STANDARD.  When io is
# PS_SPI_IO_DUAL or PS_SPI_IO_QUAD, the clock is generated and the
# data lines are set to inputs.
def ps_queue_spi_read (queue, io, word_size, in_num_words):
    """usage: int return = ps_queue_spi_read(PromiraQueueHandle queue, PromiraSpiIOMode io, u08 word_size, u32 in_num_words)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_spi_read(queue, io, word_size, in_num_words)


# Collect the actual SPI data received.  Returns number of words
# received.  This should be called after ps_collect_resp returns
# PS_SPI_CMD_READ.
def ps_collect_spi_read (collect, data_in):
    """usage: (int return, u08 word_size, u08[] data_in) = ps_collect_spi_read(PromiraCollectHandle collect, u08[] data_in)

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

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # data_in pre-processing
    __data_in = isinstance(data_in, int)
    if __data_in:
        (data_in, in_num_bytes) = (array_u08(data_in), data_in)
    else:
        (data_in, in_num_bytes) = isinstance(data_in, ArrayType) and (data_in, len(data_in)) or (data_in[0], min(len(data_in[0]), int(data_in[1])))
        if data_in.typecode != 'B':
            raise TypeError("type for 'data_in' must be array('B')")
    # Call API function
    (_ret_, word_size) = api.py_ps_collect_spi_read(collect, in_num_bytes, data_in)
    # data_in post-processing
    if __data_in: del data_in[max(0, min(_ret_, len(data_in))):]
    return (_ret_, word_size, data_in)


# enum PromiraSlaveMode
PS_SPI_SLAVE_MODE_STD = 0

# Enable the Promira as an SPI slave device
def ps_spi_slave_enable (channel, mode):
    """usage: int return = ps_spi_slave_enable(PromiraChannelHandle channel, PromiraSlaveMode mode)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_slave_enable(channel, mode)


# Disable the Promira as an SPI slave device
def ps_spi_slave_disable (channel):
    """usage: int return = ps_spi_slave_disable(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_slave_disable(channel)


# Configure the slave parameters
PS_SPI_SLAVE_NO_SS = 0x00000001
PS_SPI_MULTI_IO_WRITE = 0x00000000
PS_SPI_MULTI_IO_READ = 0x00000002
def ps_spi_std_slave_configure (channel, io, flags):
    """usage: int return = ps_spi_std_slave_configure(PromiraChannelHandle channel, PromiraSpiIOMode io, u08 flags)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_std_slave_configure(channel, io, flags)


# When PS_SPI_SLAVE_NO_SS is configured, this timeout determines a SPI
# transaction.  Returns actual ns to be used.  Minimum is 1us.
def ps_spi_slave_timeout (channel, timeout_ns):
    """usage: int return = ps_spi_slave_timeout(PromiraChannelHandle channel, u32 timeout_ns)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_slave_timeout(channel, timeout_ns)


# Allow collecting partial slave data.
def ps_spi_slave_host_read_size (channel, read_size):
    """usage: int return = ps_spi_slave_host_read_size(PromiraChannelHandle channel, u32 read_size)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_slave_host_read_size(channel, read_size)


# Set the slave response.
def ps_spi_std_slave_set_resp (channel, resp):
    """usage: int return = ps_spi_std_slave_set_resp(PromiraChannelHandle channel, u08[] resp)

    All arrays can be passed into the API as an ArrayType object or as
    a tuple (array, length), where array is an ArrayType object and
    length is an integer.  The user-specified length would then serve
    as the length argument to the API funtion (please refer to the
    product datasheet).  If only the array is provided, the array's
    intrinsic length is used as the argument to the underlying API
    function."""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # resp pre-processing
    (resp, num_bytes) = isinstance(resp, ArrayType) and (resp, len(resp)) or (resp[0], min(len(resp[0]), int(resp[1])))
    if resp.typecode != 'B':
        raise TypeError("type for 'resp' must be array('B')")
    # Call API function
    return api.py_ps_spi_std_slave_set_resp(channel, num_bytes, resp)


# Polling function to check if there are any asynchronous messages
# pending for processing.  The function takes a timeout value in units
# of milliseconds.  If the timeout is < 0, the function will block
# until data is received.  If the timeout is 0, the function will
# perform a non-blocking check.
# enum PromiraSpiSlaveStatus
PS_SPI_SLAVE_NO_DATA   = 0x00
PS_SPI_SLAVE_DATA      = 0x01
PS_SPI_SLAVE_DATA_LOST = 0x80

def ps_spi_slave_poll (channel, timeout):
    """usage: int return = ps_spi_slave_poll(PromiraChannelHandle channel, int timeout)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_slave_poll(channel, timeout)


class PromiraSpiSlaveReadInfo:
    def __init__ (self):
        self.in_data_bits  = 0
        self.out_data_bits = 0
        self.header_bits   = 0
        self.resp_id       = 0
        self.ss_mask       = 0
        self.is_last       = 0

# Read the data from an SPI slave reception.  Returns number of bytes
# put into data_in.
def ps_spi_slave_read (channel, data_in):
    """usage: (int return, PromiraSpiSlaveReadInfo read_info, u08[] data_in) = ps_spi_slave_read(PromiraChannelHandle channel, u08[] data_in)

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

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # data_in pre-processing
    __data_in = isinstance(data_in, int)
    if __data_in:
        (data_in, in_num_bytes) = (array_u08(data_in), data_in)
    else:
        (data_in, in_num_bytes) = isinstance(data_in, ArrayType) and (data_in, len(data_in)) or (data_in[0], min(len(data_in[0]), int(data_in[1])))
        if data_in.typecode != 'B':
            raise TypeError("type for 'data_in' must be array('B')")
    # Call API function
    (_ret_, c_read_info) = api.py_ps_spi_slave_read(channel, in_num_bytes, data_in)
    # read_info post-processing
    read_info = PromiraSpiSlaveReadInfo()
    (read_info.in_data_bits, read_info.out_data_bits, read_info.header_bits, read_info.resp_id, read_info.ss_mask, read_info.is_last) = c_read_info
    # data_in post-processing
    if __data_in: del data_in[max(0, min(_ret_, len(data_in))):]
    return (_ret_, read_info, data_in)


# Return number of SPI transactions lost due to the overflow of the
# internal Promira buffer.
def ps_spi_slave_data_lost_stats (channel):
    """usage: int return = ps_spi_slave_data_lost_stats(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_spi_slave_data_lost_stats(channel)



#==========================================================================
# GPIO API
#==========================================================================
PS_MODULE_ID_GPIO = 0x00000003
# enum PromiraGpioCommand
PS_GPIO_CMD_DIRECTION = 300
PS_GPIO_CMD_GET       = 301
PS_GPIO_CMD_SET       = 302
PS_GPIO_CMD_CHANGE    = 303
PS_GPIO_CMD_DELAY_MS  = 304

# Returns which GPIO pins are currently active.
def ps_gpio_query (channel):
    """usage: int return = ps_gpio_query(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_gpio_query(channel)


# Configure the GPIO, specifying the direction of each bit.
#
# A call to this function will not change the value of the pullup
# mask in the Promira.  This is illustrated by the following
# example:
#   (1) Direction mask is first set to 0x00
#   (2) Pullup is set to 0x01
#   (3) Direction mask is set to 0x01
#   (4) Direction mask is later set back to 0x00.
#
# The pullup will be active after (4).
#
# On Promira power-up, the default value of the direction
# mask is 0x00.
PS_GPIO_DIR_INPUT = 0
PS_GPIO_DIR_OUTPUT = 1
def ps_gpio_direction (channel, direction_mask):
    """usage: int return = ps_gpio_direction(PromiraChannelHandle channel, u32 direction_mask)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_gpio_direction(channel, direction_mask)


def ps_queue_gpio_direction (queue, direction_mask):
    """usage: int return = ps_queue_gpio_direction(PromiraQueueHandle queue, u32 direction_mask)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_gpio_direction(queue, direction_mask)


# Read the current digital values on the GPIO input lines.
#
# If a line is configured as an output, its corresponding bit
# position in the mask will be undefined.
def ps_gpio_get (channel):
    """usage: int return = ps_gpio_get(PromiraChannelHandle channel)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_gpio_get(channel)


def ps_queue_gpio_get (queue):
    """usage: int return = ps_queue_gpio_get(PromiraQueueHandle queue)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_gpio_get(queue)


# Set the outputs on the GPIO lines.
#
# Note: If a line is configured as an input, it will not be
# affected by this call, but the output value for that line
# will be cached in the event that the line is later
# configured as an output.
def ps_gpio_set (channel, value):
    """usage: int return = ps_gpio_set(PromiraChannelHandle channel, u32 value)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_gpio_set(channel, value)


def ps_queue_gpio_set (queue, value):
    """usage: int return = ps_queue_gpio_set(PromiraQueueHandle queue, u32 value)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_gpio_set(queue, value)


# Block until there is a change on the GPIO input lines.
# Pins configured as outputs will be ignored.
#
# The function will return either when a change has occurred or
# the timeout expires.  If the timeout expires, this function
# will return the current state of the GPIO lines.
#
# If the function ps_gpio_get is called before calling
# ps_gpio_change, ps_gpio_change will only register any changes
# from the value last returned by ps_gpio_get.
def ps_gpio_change (channel, timeout):
    """usage: int return = ps_gpio_change(PromiraChannelHandle channel, int timeout)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_gpio_change(channel, timeout)


def ps_queue_gpio_change (queue, timeout):
    """usage: int return = ps_queue_gpio_change(PromiraQueueHandle queue, int timeout)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_queue_gpio_change(queue, timeout)



#==========================================================================
# Serial PHY Module API
#==========================================================================
PS_MODULE_ID_PHY = 0x000000ff
# Configure the device by enabling/disabling I2C, SPI, and
# GPIO functions.
PS_APP_CONFIG_GPIO = 0x00000000
PS_APP_CONFIG_SPI = 0x00000001
PS_APP_CONFIG_I2C = 0x00000010
PS_APP_CONFIG_QUERY = -1
def ps_app_configure (channel, config):
    """usage: int return = ps_app_configure(PromiraChannelHandle channel, int config)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_app_configure(channel, config)


# Configure the I2C pullup resistors.
PS_I2C_PULLUP_NONE = 0x00
PS_I2C_PULLUP_BOTH = 0x03
PS_I2C_PULLUP_QUERY = 0x80
def ps_i2c_pullup (channel, pullup_mask):
    """usage: int return = ps_i2c_pullup(PromiraChannelHandle channel, u08 pullup_mask)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_i2c_pullup(channel, pullup_mask)


# Configure the target power pins.
PS_PHY_TARGET_POWER_NONE = 0x00
PS_PHY_TARGET_POWER_TARGET1_5V = 0x01
PS_PHY_TARGET_POWER_TARGET1_3V = 0x05
PS_PHY_TARGET_POWER_TARGET2 = 0x02
PS_PHY_TARGET_POWER_BOTH = 0x03
PS_PHY_TARGET_POWER_QUERY = 0x80
def ps_phy_target_power (channel, power_mask):
    """usage: int return = ps_phy_target_power(PromiraChannelHandle channel, u08 power_mask)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_phy_target_power(channel, power_mask)


# Configure the power of output signal.
PS_PHY_LEVEL_SHIFT_QUERY = -1
def ps_phy_level_shift (channel, level):
    """usage: f32 return = ps_phy_level_shift(PromiraChannelHandle channel, f32 level)"""

    if not PS_APP_LIBRARY_LOADED: return PS_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_ps_phy_level_shift(channel, level)


