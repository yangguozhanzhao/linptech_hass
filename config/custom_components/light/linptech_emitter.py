"""
领普科技 发射器ID容器
"""

import logging
from custom_components.linptech_dongle import LinptechDevice
from homeassistant.helpers.entity import Entity

def setup_platform(hass, config, add_devices, discovery_info=None):
	"""Set up the linptech emitter platform."""	
	add_devices([LinptechEmitter(hass)])


# linptech emitter
class LinptechEmitter(LinptechDevice, Entity):
	def __init__(self, hass):
		LinptechDevice.__init__(self)
		self.hass = hass
		self._state = None
		self.emitter_id_list = []
		self.hass.services.register("light", 'matching_id', self.matching_id)

	@property
	def name(self):
		"""请勿改动，ha-floorplan.html会用到，用以区别是发射器"""
		return "emitter"

	@property
	def registry_name(self):
		"""返回实体的friendly_name"""
		return "emitter"

	@property
	def state(self):
		"""返回当前的状态."""
		return self._state

	def change_id_list(self, change_data = None):
		self.emitter_id_list.append(change_data)
		self._state = change_data
		self.schedule_update_ha_state()
	
	def matching_id(self,call):
		print("matching_id>>>>>>>>>>>>>>>>>>", call.data)
		print("type(call)>>>>>>>>>>>>>>>>>>", type(call))


	