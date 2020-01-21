#==========================================================================
# promana Interface Library
#--------------------------------------------------------------------------
# Copyright (c) 2002-2015 Total Phase, Inc.
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
# To access promana through the API:
#
# 1) Use one of the following shared objects:
#      promana.so      --  Linux/Mac OSX shared object
#      promana.dll     --  Windows dynamic link library
#
# 2) Along with one of the following language modules:
#      promana.c/h     --  C/C++ API header file and interface module
#      promana_py.py   --  Python API
#      promana.cs      --  C# .NET source
#==========================================================================


#==========================================================================
# VERSION
#==========================================================================
PA_APP_API_VERSION    = 0x010a   # v1.10
PA_APP_REQ_SW_VERSION = 0x010a   # v1.10


#==========================================================================
# IMPORT
#==========================================================================
import os
import struct
import sys

from array import array, ArrayType

api = None
PA_APP_SW_VERSION = None
PA_APP_REQ_API_VERSION = None
PA_APP_LIBRARY_LOADED = None

def __initialize ():
    global api, PA_APP_SW_VERSION, PA_APP_REQ_API_VERSION, PA_APP_LIBRARY_LOADED

    try:
        import promana
        api = promana
    except ImportError, ex1:
        import imp, platform
        ext = platform.system() in ('Windows', 'Microsoft') and '.dll' or '.so'
        try:
            api = imp.load_dynamic('promana', 'promana' + ext)
        except ImportError, ex2:
            import_err_msg  = 'Error importing promana%s\n' % ext
            import_err_msg += '  Architecture of promana%s may be wrong\n' % ext
            import_err_msg += '%s\n%s' % (ex1, ex2)
            raise ImportError(import_err_msg)

    PA_APP_SW_VERSION      = api.py_version() & 0xffff
    PA_APP_REQ_API_VERSION = (api.py_version() >> 16) & 0xffff
    PA_APP_LIBRARY_LOADED  = \
        ((PA_APP_SW_VERSION >= PA_APP_REQ_SW_VERSION) and \
         (PA_APP_API_VERSION >= PA_APP_REQ_API_VERSION))


#==========================================================================
# HELPER FUNCTIONS
#==========================================================================
def array_u08 (n):  return array('B', '\0'*n)
def array_u16 (n):  return array('H', '\0\0'*n)
def array_u32 (n):  return array('I', '\0\0\0\0'*n)
def array_u64 (n):  return array('K', '\0\0\0\0\0\0\0\0'*n)
def array_s08 (n):  return array('b', '\0'*n)
def array_s16 (n):  return array('h', '\0\0'*n)
def array_s32 (n):  return array('i', '\0\0\0\0'*n)
def array_s64 (n):  return array('L', '\0\0\0\0\0\0\0\0'*n)
def array_f32 (n):  return array('f', '\0\0\0\0'*n)
def array_f64 (n):  return array('d', '\0\0\0\0\0\0\0\0'*n)


#==========================================================================
# STATUS CODES
#==========================================================================
# All API functions return an integer which is the result of the
# transaction, or a status code if negative.  The status codes are
# defined as follows:
# enum PromiraAppStatus
# General codes (0 to -99)
PA_APP_OK                       =   0
PA_APP_UNABLE_TO_LOAD_LIBRARY   =  -1
PA_APP_UNABLE_TO_LOAD_DRIVER    =  -2
PA_APP_UNABLE_TO_LOAD_FUNCTION  =  -3
PA_APP_INCOMPATIBLE_LIBRARY     =  -4
PA_APP_INCOMPATIBLE_DEVICE      =  -5
PA_APP_COMMUNICATION_ERROR      =  -6
PA_APP_UNABLE_TO_OPEN           =  -7
PA_APP_UNABLE_TO_CLOSE          =  -8
PA_APP_INVALID_HANDLE           =  -9
PA_APP_CONFIG_ERROR             = -10
PA_APP_MEMORY_ALLOC_ERROR       = -11
PA_APP_UNABLE_TO_INIT_SUBSYSTEM = -12
PA_APP_INVALID_LICENSE          = -13
PA_APP_UNKNOWN_PROTOCOL         = -14
PA_APP_STILL_ACTIVE             = -15
PA_APP_INACTIVE                 = -16
PA_APP_FUNCTION_NOT_AVAILABLE   = -17
PA_APP_READ_EMPTY               = -18

PA_APP_TIMEOUT                  = -31
PA_APP_CONNECTION_LOST          = -32

PA_APP_QUEUE_FULL               = -50

PA_APP_UNKNOWN_CMD              = -83


#==========================================================================
# GENERAL TYPE DEFINITIONS
#==========================================================================
# Connection handle type definition
# typedef PromiraConnectionHandle => integer

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
def pa_app_connect (net_addr):
    """usage: PromiraConnectionHandle return = pa_app_connect(str net_addr)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_app_connect(net_addr)


# Disconnect from the application
def pa_app_disconnect (conn):
    """usage: int return = pa_app_disconnect(PromiraConnectionHandle conn)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_app_disconnect(conn)


# Return the version matrix for the device attached to the
# given handle.  If the handle is 0 or invalid, only the
# software and required api versions are set.
def pa_app_version (conn):
    """usage: (int return, PromiraAppVersion version) = pa_app_version(PromiraConnectionHandle conn)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_version) = api.py_pa_app_version(conn)
    # version post-processing
    version = PromiraAppVersion()
    (version.software, version.firmware, version.hardware, version.sw_req_by_fw, version.fw_req_by_sw, version.api_req_by_sw) = c_version
    return (_ret_, version)


# Return the status string for the given status code.
# If the code is not valid or the library function cannot
# be loaded, return a NULL string.
def pa_app_status_string (status):
    """usage: str return = pa_app_status_string(int status)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_app_status_string(status)


# Return the device features as a bit-mask of values, or
# an error code if the handle is not valid.
PA_FEATURE_NONE = 0x00000000
PA_FEATURE_ESPI = 0x00000001
def pa_app_features (conn):
    """usage: int return = pa_app_features(PromiraConnectionHandle conn)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_app_features(conn)



#==========================================================================
# POWER API
#==========================================================================
# Configure the target power pins.
PA_PHY_TARGET_POWER_NONE = 0x00
PA_PHY_TARGET_POWER_TARGET1_5V = 0x01
PA_PHY_TARGET_POWER_TARGET1_3V = 0x05
PA_PHY_TARGET_POWER_TARGET2 = 0x02
PA_PHY_TARGET_POWER_BOTH = 0x03
PA_PHY_TARGET_POWER_QUERY = 0x80
def pa_phy_target_power (conn, config):
    """usage: int return = pa_phy_target_power(PromiraConnectionHandle conn, u08 config)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_phy_target_power(conn, config)


# Configure the power of output signal.
PA_PHY_LEVEL_SHIFT_QUERY = -1
def pa_phy_level_shift (conn, level):
    """usage: f32 return = pa_phy_level_shift(PromiraConnectionHandle conn, f32 level)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_phy_level_shift(conn, level)



#==========================================================================
# CAPTURE API
#==========================================================================
# Protocol codes
# enum PromiraProtocol
PA_PROTOCOL_NONE = 0
PA_PROTOCOL_ESPI = 1

# Trigger modes
# enum PromiraTriggerMode
PA_TRIGGER_MODE_EVENT     = 0
PA_TRIGGER_MODE_IMMEDIATE = 1

# Start capturing
def pa_capture_start (conn, protocol, trig_mode):
    """usage: int return = pa_capture_start(PromiraConnectionHandle conn, PromiraProtocol protocol, PromiraTriggerMode trig_mode)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_capture_start(conn, protocol, trig_mode)


