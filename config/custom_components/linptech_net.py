
from linptech.constant import ReceiverType, TransmitType, ReceiverChannel, TransmitChannel
from homeassistant.helpers import discovery
from linptech.linptech_protocol import LinptechProtocol
import logging
import voluptuous as vol
import time
from datetime import timedelta

from homeassistant.const import CONF_DEVICE
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import Light
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.event import track_time_interval

REQUIREMENTS = ['linptech']

# from custom_components.switch.linptech_transmit import LinptechTransmit
DOMAIN = 'linptech_net'
DATA_LINPTECH = 'linptech'
LINPTECH_NET = None
IS_LISTEN = 'is_listen'
ENTITY_ID = 'entity_id'
DEVICE_ID = 'device_id'
DEVICE_TYPE = 'device_type'
DEVICE_CHANNEL = 'device_channel'
RELAY='relay'
TRANSMITOR='transmitor'
RECEIVER='receiver'
TIME_BETWEEN_UPDATES=timedelta(seconds=600)

logging.getLogger().setLevel(logging.ERROR)

CONFIG_SCHEMA = vol.Schema({
	DOMAIN: vol.Schema({
		vol.Required(CONF_DEVICE): cv.string,
	}),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
	"""Set up the Linptech component."""
	global LINPTECH_NET
	serial_dev = config[DOMAIN].get(CONF_DEVICE)
	LINPTECH_NET = LinptechNet(hass, serial_dev, config)
	hass.states.set('linptech.listen', False,attributes={"hidden":True})
	track_time_interval(hass,LINPTECH_NET.update_state, TIME_BETWEEN_UPDATES)
	# 监听设备，即增加设备

	def listen_device(call):
		hass.states.set('linptech.listen', call.data.get(IS_LISTEN),attributes={"hidden":True})
		LINPTECH_NET.is_listen = call.data.get(IS_LISTEN)
	
	# 增加设备
	def load_device(call):
		dev_id = call.data.get(DEVICE_ID)
		dev_type = call.data.get(DEVICE_TYPE)
		dev_channel = call.data.get(DEVICE_CHANNEL)
		print(dev_id,dev_type,dev_channel)
		LINPTECH_NET.load_device(dev_id,dev_type,dev_channel)

	# 删除设备，从states中删除后还会出来，暂时设置隐藏
	def delete_device(call):
		print(hass.states.remove(call.data.get(ENTITY_ID)))
		#hass.states.remove('group.all_lights')
		LINPTECH_NET.remove_device(call.data.get(ENTITY_ID))
	
	def hide_device(call):
		entity_id=call.data.get(ENTITY_ID)
		LINPTECH_NET.hide_device(entity_id)

	# 打开或者关闭中继
	def set_relay(call):
		entity_id=call.data.get(ENTITY_ID)
		relay=call.data.get(RELAY)
		LINPTECH_NET.set_relay(entity_id,relay)

	# 配对服务
	def set_pair(call):
		transmitor=call.data.get(TRANSMITOR)
		receiver=call.data.get(RECEIVER)
		LINPTECH_NET.set_pair(transmitor,receiver)

	# 更新svg
	def save_svg(call):
		svg=call.data.get("svg")
		path=call.data.get("path")
		path=path.replace('/local','./config/www')
		print(path)
		with open(path,'w') as f:
			f.write(svg)
			f.close()

	hass.services.register(DOMAIN, 'listen', listen_device)
	hass.services.register(DOMAIN, 'hide_device', hide_device)
	hass.services.register(DOMAIN, 'load_device', load_device)
	hass.services.register(DOMAIN,'set_relay',set_relay)
	hass.services.register(DOMAIN,'set_pair',set_pair)
	hass.services.register(DOMAIN,'save_svg',save_svg)

	return True


class LinptechNet:

	"""Representation of an Linptech dongle:
	- register device
	- receive
	"""

	def __init__(self, hass, port, config):
		"""Initialize the Linptech dongle."""
		self.lp = LinptechProtocol(port=port, receive=self.receive)
		self.devices = []
		self.dev_info = []
		self.hass = hass
		self.config = config
		self.is_listen = False

	def register_device(self, dev):
		"""Register another device."""
		self.devices.append(dev)

	def remove_device(self, entity_id):
		dev= [dev for dev in self.devices if dev.entity_id==entity_id]
		if dev:
			self.devices.remove(dev[0])
			dev[0].schedule_update_ha_state()
	def hide_device(self,entity_id):
		dev= [dev for dev in self.devices if dev.entity_id==entity_id]
		if dev:
			dev[0].is_hidden=True
			dev[0].schedule_update_ha_state()
	
	def set_relay(self,entity_id,relay):
		dev= [dev for dev in self.devices if dev.entity_id==entity_id]
		if dev:
			self.lp.set_receiver_relay(dev.id,dev.type,relay)
			dev[0].schedule_update_ha_state()
	
	def set_pair(self,receiver,transmitor):
		receiver=[dev for dev in self.devices if dev.entity_id==receiver]
		transmitor=[dev for dev in self.devices if dev.entity_id==transmitor]
		if receiver and transmitor:
			if receiver.type in ReceiverType.ALL and transmitor.type in TransmitType.ALL:
				self.lp.write_transmit_to_receiver(receiver.id,receiver.type,receiver.channel,\
				transmitor.id,transmitor.type,transmitor.channel)

	def update_state(self,now):
		pass

	def load_device(self, dev_id, dev_type, dev_channel):
		discovery_info = {'id': dev_id,
								  'type': dev_type, 'channel': dev_channel}
		if dev_type in ReceiverType.ALL and dev_channel in ReceiverChannel.ALL:
			print("add receiver")
			discovery.load_platform(
				self.hass, 'light', 'linptech_receiver', discovery_info, self.config)
		elif dev_type in TransmitType.ALL and dev_channel in TransmitChannel.ALL:
			pass
			print("add transmitor")
			discovery.load_platform(
				self.hass, 'switch', 'linptech_transmitor', discovery_info, self.config)

	def receive(self, data, optional):
		# print(self.hass.states.get('linptech.listen').state)
		# print(self.is_listen)
		print("data=%s,optional=%s" % (data, optional))
		# print('forecast=%s' % self.lp.forecasts)
		# 触动重发机制
		for f in self.lp.forecasts:
			if f["count"] > 3:
				self.lp.forecasts.remove(f)
			elif data.startswith(f["back"]):
				self.lp.forecasts.remove(f)
				info = f["info"]+data[f["info_index"]:f["info_index"]+f["info_len"]]
				print(info)
			elif time.time()-f["timestamp"] > 0.2:
				f["count"] += 1
				f["timestamp"] = time.time()
				self.lp.ser.send(f["data"])
		# 处理data,获取设备的id，type，channels（list）
		if not self.is_listen:
			return
		dev_id = data[2:10]
		dev_type = data[10:12]
		dev_channels = []
		if  dev_type in TransmitType.ALL and data[-2:] != "00":
			dev_channels = ['0' + data[-1]]
		if dev_type == ReceiverType.R3AC:
			dev_channels = [ReceiverChannel.c1]
		if dev_type == ReceiverType.RX_4:
			dev_channels = [ReceiverChannel.c1, ReceiverChannel.c2,
							ReceiverChannel.c3, ReceiverChannel.c4]
		exist_devs = [d for d in self.devices if d.id+d.type ==
					  dev_id+dev_type and d.channel in dev_channels]
		# print("exist_devs=%s" % exist_devs)
		# 已知设备: 更新状态，前端需要确定按下的是哪个，rssi更新
		print(dev_channels)
		if exist_devs:
			for dev in exist_devs:
				dev.value_changed(data, optional)
		# 未知设备:需要加载新设备，发现新设备按钮
		elif dev_channels:
			for dev_channel in dev_channels:
				self.load_device(dev_id,dev_type,dev_channel)


# linptech device
class LinptechDevice():
	"""Parent class for all devices associated with the Linptech component.
	- send_commmand via linptech dongle
	"""

	def __init__(self, id, type, channel):
		"""Initialize linptech device."""
		self.id = id
		self.type = type
		self.channel = channel
		while not LINPTECH_NET:
			time.sleep(0.5)
		LINPTECH_NET.register_device(self)
		self.linptech_net = LINPTECH_NET
