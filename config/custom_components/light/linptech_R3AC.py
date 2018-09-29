"""
领普科技 lvr_910接收器
"""
#-*- coding:utf-8 -*-


import logging
import math
import time
import voluptuous as vol
import linptech.constant as CON
from homeassistant.components.light import (
    Light, ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, PLATFORM_SCHEMA)
from homeassistant.const import (CONF_NAME, CONF_ID)
from custom_components.linptech_dongle import LinptechDevice
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_SENDER_ID = 'sender_id'

DEFAULT_NAME = 'Linptech R3AC'


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ID):cv.string,
    vol.Optional(CONF_SENDER_ID,default=[]): vol.All(cv.ensure_list, [vol.Coerce(int)]),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the linptech light platform."""
    sender_id = config.get(CONF_SENDER_ID)
    devname = config.get(CONF_NAME)
    dev_id = config.get(CONF_ID)
    add_devices([LinptechLight(sender_id, devname, dev_id)])


class LinptechLight(LinptechDevice, Light):
    """Representation of an linptech light source."""
    def __init__(self, sender_id, devname, dev_id):
        """Initialize the linptech light source."""
        LinptechDevice.__init__(self)
        self._on_state = False
        self.rssi="00"
        self.prev_send=["",0]
        self._sender_id = sender_id
        self.dev_id = dev_id
        self._devname = devname
        self.type = CON.receiver_type["R3AC"]
        time.sleep(1)
        self.get_state()

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._devname

    @property
    def is_on(self):
        """If light is on."""
        return self._on_state
    
    def get_state(self):
        command = CON.packet_type["operate_state"] +self.dev_id+self.type+CON.receiver_channel["c1"]
        self.send_command(command)
        self.prev_send=[command,0]

    def turn_on(self, **kwargs):
        command = CON.packet_type["operate_state"]+\
                self.dev_id+self.type+\
                CON.cmd_type["control_state"]+\
                CON.receiver_channel["c1"]+CON.receiver_state['on']
        self.send_command(command)
        self.prev_send=[command,0]
        self._on_state = True

    def turn_off(self, **kwargs):
        command = CON.packet_type["operate_state"]+\
                self.dev_id+self.type+\
                CON.cmd_type["control_state"]+\
                CON.receiver_channel["c1"]+CON.receiver_state['off']
        self.send_command(command)
        self.prev_send=[command,0]
        self._on_state = False

    def value_changed(self, val):
        """Update the internal state of this device."""
        self._on_state = bool(val != 0)
        if "rssi" in self._devname:
            self._devname=self._devname[0:-2]+self.rssi
        else:
            self._devname=self._devname+",rssi="+self.rssi
        while not self.hass:
            time.sleep(0.2)
        self.schedule_update_ha_state()
