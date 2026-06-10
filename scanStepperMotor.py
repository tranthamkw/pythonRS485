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
DIGIDEVICE=0xD7


#															#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#															#

parser = argparse.ArgumentParser(
	prog='scanSRS',
	description='Scans stepper motor from 0 nstep*dstep. Records data from SRS830&SRS530.',
	epilog="e.g. python scanStepperMotor.py <dstep> <nstep>")
parser.add_argument('dstep', type=int, help='stepsize')
parser.add_argument('nstep',type=int, help='nsteps')
parser.add_argument('comment',type=str,help='comment')

args = parser.parse_args()
dstep = args.dstep
nstep = args.nstep
comment=args.comment


filename = fileIO.calculateFilename('SCAN_StpMtr_')

r=0.0
phi=0.0
f=0.0

interface.rs485Devices.init()

print("Setting timeout to 120")
interface.rs485Devices.setRS485BridgeTimeout(SRS530,120)
time.sleep(0.2)
print("Setting timeout to 120")
interface.rs485Devices.setRS485BridgeTimeout(SRS830,120)
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

# initialize steppermotor driver device.  The following two calls
# only need to be called once at the begining
# of a program, or if one needs to change it on the fly.

# Call ONE: sets stepper motor speed
interface.rs485Devices.setRS485StepperMotorSpeed(DIGIDEVICE,80)
time.sleep(0.01)

# CALL TWO: this set steps per revolution.  The default value is 100. The value
# will depend on the stepper motor, AND the gear-ratio to the final drive
# device (where the home sensor is). This is only needed if one intends to find home at somepoint.
# This setting is important for the homeing routine.  If the driver exceeds
# this number of steps whilst trying to find home, it will stop.
interface.rs485Devices.setRS485StepperMotorStepsRev(DIGIDEVICE,600)
time.sleep(0.01)



with open(filename,mode='w') as f:
	f.write(comment)
	f.write("\nsteps,x1,x2,r1,phi1,f1,r2,phi2,f2\n")
	k=0
	print("steps\tx1\tx2\tr1\tphi1\tf1\tr2\tphi2\tf2\n")


#  x1 and x2 are the DC measurements of the photodetectors. x1 is the one on the stage. x2 is the normalization PD. 

	while k<nstep:

		# Now lets make the requested move
		interface.rs485Devices.moveRS485StepperMotor(DIGIDEVICE,dstep,0)
		time.sleep(0.01)
		# now check steps to see if we are done with the move.
		steps=interface.rs485Devices.getRS485StepperMotorSteps(DIGIDEVICE)
#		print("Number of steps to go before move complete")
		time.sleep(0.2)
		while (steps>0):
#			print(steps)
			steps=interface.rs485Devices.getRS485StepperMotorSteps(DIGIDEVICE)
			time.sleep(0.2)
#		print("OK- move complete")
		time.sleep(0.5) #wait a moment to make sure data is stable
		myf=SRSinstruments.getSRS335Freq(SRS335)
		time.sleep(0.02)
		r1,phi1,f1 = SRSinstruments.getSRS830Data(SRS830)
		time.sleep(0.02)
		x1,x2,x3,x4 = SRSinstruments.getSRS830AuxIn(SRS830)
		time.sleep(0.02)
		r2,phi2,f2 = SRSinstruments.getSRS530Data(SRS530)

		print("{}\t{:.2f}\t{:.2f}\t{:.4e}\t{:.1f}\t{:.2f}\t{:.4e}\t{:.2f}\t{:.2f}".format(k*dstep,x1,x2,r1,phi1,f1,r2,phi2,f2))
		f.write("{},{},{},{},{},{},{},{},{}\n".format(k*dstep,x1,x2,r1,phi1,f1,r2,phi2,f2))
		time.sleep(0.05)
		k+=1


print("OK- moving back to original position")

interface.rs485Devices.moveRS485StepperMotor(DIGIDEVICE,dstep*nstep,1)
		# now check steps to see if we are done with the move.
steps=interface.rs485Devices.getRS485StepperMotorSteps(DIGIDEVICE)
#print("Number of steps to go before move complete")
time.sleep(0.2)
while (steps>0):
	sys.stdout.write(".")
	sys.stdout.flush()
	steps=interface.rs485Devices.getRS485StepperMotorSteps(DIGIDEVICE)
	time.sleep(0.2)
sys.stdout.write("\n")
sys.stdout.flush()

print("OK- move complete")

interface.rs485Devices.stop()

os._exit(0)
