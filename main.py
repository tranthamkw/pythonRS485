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

#import usbRS485bridge
import port
#import globalVars


# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


myports=port.getallportsastext()

for i in range(len(myports)):
	print(myports[i])



os._exit(0)
