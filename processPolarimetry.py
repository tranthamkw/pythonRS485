
#mcamain.py
import sys
import time
import re
import os
import math
import argparse
# on the raspi


def getParameter(inputtext,searchtext):
	x=0
	if not re.search(searchtext,inputtext):
		print("unexpected line")
		exit(0)
	try:
		x=int(inputtext.split(",")[1])
	except ValueError:
		print("value error")
		exit(0)
	return x


def calcFourier(inputx,inputy,numpts,dx,period,m):
	sumCos=0.0
	sumSin=0.0
	k = 2.0*math.pi/float(period)
	for j in range(numpts):
		sumCos+=inputy[j]*math.cos(float(m)*k*inputx[j])*float(dx)
		sumSin+=inputy[j]*math.sin(float(m)*k*inputx[j])*float(dx)

	a=2.0*sumCos/float(period)
	b=2.0*sumSin/float(period)

	return a,b


# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


parser = argparse.ArgumentParser(
        prog='processPolarimetry',
        description='Determine Fourier coefficients a0 a2 b2 a4 b4',
        epilog="e.g. ")
parser.add_argument('filename',type=str,help='filename')

args = parser.parse_args()
filename=args.filename

with open(filename,mode='r') as f:
	line = f.readline()
	if not re.search(filename,line):
		print("invalid file")
		exit(0)
	comment = f.readline()
	print(comment)

	stepsPerRev = getParameter(f.readline(),"revolution")
	ds = getParameter(f.readline(),"Step size")
	n = getParameter(f.readline(),"data points")
#	print(stepsPerRev)
#	print(ds)
#	print(n)

	angle=[0.0 for x in range(n)]
	signal = [0.0 for x in range(n)]

	i=0
	line = f.readline() #this line should be "steps,intensity"
	line = f.readline()
	while (line and i<n):
		try:
			angle[i]=float(line.split(",")[0])
			signal[i]=float(line.split(",")[1])
			i+=1
		except ValueError:
			print("value error")
			exit(0)
		line=f.readline()


a2,b2=calcFourier(angle,signal,n,ds,stepsPerRev,2)
a4,b4=calcFourier(angle,signal,n,ds,stepsPerRev,4)
a0,b0=calcFourier(angle,signal,n,ds,stepsPerRev,0)

print("A0\t\tA2\t\tB2\t\tA4\t\tB4")
print("{:.4}\t{:.4}\t{:.4}\t{:.4}\t{:.4}".format(a0,a2,b2,a4,b4))

c2=math.sqrt(a2**2 + b2**2)
theta2=math.atan2(b2,a2)*180.0/math.pi

print("\nA0/2\t\tC2\t\ttheta2")
print("{:.4}\t{:.4}\t{:.4}".format(a0/2,c2,theta2))

os._exit(0)