# Stop capturing data
def pa_capture_stop (conn):
    """usage: int return = pa_capture_stop(PromiraConnectionHandle conn)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_capture_stop(conn)


# Trigger capture manually
def pa_capture_trigger (conn):
    """usage: int return = pa_capture_trigger(PromiraConnectionHandle conn)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_capture_trigger(conn)


# Capture status; general across protocols but used in
# protocol-specific capture-status-query functions as well
# enum PromiraCaptureStatus
PA_CAPTURE_STATUS_UNKNOWN          = -1
PA_CAPTURE_STATUS_INACTIVE         =  0
PA_CAPTURE_STATUS_PRE_TRIGGER      =  1
PA_CAPTURE_STATUS_PRE_TRIGGER_SYNC =  2
PA_CAPTURE_STATUS_POST_TRIGGER     =  3
PA_CAPTURE_STATUS_TRANSFER         =  4
PA_CAPTURE_STATUS_COMPLETE         =  5

# Wait for capture to trigger
def pa_capture_trigger_wait (conn, timeout_ms):
    """usage: (int return, PromiraCaptureStatus status) = pa_capture_trigger_wait(PromiraConnectionHandle conn, int timeout_ms)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_capture_trigger_wait(conn, timeout_ms)


class PromiraCaptureBufferStatus:
    def __init__ (self):
        self.pretrig_remaining_kb = 0
        self.pretrig_total_kb     = 0
        self.capture_remaining_kb = 0
        self.capture_total_kb     = 0

def pa_capture_status (conn):
    """usage: (int return, PromiraCaptureStatus status, PromiraCaptureBufferStatus buf_status) = pa_capture_status(PromiraConnectionHandle conn)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, status, c_buf_status) = api.py_pa_capture_status(conn)
    # buf_status post-processing
    buf_status = PromiraCaptureBufferStatus()
    (buf_status.pretrig_remaining_kb, buf_status.pretrig_total_kb, buf_status.capture_remaining_kb, buf_status.capture_total_kb) = c_buf_status
    return (_ret_, status, buf_status)


# General constants
def pa_capture_buffer_config (conn, pretrig_kb, capture_kb):
    """usage: int return = pa_capture_buffer_config(PromiraConnectionHandle conn, u32 pretrig_kb, u32 capture_kb)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_capture_buffer_config(conn, pretrig_kb, capture_kb)


def pa_capture_buffer_config_query (conn):
    """usage: (int return, u32 pretrig_kb, u32 capture_kb) = pa_capture_buffer_config_query(PromiraConnectionHandle conn)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_capture_buffer_config_query(conn)



#==========================================================================
# DIGITAL INPUT/OUTPUT CONFIGURATION
#==========================================================================
PA_DIGITAL_DIR_INPUT = 0
PA_DIGITAL_DIR_OUTPUT = 1
PA_DIGITAL_ACTIVE_LOW = 0
PA_DIGITAL_ACTIVE_HIGH = 1
# Configure the digital I/Os
def pa_digital_io_config (conn, enable, direction, polarity):
    """usage: int return = pa_digital_io_config(PromiraConnectionHandle conn, u32 enable, u32 direction, u32 polarity)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_digital_io_config(conn, enable, direction, polarity)


def pa_digital_io_config_query (conn):
    """usage: (int return, u32 enable, u32 direction, u32 polarity) = pa_digital_io_config_query(PromiraConnectionHandle conn)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    return api.py_pa_digital_io_config_query(conn)



#==========================================================================
# COMMON CAPTURE TRIGGER OPTIONS
#==========================================================================
# Packet matching modes
# enum PromiraMatchType
PA_MATCH_TYPE_DISABLED  = 0
PA_MATCH_TYPE_EQUAL     = 1
PA_MATCH_TYPE_NOT_EQUAL = 2


#==========================================================================
# COMMON STATUS/EVENT FOR READ
#==========================================================================
class PromiraReadInfo:
    def __init__ (self):
        self.timestamp = 0
        self.duration  = 0
        self.status    = 0
        self.events    = 0

# Status
PA_READ_OK = 0
PA_READ_ERR_CODE_MASK = 0x000000ff
# Event
PA_EVENT_DIGITAL_INPUT_MASK = 0x00000fff
PA_EVENT_DIGITAL_INPUT = 0x00001000
PA_EVENT_SLAVE_ID_MASK = 0x30000000
PA_EVENT_SLAVE0 = 0x00000000
PA_EVENT_SLAVE1 = 0x10000000
PA_EVENT_SLAVE2 = 0x20000000
PA_EVENT_SLAVE3 = 0x30000000
PA_EVENT_TRIGGER = 0x80000000
# SPI IO Mode for SPI and eSPI
# enum PromiraSpiIOMode
PA_SPI_IO_UNKNOWN  = -1
PA_SPI_IO_STANDARD =  0
PA_SPI_IO_DUAL     =  2
PA_SPI_IO_QUAD     =  4


#==========================================================================
# eSPI API
#==========================================================================
# enum PromiraEspiAlertPin
PA_ESPI_ALERT_UNKNOWN = 0
PA_ESPI_ALERT_PIN     = 1
PA_ESPI_ALERT_IO1     = 2

# enum PromiraEspiAlign
PA_ESPI_ALIGN_UNKNOWN    = 0
PA_ESPI_ALIGN_64_BYTES   = 1
PA_ESPI_ALIGN_128_BYTES  = 2
PA_ESPI_ALIGN_256_BYTES  = 3
PA_ESPI_ALIGN_512_BYTES  = 4
PA_ESPI_ALIGN_1024_BYTES = 5
PA_ESPI_ALIGN_2048_BYTES = 6
PA_ESPI_ALIGN_4096_BYTES = 7

class PromiraEspiOperatingCfg:
    def __init__ (self):
        self.io_mode            = 0
        self.alert_pin          = 0
        self.perif_max_req_size = 0
        self.perif_max_payload  = 0
        self.vw_max_count       = 0
        self.oob_max_payload    = 0
        self.flash_max_req_size = 0
        self.flash_max_payload  = 0

# Set the operating configuration of eSPI system
def pa_espi_operating_config (conn, slave_id, cfg):
    """usage: int return = pa_espi_operating_config(PromiraConnectionHandle conn, u08 slave_id, PromiraEspiOperatingCfg cfg)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # cfg pre-processing
    c_cfg = None
    if cfg != None:
        c_cfg = (cfg.io_mode, cfg.alert_pin, cfg.perif_max_req_size, cfg.perif_max_payload, cfg.vw_max_count, cfg.oob_max_payload, cfg.flash_max_req_size, cfg.flash_max_payload)
    # Call API function
    return api.py_pa_espi_operating_config(conn, slave_id, c_cfg)


# Read the operation configuration that eSPI system is using
def pa_espi_operating_config_read (conn, slave_id):
    """usage: (int return, PromiraEspiOperatingCfg cfg) = pa_espi_operating_config_read(PromiraConnectionHandle conn, u08 slave_id)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_cfg) = api.py_pa_espi_operating_config_read(conn, slave_id)
    # cfg post-processing
    cfg = PromiraEspiOperatingCfg()
    (cfg.io_mode, cfg.alert_pin, cfg.perif_max_req_size, cfg.perif_max_payload, cfg.vw_max_count, cfg.oob_max_payload, cfg.flash_max_req_size, cfg.flash_max_payload) = c_cfg
    return (_ret_, cfg)


