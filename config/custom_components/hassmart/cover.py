'''
HASSMART Cover v0.5
by Jones
2018-10-14
'''
import time
import socket
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from threading import Thread, Event
from homeassistant.components.cover import (CoverDevice, DOMAIN, ATTR_POSITION, PLATFORM_SCHEMA)
from homeassistant.const import (ATTR_ATTRIBUTION, CONF_HOST, EVENT_HOMEASSISTANT_STOP)
from homeassistant.helpers.event import track_utc_time_change

_LOGGER = logging.getLogger(__name__)


HS_COVER_TCP_PORT = 23
HS_COVER_DIRECTION = 'default'

SOCKET_BUFSIZE = 1024
SOCKET_TIMEOUT = 30.0
DISCOVER_TIMEOUT = 20

ATTRIBUTION = 'A HASSMART Product'

CONF_PORT = 'port'
CONF_DIRECTION = 'direction'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default = HS_COVER_TCP_PORT): cv.port,
    vol.Optional(CONF_DIRECTION, default = HS_COVER_DIRECTION): vol.In(['default', 'reverse']),
})

class HASSmartHub(object):
    '''hassmart hub init'''
    def __init__(self, tcp_ip, tcp_port, direction):
        self._tcp_ip = tcp_ip
        self._tcp_port = tcp_port
        self._conf_motor_direction = direction
        self._socket = None
        self._timeout_number = 0
        self._check_state = False
        self._threads = []
        self.thread_event = Event()
        self.callbacks = None
        self.position = None

        self.motor_status = None
        self.motor_direction = None
        self.motor_manual_start = None

        self.is_closing = None
        self.is_opening = None
        self.is_closed = True

        self.listen()

    def check_cover_state(self):
        self._check_state = True
        if self._check_socket():
            time_now = time.time()
            while self._check_state:
                time.sleep(1)
                if time.time() - time_now > DISCOVER_TIMEOUT:
                    self._check_state = False
                    _LOGGER.error('no hassmart cover response')
                    return False

            if self.motor_direction != self._conf_motor_direction:
                _LOGGER.error('changing motor direction to %s', self._conf_motor_direction)
                self.set_motor_direction(self._conf_motor_direction)
            return True
        else:
            return False

    def _create_socket(self):
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(SOCKET_TIMEOUT)
        try:
            self._socket.connect((self._tcp_ip, self._tcp_port))
        except Exception as e:
            _LOGGER.error('creat socket error %s', e)

    def _check_socket(self):
        try:
            peer = self._socket.getpeername()
            return True
        except Exception as e:
            _LOGGER.info('not connected: %s', e)
            return False

    def _send_packet(self, data):
        try:
            self._socket.send(data)
            _LOGGER.info("send packet ok: %s", data)
        except Exception as e:
            _LOGGER.error('send packet error: %s, recreating socket...', e)
            self._create_socket()

    def listen(self):
        self._create_socket()
        if self._check_socket():
            self.thread_event.set()
        else:
            _LOGGER.error('1st creating socket error, recreating...')
            self._create_socket()
        thread_listen = Thread(target = self._handle_recv_data, args = ())
        self._threads.append(thread_listen)
        thread_listen.daemon = True
        thread_listen.start()
        self.get_position()

    def stop_listen(self):
        self.thread_event.clear()
        if self._socket is not None:
            _LOGGER.info('Closing socket')
            self._socket.close()
            self._socket = None
        for thread in self._threads:
            thread.join()

    def _handle_recv_data(self):
        #self.thread_event.wait()
        while self.thread_event.is_set():
            if self._timeout_number > 1:
                _LOGGER.error("timeout > 1, recreating socket")
                self._create_socket()
                self._timeout_number = 0

            try:
                data = self._socket.recv(SOCKET_BUFSIZE)
            # except socket.timeout:
            except Exception as e:
                _LOGGER.error("recv data error: %s", e)
                self._timeout_number += 1
                continue

            if data[0] == 0x62 and data[1] == 0x01:
                _LOGGER.error("cmd error")
                continue

            if not data:
                self._create_socket()
            elif self._check_state:
                self._check_state = False
                if data[0] == 0x3C or data[0] == 0x61:
                    if data[4] == 0x00:
                        '''stop'''
                        self.is_closing = False
                        self.is_opening = False
                    elif data[4] == 0x01:
                        '''opening'''
                        self.is_closing = False
                        self.is_opening = True
                    elif data[4] == 0x02:
                        '''closing'''
                        self.is_closing = True
                        self.is_opening = False
                    elif data[4] == 0x03:
                        '''setting'''
                        pass
                    elif data[4] == 0x04:
                        '''block_stop'''
                        pass

                    if data[2] == 0x00:
                        self.motor_direction = 'default'
                    elif data[2] == 0x01:
                        self.motor_direction = 'reverse'

                    if data[3] == 0x00:
                        self.motor_manual_start = True
                    elif data[3] == 0x01:
                        self.motor_manual_start = False

                    if data[1] != 0xFF:
                        self.position = int(data[1])
                    else:
                        self.position = 50

                    self.is_closed = self.position <= 0
            else:
                self.callbacks(data)

    def get_position(self):
        packet = b"\x54\x54"
        self._send_packet(packet)

    def open_cover(self):
        packet = b"\x01\x01"
        self._send_packet(packet)

    def close_cover(self):
        packet = b"\x02\x02"
        self._send_packet(packet)

    def stop_cover(self):
        packet = b"\x03\x02"
        self._send_packet(packet)

    def set_cover_position(self, position):
        packet = [0x04]
        packet.append(int(position))
        self._send_packet(bytes(packet))

    def set_motor_direction(self, direction):
        if direction == 'default':
            packet = b"\x15\x00"
        elif direction == 'reverse':
            packet = b"\x15\x01"
        self._send_packet(packet)

