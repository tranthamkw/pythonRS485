#mcamain.py
import sys
import time
import re
import argparse
import os

import rs485Devices
import SRSinstruments
import fileIO
SRS830 = 0xC5
SRS530 = 0xCA
SRS335 = 0xC0

#															#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#															#

parser = argparse.ArgumentParser(
	prog='scanSRS',
	description='Scans SRS335 function gen from start to stop frequency. Records data from SRS830&SRS530.',
	epilog="e.g. python scanSRS.py <start f> <end f> <step f>")
parser.add_argument('startf', type=float, help='start frequency')
parser.add_argument('endf', type=float, help='end frequency')
parser.add_argument('stepf',type = float, help='step frequency')

args = parser.parse_args()
startf = args.startf
endf = args.endf
stepf = args.stepf


numloops = int((endf-startf)/stepf)+2
if numloops < 1:
	print("num loops too small or startf<endf")
	exit(-1)

filename = fileIO.calculateFilename('SCAN_SRS335_')

r=0.0
phi=0.0
f=0.0

rs485Devices.init()
print("initializing RS830")
SRSinstruments.initSRS830(SRS830)
time.sleep(0.2)
returnstring=SRSinstruments.get_ID(SRS830)
print("Found "+returnstring)

print("\ninitializing RS530  (no id string available)")
SRSinstruments.initSRS530(SRS530)
time.sleep(0.2)
returnstring=SRSinstruments.get_ID(SRS335)
print("\nFound "+returnstring)


with open(filename,mode='w') as f:
	f.write("setf,actualf,r1,phi1,f1,r2,phi2,f2\n")
	k=0
	while k<numloops:
		setf = startf + float(k)*stepf
		SRSinstruments.setSRS335Freq(SRS335,setf)
		time.sleep(1)
		myf=SRSinstruments.getSRS335Freq(SRS335)
		r1,phi1,f1 = SRSinstruments.getSRS830Data(SRS830)
		time.sleep(0.2)
		r2,phi2,f2 = SRSinstruments.getSRS530Data(SRS530)
		print("{}\t{}\t{}\t{}\t\t{}\t{}\t{}".format(myf,r1,phi1,f1,r2,phi2,f2))
		f.write("{},{},{},{},{},{},{},{}\n".format(setf,myf,r1,phi1,f1,r2,phi2,f2))
		time.sleep(0.2)
		k+=1




print("OK")

rs485Devices.stop()

os._exit(0)
