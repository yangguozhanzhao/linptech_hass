"""
领普科技 单路接收器
"""

import logging
import voluptuous as vol
import linptech.constant as CON

from homeassistant.const import (CONF_NAME, CONF_ID)
from custom_components.linptech_dongle import LinptechDevice,LinptechReceiver
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import PLATFORM_SCHEMA

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
    dev_name = config.get(CONF_NAME)
    dev_id = config.get(CONF_ID)
    add_devices([LinptechReceiver(sender_id, dev_name, dev_id,CON.receiver_type['R3AC'],CON.receiver_channel['c1'])])
