# pythonRS485

Interface between python and Ken's RS485 boards.  Boards include:

*) RS485<->GPIB bridge

*) RS485<->RS232 bridge

*) GP analog

*) GP digital

*) Dual Servo controller

*) Steppermotor

RUN FIRST:
run listports.py 

python listports.py

to get the serial number of the USB/RS485 'dongle'.  This serial number must be inserted in /interfacing/port/py before trying to run any of this. 

UTILITY scripts: 

python deviceID.py XX     where XX is the hexidecimal address of a board returns the boards' function. This is useful to establish your are communicating with the correct device.

python manualRS232.py XX "TEXT"
  where XX is the hex address of the RS485/232 bridge and TEXT is the text command to be sent to an instrument the board is connected to. This is useful if you want to build libraries for a new instrument. The "TEXT" value will be in the instrument's manual.  This is how the example libraries, e.g. SRSinstruments.py were constructed. 

python manualGPIB.py is similar

manualReadRTU.py and manualWriteRTU.py are advanced functions and normally would not be used by the casual user.

LIBRARY SCRIPTS:

interface/RS485devices.py. library for talking to di

SRSinstruments.py has code specific to addressing some SRS instruments.