def setup_platform(hass, config, add_devices, discovery_info = None):
    """Set up hassmart cover platform"""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    direction = config.get(CONF_DIRECTION)

    hub = HASSmartHub(host, port, direction)

    def stop_listening(event):
        _LOGGER.info('closing hassmart socket...')
        hub.stop_listen()

    if hub.check_cover_state():
        host = 'hassmart_' + '_'.join(host.split('.'))
        add_devices([HASSmartCover(hass, host, hub)])
        hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, stop_listening)
        return True
    else:
        hub.thread_event.clear()
        hub.stop_listen()
        return False

class HASSmartCover(CoverDevice):
    def __init__(self, hass, name, hub):
        self._name = name
        self._hass = hass
        self._unique_id = name
        
        self._closed = hub.is_closed
        self._is_opening = hub.is_opening
        self._is_closing = hub.is_closing

        self._motor_direction = hub.motor_direction
        self._motor_manual_start = hub.motor_manual_start

        self._set_position_value = None
        self._unsub_listener_cover = None

        self._position = hub.position
        self._open_cover = hub.open_cover
        self._close_cover = hub.close_cover
        self._stop_cover = hub.stop_cover
        self._get_position = hub.get_position
        self._set_position = hub.set_cover_position
        self._set_direction = hub.set_motor_direction

        hub.callbacks = self._process_data

        self._heart_beat()

    def _process_data(self, data):
        ''' handle position & motor status '''
        if data[0] == 0x3C or data[0] == 0x61:
            if data[4] == 0x00:
                self._is_opening = False
                self._is_closing = False
            elif data[4] == 0x01:
                self._is_opening = True
                self._is_closing = False
            elif data[4] == 0x02:
                self._is_opening = False
                self._is_closing = True
            elif data[4] == 0x03:
                pass
            elif data[4] == 0x04:
                self._is_opening = False
                self._is_closing = False

            if data[2] == 0x00:
                self._motor_direction = 'default'
            elif data[2] == 0x01:
                self._motor_direction = 'reverse'

            if data[3] == 0x00:
                self._motor_manual_start = True
            elif data[3] == 0x01:
                self._motor_manual_start = False

            if data[1] != 0xFF:
                self._position = int(data[1])
            else:
                self._position = 50

        self._closed = self._position <= 0

        self.schedule_update_ha_state()
        return True

    @property
    def name(self):
        """Return the name of the cover."""
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        """No polling needed for a cover."""
        return False

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return self._position

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self._closed

    @property
    def is_opening(self):
        """Return if the cover is opening."""
        return self._is_opening

    @property
    def is_closing(self):
        """Return if the cover is closing."""
        return self._is_closing

    @property
    def device_state_attributes(self):
        if self._position is not None:
            return {
                'motor_direction': self._motor_direction,
                'motor_manual_start': self._motor_manual_start,
                ATTR_ATTRIBUTION: ATTRIBUTION
            }

    def close_cover(self, **kwargs):
        """Close the cover."""
        self._close_cover()
        self.schedule_update_ha_state()

    def open_cover(self, **kwargs):
        """Open the cover."""
        self._open_cover()
        self.schedule_update_ha_state()

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        self._is_closing = False
        self._is_opening = False
        self._stop_cover()

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION)
        self._set_position_value = position
        self._set_position(position)

    def set_motor_direction(self, direction):
        self._set_direction(direction)

    def _heart_beat(self):
        track_utc_time_change(self._hass, self._handle_heart_beat, second = range(0, 60, 20))

    def _handle_heart_beat(self, now):
        #_LOGGER.error('sending heat beat request')
        self._get_position()
        self._closed = self.current_cover_position <= 0
        self.schedule_update_ha_state()