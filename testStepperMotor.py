#mcamain.py
import sys
import time
import re
import os
import argparse
import interface.rs485Devices

DELAY=0
DIGIDEVICE=0xD0
HOMESTATE=0

# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


parser = argparse.ArgumentParser(
        prog='testStepperMotor',
        description='manually move stepper motor',
        epilog="e.g. python testStepperMotor.py <steps> <dir> <speed>")
parser.add_argument('steps',type=int,help='numsteps')
parser.add_argument('dir', type=int, help='dir (0 or 1)')
parser.add_argument('spd',type=int,help='speed; try 50 to 100')

args = parser.parse_args()
requestSteps=args.steps
x = args.dir
spd=args.spd

z=0
interface.rs485Devices.init()

# initialize steppermotor driver device.  The following two calls
# only need to be called once at the begining
# of a program, or if one needs to change it on the fly.

# Call ONE: sets stepper motor speed
interface.rs485Devices.setRS485StepperMotorSpeed(DIGIDEVICE,spd)
time.sleep(0.05)

# CALL TWO: this set steps per revolution.  The default value is 100. The value
# will depend on the stepper motor, AND the gear-ratio to the final drive
# device (where the home sensor is). This is only needed if one intends to find home at somepoint.
# This setting is important for the homeing routine.  If the driver exceeds
# this number of steps whilst trying to find home, it will stop.
interface.rs485Devices.setRS485StepperMotorStepsRev(DIGIDEVICE,200)
time.sleep(0.05)


# lets find home
print("Finding home")
# first get home state
state=interface.rs485Devices.getRS485StepperMotorHomeState(DIGIDEVICE)
time.sleep(0.01)
print("Home state {}".format(state))
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

print("Starting home macro")
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


# Now lets make the requested move
print("making the requested move")
#this is all one needs to call for a steppermotor move.
interface.rs485Devices.moveRS485StepperMotor(DIGIDEVICE,requestSteps,x)
time.sleep(0.1)
# now check steps to see if we are done with the move.
# YOU DON'T HAVE TO DO THIS. one could sleep, process something else in the meantime, THEN check the status.
steps=interface.rs485Devices.getRS485StepperMotorSteps(DIGIDEVICE)
print("Number of steps to go before move complete")
time.sleep(0.01)
while (steps>0):
	print(steps)
	steps=interface.rs485Devices.getRS485StepperMotorSteps(DIGIDEVICE)
	time.sleep(0.01)


print("OK- move complete")
interface.rs485Devices.stop()
os._exit(0)
