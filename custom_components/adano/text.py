"""Support for Adano lawnmower."""

from __future__ import annotations

import json
import logging

from homeassistant.components.text import TextEntity
from homeassistant.core import HomeAssistant

from . import AdanoDataCoordinator, robot_coordinators
from .entity import AdanoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Do setup entry."""

    async_add_entities(
        [
            AdanoScheduleText(
                coordinator, "Schedule Monday", 1, "adano_schedule_text_1"
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoScheduleText(
                coordinator, "Schedule Tuesday", 2, "adano_schedule_text_2"
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoScheduleText(
                coordinator, "Schedule Wednesday", 3, "adano_schedule_text_3"
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoScheduleText(
                coordinator, "Schedule Thursday", 4, "adano_schedule_text_4"
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoScheduleText(
                coordinator, "Schedule Fridays", 5, "adano_schedule_text_5"
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoScheduleText(
                coordinator, "Schedule Saturday", 6, "adano_schedule_text_6"
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )
    async_add_entities(
        [
            AdanoScheduleText(
                coordinator, "Schedule Sunday", 7, "adano_schedule_text_7"
            )
            for coordinator in robot_coordinators(hass, entry)
        ]
    )


class AdanoScheduleText(AdanoEntity, TextEntity):
    """LawnMower Schedule text."""

    def __init__(
        self,
        coordinator: AdanoDataCoordinator,
        name: str,
        daynumber: int,
        translationkey: str,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self.data_coordinator = coordinator
        self._data_handler = self.data_coordinator.data_handler
        self._name = name
        self.mode = "text"
        self.native_max = 255
        self.native_min = 0
        self.daynumber = daynumber
        self._attr_has_entity_name = True
        self._attr_translation_key = translationkey
        self._attr_unique_id = f"{self._name}_{self.data_coordinator.dsn}"
        self._sn = self.coordinator._devicesn

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        try:
            # 06:15 - 23:30 Trim
            start = value[0:5]
            stop = value[8:13]
            trim = False
            if "Trim" in value:
                trim = True
            elif "trim" in value:
                trim = True

            retval2 = {
                "start": start,
                "stop": stop,
                "trim": trim,
            }
            retval3 = (
                str(retval2)
                .replace("'", '"')
                .replace("True", "true")
                .replace("False", "false")
            )
            val = json.loads(retval3)
            self._data_handler.get_device(self._sn).Schedule.GetDay(
                self.daynumber
            ).start = val["start"]
            self._data_handler.get_device(self._sn).Schedule.GetDay(
                self.daynumber
            ).end = val["stop"]
            self._data_handler.get_device(self._sn).Schedule.GetDay(
                self.daynumber
            ).trim = val["trim"]

        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.debug(error)

        await self.hass.async_add_executor_job(
            self._data_handler.set_schedule,
            self._data_handler.get_device(self._sn).Schedule.days,
            self._sn,
        )

    @property
    def native_value(self):
        """Return value."""
        b_trim = (
            self._data_handler.get_device(self._sn).Schedule.GetDay(self.daynumber).trim
        )
        if b_trim:
            s_trim = " Trim"
        else:
            s_trim = ""
        retval = {
            self._data_handler.get_device(self._sn)
            .Schedule.GetDay(self.daynumber)
            .start
            + " - "
            + self._data_handler.get_device(self._sn)
            .Schedule.GetDay(self.daynumber)
            .end
            + s_trim
        }

        return str(retval).replace("{", "").replace("}", "").replace("'", "")
