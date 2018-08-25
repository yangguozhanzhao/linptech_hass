"""
copy from enocean
"""
import logging
import voluptuous as vol

from homeassistant.const import CONF_DEVICE
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'linptech_dongle'

LINPTECH_DONGLE = None

CONFIG_SCHEMA = vol.Schema({
	DOMAIN: vol.Schema({
		vol.Required(CONF_DEVICE): cv.string,
	}),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
	"""Set up the Linptech component."""
	global LINPTECH_DONGLE
	serial_dev = config[DOMAIN].get(CONF_DEVICE)
	LINPTECH_DONGLE = LinptechDongle(hass, serial_dev)
	return True

class LinptechDongle:
	"""Representation of an Linptech dongle:
	- register device
	- send_commmand
	- get command callback
	"""

	def __init__(self, hass, ser):
		"""Initialize the Linptech dongle."""
		self._serial = LinptechSerial(Port=ser)
		self._serial.start()
		self._devices = []

	def register_device(self, dev):
		"""Register another device."""
		self._devices.append(dev)

	def send_command(self, packet):
		"""Send a command from the Linptech dongle."""
		
		self._serial.write(packet)


class LinptechDevice():
	"""Parent class for all devices associated with the Linptech component.
	- send_commmand via linptech dongle
	"""

	def __init__(self):

		"""Initialize linptech device."""
		while not LINPTECH_DONGLE:
			import time
			time.sleep(0.5)
		LINPTECH_DONGLE.register_device(self)
		print("2"*20)

	# get command from linptech dongle
	def send_command(self, command):
		"""send a command via the linptech dongle."""
		packet = self.packet(command)
		LINPTECH_DONGLE.send_command(packet)
	
	# linptech packet protocol
	def packet(self,command):
		# crc8 校验
		def crc8(data):
			CRC8_TABLE = [	0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15,
			0x38, 0x3f, 0x36, 0x31, 0x24, 0x23, 0x2a, 0x2d,
			0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65,
			0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d,
			0xe0, 0xe7, 0xee, 0xe9, 0xfc, 0xfb, 0xf2, 0xf5,
			0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd,
			0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85,
			0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba, 0xbd,
			0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
			0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea,
			0xb7, 0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2,
			0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a,
			0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32,
			0x1f, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0d, 0x0a,
			0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42,
			0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a,
			0x89, 0x8e, 0x87, 0x80, 0x95, 0x92, 0x9b, 0x9c,
			0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
			0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec,
			0xc1, 0xc6, 0xcf, 0xc8, 0xdd, 0xda, 0xd3, 0xd4,
			0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c,
			0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44,
			0x19, 0x1e, 0x17, 0x10, 0x05, 0x02, 0x0b, 0x0c,
			0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34,
			0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b,
			0x76, 0x71, 0x78, 0x7f, 0x6a, 0x6d, 0x64, 0x63,
			0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
			0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13,
			0xae, 0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb,
			0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83,
			0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb,
			0xe6, 0xe1, 0xe8, 0xef, 0xfa, 0xfd, 0xf4, 0xf3]
			data = binascii.unhexlify(bytes(data,"UTF-8"))
			crc = 0
			for i in range(len(data)):
				crc=CRC8_TABLE[crc^data[i]]
				crc&=0xff
			crc=hex(crc&0xff)[2:]
			if len(crc)==1:
				crc="0"+crc
			if len(crc)==0:
				crc="00"
			return crc
		
		command_len="{0:>02}".format(hex(int(len(command)/2))[2:])
		m1="00"+command_len+"0701"
		m2=command+7*"00"
		return "55"+m1+crc8(m1)+m2+crc8(m2)
		

		

##########################################################
# linptech 串口通讯部分代码
##########################################################

import sys
import threading
import time
import serial
import binascii
import logging


class LinptechSerial(object):
	def __init__(self, Port, BaudRate="57600", ByteSize="8", Parity="N", Stopbits="1"):
		self.l_serial = None
		self.alive = False
		self.port = Port
		self.baudrate = BaudRate
		self.bytesize = ByteSize
		self.parity = Parity
		self.stopbits = Stopbits
		self.thresholdValue = 16
		self.receive_data = ""
		
	def start(self):
		self.l_serial = serial.Serial()
		self.l_serial.port = self.port
		self.l_serial.baudrate = self.baudrate
		self.l_serial.bytesize = int(self.bytesize)
		self.l_serial.parity = self.parity
		self.l_serial.stopbits = int(self.stopbits)
		self.l_serial.timeout = 1
		self.l_serial.interCharTimeout = 0.3
		try:
			self.l_serial.open()
			if self.l_serial.isOpen():
				self.alive = True
		except Exception as e:
			self.alive = False
			logging.error(e)

	def stop(self):
		self.alive = False
		if self.l_serial.isOpen():
			self.l_serial.close()

	def read(self):
		while self.alive:
			try:
				number = self.l_serial.inWaiting()
				if number:
					self.receive_data += self.l_serial.read(number)
					if self.thresholdValue < len(self.receive_data):
						self.receive_data = ""
					else:
						self.receive_data = str(binascii.b2a_hex(self.receive_data))
						logging.info(self.receive_data)
			except Exception as e:
				logging.error(e)
	def write(self, data, isHex=True):
		if self.alive:
			if self.l_serial.isOpen():
				print("指令-》》》》》》》》》",data)
				if isHex:
					data = binascii.unhexlify(data)
				self.l_serial.write(data)


