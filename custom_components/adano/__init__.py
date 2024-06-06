"""Adano mower integration."""

import asyncio
import json
import logging
import os

from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .adano import AdanoRoboticmower
from .const import DH, DOMAIN, ROBOTS

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.DEVICE_TRACKER,
    Platform.LAWN_MOWER,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
]

_LOGGER = logging.getLogger(__name__)


def robot_coordinators(hass: HomeAssistant, entry: ConfigEntry):
    """Help with entity setup."""
    coordinators: list[AdanoDataCoordinator] = hass.data[DOMAIN][entry.entry_id][ROBOTS]
    yield from coordinators


async def async_setup(hass: HomeAssistant, config):  # noqa: D103
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Adano mower."""
    email = entry.data.get(CONF_EMAIL)
    password = entry.data.get(CONF_PASSWORD)

    language = hass.config.language

    data_handler = AdanoRoboticmower(email, password, language)
    await hass.async_add_executor_job(data_handler.on_load)
    if not data_handler.login_ok:
        _LOGGER.error("Login error")
        raise ConfigEntryNotReady("Login failed")
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {DH: data_handler}

    # robot = [1, 2]
    robot = data_handler.deviceArray
    robots = [AdanoDataCoordinator(hass, data_handler, devicesn) for devicesn in robot]

    await asyncio.gather(
        *[coordinator.async_config_entry_first_refresh() for coordinator in robots]
    )

    hass.data[DOMAIN][entry.entry_id][ROBOTS] = robots

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

    jdata: None
    data_loaded: bool = False
    data_default = {
        "Monday": "00:00 - 00:00",
        "Tuesday": "00:00 - 00:00",
        "Wednesday": "00:00 - 00:00",
        "Thursday": "00:00 - 00:00",
        "Friday": "00:00 - 00:00",
        "Saturday": "00:00 - 00:00",
        "Sunday": "00:00 - 00:00",
    }

    def __init__(
        self, hass: HomeAssistant, data_handler: AdanoRoboticmower, devicesn
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=DOMAIN,
            # Polling interval. Will only be polled if there are subscribers.
            # update_interval=timedelta(seconds=5),  # 60 * 60),
        )
        self.always_update = True
        self.data_handler = data_handler
        self.devicesn = devicesn
        self.data_handler.get_device(devicesn).dataupdated = self.dataupdated
        self.filepath = os.path.join(
            self.hass.config.config_dir,
            "Schedule-{}.json".format(self.devicesn.replace(" ", "_")),
        )
        _LOGGER.info(self.filepath)
        self.jdata = self.data_default
        self.hass.add_job(self.set_schedule_data)
        self.hass.add_job(self.file_exits)
        self.hass.add_job(self.load_data)

    async def set_schedule_data(self):
        """Set default."""
        self.jdata["Monday"] = await self.GetSchedule(1)
        self.jdata["Tuesday"] = await self.GetSchedule(2)
        self.jdata["Wednesday"] = await self.GetSchedule(3)
        self.jdata["Thursday"] = await self.GetSchedule(4)
        self.jdata["Friday"] = await self.GetSchedule(5)
        self.jdata["Saturday"] = await self.GetSchedule(6)
        self.jdata["Sunday"] = await self.GetSchedule(7)

    async def GetSchedule(self, daynumber: int) -> str:
        """Get schedule."""
        b_trim = (
            self.data_handler.get_device(self.devicesn).Schedule.GetDay(daynumber).trim
        )
        if b_trim:
            s_trim = " Trim"
        else:
            s_trim = ""
        retval = {
            self.data_handler.get_device(self.devicesn).Schedule.GetDay(daynumber).start
            + " - "
            + self.data_handler.get_device(self.devicesn).Schedule.GetDay(daynumber).end
            + s_trim
        }
        return str(retval).replace("{", "").replace("}", "").replace("'", "")

    async def file_exits(self):
        """Do file exists."""
        try:
            f = await self.hass.async_add_executor_job(
                open, self.filepath, "r", -1, "utf-8"
            )
            f.close()
            f.close()
        except FileNotFoundError:
            # save a new file
            await self.save_data(False)

    async def save_data(self, append: bool):
        """Save data."""
        try:
            if append:
                cfile = await self.hass.async_add_executor_job(
                    open, self.filepath, "w", -1, "utf-8"
                )
            else:
                cfile = await self.hass.async_add_executor_job(
                    open, self.filepath, "a", -1, "utf-8"
                )
            ocrdata = json.dumps(self.jdata)
            self.data_handler.get_device(self.devicesn).Schedule.SavedData = self.jdata
            cfile.write(ocrdata)
            cfile.close()
        except Exception as ex:  # noqa: BLE001
            _LOGGER.debug(f"Save data failed: {ex}")  # noqa: G004

    async def load_data(self):
        """Load data."""
        try:
            cfile = await self.hass.async_add_executor_job(
                open, self.filepath, "r", -1, "utf-8"
            )
            ocrdata = cfile.read()
            cfile.close()
            _LOGGER.debug(f"ocrdata: {ocrdata}")  # noqa: G004
            _LOGGER.debug(f"jsonload: {json.loads(ocrdata)}")  # noqa: G004

            self.jdata = json.loads(ocrdata)
            self.data_handler.get_device(self.devicesn).Schedule.SavedData = self.jdata
            self.data_loaded = True
        except Exception as ex:  # noqa: BLE001
            _LOGGER.debug(f"load data failed: {ex}")  # noqa: G004

    async def save_schedule_data(self):
        """Update schedule data on disk."""
        await self.set_schedule_data()
        await self.save_data(True)

    def dataupdated(self, devicesn: str, schedule: bool):
        """Func Callback when data is updated."""
        _LOGGER.debug(f"callback - adano {self.devicesn} data updated")  # noqa: G004
        if self.devicesn == devicesn:
            self.hass.add_job(self.async_set_updated_data, None)
        if (
            schedule
            and not self.data_handler.get_device(self.devicesn).Schedule.IsEmpty()
        ):
            self.hass.add_job(self.save_schedule_data)

    @property
    def dsn(self):
        """DeviceSerialNumber."""
        return self.devicesn

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self.unique_id),
            },
            model=self.data_handler.get_device(self.devicesn).DeviceModel,
            manufacturer="Adano Robotic Mower",
            serial_number=self.devicesn,
            name=self.data_handler.get_device(self.devicesn).DeviceName,
            sw_version=self.data_handler.get_device(self.devicesn)
            .devicedata["data"]
            .get("bbSv"),
            hw_version=self.data_handler.get_device(self.devicesn)
            .devicedata["data"]
            .get("bbHv"),
        )

    @property
    def unique_id(self) -> str:
        """Return the system descriptor."""
        return f"{DOMAIN}-{self.devicesn}"

    def update_device(self):
        """Update device."""
        self.data_handler.update_devices(self.devicesn)

    async def _async_update_data(self):
        try:
            await self.hass.async_add_executor_job(self.data_handler.update)
            return self.data_handler  # noqa: TRY300
        except Exception as ex:  # noqa: BLE001
            _LOGGER.debug(f"update failed: {ex}")  # noqa: G004
