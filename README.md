# pythonRS485

Interface between python and Ken's RS485 boards.  Boards include:
*) RS485<->GPIB bridge
*) RS485<->RS232 bridge
*) GP analog
*) GP digital
*) Servo
*) steppermotor

Folder "interface" has lower level functions to talk to the RS485 bus.

Instrument python files, e.g. SRSinstruments.py has code specific to addressing these instruments through ken'sRS485buss and boards.


RUN FIRST:
run listports.py to get the serial number of the USB/RS485 'dongle'.  This serial number must be inserted in /interfacing/port/py before trying to run any of this. 
