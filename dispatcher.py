import sys
import threading
import time
from datetime import datetime, timezone, timedelta
from struct import unpack
#import binascii
import re
#import xml.etree.ElementTree as ET

import shproto
import shproto.port


nano = None

def start(sn=None):
	global nano
	nano = shproto.port.connectdevice(sn)
	if not nano:
		print("could not connect")
		sys.exit(0)

def stop():
	global nano
	nano.close()

def sendCommand(command):
	global nano
	print("Send command: {}".format(command))
	tx_packet = shproto.packet()
	tx_packet.start()
	for i in range(len(command)):
		tx_packet.add(ord(command[i]))
	tx_packet.stop()
	nano.write(tx_packet.payload)

def readDevice():
	global nano
	timeOut=5
	delay=0.1
	READ_BUFFER = 1
	rx_byte_arr=[]
	t=0
	time.sleep(delay)
	while not((t>timeOut)or(nano.in_waiting> 0)):
		time.sleep(delay)
		t+=1
		sys.stdout.write(".")
		sys.stdout.flush()
	if (t>timeOut):
		return rx_byte_arr
	READ_BUFFER = nano.in_waiting
	try:
		with threading.Lock():
			rx_byte_arr = bytearray(nano.read(size=READ_BUFFER))
	except serial.SerialException as e:
		print("SerialException:%s\n",e)

	return rx_byte_arr

"""
		for rx_byte in rx_byte_arr:
			response.read(rx_byte)
			if response.dropped:
				shproto.dispatcher.dropped += 1
				shproto.dispatcher.total_pkts += 1
			if not response.ready:
				continue
			shproto.dispatcher.total_pkts += 1
			print("received: cmd:{}\tpayload: {}".format(response.cmd, response.payload))
			response.clear()
"""
