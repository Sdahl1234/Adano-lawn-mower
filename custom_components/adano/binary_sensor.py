"""Sensor."""
# from homeassistant.components.sensor import BinarySensorEntity, SensorDeviceClass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant

# from homeassistant.helpers.update_coordinator import (
#    CoordinatorEntity,
#    DataUpdateCoordinator,
#    UpdateFailed,
# )
from . import AdanoDataCoordinator
from .const import DOMAIN
from .entity import AdanoEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Async Setup entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        [
            AdanoBinarySensor(
                coordinator,
                BinarySensorDeviceClass.PRESENCE,
                "Dock",
                "",
                "Station",
                "mqtt",
                "",
                "adano_dock",
            )
        ]
    )

    async_add_devices(
        [
            AdanoBinarySensor(
                coordinator,
                None,  # BinarySensorDeviceClass.PRESENCE,
                "Rain sensor active",
                "",
                "rain_en",
                "mqtt",
                "mdi:weather-pouring",
                "adano_rain_sensor_active",
            )
        ]
    )

    async_add_devices(
        [
            AdanoBinarySensor(
                coordinator,
                None,
                "Multizone",
                "",
                "mul_en",
                "mqtt",
                "",
                "adano_multizone",
            )
        ]
    )

    async_add_devices(
        [
            AdanoBinarySensor(
                coordinator,
                None,
                "Multizone auto",
                "",
                "mul_auto",
                "mqtt",
                "",
                "adano_multizoneauto",
            )
        ]
    )

    async_add_devices(
        [
            AdanoBinarySensor(
                coordinator,
                BinarySensorDeviceClass.CONNECTIVITY,
                "Online",
                "",
                "deviceOnlineFlag",
                "mqtt",
                "mdi:wifi",
                "adano_online",
            )
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

        # self.translation_key = translationkey
        # self._attr_has_entity_name = True

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
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._valuepair == "Station":
            return self._data_handler.station
        elif self._valuepair == "rain_en":
            return self._data_handler.rain_en
        elif self._valuepair == "mul_en":
            return self._data_handler.mul_en
        elif self._valuepair == "mul_auto":
            return self._data_handler.mul_auto
        elif self._valuepair == "deviceOnlineFlag":
            return self._data_handler.deviceOnlineFlag == '{"online":"1"}'

    # @property
    # def device_class(self):
    #    """Return the class of this device."""
    #    return self._attr_device_class

    # @property
    # def entity_category(self):
    #    """Return the entity category of this device."""
    #    return ATTRIB_TO_ENTTIY_CATEGORY.get(self._attribute)

    @property
    def icon(self):
        """Icon."""
        return self._icon