# Status - error
PA_READ_ESPI_ERR_TYPE_MASK = 0x000000c0
PA_READ_ESPI_ERR_TYPE_MASTER = 0x00000080
PA_READ_ESPI_ERR_TYPE_SLAVE = 0x00000040
PA_READ_ESPI_ERR_TYPE_MISC = 0x000000c0
PA_READ_ESPI_ERR_FATAL_MASK = 0x00000020
# Master Error Code - Fatal
PA_READ_ESPI_MST_INVALID_RSP_CODE = 0x000000a0
PA_READ_ESPI_MST_INVALID_CYCLE_TYPE = 0x000000a1
PA_READ_ESPI_MST_NO_RSP = 0x000000a3
PA_READ_ESPI_MST_RSP_FATAL = 0x000000a4
PA_READ_ESPI_MST_PERIF_PAYLOAD = 0x000000a5
PA_READ_ESPI_MST_PERIF_REQ_SIZE = 0x000000a6
PA_READ_ESPI_MST_PERIF_4K_XING = 0x000000a7
PA_READ_ESPI_MST_VW_MAX_COUNT = 0x000000a8
PA_READ_ESPI_MST_OOB_PAYLOAD = 0x000000a9
PA_READ_ESPI_MST_FLASH_PAYLOAD = 0x000000aa
PA_READ_ESPI_MST_FLASH_REQ_SIZE = 0x000000ab
PA_READ_ESPI_MST_PERIF_PAYLOAD_SIZE = 0x000000ad
PA_READ_ESPI_MST_FLASH_PAYLOAD_SIZE = 0x000000ae
# Master Error Code - Non Fatal
PA_READ_ESPI_MST_RSP_NON_FATAL = 0x00000080
# Slave Error Code - Fatal
PA_READ_ESPI_SLV_PUT_WO_FREE = 0x00000060
PA_READ_ESPI_SLV_GET_WHEN_UNAVAIL = 0x00000061
PA_READ_ESPI_SLV_PERIF_PAYLOAD = 0x0000006a
PA_READ_ESPI_SLV_PERIF_REQ_SIZE = 0x00000062
PA_READ_ESPI_SLV_PERIF_4K_XING = 0x00000063
PA_READ_ESPI_SLV_VW_MAX_COUNT = 0x00000064
PA_READ_ESPI_SLV_OOB_PAYLOAD = 0x00000065
PA_READ_ESPI_SLV_FLASH_PAYLOAD = 0x00000066
PA_READ_ESPI_SLV_FLASH_REQ_SIZE = 0x00000067
PA_READ_ESPI_SLV_PERIF_PAYLOAD_SIZE = 0x00000068
PA_READ_ESPI_SLV_FLASH_PAYLOAD_SIZE = 0x00000069
# Slave Error Code - Non Fatal
PA_READ_ESPI_SLV_INVALID_CMD = 0x00000040
PA_READ_ESPI_SLV_INVALID_CYCLE_TYPE = 0x00000041
# Miscellaneous Error Code
PA_READ_ESPI_PARTIAL_BYTE = 0x000000e0
PA_READ_ESPI_RESET_WHILE_CS = 0x000000e1
PA_READ_ESPI_ALERT_WHILE_CS = 0x000000e2
PA_READ_ESPI_INVALID_LENGTH = 0x000000e3
PA_READ_ESPI_MORE_THAN_ONE_CS = 0x000000e4
PA_READ_ESPI_ERR_BAD_CMD_CRC = 0x00000100
PA_READ_ESPI_ERR_BAD_RSP_CRC = 0x00000200
# eSPI specific event
PA_EVENT_ESPI_ALERT_RISING = 0x00010000
PA_EVENT_ESPI_ALERT_FALLING = 0x00020000
PA_EVENT_ESPI_RESET_RISING = 0x00040000
PA_EVENT_ESPI_RESET_FALLING = 0x00080000
PA_EVENT_ESPI_INBAND_RESET = 0x00100000
PA_EVENT_ESPI_PACKET = 0x00200000
# eSPI transaction base information
# enum PromiraEspiChannel
PA_ESPI_CHANNEL_UNKNOWN = -1
PA_ESPI_CHANNEL_PERIF   =  0
PA_ESPI_CHANNEL_VW      =  1
PA_ESPI_CHANNEL_OOB     =  2
PA_ESPI_CHANNEL_FLASH   =  3
PA_ESPI_CHANNEL_INDEP   =  4

# enum PromiraEspiEnumFreq
PA_ESPI_ENUM_FREQ_UNKNOWN = -1
PA_ESPI_ENUM_FREQ_20MHZ   =  0
PA_ESPI_ENUM_FREQ_25MHZ   =  1
PA_ESPI_ENUM_FREQ_33MHZ   =  2
PA_ESPI_ENUM_FREQ_50MHZ   =  3
PA_ESPI_ENUM_FREQ_66MHZ   =  4

# eSPI packet information
class PromiraEspiPacketInfo:
    def __init__ (self):
        self.channel    = 0
        self.enum_freq  = 0
        self.io_mode    = 0
        self.length     = 0
        self.cmd_length = 0

# Read eSPI transaction
def pa_espi_read (conn, packet):
    """usage: (int return, PromiraReadInfo info, PromiraEspiPacketInfo pkt_info, u08[] packet) = pa_espi_read(PromiraConnectionHandle conn, u08[] packet)

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

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # packet pre-processing
    __packet = isinstance(packet, int)
    if __packet:
        (packet, max_bytes) = (array_u08(packet), packet)
    else:
        (packet, max_bytes) = isinstance(packet, ArrayType) and (packet, len(packet)) or (packet[0], min(len(packet[0]), int(packet[1])))
        if packet.typecode != 'B':
            raise TypeError("type for 'packet' must be array('B')")
    # Call API function
    (_ret_, c_info, c_pkt_info) = api.py_pa_espi_read(conn, max_bytes, packet)
    # info post-processing
    info = PromiraReadInfo()
    (info.timestamp, info.duration, info.status, info.events) = c_info
    # pkt_info post-processing
    pkt_info = PromiraEspiPacketInfo()
    (pkt_info.channel, pkt_info.enum_freq, pkt_info.io_mode, pkt_info.length, pkt_info.cmd_length) = c_pkt_info
    # packet post-processing
    if __packet: del packet[max(0, min(_ret_, len(packet))):]
    return (_ret_, info, pkt_info, packet)


class PromiraEspiStats:
    def __init__ (self):
        self.ch_perif      = 0
        self.ch_vw         = 0
        self.ch_oob        = 0
        self.ch_flash      = 0
        self.get_cfg       = 0
        self.set_cfg       = 0
        self.get_sts       = 0
        self.pltf_reset    = 0
        self.alert         = 0
        self.reset         = 0
        self.cmd_crc       = 0
        self.resp_crc      = 0
        self.fltr_out_pkts = 0
        self.fltr_out_cmds = 0

# Get the statistics
def pa_espi_stats_read (conn, slave_id):
    """usage: (int return, PromiraEspiStats stats) = pa_espi_stats_read(PromiraConnectionHandle conn, u08 slave_id)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # Call API function
    (_ret_, c_stats) = api.py_pa_espi_stats_read(conn, slave_id)
    # stats post-processing
    stats = PromiraEspiStats()
    (stats.ch_perif, stats.ch_vw, stats.ch_oob, stats.ch_flash, stats.get_cfg, stats.set_cfg, stats.get_sts, stats.pltf_reset, stats.alert, stats.reset, stats.cmd_crc, stats.resp_crc, stats.fltr_out_pkts, stats.fltr_out_cmds) = c_stats
    return (_ret_, stats)


