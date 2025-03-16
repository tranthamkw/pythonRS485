# usbRS485bridge
import sys
import time
import port
import serial
#import os
import threading

TIMEOUT=30
BASEREGANLG= 0x0D0D
BASEREGSERVO= 0x0A0A
BASEREG485BRIDGE232= 0x0C0C
BASEREGSTEPMTR= 0x0B0B
BASEREGFN= 0x00F0

#
# interface layer with a "waveshare" industrial USB<-->RS485 device
# https://www.amazon.com/dp/B081MB6PN2
#
#
#	+-------+
#	|RasPi	|
#	|	|>>[WaveShare USB-RS485]--------+-------[RS485Device,address xx]
#	|	|				|
#	+-------+				|
#						+-------[RS485Device,address yy]
#						|
#						|
#						+-------[RS485-232Bridge,address zz]----[Instrument RS232]
#						|
#						|
#						+-------[RS485-GPIBBridge,address xy]---[Instrument GPIB address aa]
#						|
#						|
#						+ up to 16 RS485 devices

bridge = None

crc16table = (
0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040 )

# Function to calculate CRC16 checksum
def crc16(crc, ch):
        crc = (crc >> 8) ^ crc16table[(crc ^ ch) & 0xFF]
        return (crc & 0xFFFF)

def crc16bytes(crc, st):
        for ch in st:
                crc = (crc >> 8) ^ crc16table[(crc ^ ch) & 0xFF]
        return crc

def validateRTU(buff):
	# /* len is the full length of the buffer.  The last two elements in the array
	#  are assumed to be  CRC bytes.
	length=len(buff)

	temp=0
	j=False
	if (length>3):
		temp=((buff[length-1]<<8)|(buff[length-2]))
		buff=buff[:-2]
		j=(temp==crc16bytes(0xFFFF,buff))
		#if true  // valid.yes.

	return j



def start(sn=None):
	global bridge
	try:
		with threading.Lock():
			bridge = port.connectdevice(sn)
	except serial.SerialException as e:
		print("SerialException:%s\n",e)
		print("could not connect to USB-RS485 bridge")
		sys.exit(0)

def stop():
	global bridge
	bridge.close()

def printmybyte(payload):
	for char in payload:
		sys.stdout.write(hex(char))
		sys.stdout.write(" ")
		sys.stdout.flush()
	sys.stdout.write("\n")
	sys.stdout.flush()


def write_Modbus_RTU(address, reg, writedata):
	global bridge
	cmd=[]
	temp=0

	cmd.append(address&0x00FF)  	#0
	cmd.append(0x06)		#1
	cmd.append((reg&0xFF00)>>8) #2 //MSB which register
	cmd.append(reg&0x00FF)  #3 //LSB which register 
	cmd.append((writedata & 0xFF00)>>8) #4// the next two bytes are the MSB and
	cmd.append(writedata & 0x00FF)  #5 // and LSB of the data to send
	temp=crc16bytes(0xFFFF, cmd)
	cmd.append(temp&0x00FF)  #  //before the LSByte
	cmd.append((temp&0xFF00)>>8)  #  //ensures that the MSByte is sent first as per Modbus

# debugging
#	sys.stdout.write("Tx:")
#	printmybyte(cmd)

	bridge.write(cmd)
	returndata=readDevice()
	z=-1 # // initialize an error variable.

	if len(returndata)>0:
		if(validateRTU(returndata)):
		# CRC valid.No transmission errors
		#// let make sure no machine/interpretation  errors
			if(cmd[0]==returndata[0]):   #  // then the corect machine responded
				if (returndata[1] & 0x80): #  // then an  error
					z=returndata[2] #  //in the event of an error this byte
					# // is sent by the machine  explaining the nature of the error
				else:
					z=0 #  // no errors. you're golden.
			else:
				print("Unexpected machine responded")
	else:
		print("no response from device at address {}".format(hex(address)))


	return z


def readDevice():
	global bridge

	#timeOut=5
	delay=0.25

	READ_BUFFER = 1
	rx_byte_arr=[]
	t=0
	time.sleep(delay)
	while not((t>TIMEOUT)or(bridge.in_waiting> 0)):
		time.sleep(delay)
		t+=1
#		sys.stdout.write(".")
#		sys.stdout.flush()
	if (t>TIMEOUT):
		return rx_byte_arr
	READ_BUFFER = bridge.in_waiting
	try:
		with threading.Lock():
			rx_byte_arr = bytearray(bridge.read(size=READ_BUFFER))
	except serial.SerialException as e:
		print("SerialException:%s\n",e)
