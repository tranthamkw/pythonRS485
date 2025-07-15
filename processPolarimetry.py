
#mcamain.py
import sys
import time
import re
import os
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
	print(stepsPerRev)
	print(ds)
	print(n)

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


for j in range(n):
	print("{}\t{}".format(angle[j],signal[j]))


os._exit(0)
