"""Base adano entity."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AdanoDataCoordinator


class AdanoEntity(CoordinatorEntity[AdanoDataCoordinator]):
    """Base Adano entity."""

    coordinator = AdanoDataCoordinator

    def __init__(
        self,
        coordinator: AdanoDataCoordinator,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = (
            f"{coordinator.unique_id}-{self.__class__.__name__.lower()}"
        )
