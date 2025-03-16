import serial
import serial.tools.list_ports
import re
import os

port_speed = 9600


def getallports():
    allports = serial.tools.list_ports.comports()
    nanoports = []
    for port in allports:
        if port.manufacturer == "FTDI" or re.search("^/dev/ttyUSB.*", port.device):
            # print("getallports: {}".format(port.device))
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
    for port in allports:
        portsastext.append([port.serial_number, port.device])
        # print("getallportsastext: port: {} {} {}".format(port, port.serial_number, port.device));
    return portsastext


def getportbyserialnumber(sn):
    allports = getallports()
    for port in allports:
        if port.serial_number == sn:
            return port
    return None


def getdevicebyserialnumber(sn):
    port = getportbyserialnumber(sn)
    if port is None:
        if re.match("^/", sn) and os.path.exists(sn):
            return sn
        return None
    else:
        return getportbyserialnumber(sn).device


def connectdevice(sn=None):
    nanoport=None
    if sn is None and len(getallports()) > 0:
        ports = getallports()[0]
        nanoport = ports.device
#    else:
#        nanoport = getdevicebyserialnumber(sn)
    if nanoport is None:
        print("!!! Error. Could not find FTDI device: WaveShare USB<->RS485 device.")
        exit(0)
    print("Connected to:\n\tport {}\n\tspeed {}\n\tmanufacturer {}\n\tserial number {}".format(nanoport, port_speed,ports.manufacturer,ports.serial_number))
    tty = serial.Serial(nanoport, baudrate=port_speed, bytesize=8, parity='N', stopbits=1, timeout=0.1)
    return tty
