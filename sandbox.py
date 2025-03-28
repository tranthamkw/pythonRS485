#mcamain.py
import sys
import time
#import serial
#import port
import re
#import packet
import os
#import threading
#from datetime import datetime
import KeithleyInstruments
import Sorensen
#import usbRS485bridge
#import port
#import globalVars

import interface.rs485Devices

K485GPIB=10
K485RS485=0xC3

SORENSENRS485=0xC9
SORENSENGPIB=0x0C

# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


z=0.0

interface.rs485Devices.init()


KeithleyInstruments.iniK485(K485RS485,K485GPIB)

z=KeithleyInstruments.readK485(K485RS485,K485GPIB)
print("read Keithley")
print("ammeter reading {}".format(z))

Sorensen.initSorensen120(SORENSENRS485, SORENSENGPIB)
print("Set Sorensen")
myvolts = 63.2
Sorensen.setSorensen120Volts(SORENSENRS485, SORENSENGPIB, myvolts)

time.sleep(0.1)
print("Read Sorensen")

z=Sorensen.getSorensen120Volts(SORENSENRS485, SORENSENGPIB)
print("Volts set to {}".format(z))

z=Sorensen.getSorensen120Amps(SORENSENRS485, SORENSENGPIB)
print("Iout {}".format(z))



print("OK")

interface.rs485Devices.stop()
os._exit(0)
