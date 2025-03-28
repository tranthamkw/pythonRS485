
#mcamain.py
import sys
import time
import interface.port
import re
import os
# lists all USB accessable devices.  This program should be run first to determine which 
# USB device is to be used when accessing the RS485 bus.
# multiple USB devices may be present, so later programs will access the correct device by serial number



# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#
"""
usage:

python listports.py

note the output .  There will be a list of device serial numbers. This number needs to be 
inserted in the top of port.py as we will be connecing by serial

"""

myports=interface.port.getallportsastext()


os._exit(0)
