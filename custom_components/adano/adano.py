"""AdanoPy."""
import json
import logging
from threading import Timer
import uuid

import paho.mqtt.client as mqtt
import requests

_LOGGER = logging.getLogger(__name__)


class AdanoRoboticmower:  # noqa: D101
    def __init__(self, email, password) -> None:
        """Init function."""
        self.username = email
        self.password = password
        self.deviceArray = []
        self.session = {}
        self.devicelist = {}
        self.devicedata = {}
        self.settings = {}
        self.mqttdata = {}
        self.client_id = str(uuid.uuid4())
        self.mqtt_client = None
        self.refresh_token_interval = None
        self.refresh_token_timeout = None
        self.forceupdate = False

        self.power = 0
        self.mode = 0
        self.errortype = 0
        self.station = False
        self.wifi_lv = 0
        self.rain_en = False
        self.rain_status = 0
        self.rain_delay_set = 0
        self.rain_delay_left = 0
        self.cur_min = 0
        # self.faultStatusCode = ""
        # self.faultStatusName = ""
        self.deviceOnlineFlag = False
        self.zoneOpenFlag = False
        self.mul_en = False
        self.mul_auto = False
        self.mul_zon1 = 0
        self.mul_zon2 = 0
        self.mul_zon3 = 0
        self.mul_zon4 = 0

        self.Thu = {}
        self.Tue = {}
        self.Wed = {}
        self.Sat = {}
        self.Fri = {}
        self.Sun = {}
        self.Mon = {}

    def update(self):
        """Force HA to update sensors."""
        _LOGGER.debug("Force update")

    def on_load(self):
        """Init the shit."""
        if not self.username or not self.password:
            _LOGGER.debug("Please set username and password in the instance settings")
            return

        self.login()
        if self.session.get("access_token"):
            self.get_device_list()
            self.update_devices()
            self.connect_mqtt()

        self.refresh_token_interval = Timer(
            (self.session.get("expires_in") or 3600) * 1000, self.refresh_token
        )
        self.refresh_token_interval.start()

    def login(self):
        """Login."""
        try:
            response = requests.post(
                url="http://server.sk-robot.com/api/auth/oauth/token",
                headers={
                    "Accept-Language": "da",
                    "Authorization": "Basic YXBwOmFwcA==",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Connection": "Keep-Alive",
                    "User-Agent": "okhttp/4.4.1",
                },
                data={
                    "username": self.username,
                    "password": self.password,
                    "grant_type": "password",
                    "scope": "server",
                },
                timeout=5,
            )

            response_data = response.json()
            _LOGGER.debug(json.dumps(response_data))
            self.session = response_data
        except Exception as error:
            _LOGGER.debug("Login failed")
            _LOGGER.debug(error)
            if hasattr(error, "response"):
                _LOGGER.debug(json.dumps(error.response.json()))

    def connect_mqtt(self):
        """Connect mgtt."""
        if self.mqtt_client:
            self.mqtt_client.disconnect()

        self.mqtt_client = mqtt.Client(client_id=self.client_id)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        self.mqtt_client.on_error = self.on_mqtt_error
        self.mqtt_client.on_close = self.on_mqtt_close
        self.mqtt_client.username_pw_set("app", "h4ijwkTnyrA")
        try:
            self.mqtt_client.connect(
                host="mqtts.sk-robot.com",
                keepalive=60,
            )
            _LOGGER.debug("MQTT starting loop")
            self.mqtt_client.loop_start()
        except Exception as error:
            _LOGGER.debug("MQTT connect error: " + str(error))  # noqa: G003

    def on_mqtt_disconnect(self, client, userdata, rc):
        """On mqtt disconnect."""
        _LOGGER.debug("MQTT disconnected")

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """On mqtt connect."""
        _LOGGER.debug("MQTT connected event")
        _LOGGER.debug(
            "MQTT subscribe to: " + "/app/" + str(self.session["user_id"]) + "/get"  # noqa: G003
        )
        self.mqtt_client.subscribe(
            "/app/" + str(self.session["user_id"]) + "/get", qos=0
        )
        _LOGGER.debug("MQTT subscribe ok")

    def on_mqtt_message(self, client, userdata, message):
        """On mqtt message."""
        _LOGGER.debug("MQTT message: " + message.topic + " " + message.payload.decode())  # noqa: G003
        try:
            data = json.loads(message.payload.decode())
            if "power" in data:
                self.power = data.get("power")
            if "mode" in data:
                self.mode = data.get("mode")
                if "errortype" in data:
                    self.errortype = data.get("errortype")
                    self.forceupdate = True
                else:
                    if self.errortype != 0:
                        self.forceupdate = True
                    self.errortype = 0
            if "station" in data:
                self.station = data.get("station")
            if "wifi_lv" in data:
                self.wifi_lv = data.get("wifi_lv")
            if "rain_en" in data:
                self.rain_en = data.get("rain_en")
            if "rain_status" in data:
                self.rain_status = data.get("rain_status")
            if "rain_delay_set" in data:
                self.rain_delay_set = data.get("rain_delay_set")
            if "rain_delay_left" in data:
                self.rain_delay_left = data.get("rain_delay_left")
            if "cur_min" in data:
                self.cur_min = data.get("cur_min")
            if "data" in data:
                self.deviceOnlineFlag = data.get("data")
            if "zoneOpenFlag" in data:
                self.zoneOpenFlag = data.get("zoneOpenFlag")
            if "mul_en" in data:
                self.mul_en = data.get("mul_en")
            if "mul_auto" in data:
                self.mul_auto = data.get("mul_auto")
            if "mul_zon1" in data:
                self.mul_zon1 = data.get("mul_zon1")
            if "mul_zon2" in data:
                self.mul_zon2 = data.get("mul_zon2")
            if "mul_zon3" in data:
                self.mul_zon3 = data.get("mul_zon3")
            if "mul_zon4" in data:
                self.mul_zon4 = data.get("mul_zon4")
            if "Mon" in data:
                self.Mon = data.get("Mon")
            if "Tue" in data:
                self.Tue = data.get("Tue")
            if "Wed" in data:
                self.Wed = data.get("Wed")
            if "Thu" in data:
                self.Thu = data.get("Thu")
            if "Fri" in data:
                self.Fri = data.get("Fri")
            if "Sat" in data:
                self.Sat = data.get("Sat")
            if "Sun" in data:
                self.Sun = data.get("Sun")

        except Exception as error:
            _LOGGER.debug("MQTT message error: " + str(error))  # noqa: G003
            _LOGGER.debug("MQTT message: " + message.payload.decode())  # noqa: G003

    def on_mqtt_error(self, client, userdata, error):
        """On mqtt error."""
        _LOGGER.debug("MQTT error: " + str(error))  # noqa: G003

    def on_mqtt_close(self, client, userdata, rc):
        """On mqtt close."""
        _LOGGER.debug("MQTT closed")

    def get_device_list(self):
        """Get device."""
        try:
            response = requests.get(
                url="http://server.sk-robot.com/api/mower/device-user/list",
                headers={
                    "Content-Type": "application/json",
                    "Accept-Language": "da",
                    "Authorization": "bearer " + self.session["access_token"],
                    "Host": "server.sk-robot.com",
                    "Connection": "Keep-Alive",
                    "User-Agent": "okhttp/4.4.1",
                },
                timeout=10,
            )
            response_data = response.json()
            self.devicelist = response_data
            _LOGGER.debug(json.dumps(response_data))

            if response_data["code"] != 0:
                _LOGGER.debug("Error getting device list")
                _LOGGER.debug(json.dumps(response_data))
                return

            _LOGGER.info(f"Found {len(response_data['data'])} devices")

            for device in response_data["data"]:
                device_id = device["deviceSn"]
                self.deviceArray.append(device_id)
                # name = device["deviceName"]
                self.get_settings(device_id)

        except Exception as error:
            _LOGGER.debug(error)
            if hasattr(error, "response"):
                _LOGGER.debug(json.dumps(error.response.json()))

    def get_settings(self, snr):
        """Get settings."""
        try:
            response = requests.get(
                url=f"http://server.sk-robot.com/api/mower/device-setting/{snr}",
                headers={
                    "Accept-Language": "da",
                    "Authorization": "bearer " + self.session["access_token"],
                    "Host": "server.sk-robot.com",
                    "Connection": "Keep-Alive",
                    "User-Agent": "okhttp/4.4.1",
                },
                timeout=10,
            )
            response_data = response.json()
            self.settings = response_data
            _LOGGER.debug(json.dumps(response_data))

            if response_data["code"] != 0:
                _LOGGER.debug("Error getting device settings")
                _LOGGER.debug(json.dumps(response_data))
                return
        except Exception as error:
            _LOGGER.debug(error)
            if hasattr(error, "response"):
                _LOGGER.debug(json.dumps(error.response.json()))

    def update_devices(self):
        """Update device."""
        status_array = [
            {
                "path": "status",
                "url": "http://server.sk-robot.com/api/mower/device/getBysn?sn=$id",
                "desc": "Status 1x update per hour",
            },
        ]

        for device_id in self.deviceArray:
            for element in status_array:
                url = element["url"].replace("$id", device_id)

                try:
                    response = requests.request(
                        method=element.get("method", "get"),
                        url=url,
                        headers={
                            "Accept-Language": "da",
                            "Authorization": "bearer " + self.session["access_token"],
                            "Host": "server.sk-robot.com",
                            "Connection": "Keep-Alive",
                            "User-Agent": "okhttp/4.4.1",
                        },
                        timeout=10,
                    )
                    response_data = response.json()
                    self.devicedata = response_data
                    _LOGGER.debug(json.dumps(response_data))

                    if not response_data:
                        continue

                    if response_data["code"] != 0:
                        _LOGGER.debug(response_data)
                        continue

                except Exception as error:
                    if hasattr(error, "response"):
                        if error.response.status == 401:
                            _LOGGER.debug(json.dumps(error.response.json()))
                            _LOGGER.debug(
                                "{element['path']} receive 401 error. Refresh Token in 60 seconds"
                            )
                            if self.refresh_token_timeout:
                                self.refresh_token_timeout.cancel()
                            self.refresh_token_timeout = Timer(60, self.refresh_token)
                            self.refresh_token_timeout.start()
                            return

                    _LOGGER.debug(element["url"])
                    _LOGGER.debug(error)
                    if hasattr(error, "response"):
                        _LOGGER.debug(json.dumps(error.response.json()))

    def refresh_token(self):
        """Refresh token."""
        _LOGGER.debug("Refresh token")

        try:
            response = requests.post(
                url="http://server.sk-robot.com/api/auth/oauth/token",
                headers={
                    "Accept-Language": "da",
                    "Authorization": "Basic YXBwOmFwcA==",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Host": "server.sk-robot.com",
                    "Connection": "Keep-Alive",
                    "User-Agent": "okhttp/4.4.1",
                },
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.session["refresh_token"],
                    "scope": "server",
                },
                timeout=10,
            )
            response_data = response.json()
            _LOGGER.debug(json.dumps(response_data))
            self.session = response_data
            _LOGGER.debug("Refresh successful")
        except Exception as error:
            _LOGGER.debug(error)
            if hasattr(error, "response"):
                _LOGGER.debug(json.dumps(error.response.json()))

    def unload(self):
        """Unload."""
        if self.refresh_token_timeout:
            self.refresh_token_timeout.cancel()
        if self.refresh_token_interval:
            self.refresh_token_interval.cancel()

    def start_mowing(self):
        """Start Mowing."""
        self.set_state_change("mode", 1)

    def dock(self):
        """Dock."""
        self.set_state_change("mode", 2)

    def pause(self):
        """Pause."""
        self.set_state_change("mode", 0)

    def border(self):
        """Pause."""
        self.set_state_change("mode", 4)

    def refresh(self):
        """Refresh data."""
        self.update_devices()

    def set_state_change(self, command, state):
        """Command is "mode" and state is 1 = Start, 0 = Pause, 2 = Home, 4 = Border."""
        device_id = self.DeviceSn  # self.devicedata["data"].get("id")
        try:
            response = requests.post(
                url=f"http://server.sk-robot.com/api/mower/device/setWorkStatus/{device_id}/"
                f"{self.session['user_id']}?{command}={state}",
                headers={
                    "Accept-Language": "da",
                    "Authorization": "bearer " + self.session["access_token"],
                    "Content-Type": "application/json",
                    "Host": "server.sk-robot.com",
                    "Connection": "Keep-Alive",
                    "User-Agent": "okhttp/4.4.1",
                },
                timeout=10,
            )
            response_data = response.json()
            _LOGGER.debug(json.dumps(response_data))
        except Exception as error:
            _LOGGER.debug(error)
            if hasattr(error, "response"):
                _LOGGER.debug(json.dumps(error.response.json()))

        refresh_timeout = Timer(10, self.update_devices)
        refresh_timeout.start()

    @property
    def DeviceModel(self):
        """Model."""
        for device in self.devicelist["data"]:
            deviceSn = device["deviceModelName"]
        return deviceSn

    @property
    def DeviceSn(self):
        """Serienumber."""
        for device in self.devicelist["data"]:
            deviceSn = device["deviceSn"]
        return deviceSn

    @property
    def DeviceName(self):
        """Devicename."""
        for device in self.devicelist["data"]:
            name = device["deviceName"]
        return name

    @property
    def DeviceBluetooth(self):
        """Bluetooth."""
        for device in self.devicelist["data"]:
            name = device["bluetoothMac"]
        return name

    @property
    def DeviceSW(self):
        """Device software."""
        name = self.devicedata["data"].get("bbSv")
        return name

    @property
    def DeviceHW(self):
        """Device hardware."""
        name = self.devicedata["data"].get("bbHv")
        return name

    @property
    def faultStatusName(self):
        """Fault text."""
        name = self.devicedata["data"].get("faultStatusName")
        return name
