"""
copy from enocean
"""
import logging
import voluptuous as vol
import time

from homeassistant.const import CONF_DEVICE
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import track_time_interval
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'linptech_dongle'

LINPTECH_DONGLE = None
global restartnum
restartnum = 0
TIME_BETWEEN_UPDATES=timedelta(seconds=300)

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
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	def __init__(self, hass, ser):
		"""Initialize the Linptech dongle."""
		self._serial = LinptechSerial(port=ser,receive=self.receive)
		self._serial.start()
		self._devices = []
		self.hass=hass
		track_time_interval(self.hass,self.update_devices_state, TIME_BETWEEN_UPDATES)


	def register_device(self, dev):
		"""Register another device."""
		self._devices.append(dev)

	def send_command(self, packet):
		"""Send a command from the Linptech dongle."""
		self._serial.send(packet)
	
	def update_devices_state(self,now):
		"""send query command,get lights state"""
		if self._devices:
			for device in self._devices:
				device.get_state()

	def receive(self,packet):
		if packet:
			self.logger.info("receive_packet=%s",packet)
			for device in self._devices:
				index = packet.find((device.dev_id+device.type).lower())
				if index>0:
					state=packet[index+10:index+16]
					print(int(state[-1]))
					device.value_changed(int(state[-1]))

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

	# get command from linptech dongle
	def send_command(self, command):
		"""send a command via the linptech dongle."""
		packet = self.packet(command)
		LINPTECH_DONGLE.send_command(packet)

	# linptech packet protocol
	def packet(self, command):
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
			data = binascii.unhexlify(bytes(data, "UTF-8"))
			crc = 0
			for i in range(len(data)):
				crc = CRC8_TABLE[crc ^ data[i]]
				crc &= 0xff
			crc = hex(crc & 0xff)[2:]
			if len(crc) == 1:
				crc = "0"+crc
			if len(crc) == 0:
				crc = "00"
			return crc

		command_len = "{0:>02}".format(hex(int(len(command)/2))[2:])
		m1 = "00"+command_len+"0701"
		m2 = command+7*"00"
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
try:
	import queue
except ImportError:
	import Queue as queue



class LinptechSerial(threading.Thread):
	"""
	- 实例化线程进行串口发送和读取
	transmit_queue 发送指令队列
	receive_queue 接收指令队列
	
	"""
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	def __init__(self, port, receive):
		super(LinptechSerial, self).__init__()
		self.stop_flag = threading.Event()
		self.buffer = ""
		# Setup packet queues
		self.transmit_queue = queue.Queue()
		self.receive_queue = queue.Queue()
		# Set the callback method，对外接口，接收指令
		self.receive = receive
		# Internal variable for the Base ID of the module.
		self.base_id = None
		self.restartnum = restartnum
		self.start_end_time = []
		self.port = port
		self.ser = serial.Serial(port, 57600, timeout=0.1)

	def stop(self):
		self.stop_flag.set()
	
	def rerun(self):
		self.restartnum += 1
		print("串口异常，重启次数：", self.restartnum)
		if self.restartnum == 1 or self.restartnum == 11:
			self.start_end_time.append(time.localtime(time.time()))
		# if self.restartnum > 10:
		# 	print("串口太不稳定了，请检查！！！", self.start_end_time)
		# 	self.stop_flag.set()
		# 	return 
		self.stop_flag.set()
		self.stop_flag.clear()
		self.run()
	
	def restartserial(self):
		time.sleep(5)
		self.ser = serial.Serial(self.port, 57600, timeout=0.1)

	def send(self, packet):
		"对外接口，发送指令"
		self.transmit_queue.put(packet)
		self.logger.debug("transmit_queue=%s" % self.transmit_queue.qsize())
		return True
	
	def get_from_send_queue(self):
		''' Get message from send queue, if one exists '''
		try:
			packet = self.transmit_queue.get(block=False)
			return packet
		except queue.Empty:
			pass
		return None

	def get_from_receive_queue(self):
		''' Parses messages and puts them to receive queue '''
		# Loop while we get new messages
		while self.receive_queue.qsize()>0:
			try:
				self.logger.debug("receive_queue=%s" % self.receive_queue.qsize())
				packet=self.receive_queue.get()
				self.receive(packet)
			except queue.Empty:
				pass

	def run(self):
		self.logger.info('LinptechSerial started')
		while not self.stop_flag.is_set():
			try:
				try:
					number = self.ser.inWaiting()
				except:
					self.restartserial()
					number = self.ser.inWaiting()
					print("gggggggggggggggggggggggggggggggggg"*2, number)
					pass
				if number > 20:
					self.logger.debug("numner=%s" % number)
					self.buffer += str(binascii.b2a_hex(self.ser.read(number)),encoding="utf-8")
					self.logger.debug("buffer=%s" % self.buffer)
					self.ser.flushInput()
					if self.buffer.startswith("55"):
						self.receive_queue.put(self.buffer)
					self.buffer=""
			except serial.SerialException:
				self.logger.error('Serial port exception! (device disconnected or multiple access on port?)')
				self.rerun()
			self.get_from_receive_queue()

			# If there's messages in transmit queue
			# send them
			packet = self.get_from_send_queue()
			if packet:
				try:
					self.logger.info("send_packet=%s",packet)
					self.ser.write(binascii.unhexlify(packet))
				except serial.SerialException:
					self.stop()			
			time.sleep(0.04)