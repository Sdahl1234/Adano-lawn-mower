"""Support for Adano lawnmower."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant

from . import AdanoDataCoordinator, robot_coordinators
from .entity import AdanoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Do setup entry."""

    async_add_entities(
        [
            AdanoButton(coordinator, "Start", "start", "adano_start")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoButton(coordinator, "Home", "home", "adano_home")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoButton(coordinator, "Pause", "pause", "adano_pause")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoButton(coordinator, "Border", "border", "adano_border")
            for coordinator in robot_coordinators(hass, entry)
        ]
    )


class AdanoButton(AdanoEntity, ButtonEntity):
    """LawnMower buttons."""

    def __init__(
        self,
        coordinator: AdanoDataCoordinator,
        name: str,
        valuepair: str,
        translationkey: str,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self.data_coordinator = coordinator
        self._data_handler = self.data_coordinator.data_handler
        self._name = name
        self._valuepair = valuepair
        self._attr_has_entity_name = True
        self._attr_translation_key = translationkey
        self._attr_unique_id = f"{self._name}_{self.data_coordinator.dsn}"
        self._sn = self.coordinator._devicesn

    async def async_press(self) -> None:
        """Handle the button press."""
        if self._valuepair == "home":
            await self.hass.async_add_executor_job(self._data_handler.dock, self._sn)
        elif self._valuepair == "start":
            await self.hass.async_add_executor_job(
                self._data_handler.start_mowing, self._sn
            )
        elif self._valuepair == "pause":
            await self.hass.async_add_executor_job(self._data_handler.pause, self._sn)
        elif self._valuepair == "border":
            await self.hass.async_add_executor_job(self._data_handler.border, self._sn)
