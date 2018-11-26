"""
领普科技 发射器ID容器
"""

import logging
from custom_components.linptech_dongle import LinptechDevice
from homeassistant.helpers.entity import ToggleEntity

def setup_platform(hass, config, add_devices, discovery_info=None):
	"""Set up the linptech emitter platform."""	
	add_devices([LinptechEmitter(hass)])


# linptech emitter
class LinptechEmitter(LinptechDevice, ToggleEntity):
	def __init__(self, hass):
		LinptechDevice.__init__(self)
		self.hass = hass
		self._state = None
		self.emitter_id_list = []
		self.hass.services.register("switch", 'matching_id', self.matching_id)

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

	def turn_on(self, **kwargs):
		"""Turn the switch on."""
		pass
		print(self.name + " turn_on")

	def turn_off(self, **kwargs):
		"""Turn the switch off."""
		pass
		print(self.name + " turn_off")

	def change_id_list(self, change_data = None):
		self.emitter_id_list.append(change_data)
		self._state = change_data
		self.schedule_update_ha_state()
	
	# 自定义界面上，点击配对按钮调用此方法
	# 将选中的接收器，发射器ID传过来
	def matching_id(self,call):
		print("matching_id>>>>>>>>>>>>>>>>>>", call.data["entity_id"])



	