from iogen3_driver.py import NucleusEmulator
import time

n64=NucleusEmulator("/dev/ttyACM0",921600)

packets = [
    [ 4, 0, 0, 0, 0],
    [ 4, 4, 4, 4, 4],
    [ 4, 0xc, 0xc, 0xc, 0xc],
    [ 4, 7, 7, 7, 7],
    [ 4, 0x81, 0x81, 0x81, 0x81 ],
    [ 4, 0xff, 0xff, 0xff, 0xff ]
    ]

target_address = 0x55

while True:
    for packet in packets:
        n64.i2c_write(target_address, packet)
        time.sleep(1)
        pass





