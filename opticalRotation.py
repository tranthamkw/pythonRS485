
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


DIGIDEVICE=0xD0
SRS830 = 0xC5


DELAY=0.1
HOMESTATE=1
STEPSPERREV=1500
STEPSIZE=5
#STEPSPERREV / STEPSIZE must be an integer, otherwise we will rotate more than one rev

# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


parser = argparse.ArgumentParser(
        prog='opticalRotation',
        description='collect intensity data for a full rotation',
        epilog="e.g. python examplePolarimetry")
#parser.add_argument('steps',type=int,help='numsteps')
#parser.add_argument('dir', type=int, help='dir (0 or 1)')
#parser.add_argument('spd',type=int,help='speed; try 50 to 100')

#args = parser.parse_args()
#requestSteps=args.steps
#x = args.dir
#spd=args.spd

interface.rs485Devices.init()
print("initialize steppermotor")
interface.rs485Devices.setRS485StepperMotorSpeed(DIGIDEVICE,20)
time.sleep(0.01)
interface.rs485Devices.setRS485StepperMotorStepsRev(DIGIDEVICE,STEPSPERREV)
time.sleep(0.01)

#print("Setting RS232 timeout to 32")
#interface.rs485Devices.setRS485BridgeTimeout(SRS830,32)
#time.sleep(DELAY)

print("initialize RS830")
SRSinstruments.initSRS830(SRS830)
time.sleep(DELAY)

returnstring=SRSinstruments.get_ID(SRS830)
print("Found "+returnstring)
filename = fileIO.calculateFilename('OP_') #auto filename


# lets find home
print("Finding polarizer home")
# first get home state
state=interface.rs485Devices.getRS485StepperMotorHomeState(DIGIDEVICE)
time.sleep(0.01)
if (state==HOMESTATE):
	print("Already home. Reversing 50 steps")
	interface.rs485Devices.moveRS485StepperMotor(DIGIDEVICE,50,0)
	steps=interface.rs485Devices.getRS485StepperMotorSteps(DIGIDEVICE)
	#Dont move on until this move is complete
	while (steps>0):
		sys.stdout.write(".")
		sys.stdout.flush()
		steps=interface.rs485Devices.getRS485StepperMotorSteps(DIGIDEVICE)
		time.sleep(0.01)

print("\nStarting home macro")
interface.rs485Devices.findHomeRS485StepperMotor(DIGIDEVICE,HOMESTATE,1)
time.sleep(0.1)

"""
This next loop needs to have some error trapping.  IF the motor never 
finds home, or we're looking for the wrong state, or
the home-wiring connection gets broken, or TJG walks into the lab, or ....  this will go forever.

So i put Put a hard limit on the number of times we check
"""
state=interface.rs485Devices.getRS485StepperMotorHomeState(DIGIDEVICE)
time.sleep(0.01)
n=0
while ((state!=HOMESTATE)&(n<10)):
	sys.stdout.write(".")
	state=interface.rs485Devices.getRS485StepperMotorHomeState(DIGIDEVICE)
	time.sleep(0.01)
	n+=1
	sys.stdout.flush()

state=interface.rs485Devices.getRS485StepperMotorHomeState(DIGIDEVICE)
time.sleep(0.01)
if (state!=HOMESTATE):
	print("Homing error")
	exit(-1)
else:
	print("\n Found home")





j=0
print("Taking data. Saving to file: {}".format(filename))

with open(filename,mode='w') as f:
	f.write("steps,intensity\n")
	for j in range(0,STEPSPERREV,STEPSIZE):
		interface.rs485Devices.moveRS485StepperMotor(DIGIDEVICE,STEPSIZE,0)
		time.sleep(0.5)
#       the following is supposed to be faster than individual calls 
		x1,x2,x3,x4 = SRSinstruments.getSRS830AuxIn(SRS830)
		time.sleep(DELAY)
		print("{}\t{}".format(j,x1))
		f.write("{},{}\n".format(j,x1))


print("\nOK-")
interface.rs485Devices.stop()
os._exit(0)
