"""
领普科技 接收器:R3AC,RX-4
"""

import logging
import voluptuous as vol

from homeassistant.const import (CONF_NAME, CONF_ID,CONF_TYPE)
from custom_components.linptech_dongle import LinptechDevice
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import PLATFORM_SCHEMA

from homeassistant.components.light import Light
import time
REQUIREMENTS = ['linptech==0.1.7']
CONF_SENDER_ID = 'transmitors'
CONF_CHANNEL="channel"
DEFAULT_NAME = 'Linptech Receiver'
LIGHT_ID = "light_id"

from linptech.constant import CmdType,State,ReceiverChannel,ReceiverType,PacketType
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(CONF_ID):cv.string,
	vol.Optional(CONF_SENDER_ID,default=[]): vol.All(cv.ensure_list, [vol.Coerce(int)]),
	vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
	vol.Optional(CONF_TYPE, default=ReceiverType.R3AC): vol.In(ReceiverType.ALL),
	vol.Optional(CONF_CHANNEL, default=ReceiverChannel.c1): vol.In(ReceiverChannel.ALL),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
	"""Set up the linptech light platform."""	
	t_id = config.get(CONF_SENDER_ID)
	r_name = config.get(CONF_NAME)
	r_id = config.get(CONF_ID)
	r_channel = config.get(CONF_CHANNEL)
	r_type = config.get(CONF_TYPE)
	add_devices([LinptechReceiver(t_id, r_name, r_id,r_type,r_channel)])

# linptech receiver
class LinptechReceiver(LinptechDevice, Light):

	"""Representation of an linptech light source."""
	def __init__(self, t_id, r_name,r_id,r_type,r_channel):
		"""Initialize the linptech light source."""
		LinptechDevice.__init__(self)
		self.on_state = False
		self.rssi="00"
		self.prev_send=["",0]

		self.t_id = t_id
		self.r_id = r_id
		self.r_name = r_name
		self.r_type = r_type
		self.r_channel=r_channel
		time.sleep(1)
		self.get_state()

	@property
	def name(self):
		"""Return the name of the device if any."""
		return self.r_name

	@property
	def is_on(self):
		"""If light is on."""
		return self.on_state

	@property
	def device_state_attributes(self):
		"""设置灯的ID，作为其他属性."""
		return {
			LIGHT_ID: self.r_id,
		}

	
	def get_state(self):
		try:
			command = PacketType.state +self.r_id+self.r_type+self.r_channel
			#print(command)
			self.send_command(command)
			self.prev_send=[command,0]
		except :
			logging.error("receiver get_state error")
			pass
		
	def turn_on(self, **kwargs):
		try:
			command = PacketType.state+self.r_id+self.r_type+\
				CmdType.write_state+self.r_channel+self.r_channel
			self.send_command(command)
			self.prev_send=[command,0]
			self.on_state = True
		except :
			logging.error("receiver turn on error")
			pass
		

	def turn_off(self, **kwargs):
		try:
			command = PacketType.state+self.r_id+self.r_type+\
				CmdType.write_state+self.r_channel+State.off
			self.send_command(command)
			self.prev_send=[command,0]
			self.on_state = False
		except :
			logging.error("receiver turn off error")
		

	def value_changed(self, val=None):
		"""Update the internal state of this device."""
		try:
			if val is not None:
				self.on_state = bool(int(val,16)&int(self.r_channel) == int(self.r_channel))
			if "rssi" in self.r_name:
				self.r_name=self.r_name[0:-2]+self.rssi
			else:
				self.r_name=self.r_name+",rssi="+self.rssi
			while not self.hass:
				time.sleep(0.2)
			self.schedule_update_ha_state()
		except :
			logging.error("receiver value changed error")