
#mcamain.py
import sys
import time
import re
import os
import math
import argparse
import interface.rs485Devices
import SRSinstruments
import KeithleyInstruments

import fileIO  # There is an 'automatic' file-namer, based on time of day. There MUST be a ~/data directory
# on the raspi


DIGIDEVICE=0xD0 # the steppermotor
SRS830 = 0xC5 #photodetector/amplfier -> SRS830 AD input 2

DELAY=0.2
#standard delay between calls to the rs485 buss
HOMESTATE=1
STEPSPERREV=1500

#STEPSPERREV / STEPSIZE must be an integer, otherwise we will rotate more than one rev

## these instruments need both the RS485bridge address, and , since GPIB is addressable, we have
## to set the appropriate GPIB address.
K485GPIB=10
K485RS485=0xC3


def calcFourier(inputx,inputy,numpts,dx,period,numr,m):
	sumCos=0.0
	sumSin=0.0
	k = 2.0*math.pi/float(period)
	for j in range(numpts):
		sumCos+=inputy[j]*math.cos(float(m)*k*inputx[j])*float(dx)
		sumSin+=inputy[j]*math.sin(float(m)*k*inputx[j])*float(dx)
	a=2.0*sumCos/float(numr*period)
	b=2.0*sumSin/float(numr*period)
	return a,b

def findHome(address,l,dx,hs):
	# first get home state
	state=interface.rs485Devices.getRS485StepperMotorHomeState(address)
	time.sleep(DELAY)
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
			time.sleep(DELAY)

	sys.stdout.write("\nSearching for home...")
	interface.rs485Devices.findHomeRS485StepperMotor(address,hs,1)
	time.sleep(DELAY)
	"""
	This next loop needs to have some error trapping.  IF the motor never 
	"""
	state=interface.rs485Devices.getRS485StepperMotorHomeState(address)
	time.sleep(DELAY)
	n=0
	while ((state!=hs)&(n<30)):
		sys.stdout.write(".")
		state=interface.rs485Devices.getRS485StepperMotorHomeState(address)
		time.sleep(DELAY)
		n+=1
		sys.stdout.flush()
	state=interface.rs485Devices.getRS485StepperMotorHomeState(address)
	time.sleep(DELAY)
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
parser.add_argument('stepsize', type=int, help='Polarimeter step size, ds. 1500/ds must be an integer')
parser.add_argument('numrev',type=int,help='number of revolutions')
parser.add_argument('dt',type=float,help='time to wait between data points for collection')
parser.add_argument('comment',type=str,help='useful comment')

args = parser.parse_args()
comment=args.comment
stepsize=args.stepsize
deltaT=args.dt
numrevs=args.numrev

interface.rs485Devices.init()
print("initialize steppermotor")
interface.rs485Devices.setRS485StepperMotorSpeed(DIGIDEVICE,100)
time.sleep(DELAY)
interface.rs485Devices.setRS485StepperMotorStepsRev(DIGIDEVICE,STEPSPERREV)
time.sleep(DELAY)



print("initalize K485")
KeithleyInstruments.iniK485(K485RS485,K485GPIB)
time.sleep(DELAY)

print("initialize RS830")
SRSinstruments.initSRS830(SRS830)
time.sleep(DELAY)

returnstring=SRSinstruments.get_ID(SRS830)
print("Found "+returnstring)

filename = fileIO.calculateFilename('OP_') #auto filename

# lets find home
print("Finding polarizer home")
findHome(DIGIDEVICE,STEPSPERREV,stepsize,HOMESTATE)

interface.rs485Devices.setRS485StepperMotorSpeed(DIGIDEVICE,20)
time.sleep(DELAY)


# take data
print("take data")
j=0
angle=[]
pmt=[]
volts1=[]

for j in range(0,numrevs*STEPSPERREV,stepsize):
	interface.rs485Devices.moveRS485StepperMotor(DIGIDEVICE,stepsize,0)
	time.sleep(deltaT)
# time to allow for signal to settle.
# get photometer reading.  the following is supposed to be faster than individual calls 
	x1,x2,x3,x4 = SRSinstruments.getSRS830AuxIn(SRS830)
	time.sleep(DELAY)

	if (x1==0):
		time.sleep(DELAY)
		x1,x2,x3,x4 = SRSinstruments.getSRS830AuxIn(SRS830)
	z=KeithleyInstruments.readK485(K485RS485,K485GPIB)
	if (z==0):
		time.sleep(DELAY)
		z=KeithleyInstruments.readK485(K485RS485,K485GPIB)

	time.sleep(DELAY)
	print("{}\t{}\t{}".format(j,z,x1))
	angle.append(j)
	pmt.append(z)
	volts1.append(x1)



n=len(pmt)
a2,b2=calcFourier(angle,pmt,n,stepsize,STEPSPERREV,numrevs,2)
a4,b4=calcFourier(angle,pmt,n,stepsize,STEPSPERREV,numrevs,4)
a0,b0=calcFourier(angle,pmt,n,stepsize,STEPSPERREV,numrevs,0)
print("Fourier coefficients an Cos(nkx) bn Sin(nkx)")
print("A0/2\t\tA2\t\tB2\t\tA4\t\tB4")
print("{:.4}\t{:.4}\t{:.4}\t{:.4}\t{:.4}".format(a0/2,a2,b2,a4,b4))

c2=math.sqrt(a2**2 + b2**2)
theta2=math.atan2(b2,a2)*180.0/math.pi
print("\nFourier coefficients cn Cos(nkx + thetan)")
print("A0/2\t\tC2\t\ttheta2")
print("{:.4}\t\t{:.4}\t\t{:.4}".format(a0/2,c2,theta2))

#calculate noise variance
variance = 0.0
k = 2.0*math.pi/float(STEPSPERREV)
for j in range(n):
	ffit=a0/2+a2*math.cos(2.0*k*angle[j])+b2*math.sin(2.0*k*angle[j])+a4*math.cos(4.0*k*angle[j])+b4*math.sin(4.0*k*angle[j])
	variance+=(pmt[j]-ffit)**2
variance = variance/float(n-5)
variance =math.sqrt(variance)
print("\n Variance = {:.5}".format(variance))

print("\n Variance/A0 = {:.5}".format(variance/a0))
print("Saving to file: {}".format(filename))

with open(filename,mode='w') as f:
	f.write("{}\n".format(filename))
	f.write("{}\n".format(comment))
	f.write("Steps per revolution,{}\n".format(STEPSPERREV))
	f.write("Step size,{}\n".format(stepsize))
	f.write("Num data points,{}\n".format(len(pmt)))
	f.write("Delay between data points,{}\n".format(deltaT))
	f.write("Fourier Coefficients\n")
	f.write("A0,A2,B2,A4,B4\n")
	f.write("{},{},{},{},{}\n".format(a0,a2,b2,a4,b4))
	f.write("Fourier coefficients cn Cos(nkx + theta_n)\n")
	f.write("A0/2,C2,theta2\n")
	f.write("{},{},{}\n".format(a0/2,c2,theta2))
	f.write("Variance,{}\n".format(variance))
	f.write("steps,intensity,voltsAD1\n")
	for j in range(len(pmt)):
		f.write("{},{},{}\n".format(angle[j],pmt[j],volts1[j]))

print("\nOK")
interface.rs485Devices.stop()

os._exit(0)
