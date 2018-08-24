"""
文件名 hachina.py.

演示程序，读取配置文件的内容.
"""

import logging
# 引入这两个库，用于配置文件格式校验
from datetime import timedelta
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.event import track_time_interval

DOMAIN = "hachina"
ENTITYID = DOMAIN + ".hello_world"

CONF_STEP = "step"
DEFAULT_STEP = 3
TIME_BETWEEN_UPDATES = timedelta(seconds=3)

# 预定义配置文件中的key值
CONF_NAME_TOBE_DISPLAYED = "name_tobe_displayed"
CONF_SLOGON = "slogon"

# 预定义缺省的配置值
DEFAULT_SLOGON = "积木构建智慧空间！"

_LOGGER = logging.getLogger(__name__)

# 配置文件的样式
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                # “name_tobe_displayed”在配置文件中是必须存在的（Required），否则报错，它的类型是字符串
                vol.Required(CONF_NAME_TOBE_DISPLAYED): cv.string,
                # “slogon”在配置文件中可以没有（Optional），如果没有缺省值为“积木构建智慧空间！”，它的类型是字符串
                vol.Optional(CONF_SLOGON, default=DEFAULT_SLOGON): cv.string,
                vol.Optional(CONF_STEP,default=DEFAULT_STEP):cv.positive_int,
            }),
    },
    extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """配置文件加载后，setup被系统调用."""
    # config[DOMAIN]代表这个域下的配置信息
    conf = config[DOMAIN]
    # 获得具体配置项信息
    friendly_name = conf.get(CONF_NAME_TOBE_DISPLAYED)
    slogon = conf.get(CONF_SLOGON)
    step=conf.get(CONF_STEP)

    _LOGGER.info("Get the configuration %s=%s; %s=%s;%s=%d",
                 CONF_NAME_TOBE_DISPLAYED, friendly_name,
                 CONF_SLOGON, slogon,CONF_STEP,step)

    # 根据配置内容设置属性值
    attr = {"icon": "mdi:yin-yang",
            "friendly_name": friendly_name,
            "slogon": slogon,
            "unit_of_measurement":"steps"}
    hass.states.set(ENTITYID, '太棒了', attributes=attr)
    GrowingState(hass,step,attr)
    return True

class GrowingState(object):
    
    def __init__(self,hass,step,attr):
        self._hass = hass
        self._step = step
        self._attr = attr
        self._state = 0

        self._hass.states.set(ENTITYID,self._state,attributes=self._attr)
        track_time_interval(self._hass,self.update,TIME_BETWEEN_UPDATES)
        
    def update(self,now):
        _LOGGER.info("GrowingState is updating")
        self._state = self._state + self._step
        self._hass.states.set(ENTITYID,self._state,attributes=self._attr)