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




usbRS485bridge.start()
time.sleep(0.1)

print("Sending...")
y=usbRS485bridge.write_Modbus_RTU(0xA3, 0x03, 42)

print("return errors? (0=OK) {}".format(y))
time.sleep(0.1)


print("stop")
usbRS485bridge.stop()


os._exit(0)
