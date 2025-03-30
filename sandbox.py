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
import SRSinstruments
#import usbRS485bridge
#import port
#import globalVars

import interface.rs485Devices


SRS830 = 0xC5
SRS530 = 0xCA
SRS335 = 0xC0

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
myvolts = 12.1
Sorensen.setSorensen120Volts(SORENSENRS485, SORENSENGPIB, myvolts)

time.sleep(0.1)
print("Read Sorensen")

z=Sorensen.getSorensen120Volts(SORENSENRS485, SORENSENGPIB)
print("Volts set to {}".format(z))

z=Sorensen.getSorensen120Amps(SORENSENRS485, SORENSENGPIB)
print("Iout {}".format(z))


print("Testing SRS530 analog output function X6. Ten settings from 3.0 to 3.09 in increments of 0.01")
for j in range(10):
	outvolts=3.0+float(j)/100.0
	SRSinstruments.setSRS530AD(SRS530,6,outvolts)
	time.sleep(0.2)
	z = SRSinstruments.getSRS530AD(SRS530,6)
	print("{}\t{} Volts".format(j,z))
	time.sleep(0.2)


print("OK")

interface.rs485Devices.stop()
os._exit(0)
