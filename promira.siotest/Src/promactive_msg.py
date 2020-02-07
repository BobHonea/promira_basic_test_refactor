import promact_is_py as pmact
import collections 
import sys

class promactMessages:
  

      
  PROMACT_ERRORS=[  (pmact.PS_APP_OK, "ok" ), 
    (pmact.PS_APP_UNABLE_TO_LOAD_LIBRARY, "unable to load library" ),
    (pmact.PS_APP_UNABLE_TO_LOAD_DRIVER, "unable to load USB driver" ),
    (pmact.PS_APP_UNABLE_TO_LOAD_FUNCTION, "unable to load binding function" ),
    (pmact.PS_APP_INCOMPATIBLE_LIBRARY, "incompatible library version" ),
    (pmact.PS_APP_INCOMPATIBLE_DEVICE, "incompatible device version" ),
    (pmact.PS_APP_COMMUNICATION_ERROR, "communication error" ),
    (pmact.PS_APP_UNABLE_TO_OPEN, "unable to open device" ),
    (pmact.PS_APP_UNABLE_TO_CLOSE, "unable to close device" ),
    (pmact.PS_APP_INVALID_HANDLE, "invalid device handle" ),
    (pmact.PS_APP_CONFIG_ERROR, "configuration error" ),
    (pmact.PS_APP_MEMORY_ALLOC_ERROR, "unable to allocate memory" ),
    (pmact.PS_APP_UNABLE_TO_INIT_SUBSYSTEM, "unable to initialize subsystem" ),
    (pmact.PS_APP_INVALID_LICENSE, "invalid license" ),
    (pmact.PS_APP_PENDING_ASYNC_CMD, "pending respones to collect" ),
    (pmact.PS_APP_TIMEOUT, "timeout to collect a response" ),
    (pmact.PS_APP_CONNECTION_LOST, "connection lost" ),
    (pmact.PS_APP_CONNECTION_FULL, "too many connections" ),
    (pmact.PS_APP_QUEUE_FULL, "queue is full" ),
    (pmact.PS_APP_QUEUE_INVALID_CMD_TYPE, "invalid command to be added" ),
    (pmact.PS_APP_QUEUE_EMPTY, "no command to send" ),
    (pmact.PS_APP_NO_MORE_CMDS_TO_COLLECT, "no more response to collect" ),
    (pmact.PS_APP_UNKNOWN_CMD, "unknown response received" ),
    (pmact.PS_APP_MISMATCHED_CMD, "response doesn't match with the command" ),
    (pmact.PS_APP_UNKNOWN_CMD, "unknown command sent" ),
    (pmact.PS_APP_LOST_RESPONSE, "response queue in the device was full" ),
    (pmact.PS_I2C_NOT_AVAILABLE, "i2c feature not available" ),
    (pmact.PS_I2C_NOT_ENABLED, "i2c not enabled" ),
    (pmact.PS_I2C_READ_ERROR, "i2c read error" ),
    (pmact.PS_I2C_WRITE_ERROR, "i2c write error" ),
    (pmact.PS_I2C_SLAVE_BAD_CONFIG, "i2c slave enable bad config" ),
    (pmact.PS_I2C_SLAVE_READ_ERROR, "i2c slave read error" ),
    (pmact.PS_I2C_SLAVE_TIMEOUT, "i2c slave timeout" ),
    (pmact.PS_I2C_DROPPED_EXCESS_BYTES, "i2c slave dropped excess bytes" ),
    (pmact.PS_I2C_BUS_ALREADY_FREE, "i2c bus already free" ),
    (pmact.PS_SPI_NOT_AVAILABLE, "spi feature not available" ),
    (pmact.PS_SPI_NOT_ENABLED, "spi not enabled" ),
    (pmact.PS_SPI_WRITE_0_BYTES, "spi write 0 bytes" ),
    (pmact.PS_SPI_SLAVE_READ_ERROR, "spi slave read error" ),
    (pmact.PS_SPI_SLAVE_TIMEOUT, "spi slave timeout" ),
    (pmact.PS_SPI_DROPPED_EXCESS_BYTES, "spi slave dropped excess bytes" ) ]




  
  collectResponse=collections.namedtuple('collectResponse', 'code message')
  
  resp_i2cWrite=collectResponse(code=pmact.PS_I2C_CMD_WRITE, message="Response for ps_queue_i2c_write")
  resp_i2cRead=collectResponse(code=pmact.PS_I2C_CMD_READ, message="Response for ps_queue_i2c_read")
  resp_i2cDelay=collectResponse(code=pmact.PS_I2C_CMD_DELAY_MS, message="Response for ps_queue_delay_ms")
  resp_spiOE=collectResponse(code=pmact.PS_SPI_CMD_OE, message="Response for ps_queue_spi_oe")
  resp_spiSS=collectResponse(code=pmact.PS_SPI_CMD_SS, message="Response for ps_queue_spi_ss")
  resp_spiDelayCycles=collectResponse(code=pmact.PS_SPI_CMD_DELAY_CYCLES, message="Response for ps_queue_spi_delay_cycles")
  resp_spiDelayMS=collectResponse(code=pmact.PS_SPI_CMD_DELAY_MS, message="Response for ps_queue_delay_ms")
  resp_spiDelayNS=collectResponse(code=pmact.PS_SPI_CMD_DELAY_NS, message="Response for ps_queue_spi_delay_ns")
  resp_spiRead=collectResponse(code=pmact.PS_SPI_CMD_READ, message="Response for ps_queue_spi_write")
  resp_gpioDirection=collectResponse(code=pmact.PS_GPIO_CMD_DIRECTION, message="Response for ps_queue_gpio_direction")
  resp_gpioGet=collectResponse(code=pmact.PS_GPIO_CMD_GET, message="Response for ps_queue_gpio_get")
  resp_gpioSet=collectResponse(code=pmact.PS_GPIO_CMD_SET, message="Response for ps_queue_gpio_set")
  resp_gpioChange=collectResponse(code=pmact.PS_GPIO_CMD_CHANGE, message="Response for ps_queue_gpio_change")
  resp_gpioDelayMS=collectResponse(code=pmact.PS_GPIO_CMD_DELAY_MS, message="Response for ps_queue_delay_ms")
  resp_appNoMoreCmds=collectResponse(code=pmact.PS_APP_NO_MORE_CMDS_TO_COLLECT, message="Response nothing to collect")
  
  COLLECT_RESPONSE_MSG = [ resp_i2cWrite, resp_i2cRead, resp_i2cDelay,
                            resp_spiOE, resp_spiSS, resp_spiDelayCycles,
                            resp_spiDelayMS, resp_spiDelayNS, resp_spiRead,
                            resp_gpioDirection, resp_gpioGet, resp_gpioSet,
                            resp_gpioChange, resp_gpioDelayMS,
                            resp_appNoMoreCmds ]
  
  COLLECT_RESPONSES= [  pmact.PS_I2C_CMD_WRITE, pmact.PS_I2C_CMD_READ,
                        pmact.PS_I2C_CMD_DELAY_MS, pmact.PS_SPI_CMD_OE,
                        pmact.PS_SPI_CMD_SS, pmact.PS_SPI_CMD_DELAY_CYCLES,
                        pmact.PS_SPI_CMD_DELAY_MS, pmact.PS_SPI_CMD_DELAY_NS,
                        pmact.PS_SPI_CMD_READ, pmact.PS_GPIO_CMD_DIRECTION,
                        pmact.PS_GPIO_CMD_GET, pmact.PS_GPIO_CMD_SET,
                        pmact.PS_GPIO_CMD_CHANGE, pmact.PS_GPIO_CMD_DELAY_MS,
                        pmact.PS_APP_NO_MORE_CMDS_TO_COLLECT ]
  
  def __init_(self):
    pass

  def fatalError(self, reason):
    print("Fatal: "+reason)
    sys.exit()
    
    
  def apiIfError(self, result_code):
    if result_code == pmact.PS_APP_OK or result_code>0:
      return False 
    
    for error_id in self.PROMACT_ERRORS:
      if error_id[0] == result_code:
        print(error_id[1])
        return True
    
    print("unspecified API error")
    return True
  
  
    
  def appStatusString(self, app_status):
    return(pmact.ps_app_status_string(app_status))
  
  def resultString(self, result_code):
    for item in self.PROMACT_ERRORS:
      if item[0]==result_code:
        return item[1]

  def getResponseMessage(self, response):
    for colresp in self.COLLECT_RESPONSE_MSG:
      if colresp.code==response:
        return True, colresp.message
    return False, "collect response message not found"

  def showCollectResponseMsg(self, response):
    if response not in self.COLLECT_RESPONSES:
      self.fatalError("unknown collect response")

 
    found, message=self.getResponseMessage(response)
    print("Collect Response: "+message)
    
  pass
    