# debugging
#	sys.stdout.write("Rx:  ")
#	printmybyte(rx_byte_arr)
	return rx_byte_arr


def write_Bridge_StringRTU(address, writestring):
	global bridge
# Writes an ascii command to a 485-232/GPIB bridge device. this routine DOES append a CR to data,
# which is a very common terminator character with RS232 ascii communications.
# 
# The bridge device is addressed, and data is written to a register.  The bridge strips this, and the CRC
# portions before passing on to the writestring to RS232/GPIB.

	cmd=[]
	temp=0
	reg=BASEREG485BRIDGE232+32
#	reg=3084+32
	cmd.append(address&0x00FF)  	#0
	cmd.append(0x06)		#1
	cmd.append((reg&0xFF00)>>8) #2 //MSB which register
	cmd.append(reg&0x00FF)  #3 //LSB which register 

	for j in range (len(writestring)):
		cmd.append(ord(writestring[j]) & 0x00FF)  # append the ascii number associated with each character of the string

	cmd.append(13) #append a CR
#	cmd.append(13) #TODO do we need two of them?

	temp=crc16bytes(0xFFFF, cmd) #calculate the CRC bytes

	cmd.append(temp&0x00FF)  #  //before the LSByte
	cmd.append((temp&0xFF00)>>8)  #  //ensures that the MSByte is sent first as per Modbus
# debugging
#	sys.stdout.write("Tx:")
#	printmybyte(cmd)

	bridge.write(cmd)
	rtnData=readDevice()

#	sys.stdout.write("Rx:")
#	printmybyte(rtnData)

	status=1
	returnData=[]
	if(len(rtnData)>0):
		if not (len(rtnData)==rtnData[2]+5):
			print("Unexpected number of return bytes")
			print("rtnData[2]= {}".format(rtnData[2]))
			print("len(rtnData)= {}".format(len(rtnData)))

		if(validateRTU(rtnData)):
			if (not (rtnData[1] & 0x80)):
				returnData=rtnData[3:-2]
				status=0
			else:
				status=rtnData[2]<<8|rtnData[3]
				print("writeRS232Bridge process returned error ")
		else:
			print("CRC bytes in response invalid")
	else:
		status=1;
		print("WriteBridge: No Response from bridge at RS485 address {}".format(hex(address)))

	return status,returnData



def read_Modbus_RTU(address,reg):
	"""
	   This layer packs together a Modbus style command to read messages. they 
	   are send to rs485 communication
	   any  returned data is placed in cnReturnData. 
	"""
	global bridge
	cmd=[]
	temp=0

	# build a Modbus RTU style command message to send 
	cmd.append(address&0x00FF)
	cmd.append(0x03) # //command to read register(s)
	cmd.append((reg&0xFF00)>>8)  #  //MSB which register
	cmd.append(reg&0x00FF) # //LSB which register  to start from
	cmd.append(0x00) # //MSB how many
	cmd.append(0x01) #//LSB how many registers to read...   just one, thank you very much

	temp = crc16bytes(0xFFFF,cmd)   # //calculate the crc bytes

	cmd.append(temp&0x00FF) # //before the LSByte
	cmd.append((temp&0xFF00)>>8) # //ensures that the MSByte is sent 
# debugging
#	sys.stdout.write("Tx:  ")
#	printmybyte(cmd)

	bridge.write(cmd)
	returndata=readDevice()

	z=-1	# //my way of recording errors
	tempint=[]
	if len(returndata)>0:
		if(validateRTU(returndata)):
		 # CRC valid
			if(returndata[0]==cmd[0]): # //  the correct machine responded
				if(returndata[1] & 0x80): #  an error occured
					z=(returndata[2]<<8)|returndata[3] #the nature of the error is returned here
					print("error returnded")
				else: # all good(see below)
					tempint=returndata[3:-2]
					z=0;
			else:
				print("\nRead RTU: unexpected machine responded")
		else:
			print("\nRead RTU: Invalid CRC")
	else:
		print("\nRead RTU no response from device at address {}".format(hex(address)))

	return z,tempint

"""
All good lets do something with the data.
The return structure looks like
byte0: echo address
byte1: echo command. If command is 03, then 03 is expected. However, if there is an error it will return 83
byte2: number of bytes of data to follow: n
byte3: data byte 0....
byte3+n: data byte n-1
byte 3+n+1: LSB of CRC
byte 3+n+2: MSB of CRC
"""
