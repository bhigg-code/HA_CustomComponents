"""Select entities for JVC Projector."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, INPUT_CODES, PICTURE_MODE_CODES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up JVC Projector select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        JvcInputSelect(coordinator, entry),
        JvcPictureModeSelect(coordinator, entry),
    ])


class JvcInputSelect(CoordinatorEntity, SelectEntity):
    """Select entity for JVC Projector input."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"jvc_projector_input_{entry.entry_id}"
        self._attr_name = "JVC Projector Input"
        self._attr_options = list(INPUT_CODES.keys())

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
        )

    @property
    def current_option(self) -> str | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("input")

    @property
    def available(self) -> bool:
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("power") == "on"

    async def async_select_option(self, option: str) -> None:
        """Change the input."""
        await self.coordinator.client.set_input(option)
        await self.coordinator.async_request_refresh()


class JvcPictureModeSelect(CoordinatorEntity, SelectEntity):
    """Select entity for JVC Projector picture mode."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"jvc_projector_picture_mode_{entry.entry_id}"
        self._attr_name = "JVC Projector Picture Mode"
        self._attr_options = list(PICTURE_MODE_CODES.keys())

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
        )

    @property
    def current_option(self) -> str | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("picture_mode")

    @property
    def available(self) -> bool:
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("power") == "on"

    async def async_select_option(self, option: str) -> None:
        """Change the picture mode."""
        await self.coordinator.client.set_picture_mode(option)
        await self.coordinator.async_request_refresh()