# For channel match bitmask
PA_ESPI_CHANNEL_MATCH_PERIF = 0x00000001
PA_ESPI_CHANNEL_MATCH_VW = 0x00000002
PA_ESPI_CHANNEL_MATCH_OOB = 0x00000004
PA_ESPI_CHANNEL_MATCH_FLASH = 0x00000008
PA_ESPI_CHANNEL_MATCH_INDEP = 0x00000010
# eSPI packet matching configuration
class PromiraEspiPacketMatch:
    def __init__ (self):
        self.ch_match_bitmask = 0
        self.cmd_match_type   = 0
        self.cmd_match_val    = 0

# Hardware filtering configuration
def pa_espi_hw_filter_config (conn, slave_id, pkt_match):
    """usage: int return = pa_espi_hw_filter_config(PromiraConnectionHandle conn, u08 slave_id, PromiraEspiPacketMatch pkt_match)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # pkt_match pre-processing
    c_pkt_match = None
    if pkt_match != None:
        c_pkt_match = (pkt_match.ch_match_bitmask, pkt_match.cmd_match_type, pkt_match.cmd_match_val)
    # Call API function
    return api.py_pa_espi_hw_filter_config(conn, slave_id, c_pkt_match)


# Condtions for trigger
PA_ESPI_ACT_ON_DIG_IN_MASK = 0x00000fff
PA_ESPI_ACT_ON_ALERT = 0x00010000
PA_ESPI_ACT_ON_RESET = 0x00040000
PA_ESPI_ACT_ON_SLAVE_BITMASK = 0xf0000000
# Actions when triggered
PA_ESPI_ACTION_DIG_OUT_MASK = 0x00000fff
PA_ESPI_ACTION_TRIGGER = 0x80000000
# Simple trigger configuration
def pa_espi_simple_trigger_config (conn, act_on, pkt_match, actions):
    """usage: int return = pa_espi_simple_trigger_config(PromiraConnectionHandle conn, u32 act_on, PromiraEspiPacketMatch pkt_match, u32 actions)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # pkt_match pre-processing
    c_pkt_match = None
    if pkt_match != None:
        c_pkt_match = (pkt_match.ch_match_bitmask, pkt_match.cmd_match_type, pkt_match.cmd_match_val)
    # Call API function
    return api.py_pa_espi_simple_trigger_config(conn, act_on, c_pkt_match, actions)


# Array_u08: 16 bytes long
class PromiraEspiAdvancedTrigBytes16:
    def __init__ (self):
        self.byte0 = 0
        self.byte1 = 0
        self.byte2 = 0
        self.byte3 = 0
        self.byte4 = 0
        self.byte5 = 0
        self.byte6 = 0
        self.byte7 = 0
        self.byte8 = 0
        self.byte9 = 0
        self.byteA = 0
        self.byteB = 0
        self.byteC = 0
        self.byteD = 0
        self.byteE = 0
        self.byteF = 0

# Array_u08: 2 bytes long
class PromiraEspiAdvancedTrigBytes2:
    def __init__ (self):
        self.byte0 = 0
        self.byte1 = 0

# Advanced Trigger Option 1
class PromiraEspiAdvancedTrig1:
    def __init__ (self):
        self.cmd_byte             = 0
        self.cmd_cyc              = 0
        self.cmd_tag              = 0
        self.cmd_len              = 0
        self.cmd_addr             = 0
        self.cmd_data             = PromiraEspiAdvancedTrigBytes16()
        self.cmd_data_mask        = PromiraEspiAdvancedTrigBytes16()
        self.rsp_byte             = 0
        self.rsp_cyc              = 0
        self.rsp_tag              = 0
        self.rsp_len              = 0
        self.rsp_addr             = 0
        self.rsp_data             = PromiraEspiAdvancedTrigBytes16()
        self.rsp_data_mask        = PromiraEspiAdvancedTrigBytes16()
        self.sts_byte             = PromiraEspiAdvancedTrigBytes2()
        self.sts_mask             = PromiraEspiAdvancedTrigBytes2()
        self.trg_pin              = 0
        self.trg_pin_polarity     = 0
        self.trg_pin_direction    = 0
        self.cmd_byte_enable      = 0
        self.cmd_cyc_enable       = 0
        self.cmd_tag_enable       = 0
        self.cmd_len_enable       = 0
        self.cmd_addr_enable      = 0
        self.cmd_data_enable      = 0
        self.rsp_byte_enable      = 0
        self.rsp_cyc_enable       = 0
        self.rsp_tag_enable       = 0
        self.rsp_len_enable       = 0
        self.rsp_addr_enable      = 0
        self.rsp_data_enable      = 0
        self.sts_byte_enable      = 0
        self.trg_pin_enable       = 0
        self.lvl_select_enable    = 0
        self.lvl_select_immediate = 0

# Advanced Trigger Option 2
class PromiraEspiAdvancedTrig2:
    def __init__ (self):
        self.cmd_byte2               = 0
        self.cmd_cyc2                = 0
        self.cmd_tag2                = 0
        self.cmd_len2                = 0
        self.cmd_addr2               = 0
        self.cmd_data2               = PromiraEspiAdvancedTrigBytes16()
        self.cmd_data_mask2          = PromiraEspiAdvancedTrigBytes16()
        self.trg_pin_req             = 0
        self.trg_pin_req_polarity    = 0
        self.trg_pin_req_direction   = 0
        self.trg_pin_cmpl0           = 0
        self.trg_pin_cmpl0_polarity  = 0
        self.trg_pin_cmpl0_direction = 0
        self.trg_pin_cmpl1           = 0
        self.trg_pin_cmpl1_polarity  = 0
        self.trg_pin_cmpl1_direction = 0
        self.trg_pin_cmpl2           = 0
        self.trg_pin_cmpl2_polarity  = 0
        self.trg_pin_cmpl2_direction = 0
        self.cmd_byte2_enable        = 0
        self.cmd_cyc2_enable         = 0
        self.cmd_tag2_enable         = 0
        self.cmd_len2_enable         = 0
        self.cmd_addr2_enable        = 0
        self.cmd_data2_enable        = 0
        self.succ_cmpl_enable        = 0
        self.unsucc_cmpl_enable      = 0
        self.trg_pin_req_enable      = 0
        self.trg_pin_cmpl0_enable    = 0
        self.trg_pin_cmpl1_enable    = 0
        self.trg_pin_cmpl2_enable    = 0

# Advanced Trigger Option Error
class PromiraEspiAdvancedTrigError:
    def __init__ (self):
        self.err_code        = 0
        self.err_code_enable = 0

