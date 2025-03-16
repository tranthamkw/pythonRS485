import sys
import time
#import serial
#import port
#import logging
#import packet
import os
import re
from datetime import datetime

def calculateFilename(prefix):
	filename=""
	file=""
	data_directory  = "/home/pi/data/"
	if not os.path.exists(data_directory):
		print("path does not exist")
		os._exit(-1)
	t1=time.time()
	end_time = datetime.fromtimestamp(t1)
	dir_ext = "{}/".format(end_time.strftime("%Y-%m-%d"))
	file="{}{}.csv".format(prefix,end_time.strftime("%Y-%m-%d_%H%M%S"))
	data_directory = data_directory+dir_ext
	if not os.path.exists(data_directory):
		os.makedirs(data_directory)
	filename=data_directory+file
	return filename
