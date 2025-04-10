import serial
import serial.tools.list_ports
import re
import os

port_speed = 9600  # this is required

SERIAL="B0013IWJ"
# the device serial number to use.  Run listports.py FIRST to determine the serial number of your device
# this is important if there are mulitple usb devices connected.


def getallports():
	allports = serial.tools.list_ports.comports()
	nanoports = []
	for port in allports:
		nanoports.append(port)
	return nanoports


def getallportssn():
    allports = getallports()
    portssn = []
    for port in allports:
        portssn.append(port.serial_number)
    return portssn


def getallportsastext():
	allports = getallports()
	portsastext = []
	print("Port\tSerial\tDevice")
	for port in allports:
		portsastext.append([port.serial_number, port.device])
		print("getallportsastext: port: {}\t{}\t{}".format(port, port.serial_number, port.device));
	return portsastext


def getportbyserialnumber(sn):
	allports = getallports()
	for port in allports:
		if re.search(sn,str(port.serial_number)):
			return port
	return None

def connectdevice(sn=None):
	nanoport=None
	if sn is None and len(getallports()) > 0:
		ports=getportbyserialnumber(SERIAL)
		if ports is not None:
			nanoport = ports.device
	if nanoport is None:
		print("!!! Error. Could not find FTDI USB<->RS485 device serial "+ SERIAL)
		exit(0)
	print("Connected to:\n\tport {}\n\tspeed {}\n\tmanufacturer {}\n\tserial number {}".format(nanoport, port_speed,ports.manufacturer,ports.serial_number))
	tty = serial.Serial(nanoport, baudrate=port_speed, bytesize=8, parity='N', stopbits=1, timeout=0.1)
	return tty