# Advanced Trigger Configuration
def pa_espi_adv_trig_config (conn, slave_id, pkt_adv_trig1_level1, pkt_adv_trig1_level2, pkt_adv_trig1_level3, pkt_adv_trig1_level4, pkt_adv_trig2, pkt_adv_trig_error):
    """usage: int return = pa_espi_adv_trig_config(PromiraConnectionHandle conn, u08 slave_id, PromiraEspiAdvancedTrig1 pkt_adv_trig1_level1, PromiraEspiAdvancedTrig1 pkt_adv_trig1_level2, PromiraEspiAdvancedTrig1 pkt_adv_trig1_level3, PromiraEspiAdvancedTrig1 pkt_adv_trig1_level4, PromiraEspiAdvancedTrig2 pkt_adv_trig2, PromiraEspiAdvancedTrigError pkt_adv_trig_error)"""

    if not api:  __initialize()
    if not PA_APP_LIBRARY_LOADED: return PA_APP_INCOMPATIBLE_LIBRARY
    # pkt_adv_trig1_level1 pre-processing
    c_pkt_adv_trig1_level1 = None
    if pkt_adv_trig1_level1 != None:
        c_pkt_adv_trig1_level1 = (pkt_adv_trig1_level1.cmd_byte, pkt_adv_trig1_level1.cmd_cyc, pkt_adv_trig1_level1.cmd_tag, pkt_adv_trig1_level1.cmd_len, pkt_adv_trig1_level1.cmd_addr, pkt_adv_trig1_level1.cmd_data.byte0, pkt_adv_trig1_level1.cmd_data.byte1, pkt_adv_trig1_level1.cmd_data.byte2, pkt_adv_trig1_level1.cmd_data.byte3, pkt_adv_trig1_level1.cmd_data.byte4, pkt_adv_trig1_level1.cmd_data.byte5, pkt_adv_trig1_level1.cmd_data.byte6, pkt_adv_trig1_level1.cmd_data.byte7, pkt_adv_trig1_level1.cmd_data.byte8, pkt_adv_trig1_level1.cmd_data.byte9, pkt_adv_trig1_level1.cmd_data.byteA, pkt_adv_trig1_level1.cmd_data.byteB, pkt_adv_trig1_level1.cmd_data.byteC, pkt_adv_trig1_level1.cmd_data.byteD, pkt_adv_trig1_level1.cmd_data.byteE, pkt_adv_trig1_level1.cmd_data.byteF, pkt_adv_trig1_level1.cmd_data_mask.byte0, pkt_adv_trig1_level1.cmd_data_mask.byte1, pkt_adv_trig1_level1.cmd_data_mask.byte2, pkt_adv_trig1_level1.cmd_data_mask.byte3, pkt_adv_trig1_level1.cmd_data_mask.byte4, pkt_adv_trig1_level1.cmd_data_mask.byte5, pkt_adv_trig1_level1.cmd_data_mask.byte6, pkt_adv_trig1_level1.cmd_data_mask.byte7, pkt_adv_trig1_level1.cmd_data_mask.byte8, pkt_adv_trig1_level1.cmd_data_mask.byte9, pkt_adv_trig1_level1.cmd_data_mask.byteA, pkt_adv_trig1_level1.cmd_data_mask.byteB, pkt_adv_trig1_level1.cmd_data_mask.byteC, pkt_adv_trig1_level1.cmd_data_mask.byteD, pkt_adv_trig1_level1.cmd_data_mask.byteE, pkt_adv_trig1_level1.cmd_data_mask.byteF, pkt_adv_trig1_level1.rsp_byte, pkt_adv_trig1_level1.rsp_cyc, pkt_adv_trig1_level1.rsp_tag, pkt_adv_trig1_level1.rsp_len, pkt_adv_trig1_level1.rsp_addr, pkt_adv_trig1_level1.rsp_data.byte0, pkt_adv_trig1_level1.rsp_data.byte1, pkt_adv_trig1_level1.rsp_data.byte2, pkt_adv_trig1_level1.rsp_data.byte3, pkt_adv_trig1_level1.rsp_data.byte4, pkt_adv_trig1_level1.rsp_data.byte5, pkt_adv_trig1_level1.rsp_data.byte6, pkt_adv_trig1_level1.rsp_data.byte7, pkt_adv_trig1_level1.rsp_data.byte8, pkt_adv_trig1_level1.rsp_data.byte9, pkt_adv_trig1_level1.rsp_data.byteA, pkt_adv_trig1_level1.rsp_data.byteB, pkt_adv_trig1_level1.rsp_data.byteC, pkt_adv_trig1_level1.rsp_data.byteD, pkt_adv_trig1_level1.rsp_data.byteE, pkt_adv_trig1_level1.rsp_data.byteF, pkt_adv_trig1_level1.rsp_data_mask.byte0, pkt_adv_trig1_level1.rsp_data_mask.byte1, pkt_adv_trig1_level1.rsp_data_mask.byte2, pkt_adv_trig1_level1.rsp_data_mask.byte3, pkt_adv_trig1_level1.rsp_data_mask.byte4, pkt_adv_trig1_level1.rsp_data_mask.byte5, pkt_adv_trig1_level1.rsp_data_mask.byte6, pkt_adv_trig1_level1.rsp_data_mask.byte7, pkt_adv_trig1_level1.rsp_data_mask.byte8, pkt_adv_trig1_level1.rsp_data_mask.byte9, pkt_adv_trig1_level1.rsp_data_mask.byteA, pkt_adv_trig1_level1.rsp_data_mask.byteB, pkt_adv_trig1_level1.rsp_data_mask.byteC, pkt_adv_trig1_level1.rsp_data_mask.byteD, pkt_adv_trig1_level1.rsp_data_mask.byteE, pkt_adv_trig1_level1.rsp_data_mask.byteF, pkt_adv_trig1_level1.sts_byte.byte0, pkt_adv_trig1_level1.sts_byte.byte1, pkt_adv_trig1_level1.sts_mask.byte0, pkt_adv_trig1_level1.sts_mask.byte1, pkt_adv_trig1_level1.trg_pin, pkt_adv_trig1_level1.trg_pin_polarity, pkt_adv_trig1_level1.trg_pin_direction, pkt_adv_trig1_level1.cmd_byte_enable, pkt_adv_trig1_level1.cmd_cyc_enable, pkt_adv_trig1_level1.cmd_tag_enable, pkt_adv_trig1_level1.cmd_len_enable, pkt_adv_trig1_level1.cmd_addr_enable, pkt_adv_trig1_level1.cmd_data_enable, pkt_adv_trig1_level1.rsp_byte_enable, pkt_adv_trig1_level1.rsp_cyc_enable, pkt_adv_trig1_level1.rsp_tag_enable, pkt_adv_trig1_level1.rsp_len_enable, pkt_adv_trig1_level1.rsp_addr_enable, pkt_adv_trig1_level1.rsp_data_enable, pkt_adv_trig1_level1.sts_byte_enable, pkt_adv_trig1_level1.trg_pin_enable, pkt_adv_trig1_level1.lvl_select_enable, pkt_adv_trig1_level1.lvl_select_immediate)
    # pkt_adv_trig1_level2 pre-processing
    c_pkt_adv_trig1_level2 = None
    if pkt_adv_trig1_level2 != None:
        c_pkt_adv_trig1_level2 = (pkt_adv_trig1_level2.cmd_byte, pkt_adv_trig1_level2.cmd_cyc, pkt_adv_trig1_level2.cmd_tag, pkt_adv_trig1_level2.cmd_len, pkt_adv_trig1_level2.cmd_addr, pkt_adv_trig1_level2.cmd_data.byte0, pkt_adv_trig1_level2.cmd_data.byte1, pkt_adv_trig1_level2.cmd_data.byte2, pkt_adv_trig1_level2.cmd_data.byte3, pkt_adv_trig1_level2.cmd_data.byte4, pkt_adv_trig1_level2.cmd_data.byte5, pkt_adv_trig1_level2.cmd_data.byte6, pkt_adv_trig1_level2.cmd_data.byte7, pkt_adv_trig1_level2.cmd_data.byte8, pkt_adv_trig1_level2.cmd_data.byte9, pkt_adv_trig1_level2.cmd_data.byteA, pkt_adv_trig1_level2.cmd_data.byteB, pkt_adv_trig1_level2.cmd_data.byteC, pkt_adv_trig1_level2.cmd_data.byteD, pkt_adv_trig1_level2.cmd_data.byteE, pkt_adv_trig1_level2.cmd_data.byteF, pkt_adv_trig1_level2.cmd_data_mask.byte0, pkt_adv_trig1_level2.cmd_data_mask.byte1, pkt_adv_trig1_level2.cmd_data_mask.byte2, pkt_adv_trig1_level2.cmd_data_mask.byte3, pkt_adv_trig1_level2.cmd_data_mask.byte4, pkt_adv_trig1_level2.cmd_data_mask.byte5, pkt_adv_trig1_level2.cmd_data_mask.byte6, pkt_adv_trig1_level2.cmd_data_mask.byte7, pkt_adv_trig1_level2.cmd_data_mask.byte8, pkt_adv_trig1_level2.cmd_data_mask.byte9, pkt_adv_trig1_level2.cmd_data_mask.byteA, pkt_adv_trig1_level2.cmd_data_mask.byteB, pkt_adv_trig1_level2.cmd_data_mask.byteC, pkt_adv_trig1_level2.cmd_data_mask.byteD, pkt_adv_trig1_level2.cmd_data_mask.byteE, pkt_adv_trig1_level2.cmd_data_mask.byteF, pkt_adv_trig1_level2.rsp_byte, pkt_adv_trig1_level2.rsp_cyc, pkt_adv_trig1_level2.rsp_tag, pkt_adv_trig1_level2.rsp_len, pkt_adv_trig1_level2.rsp_addr, pkt_adv_trig1_level2.rsp_data.byte0, pkt_adv_trig1_level2.rsp_data.byte1, pkt_adv_trig1_level2.rsp_data.byte2, pkt_adv_trig1_level2.rsp_data.byte3, pkt_adv_trig1_level2.rsp_data.byte4, pkt_adv_trig1_level2.rsp_data.byte5, pkt_adv_trig1_level2.rsp_data.byte6, pkt_adv_trig1_level2.rsp_data.byte7, pkt_adv_trig1_level2.rsp_data.byte8, pkt_adv_trig1_level2.rsp_data.byte9, pkt_adv_trig1_level2.rsp_data.byteA, pkt_adv_trig1_level2.rsp_data.byteB, pkt_adv_trig1_level2.rsp_data.byteC, pkt_adv_trig1_level2.rsp_data.byteD, pkt_adv_trig1_level2.rsp_data.byteE, pkt_adv_trig1_level2.rsp_data.byteF, pkt_adv_trig1_level2.rsp_data_mask.byte0, pkt_adv_trig1_level2.rsp_data_mask.byte1, pkt_adv_trig1_level2.rsp_data_mask.byte2, pkt_adv_trig1_level2.rsp_data_mask.byte3, pkt_adv_trig1_level2.rsp_data_mask.byte4, pkt_adv_trig1_level2.rsp_data_mask.byte5, pkt_adv_trig1_level2.rsp_data_mask.byte6, pkt_adv_trig1_level2.rsp_data_mask.byte7, pkt_adv_trig1_level2.rsp_data_mask.byte8, pkt_adv_trig1_level2.rsp_data_mask.byte9, pkt_adv_trig1_level2.rsp_data_mask.byteA, pkt_adv_trig1_level2.rsp_data_mask.byteB, pkt_adv_trig1_level2.rsp_data_mask.byteC, pkt_adv_trig1_level2.rsp_data_mask.byteD, pkt_adv_trig1_level2.rsp_data_mask.byteE, pkt_adv_trig1_level2.rsp_data_mask.byteF, pkt_adv_trig1_level2.sts_byte.byte0, pkt_adv_trig1_level2.sts_byte.byte1, pkt_adv_trig1_level2.sts_mask.byte0, pkt_adv_trig1_level2.sts_mask.byte1, pkt_adv_trig1_level2.trg_pin, pkt_adv_trig1_level2.trg_pin_polarity, pkt_adv_trig1_level2.trg_pin_direction, pkt_adv_trig1_level2.cmd_byte_enable, pkt_adv_trig1_level2.cmd_cyc_enable, pkt_adv_trig1_level2.cmd_tag_enable, pkt_adv_trig1_level2.cmd_len_enable, pkt_adv_trig1_level2.cmd_addr_enable, pkt_adv_trig1_level2.cmd_data_enable, pkt_adv_trig1_level2.rsp_byte_enable, pkt_adv_trig1_level2.rsp_cyc_enable, pkt_adv_trig1_level2.rsp_tag_enable, pkt_adv_trig1_level2.rsp_len_enable, pkt_adv_trig1_level2.rsp_addr_enable, pkt_adv_trig1_level2.rsp_data_enable, pkt_adv_trig1_level2.sts_byte_enable, pkt_adv_trig1_level2.trg_pin_enable, pkt_adv_trig1_level2.lvl_select_enable, pkt_adv_trig1_level2.lvl_select_immediate)
    # pkt_adv_trig1_level3 pre-processing
    c_pkt_adv_trig1_level3 = None
    if pkt_adv_trig1_level3 != None:
        c_pkt_adv_trig1_level3 = (pkt_adv_trig1_level3.cmd_byte, pkt_adv_trig1_level3.cmd_cyc, pkt_adv_trig1_level3.cmd_tag, pkt_adv_trig1_level3.cmd_len, pkt_adv_trig1_level3.cmd_addr, pkt_adv_trig1_level3.cmd_data.byte0, pkt_adv_trig1_level3.cmd_data.byte1, pkt_adv_trig1_level3.cmd_data.byte2, pkt_adv_trig1_level3.cmd_data.byte3, pkt_adv_trig1_level3.cmd_data.byte4, pkt_adv_trig1_level3.cmd_data.byte5, pkt_adv_trig1_level3.cmd_data.byte6, pkt_adv_trig1_level3.cmd_data.byte7, pkt_adv_trig1_level3.cmd_data.byte8, pkt_adv_trig1_level3.cmd_data.byte9, pkt_adv_trig1_level3.cmd_data.byteA, pkt_adv_trig1_level3.cmd_data.byteB, pkt_adv_trig1_level3.cmd_data.byteC, pkt_adv_trig1_level3.cmd_data.byteD, pkt_adv_trig1_level3.cmd_data.byteE, pkt_adv_trig1_level3.cmd_data.byteF, pkt_adv_trig1_level3.cmd_data_mask.byte0, pkt_adv_trig1_level3.cmd_data_mask.byte1, pkt_adv_trig1_level3.cmd_data_mask.byte2, pkt_adv_trig1_level3.cmd_data_mask.byte3, pkt_adv_trig1_level3.cmd_data_mask.byte4, pkt_adv_trig1_level3.cmd_data_mask.byte5, pkt_adv_trig1_level3.cmd_data_mask.byte6, pkt_adv_trig1_level3.cmd_data_mask.byte7, pkt_adv_trig1_level3.cmd_data_mask.byte8, pkt_adv_trig1_level3.cmd_data_mask.byte9, pkt_adv_trig1_level3.cmd_data_mask.byteA, pkt_adv_trig1_level3.cmd_data_mask.byteB, pkt_adv_trig1_level3.cmd_data_mask.byteC, pkt_adv_trig1_level3.cmd_data_mask.byteD, pkt_adv_trig1_level3.cmd_data_mask.byteE, pkt_adv_trig1_level3.cmd_data_mask.byteF, pkt_adv_trig1_level3.rsp_byte, pkt_adv_trig1_level3.rsp_cyc, pkt_adv_trig1_level3.rsp_tag, pkt_adv_trig1_level3.rsp_len, pkt_adv_trig1_level3.rsp_addr, pkt_adv_trig1_level3.rsp_data.byte0, pkt_adv_trig1_level3.rsp_data.byte1, pkt_adv_trig1_level3.rsp_data.byte2, pkt_adv_trig1_level3.rsp_data.byte3, pkt_adv_trig1_level3.rsp_data.byte4, pkt_adv_trig1_level3.rsp_data.byte5, pkt_adv_trig1_level3.rsp_data.byte6, pkt_adv_trig1_level3.rsp_data.byte7, pkt_adv_trig1_level3.rsp_data.byte8, pkt_adv_trig1_level3.rsp_data.byte9, pkt_adv_trig1_level3.rsp_data.byteA, pkt_adv_trig1_level3.rsp_data.byteB, pkt_adv_trig1_level3.rsp_data.byteC, pkt_adv_trig1_level3.rsp_data.byteD, pkt_adv_trig1_level3.rsp_data.byteE, pkt_adv_trig1_level3.rsp_data.byteF, pkt_adv_trig1_level3.rsp_data_mask.byte0, pkt_adv_trig1_level3.rsp_data_mask.byte1, pkt_adv_trig1_level3.rsp_data_mask.byte2, pkt_adv_trig1_level3.rsp_data_mask.byte3, pkt_adv_trig1_level3.rsp_data_mask.byte4, pkt_adv_trig1_level3.rsp_data_mask.byte5, pkt_adv_trig1_level3.rsp_data_mask.byte6, pkt_adv_trig1_level3.rsp_data_mask.byte7, pkt_adv_trig1_level3.rsp_data_mask.byte8, pkt_adv_trig1_level3.rsp_data_mask.byte9, pkt_adv_trig1_level3.rsp_data_mask.byteA, pkt_adv_trig1_level3.rsp_data_mask.byteB, pkt_adv_trig1_level3.rsp_data_mask.byteC, pkt_adv_trig1_level3.rsp_data_mask.byteD, pkt_adv_trig1_level3.rsp_data_mask.byteE, pkt_adv_trig1_level3.rsp_data_mask.byteF, pkt_adv_trig1_level3.sts_byte.byte0, pkt_adv_trig1_level3.sts_byte.byte1, pkt_adv_trig1_level3.sts_mask.byte0, pkt_adv_trig1_level3.sts_mask.byte1, pkt_adv_trig1_level3.trg_pin, pkt_adv_trig1_level3.trg_pin_polarity, pkt_adv_trig1_level3.trg_pin_direction, pkt_adv_trig1_level3.cmd_byte_enable, pkt_adv_trig1_level3.cmd_cyc_enable, pkt_adv_trig1_level3.cmd_tag_enable, pkt_adv_trig1_level3.cmd_len_enable, pkt_adv_trig1_level3.cmd_addr_enable, pkt_adv_trig1_level3.cmd_data_enable, pkt_adv_trig1_level3.rsp_byte_enable, pkt_adv_trig1_level3.rsp_cyc_enable, pkt_adv_trig1_level3.rsp_tag_enable, pkt_adv_trig1_level3.rsp_len_enable, pkt_adv_trig1_level3.rsp_addr_enable, pkt_adv_trig1_level3.rsp_data_enable, pkt_adv_trig1_level3.sts_byte_enable, pkt_adv_trig1_level3.trg_pin_enable, pkt_adv_trig1_level3.lvl_select_enable, pkt_adv_trig1_level3.lvl_select_immediate)
    # pkt_adv_trig1_level4 pre-processing
    c_pkt_adv_trig1_level4 = None
    if pkt_adv_trig1_level4 != None:
        c_pkt_adv_trig1_level4 = (pkt_adv_trig1_level4.cmd_byte, pkt_adv_trig1_level4.cmd_cyc, pkt_adv_trig1_level4.cmd_tag, pkt_adv_trig1_level4.cmd_len, pkt_adv_trig1_level4.cmd_addr, pkt_adv_trig1_level4.cmd_data.byte0, pkt_adv_trig1_level4.cmd_data.byte1, pkt_adv_trig1_level4.cmd_data.byte2, pkt_adv_trig1_level4.cmd_data.byte3, pkt_adv_trig1_level4.cmd_data.byte4, pkt_adv_trig1_level4.cmd_data.byte5, pkt_adv_trig1_level4.cmd_data.byte6, pkt_adv_trig1_level4.cmd_data.byte7, pkt_adv_trig1_level4.cmd_data.byte8, pkt_adv_trig1_level4.cmd_data.byte9, pkt_adv_trig1_level4.cmd_data.byteA, pkt_adv_trig1_level4.cmd_data.byteB, pkt_adv_trig1_level4.cmd_data.byteC, pkt_adv_trig1_level4.cmd_data.byteD, pkt_adv_trig1_level4.cmd_data.byteE, pkt_adv_trig1_level4.cmd_data.byteF, pkt_adv_trig1_level4.cmd_data_mask.byte0, pkt_adv_trig1_level4.cmd_data_mask.byte1, pkt_adv_trig1_level4.cmd_data_mask.byte2, pkt_adv_trig1_level4.cmd_data_mask.byte3, pkt_adv_trig1_level4.cmd_data_mask.byte4, pkt_adv_trig1_level4.cmd_data_mask.byte5, pkt_adv_trig1_level4.cmd_data_mask.byte6, pkt_adv_trig1_level4.cmd_data_mask.byte7, pkt_adv_trig1_level4.cmd_data_mask.byte8, pkt_adv_trig1_level4.cmd_data_mask.byte9, pkt_adv_trig1_level4.cmd_data_mask.byteA, pkt_adv_trig1_level4.cmd_data_mask.byteB, pkt_adv_trig1_level4.cmd_data_mask.byteC, pkt_adv_trig1_level4.cmd_data_mask.byteD, pkt_adv_trig1_level4.cmd_data_mask.byteE, pkt_adv_trig1_level4.cmd_data_mask.byteF, pkt_adv_trig1_level4.rsp_byte, pkt_adv_trig1_level4.rsp_cyc, pkt_adv_trig1_level4.rsp_tag, pkt_adv_trig1_level4.rsp_len, pkt_adv_trig1_level4.rsp_addr, pkt_adv_trig1_level4.rsp_data.byte0, pkt_adv_trig1_level4.rsp_data.byte1, pkt_adv_trig1_level4.rsp_data.byte2, pkt_adv_trig1_level4.rsp_data.byte3, pkt_adv_trig1_level4.rsp_data.byte4, pkt_adv_trig1_level4.rsp_data.byte5, pkt_adv_trig1_level4.rsp_data.byte6, pkt_adv_trig1_level4.rsp_data.byte7, pkt_adv_trig1_level4.rsp_data.byte8, pkt_adv_trig1_level4.rsp_data.byte9, pkt_adv_trig1_level4.rsp_data.byteA, pkt_adv_trig1_level4.rsp_data.byteB, pkt_adv_trig1_level4.rsp_data.byteC, pkt_adv_trig1_level4.rsp_data.byteD, pkt_adv_trig1_level4.rsp_data.byteE, pkt_adv_trig1_level4.rsp_data.byteF, pkt_adv_trig1_level4.rsp_data_mask.byte0, pkt_adv_trig1_level4.rsp_data_mask.byte1, pkt_adv_trig1_level4.rsp_data_mask.byte2, pkt_adv_trig1_level4.rsp_data_mask.byte3, pkt_adv_trig1_level4.rsp_data_mask.byte4, pkt_adv_trig1_level4.rsp_data_mask.byte5, pkt_adv_trig1_level4.rsp_data_mask.byte6, pkt_adv_trig1_level4.rsp_data_mask.byte7, pkt_adv_trig1_level4.rsp_data_mask.byte8, pkt_adv_trig1_level4.rsp_data_mask.byte9, pkt_adv_trig1_level4.rsp_data_mask.byteA, pkt_adv_trig1_level4.rsp_data_mask.byteB, pkt_adv_trig1_level4.rsp_data_mask.byteC, pkt_adv_trig1_level4.rsp_data_mask.byteD, pkt_adv_trig1_level4.rsp_data_mask.byteE, pkt_adv_trig1_level4.rsp_data_mask.byteF, pkt_adv_trig1_level4.sts_byte.byte0, pkt_adv_trig1_level4.sts_byte.byte1, pkt_adv_trig1_level4.sts_mask.byte0, pkt_adv_trig1_level4.sts_mask.byte1, pkt_adv_trig1_level4.trg_pin, pkt_adv_trig1_level4.trg_pin_polarity, pkt_adv_trig1_level4.trg_pin_direction, pkt_adv_trig1_level4.cmd_byte_enable, pkt_adv_trig1_level4.cmd_cyc_enable, pkt_adv_trig1_level4.cmd_tag_enable, pkt_adv_trig1_level4.cmd_len_enable, pkt_adv_trig1_level4.cmd_addr_enable, pkt_adv_trig1_level4.cmd_data_enable, pkt_adv_trig1_level4.rsp_byte_enable, pkt_adv_trig1_level4.rsp_cyc_enable, pkt_adv_trig1_level4.rsp_tag_enable, pkt_adv_trig1_level4.rsp_len_enable, pkt_adv_trig1_level4.rsp_addr_enable, pkt_adv_trig1_level4.rsp_data_enable, pkt_adv_trig1_level4.sts_byte_enable, pkt_adv_trig1_level4.trg_pin_enable, pkt_adv_trig1_level4.lvl_select_enable, pkt_adv_trig1_level4.lvl_select_immediate)
    # pkt_adv_trig2 pre-processing
    c_pkt_adv_trig2 = None
    if pkt_adv_trig2 != None:
        c_pkt_adv_trig2 = (pkt_adv_trig2.cmd_byte2, pkt_adv_trig2.cmd_cyc2, pkt_adv_trig2.cmd_tag2, pkt_adv_trig2.cmd_len2, pkt_adv_trig2.cmd_addr2, pkt_adv_trig2.cmd_data2.byte0, pkt_adv_trig2.cmd_data2.byte1, pkt_adv_trig2.cmd_data2.byte2, pkt_adv_trig2.cmd_data2.byte3, pkt_adv_trig2.cmd_data2.byte4, pkt_adv_trig2.cmd_data2.byte5, pkt_adv_trig2.cmd_data2.byte6, pkt_adv_trig2.cmd_data2.byte7, pkt_adv_trig2.cmd_data2.byte8, pkt_adv_trig2.cmd_data2.byte9, pkt_adv_trig2.cmd_data2.byteA, pkt_adv_trig2.cmd_data2.byteB, pkt_adv_trig2.cmd_data2.byteC, pkt_adv_trig2.cmd_data2.byteD, pkt_adv_trig2.cmd_data2.byteE, pkt_adv_trig2.cmd_data2.byteF, pkt_adv_trig2.cmd_data_mask2.byte0, pkt_adv_trig2.cmd_data_mask2.byte1, pkt_adv_trig2.cmd_data_mask2.byte2, pkt_adv_trig2.cmd_data_mask2.byte3, pkt_adv_trig2.cmd_data_mask2.byte4, pkt_adv_trig2.cmd_data_mask2.byte5, pkt_adv_trig2.cmd_data_mask2.byte6, pkt_adv_trig2.cmd_data_mask2.byte7, pkt_adv_trig2.cmd_data_mask2.byte8, pkt_adv_trig2.cmd_data_mask2.byte9, pkt_adv_trig2.cmd_data_mask2.byteA, pkt_adv_trig2.cmd_data_mask2.byteB, pkt_adv_trig2.cmd_data_mask2.byteC, pkt_adv_trig2.cmd_data_mask2.byteD, pkt_adv_trig2.cmd_data_mask2.byteE, pkt_adv_trig2.cmd_data_mask2.byteF, pkt_adv_trig2.trg_pin_req, pkt_adv_trig2.trg_pin_req_polarity, pkt_adv_trig2.trg_pin_req_direction, pkt_adv_trig2.trg_pin_cmpl0, pkt_adv_trig2.trg_pin_cmpl0_polarity, pkt_adv_trig2.trg_pin_cmpl0_direction, pkt_adv_trig2.trg_pin_cmpl1, pkt_adv_trig2.trg_pin_cmpl1_polarity, pkt_adv_trig2.trg_pin_cmpl1_direction, pkt_adv_trig2.trg_pin_cmpl2, pkt_adv_trig2.trg_pin_cmpl2_polarity, pkt_adv_trig2.trg_pin_cmpl2_direction, pkt_adv_trig2.cmd_byte2_enable, pkt_adv_trig2.cmd_cyc2_enable, pkt_adv_trig2.cmd_tag2_enable, pkt_adv_trig2.cmd_len2_enable, pkt_adv_trig2.cmd_addr2_enable, pkt_adv_trig2.cmd_data2_enable, pkt_adv_trig2.succ_cmpl_enable, pkt_adv_trig2.unsucc_cmpl_enable, pkt_adv_trig2.trg_pin_req_enable, pkt_adv_trig2.trg_pin_cmpl0_enable, pkt_adv_trig2.trg_pin_cmpl1_enable, pkt_adv_trig2.trg_pin_cmpl2_enable)
    # pkt_adv_trig_error pre-processing
    c_pkt_adv_trig_error = None
    if pkt_adv_trig_error != None:
        c_pkt_adv_trig_error = (pkt_adv_trig_error.err_code, pkt_adv_trig_error.err_code_enable)
    # Call API function
    return api.py_pa_espi_adv_trig_config(conn, slave_id, c_pkt_adv_trig1_level1, c_pkt_adv_trig1_level2, c_pkt_adv_trig1_level3, c_pkt_adv_trig1_level4, c_pkt_adv_trig2, c_pkt_adv_trig_error)


