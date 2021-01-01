#!/bin/bash

# Launch Notes: @honea on 12/31/2020
#
# "promira_test.py" is the spi-clock frequency sweeping test of
# a SPI EEPROM.
#
# These steps are necessary to launch "promira_test.py"
# 1. Set the PYTHONPATH to include the program source
# 2. Set the PYTHONPATH to include the Totalphase libraries for Promira/Aardvark
# 3. Launch the app with Python v3, and with super-user rights.

# If you launch without sudo, the "keyboard" moduld becomes inaccessible
# and the program will fail.


export  PYTHONPATH=$PYTHONPATH:~/repo/haven-main/software/tools/pytests/promira.siotest/Src
export  PYTHONPATH=$PYTHONPATH:~/repo/haven-main/software/tools/pytests/promira.siotest/SerialPlatformAPI_Promact_IS
sudo python3 promira_test.py

