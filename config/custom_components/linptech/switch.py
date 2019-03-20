"""
领普科技 发射器:K5,K4R
"""

import logging
import voluptuous as vol

from homeassistant.const import (CONF_NAME, CONF_ID,CONF_TYPE)
from custom_components.linptech import LinptechDevice,LINPTECH_NET
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.components.switch import PLATFORM_SCHEMA
import traceback


import time
_LOGGER = logging.getLogger(__name__)

CONF_SENDER_ID = 'transmitors'
CONF_CHANNEL="channel"
DEFAULT_NAME = 'Linptech Transmitor'

from linptech.constant import CmdType,State,ReceiverChannel,ReceiverType,PacketType
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(CONF_ID):cv.string,
	vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
	vol.Optional(CONF_TYPE, default=ReceiverType.R3AC): vol.In(ReceiverType.ALL),
	vol.Optional(CONF_CHANNEL, default=ReceiverChannel.c1): vol.In(ReceiverChannel.ALL),
})

def setup_platform(hass, config, add_devices, discovery_info):
	"""Set up the linptech Transmitor platform."""
	_LOGGER.debug(discovery_info)
	t_name = discovery_info['id'] if discovery_info else config.get(CONF_NAME)
	t_id = discovery_info['id'] if discovery_info else config.get(CONF_ID)
	t_channel =discovery_info['channel'] if discovery_info else config.get(CONF_CHANNEL)
	t_type =discovery_info['type'] if discovery_info else  config.get(CONF_TYPE)
	add_devices([LinptechTransmitor(hass, t_name, t_id,t_type,t_channel)])

# linptech transmit
class LinptechTransmitor(LinptechDevice, ToggleEntity):
	"""Representation of an linptech transmitor source."""
	def __init__(self,hass, t_name, t_id,t_type,t_channel):
		LinptechDevice.__init__(self,t_id,t_type,t_channel)
		self.hass = hass
		self.on_state = False
		self.rssi="00"
		self.t_name=t_name
		self.is_hidden=False

	@property
	def name(self):
		"""Return the name of the device if any."""
		return self.t_name

	@property
	def is_on(self):
		"""If light is on."""
		return self.on_state
	
	@property
	def assumed_state(self):
		return True
	
	@property
	def hidden(self):
		return self.is_hidden

	@property
	def device_state_attributes(self):
		return {
			"id":self.id,
			"type":self.type,
			"channel":self.channel
			}
		
	def turn_on(self, **kwargs):
		try:
			self.linptech_net.lp.switch_on(self.id,self.type,self.channel)
			self.on_state = True
		except :
			logging.error("receiver turn on error")
			pass
		
	def turn_off(self, **kwargs):
		try:
			self.linptech_net.lp.switch_off(self.id,self.type,self.channel)
			self.on_state = False
		except :
			logging.error("receiver turn off error")
	
	def value_changed(self, data, optional):
		self.rssi = "{0:>02}".format(int(optional[0:2],16))
		if "rssi" in self.t_name:
			self.t_name=self.t_name[0:-2]+self.rssi
		else:
			self.t_name=self.t_name+",rssi="+self.rssi
		self.schedule_update_ha_state()



	