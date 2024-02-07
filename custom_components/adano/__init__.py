"""Adano mower integration."""
from datetime import timedelta
import logging

import async_timeout  # noqa: TID251

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant

# from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .adano import AdanoRoboticmower
from .const import DOMAIN

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.LAWN_MOWER,
    Platform.SENSOR,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config):  # noqa: D103
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Adano mower."""
    email = entry.data.get(CONF_EMAIL)
    password = entry.data.get(CONF_PASSWORD)

    data_handler = AdanoRoboticmower(email, password)
    await hass.async_add_executor_job(data_handler.on_load)
    data_coordinator = AdanoDataCoordinator(hass, data_handler)

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    hass.data[DOMAIN][entry.entry_id] = data_coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_entry))

    return True


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class AdanoDataCoordinator(DataUpdateCoordinator):  # noqa: D101
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, data_handler) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=DOMAIN,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=5),  # 60 * 60),
        )
        self.data_handler = data_handler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self.unique_id),
            },
            model=self.data_handler.DeviceModel,
            manufacturer="Adano Robotic Mower",
            serial_number=self.data_handler.DeviceSn,
            name=self.data_handler.DeviceName,
            sw_version=self.data_handler.DeviceSW,
            hw_version=self.data_handler.DeviceHW,
        )

    @property
    def unique_id(self) -> str:
        """Return the system descriptor."""
        entry = self.config_entry
        if entry.unique_id:
            return entry.unique_id
        assert entry.entry_id
        return entry.entry_id

    async def _async_update_data(self):
        _LOGGER.debug("_async_update_data")

        if self.data_handler.forceupdate:
            self.data_handler.forceupdate = False
            try:
                await self.hass.async_add_executor_job(self.data_handler.update_devices)
            except Exception as ex:
                _LOGGER.debug(f"forced updated failed: {ex}")  # noqa: G004
        else:
            try:
                async with async_timeout.timeout(100):
                    await self.data_handler.update()
                    return self.data_handler
            except Exception as ex:
                _LOGGER.debug(f"_async_update timed out: {ex}")  # noqa: G004
