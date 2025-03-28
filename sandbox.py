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
#import usbRS485bridge
import port
#import globalVars
import rs485Devices

K485GPIB=10
K485RS485=0xC3

# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#
z=0.0



rs485Devices.init()


KeithleyInstruments.iniK485(K485RS485,K485GPIB)

z=KeithleyInstruments.readK485(K485RS485,K485GPIB)

print("ammeter reading {}".format(z))

print("OK")

rs485Devices.stop()
os._exit(0)
