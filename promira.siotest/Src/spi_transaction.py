def spi_master_cmd (self, cmd_spec, xfer_array=None):
    
#    xfer_length=cmd_spec[self.SPISPEC_LENITEM][self.SPISPEC_XFERLEN_SUBITEM]
#    xfer_type=cmd_spec[self.SPISPEC_XFERTYPE_SUBITEM]


    # if xfer_length!=0 then xfer_type!=NONE
    # if xfer_array=None then xfer_type != OUTPUT 
    # if xfer_array!=None then xfer_length == len(xfer_array)
    # type length arraydef

    # SPI COMMAND MODE DATA HAS THESE ELEMENTS
    # SPI/SQI/SQX(BOTH) MODE
    # COUNT OF ADDRESS TRANSACTION CYCLES (ADDRESS BYTES WRITTEN TO DEVICE)
    # COUNT OF DUMMY TRANSACTION CYCLES (DON'T CARE BYTE WRITTEN TO DEVICE)
    # COUNT OF DATA TRANSACTION CYCLES (DATA EXCHANGED WITH DEVICE) ***
    # *** ON READ COMMANDS THE INCOMING DATA IS RELEVANT, OUTGOING IS DON'T CARE
    # *** ON WRITE COMMANDS THE OUTGOING DATA IS RELEVANT, INCOMING IS DON'T CARE
    # *** COMMANDS WHERE MEANINGFUL DATA IS OUTPUT *AND* INPUT IS POSSIBLE, BUT 
    #     NOT DEFINED FOR THIS EEPROM COMMAND SET

    # Insure no bush-league errors in command specification    
    if  ( (xfer_length==0 and (xfer_array!=None or xfer_type!=self.SPISPEC_XFERTYPE_NONE)) 
          or (xfer_array==None and xfer_type==self.SPISPEC_XFERTYPE_OUTPUT)
          or (xfer_length>0 and xfer_array!=None and xfer_length!=len(xfer_array))
        ):
      print("spi_master_cmd_error: command specification error")
      exit(-1)
      
    
    # provide for input array when add_implicit_resolver
    data_in=promira.array_u08(xfer_length+1)
      
    # at this point:
    #   xfer_array is defined if we have data to send or receive after the command

    data_out=promira.array('B', cmd_spec[self.SPISPEC_CMDBYTE])
    if xfer_type==self.SPISPEC_XFERTYPE_OUTPUT:
      data_out+=xfer_array
    else:
      data_out+=data_in


    # Write length+3 bytes for data plus command and 2 address bytes
    (xfer_retcode, data_in) = promira.aa_spi_write(self.m_Aardvark, data_out, data_in)

    data_in=data_in[1:]
    if (len(data_in)!=xfer_length):
      print("spi_master_cmd_error: byte transfer count over/under-flow")
      exit(-1)
      
    return (len(data_in), data_in)
      
    