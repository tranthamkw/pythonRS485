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

import usbRS485bridge

#import globalVars


#															#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#															#




argc=len(argv)

if (argc==4):
	usbRS485bridge.start()
	time.sleep(0.1)

	print("Sending...")
	y=usbRS485bridge.write_Modbus_RTU(0xA3, 0x03, 42)

	print("return errors? (0=OK) {}".format(y))
	time.sleep(0.1)

	print("stop")
	usbRS485bridge.stop()

else:
	print("Usage: python manualRTU.py [RS485address] [register-of-device] [value-to-write]")
	print("e.g.")
	print("python")

os._exit(0)
