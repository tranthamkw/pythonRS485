#mcamain.py
import sys
import time
import re
import argparse
import os

import interface.rs485Devices
import SRSinstruments
import fileIO
SRS830 = 0xC6
SRS530 = 0xC5

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
parser.add_argument('comment',type=str,help='comment')

args = parser.parse_args()
startf = args.startf
endf = args.endf
stepf = args.stepf
comment=args.comment




numloops = int((endf-startf)/stepf)+2
if numloops < 1:
	print("num loops too small or startf<endf")
	exit(-1)

filename = fileIO.calculateFilename('SCAN_SRS335_')

r=0.0
phi=0.0
f=0.0

interface.rs485Devices.init()

time.sleep(0.1)

print("Setting timeout")
#interface.rs485Devices.setRS485BridgeTimeout(SRS335,380)
time.sleep(0.2)
interface.rs485Devices.setRS485BridgeTimeout(SRS830,200)
time.sleep(0.2)
interface.rs485Devices.setRS485BridgeTimeout(SRS530,200)
time.sleep(0.2)





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
	f.write(comment)
	f.write("\nsetf,x1,x2,r1,phi1,f1,r2,phi2,f2\n")
	k=0
	print("setf\tx1\tx2\tr1\tphi1\tf1\tr2\tphi2\tf2\n")
	while k<numloops:
		setf = startf + float(k)*stepf
		SRSinstruments.setSRS335Freq(SRS335,setf)
		time.sleep(1.5)
		myf=SRSinstruments.getSRS335Freq(SRS335)
		time.sleep(0.1)
		r1,phi1,f1 = SRSinstruments.getSRS830Data(SRS830)
		time.sleep(0.1)
		r2,phi2,f2 = SRSinstruments.getSRS530Data(SRS530)
		time.sleep(0.1)
		x1,x2,x3,x4 = SRSinstruments.getSRS830AuxIn(SRS830)
		print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(setf,x1,x2,r1,phi1,f1,r2,phi2,f2))
		f.write("{},{},{},{},{},{},{},{},{}\n".format(setf,x1,x2,r1,phi1,f1,r2,phi2,f2))
		time.sleep(0.1)
		k+=1


print("OK")

interface.rs485Devices.stop()

os._exit(0)
