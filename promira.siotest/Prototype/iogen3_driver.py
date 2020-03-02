import numpy as np
import time as t
import serial
import serial.tools.list_ports
#import tkinter



# Used for instrument autodetect
INSTRUMENT_NAME = 'NucleusSerialEmulator'
DEBUG_ON = True


class GraDevice:
    (MAIN, SUB) = [1, 0]


class NucleusEmulator:

    # Holds the serial object to Nucleus
    inst = None

    def __init__(self, instr_addr=None, BAUDRATE = 921600, TIMEOUT=1):

        # Autofind instrument if no address provided
        if instr_addr is None:
            ports = serial.tools.list_ports.comports()

            # Iterate through list_resources and find one with the correct instrument name
            for portcandidate in ports:
                print(portcandidate.device + " " + portcandidate.description)
                try:
                    self.inst = serial.Serial(portcandidate.device, BAUDRATE, timeout=TIMEOUT)

                    # Return device to known good state
                    self.inst.write('?\r\n'.encode())
                    t.sleep(.1)
                    self.inst.read_all()

                    # Check if this is a Nucleus
                    self.inst.write('i\r\n'.encode())
                    result = self.inst.readline().decode("utf-8")
                    print('read the following: ')
                    print(result)
                    print("\n")
                    if result.__contains__('Nucleus Serial Emulator SW Rev'):

                        if result.__contains__('Nucleus Serial Emulator SW Rev1.1'):
                            print('Found Nucleus with current FW!')
                        else:
                            print('Found Nucleus with outdated firmware.')
                            print('To update Nucleus firmware please follow the instructions on go/nucleus_emulator')
                        self.clear_buffers()
                        break
                    else:
                        self.inst = None

                except:
                    print('Not that one, try next one!')
                    self.inst = None

        # If visa address is explicitly given, just use it
        else:

            try:
                self.inst = serial.Serial(instr_addr, BAUDRATE, timeout=TIMEOUT)
                self.inst.write('i\r\n'.encode())
                result = self.inst.readline().decode("utf-8")
                print('read the following: ' + result)
                # was'SW Rev0.1'.encode()
                if result.__contains__('Nucleus Serial Emulator SW Rev1.1'):
                    print('Found Nucleus!')
                else:
                    self.inst = None

            except:
                print('Error - the specified address didnt work')
                self.inst = None

        # Check if we found a valid
        if self.inst is None:
            print('Error - Instrument not found! You might try pressing the black reset button')
            raise Exception('Error - Instrument not found!')

    def query_io(self,msg_in,twait=0.2):
        self.inst.write(msg_in + b'\n')
        t.sleep(twait)
        rd_in = self.inst.read_all()
        print(rd_in.decode())
        return rd_in

    def io_help(self):
        self.query_io(b'?')

    def i2c_write(self, addr, packet_array):
        if self.inst is None:
            print('Error: instrument not initiated')
            return False
        else:
            self.clear_buffers()

            octets = hex(len(packet_array))[2:]
            write_packet = "iw " + to_bytes(octets,1) + " " + to_bytes(hex(addr)[2:],1)

            for packet_octet in packet_array:
                write_packet += " " + to_bytes(hex(packet_octet)[2:],1)

            if DEBUG_ON:
                print ('I2C writing: ' + write_packet)

            self.inst.write((write_packet + '\r\n').encode())

            reply = str(self.inst.read_all().decode("utf-8"))
            if DEBUG_ON:
                print(reply)

            if reply.__contains__('I2C wrote'):
                return True
            else:
                return False

    def i2c_read(self, octets, addr):
        if self.inst is None:
            print('Error: instrument not initiated')
            return False
        else:
            self.clear_buffers()

            write_packet = "ir " + to_bytes(hex(octets)[2:],1) + " " + to_bytes(hex(addr)[2:],1)
            self.inst.write((write_packet + '\r\n').encode())
            result_int = [0] * octets
            for i in range(0, octets):
                result = self.inst.readline().decode("utf-8")
                if result.__contains__('I2C read') and not result.__contains__('failed'):
                    result_int[i] = int(result.split(' ')[2], 16)
                else:
                    return False

            if DEBUG_ON is True:
                print(result_int)

            return result_int

    def i2c_write_reg(self, addr, reg, packet):
        if self.inst is None:
            print('Error: instrument not initiated')
            return False
        else:
            return self.i2c_write(addr, [reg] + packet)

    def i2c_read_reg(self, octets, addr, reg):
        if self.inst is None:
            print('Error: instrument not initiated')
            return False
        else:
            self.i2c_write(addr, [reg])
            result = self.i2c_read(octets, addr)
            if DEBUG_ON:
                print(result)
            return result

    def clear_buffers(self,twait=0.2):
        t.sleep(twait)
        self.inst.read_all()

    def close(self):
        if self.inst is not None:
            self.inst.close()

    def speedy_random_write_verify(self, main_or_sub, addr, value):
        self.speedy_random_write(main_or_sub, addr, value)
        if self.speedy_random_read(main_or_sub, addr) == value:
            return True
        else:
            return False

    def speedy_random_write(self, main_or_sub, addr, value):
        if self.inst is None:
            print('Error: instrument not initiated')
            return False
        else:
            #TODO 16b to 8b
            write_packet = "rw " + to_bytes(hex(main_or_sub)[2:], 1) + " " + to_bytes(hex(addr)[2:], 2) + " " + to_bytes(hex(value)[2:], 1)
            '''
            write_packet += str(hex((addr & 0xf00)>>8)).split("x")[1] + " "
            write_packet += str(hex(addr & 0xff)).split("x")[1]+ " "
            write_packet += str(hex(value & 0xff)).split("x")[1]
            '''

            self.clear_buffers()

            if DEBUG_ON:
                print('I2C writing: ' + write_packet)

            self.inst.write((write_packet + '\r\n').encode())

            reply = str(self.inst.readline().decode("utf-8"))
            if DEBUG_ON:
                print(reply)

            if reply.__contains__('Speedy RW') and reply.__contains__('succeeded'):
                return True
            else:
                return False

    def speedy_random_read(self, main_or_sub, addr):
        if self.inst is None:
            print('Error: instrument not initiated')
            return False
        else:
            self.clear_buffers()
            #TODO 16b to 8b
            write_packet = "rr " + to_bytes(hex(main_or_sub)[2:], 1) + " " + to_bytes(hex(addr)[2:], 2)
            '''
            write_packet += str(hex((addr & 0xf00)>>8)).split("x")[1] + " "
            write_packet += str(hex(addr & 0xff)).split("x")[1]
            '''
            self.inst.write((write_packet + '\r\n').encode())

            result = self.inst.readline().decode("utf-8")
            if result.__contains__('Speedy RR') and not result.__contains__('failed'):
                result_int = int(result.split(' ')[5], 16)
            else:
                return False

            if DEBUG_ON is True:
                print(result_int)

            return result_int


    def io_i(self):
        self.query_io(b'i')

    #out_mask is int
    def io_cf(self,out_mask):
        self.query_io(b'cf '+bytes(to_bytes(hex(out_mask)[2:],2),'utf8'))

    def io_rd(self):
        self.query_io(b'rd')

    #out_val is int
    def io_wo(self,out_val):
        self.query_io(b'wo '+bytes(to_bytes(hex(out_val)[2:],2),'utf8'))

    #alist is an int, tstamp float, out_val int
    def io_ai(self,alist,tstamp,out_val,fclk=80e6):
        out_val_b = bytes(to_bytes(hex(out_val)[2:],2),'utf8')
        tstamp_b = bytes(t_to_hex_counts(fclk,tstamp,4),'utf8')
        alist_b = bytes(to_bytes(hex(alist)[2:],1),'utf8')
        self.query_io(b'ai ' + alist_b + b' ' + tstamp_b + b' ' + out_val_b)

    #alist is int
    def io_c(self,alist):
        alist_b = bytes(to_bytes(hex(alist)[2:],1),'utf8')
        self.query_io(b'c ' + alist_b)

    #alist is int
    def io_s(self,alist):
        alist_b = bytes(to_bytes(hex(alist)[2:],1),'utf8')
        self.query_io(b's ' + alist_b)

    #pwl_tuples is list of tuples [(t0,val0),(t1,val1),(t2,val2)]
    def io_ai_pwl(self,alist,pwl_tuples,fclk=80e6,rst_io=0,twait=0.2):
        if rst_io:
            self.io_wo('0')
        self.io_c(alist)
        t.sleep(twait)
        for v in pwl_tuples:
            self.io_ai(alist,v[0],v[1],fclk=80e6)
            t.sleep(twait)

