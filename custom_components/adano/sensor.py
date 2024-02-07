"""Sensor."""
# import logging
import time

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

# from homeassistant.helpers.update_coordinator import (
#    CoordinatorEntity,
#    DataUpdateCoordinator,
#    UpdateFailed,
# )
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant

from . import AdanoDataCoordinator
from .const import (
    ADANO_CHARGING,
    ADANO_DRY,
    ADANO_DRY_COUNTDOWN,
    ADANO_GOING_HOME,
    ADANO_MOWING,
    ADANO_MOWING_BORDER,
    ADANO_STANDBY,
    ADANO_UNKNOWN,
    ADANO_WET,
    DOMAIN,
)
from .entity import AdanoEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Async Setup entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        [
            AdanoSensorInt(
                coordinator,
                SensorDeviceClass.BATTERY,
                "Battery",
                PERCENTAGE,
                "Power",
                "mqtt",
                "mdi:battery",
                "adano_battery",
            )
        ]
    )
    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "Mower status",
                "",
                "Mode",
                "mqtt",
                "",
                "adano_mower_state",
            )
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
                "mqtt",
                "mdi:wifi",
                "adano_wifi_level",
            )
        ]
    )

    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "Rain sensor",
                "",
                "rain_status",
                "mqtt",
                "mdi:weather-pouring",
                "adano_rain_status",
            )
        ]
    )

    async_add_devices(
        [
            AdanoSensorInt(
                coordinator,
                SensorDeviceClass.DURATION,
                "Rain senor wait time",
                "min",
                "rain_delay_set",
                "mqtt",
                "mdi:clock-time-three-outline",
                "adano_rain_delay_set",
            )
        ]
    )
    async_add_devices(
        [
            AdanoSensorInt(
                coordinator,
                SensorDeviceClass.DURATION,
                "Rain sensor time left",
                "min",
                "rain_delay_left",
                "mqtt",
                "mdi:clock-time-three-outline",
                "adano_sensor_counter",
            )
        ]
    )

    async_add_devices(
        [
            AdanoSensorInt(
                coordinator,
                SensorDeviceClass.DURATION,
                "Actual mowing time",
                "min",
                "cur_min",
                "mqtt",
                "mdi:clock-time-three-outline",
                "adano_mowing_time",
            )
        ]
    )
    async_add_devices(
        [
            AdanoSensorInt(
                coordinator,
                SensorDeviceClass.POWER_FACTOR,
                "Zone 1 start",
                "%",
                "mul_zon1",
                "mqtt",
                "mdi:map",
                "adanozone1",
            )
        ]
    )
    async_add_devices(
        [
            AdanoSensorInt(
                coordinator,
                SensorDeviceClass.POWER_FACTOR,
                "Zone 2 start",
                "%",
                "mul_zon2",
                "mqtt",
                "mdi:map",
                "adanozone2",
            )
        ]
    )
    async_add_devices(
        [
            AdanoSensorInt(
                coordinator,
                SensorDeviceClass.POWER_FACTOR,
                "Zone 3 start",
                "%",
                "mul_zon3",
                "mqtt",
                "mdi:map",
                "adanozone3",
            )
        ]
    )
    async_add_devices(
        [
            AdanoSensorInt(
                coordinator,
                SensorDeviceClass.POWER_FACTOR,
                "Zone 4 start",
                "%",
                "mul_zon4",
                "mqtt",
                "mdi:map",
                "adanozone4",
            )
        ]
    )
    #
    async_add_devices(
        [
            AdanoSensorInt(
                coordinator,
                None,
                "Error code",
                "",
                "errortype",
                "mqtt",
                "mdi:alert-circle",
                "adano_error",
            )
        ]
    )

    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "ErrorText",
                "",
                "faultStatusName",
                "devicedata",
                "mdi:alert-circle",
                "adano_error_text",
            )
        ]
    )

    async_add_devices(
        [
            AdanoSensor(
                coordinator,
                None,
                "Schedule",
                "",
                "Schedule",
                "mqtt",
                "mdi:calendar",
                "adano_schedule",
            )
        ]
    )

    if 1 == 2:  # noqa: PLR0133
        for device in coordinator.data_handler.devicelist["data"]:
            for valpairs in device:
                async_add_devices(
                    [
                        AdanoSensor(
                            coordinator, None, valpairs, "", valpairs, "devicelist", ""
                        )
                    ]
                )

    if 1 == 2:  # noqa: PLR0133
        data = coordinator.data_handler.devicedata["data"]
        for valpairs in data:
            async_add_devices(
                [
                    AdanoSensor(
                        coordinator, None, valpairs, "", valpairs, "devicedata", ""
                    )
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
        self._attr_unique_id = self._name

        self._attr_state_class = None
        self._attr_entity_category = None

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
                )
            if End is not None:
                attributes[f"{day}_End"] = time.strftime(
                    "%H:%M", time.gmtime(int(End) * 60)
                )
            if Trimming is not None:
                attributes[f"{day}_Border"] = Trimming

    # @property
    # def name(self):
    #    """Return the name of the sensor."""
    #    return self._name

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will reflect this.
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return True  # self._data_handler.is_online

    # @property
    # def unique_id(self):
    #    """Return a unique ID."""
    #    # return "adano_Adano_adano"
    #    return f"{self._name}_{self._source}_{self._valuepair}"

    @property
    def state(self):  # noqa: C901
        """State."""
        # Hent data fra data_handler her
        if self._source == "devicelist":
            for device in self._data_handler.devicelist["data"]:
                val = device[self._valuepair]
        elif self._source == "devicedata":
            val = self._data_handler.devicedata["data"].get(self._valuepair)
        elif self._valuepair == "Mode":
            ival = self._data_handler.mode
            if self._data_handler.errortype != 0:
                val = (
                    "Fejl: "
                    + self._data_handler.faultStatusName
                    + " ("
                    + str(self._data_handler.errortype)
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
                val = ADANO_MOWING_BORDER
            elif ival == 7:
                val = ADANO_UNKNOWN
            else:
                val = ADANO_UNKNOWN
        elif self._valuepair == "wifi_lv":
            val = self._data_handler.wifi_lv
        elif self._valuepair == "rain_status":
            ival = self._data_handler.rain_status
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
        return val

    @property
    def extra_state_attributes(self):  # noqa: C901
        """Attributes to schedule."""
        attributes = {}
        if self._valuepair == "Schedule":
            data = self._data_handler.Mon
            self.AddAttributes("Monday", data, attributes)
            data = self._data_handler.Tue
            self.AddAttributes("Tuesday", data, attributes)
            data = self._data_handler.Wed
            self.AddAttributes("Wednesday", data, attributes)
            data = self._data_handler.Thu
            self.AddAttributes("Thursday", data, attributes)
            data = self._data_handler.Fri
            self.AddAttributes("Friday", data, attributes)
            data = self._data_handler.Sat
            self.AddAttributes("Saturday", data, attributes)
            data = self._data_handler.Sun
            self.AddAttributes("Sunday", data, attributes)

        return attributes

    @property
    def icon(self):
        """Icon."""
        return self._icon


class AdanoSensorInt(AdanoEntity, SensorEntity):
    """Adano sensor integer."""

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
        self._attr_unique_id = self._name

    # @property
    # def name(self):
    #    """Return the name of the sensor."""
    #    return self._name

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will reflect this.
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return True  # self._data_handler.is_online

    # @property
    # def unique_id(self):
    #    """Return a unique ID."""
    #    return f"{self._name}_{self._source}_{self._valuepair}"

    @property
    def native_value(self):
        """Return value."""
        if self._valuepair == "Power":
            return self._data_handler.power
        if self._valuepair == "rain_delay_set":
            return self._data_handler.rain_delay_set
        if self._valuepair == "rain_delay_left":
            return self._data_handler.rain_delay_left
        if self._valuepair == "cur_min":
            return self._data_handler.cur_min
        if self._valuepair == "mul_zon1":
            return self._data_handler.mul_zon1
        if self._valuepair == "mul_zon2":
            return self._data_handler.mul_zon2
        if self._valuepair == "mul_zon3":
            return self._data_handler.mul_zon3
        if self._valuepair == "mul_zon4":
            return self._data_handler.mul_zon4
        if self._valuepair == "errortype":
            return self._data_handler.errortype

    @property
    def icon(self):
        """Icon."""
        return self._icon