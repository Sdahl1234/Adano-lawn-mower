"""Support for Adano lawnmower."""

from __future__ import annotations

import logging

from homeassistant.components.lawn_mower import (
    #    SERVICE_DOCK,
    #    SERVICE_PAUSE,
    #    SERVICE_START_MOWING,
    #    LawnMowerActivity,
    LawnMowerEntity,
    LawnMowerEntityFeature,
)

# from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# from homeassistant.helpers.entity import Entity, EntityDescription
# from homeassistant.helpers.entity_component import EntityComponent
# from homeassistant.helpers.typing import ConfigType
from . import AdanoDataCoordinator
from .const import (
    ADANO_CHARGING,
    ADANO_GOING_HOME,
    ADANO_MOWING,
    ADANO_MOWING_BORDER,
    ADANO_STANDBY,
    ADANO_UNKNOWN,
    DOMAIN,
)
from .entity import AdanoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Do setup entry."""
    async_add_entities([AdanoLawnMower(hass.data[DOMAIN][entry.entry_id])])


class AdanoLawnMower(AdanoEntity, LawnMowerEntity):
    """LawnMower."""

    def __init__(self, coordinator: AdanoDataCoordinator) -> None:
        """Initialize the heater."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._data_handler = self.coordinator.data_handler
        self._name = self._data_handler.DeviceName

    @property
    def translation_key(self) -> str:
        """Translationkey."""
        return "adano_lawnmower"

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return (
            LawnMowerEntityFeature.START_MOWING
            | LawnMowerEntityFeature.PAUSE
            | LawnMowerEntityFeature.DOCK
        )

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"adano_lawnmower.{self._data_handler.DeviceName}"

    @property
    def name(self):
        """Return the name of the device, if any."""
        return self._name

    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return True

    @property
    def state(self) -> str | None:
        """Return the current state."""
        if self._data_handler.errortype != 0:
            return (
                "Fejl: "
                + self._data_handler.faultStatusName
                + " ("
                + str(self._data_handler.errortype)
                + ")"
            )
        ival = self._data_handler.mode
        if ival == 0:
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
        return val

    async def async_start_mowing(self) -> None:
        """Start or resume mowing."""
        await self.hass.async_add_executor_job(self._data_handler.start_mowing)

    async def async_dock(self) -> None:
        """Dock the mower."""
        await self.hass.async_add_executor_job(self._data_handler.dock)

    async def async_pause(self) -> None:
        """Pause the lawn mower."""
        await self.hass.async_add_executor_job(self._data_handler.pause)

    async def async_update(self):
        """Get the latest data."""
        self._data_handler = self.coordinator.data_handler
