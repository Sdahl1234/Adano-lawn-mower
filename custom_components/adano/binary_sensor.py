"""Sensor."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant

from . import AdanoDataCoordinator, robot_coordinators
from .entity import AdanoEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Async Setup entry."""

    async_add_devices(
        [
            AdanoBinarySensor(
                coordinator,
                BinarySensorDeviceClass.PRESENCE,
                "Dock",
                None,
                "Station",
                "",
                "adano_dock",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )

    async_add_devices(
        [
            AdanoBinarySensor(
                coordinator,
                None,  # BinarySensorDeviceClass.PRESENCE,
                "Rain sensor active",
                None,
                "rain_en",
                "mdi:weather-pouring",
                "adano_rain_sensor_active",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )

    async_add_devices(
        [
            AdanoBinarySensor(
                coordinator,
                None,
                "Multizone",
                None,
                "mul_en",
                "",
                "adano_multizone",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )

    async_add_devices(
        [
            AdanoBinarySensor(
                coordinator,
                None,
                "Multizone auto",
                None,
                "mul_auto",
                "",
                "adano_multizoneauto",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )

    async_add_devices(
        [
            AdanoBinarySensor(
                coordinator,
                BinarySensorDeviceClass.CONNECTIVITY,
                "Online",
                None,
                "deviceOnlineFlag",
                "mdi:wifi",
                "adano_online",
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )


class AdanoBinarySensor(AdanoEntity, BinarySensorEntity):
    """Adano sensor."""

    def __init__(
        self,
        coordinator: AdanoDataCoordinator,
        device_class: BinarySensorDeviceClass,
        name: str,
        unit: str,
        valuepair: str,
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
        self._icon = icon
        self._attr_has_entity_name = True
        self._attr_translation_key = translationkey
        self._attr_unique_id = f"{self._name}_{self.data_coordinator.dsn}"
        self._sn = self.coordinator._devicesn

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will reflect this.
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return True  # self._data_handler.is_online

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._valuepair == "Station":
            return self._data_handler.get_device(self._sn).station
        if self._valuepair == "rain_en":
            return self._data_handler.get_device(self._sn).rain_en
        if self._valuepair == "mul_en":
            return self._data_handler.get_device(self._sn).mul_en
        if self._valuepair == "mul_auto":
            return self._data_handler.get_device(self._sn).mul_auto
        if self._valuepair == "deviceOnlineFlag":
            return (
                self._data_handler.get_device(self._sn).deviceOnlineFlag
                == '{"online":"1"}'
            )

    @property
    def icon(self):
        """Icon."""
        return self._icon
