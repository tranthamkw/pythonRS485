#mcamain.py
import sys
import time
import re
import os
import argparse
import interface.rs485Devices

DELAY=0
DIGIDEVICE=0xD9


# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


parser = argparse.ArgumentParser(
        prog='scanSEE',
        description='Scans KEPCO power supply from start to stop potential',
        epilog="e.g. python scanSEE.py <start v> <end v> <step v>")
parser.add_argument('steps',type=int,help='numsteps')
parser.add_argument('dir', type=int, help='start volts')
parser.add_argument('spd',type=int,help='speed')

args = parser.parse_args()
steps=args.steps
x = args.dir
spd=args.spd

z=0
interface.rs485Devices.init()


interface.rs485Devices.setRS485StepperMotorSpeed(DIGIDEVICE,spd)

time.sleep(0.05)
spr=interface.rs485Devices.getRS485StepperMotorStepsRev(DIGIDEVICE)

interface.rs485Devices.moveRS485StepperMotor(DIGIDEVICE,steps,x)

steps=interface.rs485Devices.getRS485StepperMotorSteps(DIGIDEVICE)

while (steps>0):
	print(steps)
	steps=interface.rs485Devices.getRS485StepperMotorSteps(DIGIDEVICE)



print("OK")
interface.rs485Devices.stop()
os._exit(0)
