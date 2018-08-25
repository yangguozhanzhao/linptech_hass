import json
from urllib import request,parse
import logging
from datetime import timedelta
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ATTRIBUTION, ATTR_FRIENDLY_NAME, TEMP_CELSIUS)

from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv 
import homeassistant.util.dt as dt_util

## 异步处理
import asyncio
import async_timeout
import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)
TIME_BETWEEN_UPDATES=timedelta(seconds=60)

CONF_CITY = "city"
CONF_APPKEY = "appkey"
CONF_OPTIONS = "options"

OPTIONS = {
    "temprature":["hachina_temperature","室外温度","mdi:themometer",TEMP_CELSIUS],
    "humidity":["hachina_hunidity","室外湿度","mdi:water-percent","%"],
    "pm25":["hachina_pm25","PM2.5","mdi:walk","ug/m3"],
}

ATTR_UPDATE_TIME = "更新时间"
ATTRIBUTION = "来自京东万象的天气数据"

PLATFORM_SCHEMA=PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CITY,default="wuhan"):cv.string,
    vol.Required(CONF_APPKEY):cv.string,
    vol.Required(CONF_OPTIONS,default=[]):vol.All(cv.ensure_list,[vol.In(OPTIONS)])
})

@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """配置文件在sensor域下出现hachina平台时，会自动调用sensor目录下hachina.py中的setup_platform函数."""
    _LOGGER.info("setup platform sensor.hachina...")

    city=config.get(CONF_CITY)
    appkey = config.get(CONF_APPKEY)

    data=WeatherData(hass,city,appkey)
    yield from data.async_update(dt_util.now())
    async_track_time_interval(hass,data.async_update,TIME_BETWEEN_UPDATES)
    # 定义一个设备组，在其中装入了一个我们定义的设备HAChinaTemperatureSensor
    dev = []
    for option in config[CONF_OPTIONS]:
        dev.append(HAChinaTemperatureSensor(data,option))

    # 将设备加载入系统中
    async_add_devices(dev, True)


class HAChinaTemperatureSensor(Entity):
    """定义一个温度传感器的类，继承自HomeAssistant的Entity类."""

    def __init__(self,data,option):
        """初始化，状态值为空."""
        self._data=data
        self._object_id = OPTIONS[option][0]
        self._friendly_name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._unit_of_measurement = OPTIONS[option][3]

        self._type=option
        self._state = None
        self._updatetime = None



    @property
    def name(self):
        """返回实体的名字。通过python装饰器@property，使访问更自然（方法变成属性调用，可以直接使用xxx.name）."""
        return self._object_id

    @property
    def registry_name(self):
        """返回实体的friendly_name属性."""
        return self._friendly_name

    @property
    def state(self):
        """返回当前的状态."""
        return self._state

    @property
    def icon(self):
        """返回icon属性."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """返回unit_of_measuremeng属性."""
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
        """设置其它一些属性值."""
        if self._state is not None:
            return {
                ATTR_ATTRIBUTION: ATTRIBUTION,
                ATTR_UPDATE_TIME:self._updatetime
            }

    @asyncio.coroutine
    def async_update(self):
        """更新函数，在sensor组件下系统会定时自动调用（时间间隔在配置文件中可以调整，缺省为30秒）."""
        self._updatetime = self._data.updatetime

        if self._type =="temprature":
            self._state=self._data.temprature
        elif self._type == "humidity":
            self._state = self._data.humidity
        elif self._type == "pm25":
            self._state = self._data.pm25

class WeatherData(object):
    def __init__(self,hass,city,appkey):
        self._hass=hass
        self._url="https://way.jd.com/he/freeweather"
        self._params = {"city":city,"appkey":appkey,}
        self._temprature = None
        self._humidity = None
        self._pm25 = None
        self._updatetime = None

    @property
    def temprature(self):
        return self._temprature
    
    @property
    def humidity(self):
        return self._humidity
    
    @property
    def pm25(self):
        return self._pm25
    
    @property
    def updatetime(self):
        return self._updatetime
    
    @asyncio.coroutine
    def async_update(self,now):
        _LOGGER.info("update from jingdong api")

        try:
            session = async_get_clientsession(self._hass)
            with async_timeout.timeout(15,loop=self._hass.loop):
                response = yield from session.post(self._url,data=self._params)
        except(asyncio.TimeoutError,aiohttp.ClientError):
            _LOGGER.error("ERROR while accessing:%s",self._url)
            return
        
        if response.status != 200:
            _LOGGER.error("ERROR while accessing:%s,status=%d",self._url,response.status)
            return
        
        result=yield from response.json()
        if result is None:
            _LOGGER.error("Request api Error")
            return
        elif result["code"] != "10000":
            _LOGGER.error("Error API return,code=%s,msg=%s",result["code"],result["msg"])
            return
        all_result = result["result"]["HeWeather5"][0]
        self._temprature = all_result["now"]["tmp"]
        self._humidity = all_result["now"]["hum"]
        self._pm25 = all_result["aqi"]["city"]["pm25"]
        self._updatetime = all_result["basic"]["update"]["loc"]