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
from linptech.serial_communicator import LinptechSerial

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'linptech_dongle'

LINPTECH_DONGLE = None
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

	def send(self, data):
		"""Send a command from the Linptech dongle."""
		self._serial.send(data)
	
	def update_devices_state(self,now):
		"""send query command,get lights state"""
		if self._devices:
			for device in self._devices:
				device.get_state()

	def receive(self,data,optional):
		self.logger.info("data=%s,optional=%s" % (data,optional))
		for device in self._devices:
			index = data.find((device.dev_id+device.type).lower())
			if index>0:
				state=data[index+10:index+16]
				print(int(state[-1]))
				device.value_changed(int(state[-1]))

class LinptechDevice():
	"""Parent class for all devices associated with the Linptech component.
	- send_commmand via linptech dongle
	"""

	def __init__(self):
		"""Initialize linptech device."""
		while not LINPTECH_DONGLE:
			time.sleep(0.5)
		LINPTECH_DONGLE.register_device(self)

	# get command from linptech dongle
	def send_command(self, command):
		"""send a command via the linptech dongle."""
		LINPTECH_DONGLE.send(command)
