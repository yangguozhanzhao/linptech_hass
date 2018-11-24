
import logging
import voluptuous as vol
import time

from homeassistant.const import CONF_DEVICE
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import track_time_interval
from datetime import timedelta
from homeassistant.components.light import Light

REQUIREMENTS = ['linptech==0.1.7']
from linptech.serial_communicator import LinptechSerial

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'linptech_dongle'

LINPTECH_DONGLE = None
TIME_BETWEEN_UPDATES=timedelta(seconds=600)

logging.getLogger().setLevel(logging.ERROR)

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
		self._serial = LinptechSerial(port=ser,receive=self.receive)
		self._serial.setDaemon(True)
		self._serial.start()
		self._devices = []
		self._emitter = None
		self._emitteridlist = []
		self.hass=hass
		track_time_interval(self.hass,self.update_devices_state, TIME_BETWEEN_UPDATES)


	def register_device(self, dev):
		"""Register another device."""
		self._devices.append(dev)

	def register_emitter(self, dev):
		self._emitter = dev

	def send(self, data):
		"""Send a command from the Linptech dongle."""
		logging.info("data=%s" % data)
		try:
			self._serial.send(data)
		except :
			print("dongle send error")
			pass
		

	def update_devices_state(self,now):
		"""send query command,get lights state"""
		if self._devices:
			for device in self._devices:
				time.sleep(2)
				device.get_state()

	def receive(self,data,optional):
		logging.info("data=%s,optional=%s" % (data,optional))
		try:
			for device in self._devices:
				if device.r_id.lower()== data[2:10]:
					device.prev_send=["",0]
					state=data[16:18]
					device.rssi="{0:>02}".format(int(optional[0:2],16))
					device.value_changed(state)
				elif device.prev_send[0] and device.prev_send[1] <= 2:
					logging.info("prev_send=%s,times=%d" % (device.prev_send[0],device.prev_send[1]))
					self._serial.send(device.prev_send[0])
					device.prev_send[1] += 1
					time.sleep(0.02)
				elif device.prev_send[1]>2:
					device.rssi="00"
					device.prev_send=["",0]
					device.value_changed()
				else:
					if not(data[2:10] in self._emitteridlist) and data[2:3] != "8":
						self._emitteridlist.append(data[2:10])
						self._emitter.change_id_list(data[2:10])
		except :
			logging.info("dongle receive error")
		

# linptech device
class LinptechDevice():
	"""Parent class for all devices associated with the Linptech component.
	- send_commmand via linptech dongle
	"""

	def __init__(self):
		"""Initialize linptech device."""
		while not LINPTECH_DONGLE:
			time.sleep(0.5)
		if isinstance(self, Light):
			LINPTECH_DONGLE.register_device(self)
		else:
			LINPTECH_DONGLE.register_emitter(self)

	# get command from linptech dongle
	def send_command(self, command):
		"""send a command via the linptech dongle."""
		LINPTECH_DONGLE.send(command)