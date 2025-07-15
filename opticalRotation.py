
#mcamain.py
import sys
import time
import re
import os
import argparse
import interface.rs485Devices
import SRSinstruments
import fileIO  # There is an 'automatic' file-namer, based on time of day. There MUST be a ~/data directory
# on the raspi


DIGIDEVICE=0xD0 # the steppermotor
SRS830 = 0xC5 #photodetector/amplfier -> SRS830 AD input 2


DELAY=0.05
#standard delay between calls to the rs485 buss
HOMESTATE=1
STEPSPERREV=1500
STEPSIZE=20

#STEPSPERREV / STEPSIZE must be an integer, otherwise we will rotate more than one rev

def findHome(address,l,dx,hs):
	# first get home state
	state=interface.rs485Devices.getRS485StepperMotorHomeState(address)
	time.sleep(0.02)
	if (state==hs):
		rx=int(l/20)
		print("Already home. Reversing {} steps".format(rx))
		interface.rs485Devices.moveRS485StepperMotor(address,rx,0)
		steps=interface.rs485Devices.getRS485StepperMotorSteps(address)
	#Dont move on until this move is complete
		while (steps>0):
			sys.stdout.write(".")
			sys.stdout.flush()
			steps=interface.rs485Devices.getRS485StepperMotorSteps(address)
			time.sleep(0.02)

	sys.stdout.write("\nSearching for home...")
	interface.rs485Devices.findHomeRS485StepperMotor(address,hs,1)
	time.sleep(0.02)
	"""
	This next loop needs to have some error trapping.  IF the motor never 
	"""
	state=interface.rs485Devices.getRS485StepperMotorHomeState(address)
	time.sleep(0.02)
	n=0
	while ((state!=hs)&(n<30)):
		sys.stdout.write(".")
		state=interface.rs485Devices.getRS485StepperMotorHomeState(address)
		time.sleep(0.02)
		n+=1
		sys.stdout.flush()
	state=interface.rs485Devices.getRS485StepperMotorHomeState(address)
	time.sleep(0.02)
	if (state!=hs):
		print("\nHoming error")
		exit(-1)
	else:
		print("\nFound home")



# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


parser = argparse.ArgumentParser(
        prog='opticalRotation',
        description='collect intensity data for a full rotation',
        epilog="e.g. python examplePolarimetry")
parser.add_argument('comment',type=str,help='useful comment')
#parser.add_argument('dir', type=int, help='dir (0 or 1)')
#parser.add_argument('spd',type=int,help='speed; try 50 to 100')

args = parser.parse_args()
comment=args.comment
#x = args.dir
#spd=args.spd

interface.rs485Devices.init()
print("initialize steppermotor")
interface.rs485Devices.setRS485StepperMotorSpeed(DIGIDEVICE,20)
time.sleep(DELAY)
interface.rs485Devices.setRS485StepperMotorStepsRev(DIGIDEVICE,STEPSPERREV)
time.sleep(DELAY)


print("initialize RS830")
SRSinstruments.initSRS830(SRS830)
time.sleep(DELAY)

returnstring=SRSinstruments.get_ID(SRS830)
print("Found "+returnstring)

filename = fileIO.calculateFilename('OP_') #auto filename

# lets find home
print("Finding polarizer home")
findHome(DIGIDEVICE,STEPSPERREV,STEPSIZE,HOMESTATE)


# take data
print("take data")
j=0
angle=[]
pmt=[]

for j in range(0,STEPSPERREV,STEPSIZE):
	interface.rs485Devices.moveRS485StepperMotor(DIGIDEVICE,STEPSIZE,0)
	time.sleep(0.5)
# time to allow for signal to settle.
# get photometer reading.  the following is supposed to be faster than individual calls 
	x1,x2,x3,x4 = SRSinstruments.getSRS830AuxIn(SRS830)
	time.sleep(DELAY)
	print("{}\t{}".format(j,x1))
	angle.append(j)
	pmt.append(x1)


print("Saving to file: {}".format(filename))

with open(filename,mode='w') as f:
	f.write("{}\n".format(filename))
	f.write("{}\n".format(comment))
	f.write("Steps per revolution,{}\n".format(STEPSPERREV))
	f.write("Step size,{}\n".format(STEPSIZE))
	f.write("Num data points,{}\n".format(len(pmt)))
	f.write("steps,intensity\n")
	for j in range(len(pmt)):
		f.write("{},{}\n".format(angle[j],pmt[j]))


print("\nOK-")
interface.rs485Devices.stop()
os._exit(0)
