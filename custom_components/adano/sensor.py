"""Sensor."""

# import logging
import time

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant

from . import AdanoDataCoordinator, robot_coordinators
from .const import (
    ADANO_CHARGING,
    ADANO_DRY,
    ADANO_DRY_COUNTDOWN,
    ADANO_GOING_HOME,
    ADANO_MOWING,
    ADANO_MOWING_BORDER,
    ADANO_STANDBY,
    ADANO_UNKNOWN,
    ADANO_UNKNOWN_4,
    ADANO_WET,
)
from .entity import AdanoEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Async Setup entry."""

    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                SensorDeviceClass.BATTERY,
                "Battery",
                PERCENTAGE,
                "Power",
                "",
                "mdi:battery",
                "adano_battery",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "Mower status",
                None,
                "Mode",
                "",
                "",
                "adano_mower_state",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "Wifi level",
                "Streger",
                "wifi_lv",
                "",
                "mdi:wifi",
                "adano_wifi_level",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "State change error",
                None,
                "state_error",
                "",
                "mdi:alert-circle",
                "adano_state_error",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "Rain sensor",
                None,
                "rain_status",
                "",
                "mdi:weather-pouring",
                "adano_rain_status",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                SensorDeviceClass.DURATION,
                "Rain senor wait time",
                "min",
                "rain_delay_set",
                "",
                "mdi:clock-time-three-outline",
                "adano_rain_delay_set",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                SensorDeviceClass.DURATION,
                "Rain sensor time left",
                "min",
                "rain_delay_left",
                "",
                "mdi:clock-time-three-outline",
                "adano_sensor_counter",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                SensorDeviceClass.DURATION,
                "Actual mowing time",
                "min",
                "cur_min",
                "",
                "mdi:clock-time-three-outline",
                "adano_mowing_time",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                SensorDeviceClass.POWER_FACTOR,
                "Zone 1 start",
                "%",
                "mul_zon1",
                "",
                "mdi:map",
                "adanozone1",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                SensorDeviceClass.POWER_FACTOR,
                "Zone 2 start",
                "%",
                "mul_zon2",
                "",
                "mdi:map",
                "adanozone2",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                SensorDeviceClass.POWER_FACTOR,
                "Zone 3 start",
                "%",
                "mul_zon3",
                "",
                "mdi:map",
                "adanozone3",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                SensorDeviceClass.POWER_FACTOR,
                "Zone 4 start",
                "%",
                "mul_zon4",
                "",
                "mdi:map",
                "adanozone4",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "Error code",
                None,
                "errortype",
                "",
                "mdi:alert-circle",
                "adano_error",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "ErrorText",
                None,
                "errortype",
                "Etext",
                "mdi:alert-circle",
                "adano_error_text",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "Schedule",
                None,
                "Schedule",
                "",
                "mdi:calendar",
                "adano_schedule",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )


class AdanoSensor(AdanoEntity, SensorEntity):
    """Adano sensor."""

    def __init__(
        self,
        coordinator: AdanoDataCoordinator,
        device_class: SensorDeviceClass,
        name: str,
        unit: str,
        valuepair: str,
        source: str,
        icon: str,
        translationkey: str,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self.data_coordinator = coordinator
        self._data_handler = self.data_coordinator.data_handler
        self._name = name
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._valuepair = valuepair
        self._source = source
        self._icon = icon
        self._attr_has_entity_name = True
        self._attr_translation_key = translationkey
        self._attr_unique_id = f"{self._name}_{self.data_coordinator.dsn}"
        self._sn = self.coordinator.devicesn

    def AddAttributes(self, day: str, data: any, attributes: dict) -> None:
        """Add schedule."""

        if len(data) > 0:
            Start = None
            End = None
            Trimming = None
            for key, value in data.items():
                if key == "slice":
                    for a in value[0].items():
                        if a[0] == "start":
                            Start = a[1]
                        if a[0] == "end":
                            End = a[1]
                if key == "Trimming":
                    Trimming = value
            if Start is not None:
                attributes[f"{day}_Start"] = time.strftime(
                    "%H:%M", time.gmtime(int(Start) * 60)
                )[0:5]
            if End is not None:
                attributes[f"{day}_End"] = time.strftime(
                    "%H:%M", time.gmtime(int(End) * 60)
                )[0:5]
            if Trimming is not None:
                attributes[f"{day}_Border"] = Trimming

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will reflect this.
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return True

    @property
    def state(self):  # noqa: C901
        """State."""
        # Hent data fra data_handler her
        if self._source == "devicedata":
            val = (
                self._data_handler.get_device(self._sn)
                .devicedata["data"]
                .get(self._valuepair)
            )
        elif self._valuepair == "Mode":
            ival = self._data_handler.get_device(self._sn).mode
            if self._data_handler.get_device(self._sn).errortype != 0:
                val = (
                    self._data_handler.get_device(self._sn)
                    .devicedata["data"]
                    .get("faultStatusCode")
                    + " ("
                    + str(self._data_handler.get_device(self._sn).errortype)
                    + ")"
                )
            elif ival == 0:
                val = ADANO_STANDBY
            elif ival == 1:
                val = ADANO_MOWING
            elif ival == 2:
                val = ADANO_GOING_HOME
            elif ival == 3:
                val = ADANO_CHARGING
            elif ival == 4:
                val = ADANO_UNKNOWN_4
            elif ival == 7:
                val = ADANO_MOWING_BORDER
            else:
                val = ADANO_UNKNOWN
        elif self._valuepair == "wifi_lv":
            val = self._data_handler.get_device(self._sn).wifi_lv
        elif self._valuepair == "rain_status":
            ival = self._data_handler.get_device(self._sn).rain_status
            if ival == 0:
                val = ADANO_DRY
            elif ival == 1:
                val = ADANO_DRY_COUNTDOWN
            elif ival == 2:
                val = ADANO_WET
            else:
                val = ADANO_UNKNOWN
        elif self._valuepair == "Schedule":
            val = "Schedule"
        elif self._valuepair == "state_error":
            val = self._data_handler.get_device(self._sn).error_text
        elif self._valuepair == "Power":
            val = self._data_handler.get_device(self._sn).power
        elif self._valuepair == "rain_delay_set":
            val = self._data_handler.get_device(self._sn).rain_delay_set
        elif self._valuepair == "rain_delay_left":
            val = self._data_handler.get_device(self._sn).rain_delay_left
        elif self._valuepair == "cur_min":
            val = self._data_handler.get_device(self._sn).cur_min
        elif self._valuepair == "mul_zon1":
            val = self._data_handler.get_device(self._sn).mul_zon1
        elif self._valuepair == "mul_zon2":
            val = self._data_handler.get_device(self._sn).mul_zon2
        elif self._valuepair == "mul_zon3":
            val = self._data_handler.get_device(self._sn).mul_zon3
        elif self._valuepair == "mul_zon4":
            val = self._data_handler.get_device(self._sn).mul_zon4
        elif self._valuepair == "errortype":
            val = self._data_handler.get_device(self._sn).errortype
            if self._source == "Etext":
                if val == 0:
                    val = "normal"
                elif val == 2:
                    val = "For mange forhindringer"
                elif val == 16:
                    val = "Uden for kanttråden"
                elif val == 32:
                    val = "Startet uden for kanttråden"
                elif val == 262144:
                    val = "Ladestrømmen er for høj"
                else:
                    val = "Ukendt fejl"
        return val

    @property
    def extra_state_attributes(self):
        """Attributes to schedule."""
        attributes = {}
        if self._valuepair == "Schedule":
            data = self._data_handler.get_device(self._sn).Schedule.GetDay(1).mqtt_day
            self.AddAttributes("Monday", data, attributes)
            data = self._data_handler.get_device(self._sn).Schedule.GetDay(2).mqtt_day
            self.AddAttributes("Tuesday", data, attributes)
            data = self._data_handler.get_device(self._sn).Schedule.GetDay(3).mqtt_day
            self.AddAttributes("Wednesday", data, attributes)
            data = self._data_handler.get_device(self._sn).Schedule.GetDay(4).mqtt_day
            self.AddAttributes("Thursday", data, attributes)
            data = self._data_handler.get_device(self._sn).Schedule.GetDay(5).mqtt_day
            self.AddAttributes("Friday", data, attributes)
            data = self._data_handler.get_device(self._sn).Schedule.GetDay(6).mqtt_day
            self.AddAttributes("Saturday", data, attributes)
            data = self._data_handler.get_device(self._sn).Schedule.GetDay(7).mqtt_day
            self.AddAttributes("Sunday", data, attributes)

        return attributes

    @property
    def icon(self):
        """Icon."""
        return self._icon
