"""Base adano entity."""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AdanoDataCoordinator


class AdanoEntity(CoordinatorEntity[AdanoDataCoordinator]):
    """Base Adano entity."""

    # _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AdanoDataCoordinator,
    ) -> None:
        """Init."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info
