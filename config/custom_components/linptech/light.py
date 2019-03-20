"""
领普科技 接收器:R3AC,RX-4
"""

import logging
import voluptuous as vol

from homeassistant.const import (CONF_NAME, CONF_ID,CONF_TYPE)
from custom_components.linptech import LinptechDevice,LINPTECH_NET
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import PLATFORM_SCHEMA
from homeassistant.components.light import Light
import time
from datetime import timedelta
from homeassistant.helpers.event import track_time_interval


CONF_SENDER_ID = 'transmitors'
CONF_CHANNEL="channel"
DEFAULT_NAME = 'Linptech Receiver'
TIME_BETWEEN_UPDATES=timedelta(seconds=600)


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
	t_id =  config.get(CONF_SENDER_ID)
	r_name = config.get(CONF_NAME)
	r_id =  config.get(CONF_ID)
	r_channel = config.get(CONF_CHANNEL) 
	r_type = config.get(CONF_TYPE)
	add_devices([LinptechReceiver(hass,t_id, r_name, r_id,r_type,r_channel)])


# linptech receiver
class LinptechReceiver(LinptechDevice, Light):
	"""Representation of an linptech light source."""
	def __init__(self,hass, t_id, r_name, r_id,r_type,r_channel):
		"""Initialize the linptech light source."""
		LinptechDevice.__init__(self,r_id,r_type,r_channel)
		self.hass = hass
		self.on_state = False
		self.rssi="00"
		self.t_id = t_id
		self.r_name = r_name
		self.is_hidden=False
		track_time_interval(self.hass,self.update_state, TIME_BETWEEN_UPDATES)

	@property
	def name(self):
		"""Return the name of the device if any."""
		return self.r_name

	@property
	def is_on(self):
		"""If light is on."""
		return self.on_state
	
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
	def get_state(self):
		try:
			self.linptech_net.lp.read_receiver_state(self.id,self.type)
		except Exception as e:
			logging.error("receiver get_state error:%s",e)
	def update_state(self,time):
		self.get_state()
	def turn_on(self, **kwargs):
		try:
			self.linptech_net.lp.set_receiver_on(self.id,self.type,self.channel)
			self.on_state = True
		except Exception as e:
			logging.error("receiver turn on error:%s",e)
			pass
	
	def turn_off(self, **kwargs):
		try:
			self.linptech_net.lp.set_receiver_off(self.id,self.type,self.channel)
			self.on_state = False
		except Exception as e:
			logging.error("receiver turn off error:%s",e)
		
	def value_changed(self, data, optional):
		self.rssi = "{0:>02}".format(int(optional[0:2],16))
		try:
			self.on_state = bool(int(data[-1],16)&int(self.channel) == int(self.channel))
			if "rssi" in self.r_name:
				self.r_name=self.r_name[0:-2]+self.rssi
			else:
				self.r_name=self.r_name+",rssi="+self.rssi
			self.schedule_update_ha_state()
		except Exception as e:
			logging.error("receiver value changed error:%s",e)