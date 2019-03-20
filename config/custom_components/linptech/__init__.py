from linptech.constant import ReceiverType, TransmitType, ReceiverChannel, TransmitChannel
from homeassistant.helpers import discovery
from linptech.linptech_protocol import LinptechProtocol
import logging
import voluptuous as vol
import time

from homeassistant.const import CONF_DEVICE
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import Light
from homeassistant.helpers.entity import ToggleEntity

REQUIREMENTS = ['linptech']

# from custom_components.switch.linptech_transmit import LinptechTransmit
DOMAIN = 'linptech'
LINPTECH_NET = None
RECEIVER='receiver'

logging.getLogger().setLevel(logging.INFO)

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

	def register_device(self, dev):
		"""Register another device."""
		self.devices.append(dev)

	def receive(self, data, optional):
		# print(self.hass.states.get('linptech.listen').state)
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
		# elif dev_channels:
		# 	for dev_channel in dev_channels:
		# 		self.load_device(dev_id,dev_type,dev_channel)


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