### FUNCTIONS NEEDED BY DRIVER, NOT INCLUDED IN DIVER ###
### DO NOT ADD TO NucleusEmulator CLASS ###

#Fits hex_in into bytes and adds spaces between bytes
def to_bytes(hex_in,bytes):
    hex_nibs = len(hex_in)
    if hex_nibs > bytes*2:
        print("Problem with " + hex_in)
        raise Exception('Hex requested exceeds ' + str(bytes) + ' bytes!')
    hex_new = hex_in
    for x in range(bytes*2 - hex_nibs):
        hex_new = '0' + hex_new

    f_hex = ''
    len_hex = len(hex_new)

    for x in range(len_hex):
        f_hex = hex_new[-1*(x+1)] + f_hex
        if (x != (len_hex-1)) and (x%2!=0):
            f_hex = ' ' + f_hex

    return f_hex

#Creates hex from amount of time desired
def t_to_hex_counts(fclk,t,bytes):
    counts = hex(int(t*fclk))[2::]
    return to_bytes(counts,bytes)

def pd_from_file(file_path=''):
    ### READ IN IO WRITER TABLE ###
    if not file_path:
        file_path = filedialog.askopenfilename()

    io_in = pd.read_csv(file_path, skiprows=1)
    return io_in

def pwl_from_file(pd_in):

    hdrs = list(pd_in.columns.values)

    ### DROP UNNAMED COLUMNS ###
    drop_list = []
    for x in hdrs:
        if 'Unnamed' in x:
            drop_list.append(x)
    pd_in = pd_in.drop(columns=drop_list)
    hdrs = list(pd_in.columns.values)

    ### REPLACE nan's WITH PREVIOUS VALUE ###
    for x in hdrs:
        for i,y in enumerate(pd_in[x]):
            if (y is None) or (y == ''):
                y = np.nan
            else:
                y = float(y)
            if np.isnan(y):
                pd_in[x][i] = pd_in[x][i-1]

    ### CONVERT COLUMNS OF 1's AND 0's TO HEX
    t_list = pd_in[hdrs[0]].to_list()
    hex_list = []
    for r in pd_in.iterrows():
        hex_list.append(int(''.join([str(int(x)) for x in r[1][1::]])[-1::-1],2))

    pwl_list = [(float(t_list[i]),x) for i,x in enumerate(hex_list)]
    return pwl_list




if __name__ == '__main__':
    print('Not for use as main! ... exiting!')
'''
    # For testing
    # dmm = NucleusEmulator()
    myins = NucleusEmulator()
    # myins.i2c_write('16', ['b8'])
    # myins.i2c_write(0x16, [0xb8])
    # print(myins.i2c_read(1, '16'))
    # sendln 'iw 03 6C AB D8 10'

    myins.speedy_random_write(0x163, 0xaa)
    myins.speedy_random_read(0x163)

    myins.i2c_write_reg(0x6c, 0xab, [0xd8, 0x10])
    myins.i2c_read_reg(1, 0x16, 0xb8)

    myins.close()

'''