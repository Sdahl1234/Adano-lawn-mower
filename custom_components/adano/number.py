"""Support for Adano lawnmower."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant

from . import AdanoDataCoordinator, robot_coordinators
from .entity import AdanoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Do setup entry."""

    async_add_entities(
        [
            AdanoRainDelayNumber(coordinator, "Rain delay", "adano_rain_delay")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoZoneNumber(coordinator, "Zone1", 1, "adano_zone1")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoZoneNumber(coordinator, "Zone2", 2, "adano_zone2")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoZoneNumber(coordinator, "Zone3", 3, "adano_zone3")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoZoneNumber(coordinator, "Zone4", 4, "adano_zone4")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )

    async_add_entities(
        [
            AdanoMulNumber(coordinator, "MulZone1", 1, "adano_mulpro1")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoMulNumber(coordinator, "MulZone2", 2, "adano_mulpro2")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoMulNumber(coordinator, "MulZone3", 3, "adano_mulpro3")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoMulNumber(coordinator, "MulZone4", 4, "adano_mulpro4")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )


class AdanoRainDelayNumber(AdanoEntity, NumberEntity):
    """LawnMower number."""

    def __init__(
        self,
        coordinator: AdanoDataCoordinator,
        name: str,
        translationkey: str,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self.data_coordinator = coordinator
        self._data_handler = self.data_coordinator.data_handler
        self._name = name
        self.native_max_value = 720
        self.native_min_value = 0
        self.native_step = 1
        self.native_unit_of_measurement = "min"
        self._attr_has_entity_name = True
        self._attr_translation_key = translationkey
        self._attr_unique_id = f"{self._name}_{self.data_coordinator.dsn}"
        self._sn = self.coordinator.devicesn
        self.icon = "mdi:clock-time-three-outline"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.hass.async_add_executor_job(
            self._data_handler.set_rain_status,
            self._data_handler.get_device(self._sn).rain_en,
            value,
            self._sn,
        )

    @property
    def native_value(self):
        """Return value."""
        return self._data_handler.get_device(self._sn).rain_delay_set


class AdanoZoneNumber(AdanoEntity, NumberEntity):
    """LawnMower number."""

    def __init__(
        self,
        coordinator: AdanoDataCoordinator,
        name: str,
        zonenumber: int,
        translationkey: str,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self.data_coordinator = coordinator
        self._data_handler = self.data_coordinator.data_handler
        self._name = name
        self.native_max_value = 100
        self.native_min_value = 0
        self.native_step = 1
        self.native_unit_of_measurement = "%"
        self._attr_has_entity_name = True
        self._attr_translation_key = translationkey
        self._attr_unique_id = f"{self._name}_{self.data_coordinator.dsn}"
        self._sn = self.coordinator.devicesn
        self.icon = "mdi:map"
        self.zonenumber = zonenumber

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        if self.zonenumber == 1:
            await self.hass.async_add_executor_job(
                self._data_handler.set_zone_status,
                self._data_handler.get_device(self._sn).mul_auto,
                self._data_handler.get_device(self._sn).mul_en,
                value,
                self._data_handler.get_device(self._sn).mul_zon2,
                self._data_handler.get_device(self._sn).mul_zon3,
                self._data_handler.get_device(self._sn).mul_zon4,
                self._data_handler.get_device(self._sn).mulpro_zon1,
                self._data_handler.get_device(self._sn).mulpro_zon2,
                self._data_handler.get_device(self._sn).mulpro_zon3,
                self._data_handler.get_device(self._sn).mulpro_zon4,
                self._sn,
            )
        if self.zonenumber == 2:
            await self.hass.async_add_executor_job(
                self._data_handler.set_zone_status,
                self._data_handler.get_device(self._sn).mul_auto,
                self._data_handler.get_device(self._sn).mul_en,
                self._data_handler.get_device(self._sn).mul_zon1,
                value,
                self._data_handler.get_device(self._sn).mul_zon3,
                self._data_handler.get_device(self._sn).mul_zon4,
                self._data_handler.get_device(self._sn).mulpro_zon1,
                self._data_handler.get_device(self._sn).mulpro_zon2,
                self._data_handler.get_device(self._sn).mulpro_zon3,
                self._data_handler.get_device(self._sn).mulpro_zon4,
                self._sn,
            )
        if self.zonenumber == 3:
            await self.hass.async_add_executor_job(
                self._data_handler.set_zone_status,
                self._data_handler.get_device(self._sn).mul_auto,
                self._data_handler.get_device(self._sn).mul_en,
                self._data_handler.get_device(self._sn).mul_zon1,
                self._data_handler.get_device(self._sn).mul_zon2,
                value,
                self._data_handler.get_device(self._sn).mul_zon4,
                self._data_handler.get_device(self._sn).mulpro_zon1,
                self._data_handler.get_device(self._sn).mulpro_zon2,
                self._data_handler.get_device(self._sn).mulpro_zon3,
                self._data_handler.get_device(self._sn).mulpro_zon4,
                self._sn,
            )
        if self.zonenumber == 4:
            await self.hass.async_add_executor_job(
                self._data_handler.set_zone_status,
                self._data_handler.get_device(self._sn).mul_auto,
                self._data_handler.get_device(self._sn).mul_en,
                self._data_handler.get_device(self._sn).mul_zon1,
                self._data_handler.get_device(self._sn).mul_zon2,
                self._data_handler.get_device(self._sn).mul_zon3,
                value,
                self._data_handler.get_device(self._sn).mulpro_zon1,
                self._data_handler.get_device(self._sn).mulpro_zon2,
                self._data_handler.get_device(self._sn).mulpro_zon3,
                self._data_handler.get_device(self._sn).mulpro_zon4,
                self._sn,
            )

    @property
    def native_value(self):
        """Return value."""
        if self.zonenumber == 1:
            return self._data_handler.get_device(self._sn).mul_zon1
        if self.zonenumber == 2:
            return self._data_handler.get_device(self._sn).mul_zon2
        if self.zonenumber == 3:
            return self._data_handler.get_device(self._sn).mul_zon3
        if self.zonenumber == 4:
            return self._data_handler.get_device(self._sn).mul_zon4


class AdanoMulNumber(AdanoEntity, NumberEntity):
    """LawnMower number."""

    def __init__(
        self,
        coordinator: AdanoDataCoordinator,
        name: str,
        mulnumber: int,
        translationkey: str,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self.data_coordinator = coordinator
        self._data_handler = self.data_coordinator.data_handler
        self._name = name
        self.native_max_value = 100
        self.native_min_value = 0
        self.native_step = 1
        self.native_unit_of_measurement = "%"
        self._attr_has_entity_name = True
        self._attr_translation_key = translationkey
        self._attr_unique_id = f"{self._name}_{self.data_coordinator.dsn}"
        self._sn = self.coordinator.devicesn
        self.icon = "mdi:map"
        self.mulnumber = mulnumber

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        if self.mulnumber == 1:
            await self.hass.async_add_executor_job(
                self._data_handler.set_zone_status,
                self._data_handler.get_device(self._sn).mul_auto,
                self._data_handler.get_device(self._sn).mul_en,
                self._data_handler.get_device(self._sn).mul_zon1,
                self._data_handler.get_device(self._sn).mul_zon2,
                self._data_handler.get_device(self._sn).mul_zon3,
                self._data_handler.get_device(self._sn).mul_zon4,
                value,
                self._data_handler.get_device(self._sn).mulpro_zon2,
                self._data_handler.get_device(self._sn).mulpro_zon3,
                self._data_handler.get_device(self._sn).mulpro_zon4,
                self._sn,
            )
        if self.mulnumber == 2:
            await self.hass.async_add_executor_job(
                self._data_handler.set_zone_status,
                self._data_handler.get_device(self._sn).mul_auto,
                self._data_handler.get_device(self._sn).mul_en,
                self._data_handler.get_device(self._sn).mul_zon1,
                self._data_handler.get_device(self._sn).mul_zon2,
                self._data_handler.get_device(self._sn).mul_zon3,
                self._data_handler.get_device(self._sn).mul_zon4,
                self._data_handler.get_device(self._sn).mulpro_zon1,
                value,
                self._data_handler.get_device(self._sn).mulpro_zon3,
                self._data_handler.get_device(self._sn).mulpro_zon4,
                self._sn,
            )
        if self.mulnumber == 3:
            await self.hass.async_add_executor_job(
                self._data_handler.set_zone_status,
                self._data_handler.get_device(self._sn).mul_auto,
                self._data_handler.get_device(self._sn).mul_en,
                self._data_handler.get_device(self._sn).mul_zon1,
                self._data_handler.get_device(self._sn).mul_zon2,
                self._data_handler.get_device(self._sn).mul_zon3,
                self._data_handler.get_device(self._sn).mul_zon4,
                self._data_handler.get_device(self._sn).mulpro_zon1,
                self._data_handler.get_device(self._sn).mulpro_zon2,
                value,
                self._data_handler.get_device(self._sn).mulpro_zon4,
                self._sn,
            )
        if self.mulnumber == 4:
            await self.hass.async_add_executor_job(
                self._data_handler.set_zone_status,
                self._data_handler.get_device(self._sn).mul_auto,
                self._data_handler.get_device(self._sn).mul_en,
                self._data_handler.get_device(self._sn).mul_zon1,
                self._data_handler.get_device(self._sn).mul_zon2,
                self._data_handler.get_device(self._sn).mul_zon3,
                self._data_handler.get_device(self._sn).mul_zon4,
                self._data_handler.get_device(self._sn).mulpro_zon1,
                self._data_handler.get_device(self._sn).mulpro_zon2,
                self._data_handler.get_device(self._sn).mulpro_zon3,
                value,
                self._sn,
            )

    @property
    def native_value(self):
        """Return value."""
        if self.mulnumber == 1:
            return self._data_handler.get_device(self._sn).mulpro_zon1
        if self.mulnumber == 2:
            return self._data_handler.get_device(self._sn).mulpro_zon2
        if self.mulnumber == 3:
            return self._data_handler.get_device(self._sn).mulpro_zon3
        if self.mulnumber == 4:
            return self._data_handler.get_device(self._sn).mulpro_zon4
