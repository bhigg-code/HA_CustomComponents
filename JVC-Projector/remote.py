"""Remote entity for JVC Projector."""
import logging
from typing import Any

from homeassistant.components.remote import RemoteEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up JVC Projector remote."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([JvcProjectorRemote(coordinator, entry)])


class JvcProjectorRemote(CoordinatorEntity, RemoteEntity):
    """Remote entity for JVC Projector."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"jvc_projector_{entry.entry_id}"
        self._attr_name = "JVC Projector"

    @property
    def device_info(self) -> DeviceInfo:
        model = self.coordinator.data.get("model", "Unknown") if self.coordinator.data else "Unknown"
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"JVC {model}",
            manufacturer="JVC",
            model=model,
            sw_version=self.coordinator.data.get("software_version") if self.coordinator.data else None,
        )

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        power = self.coordinator.data.get("power", "off")
        return power in ("on", "warming")

    @property
    def state(self) -> str:
        if not self.coordinator.data:
            return "off"
        return self.coordinator.data.get("power", "off")

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        return {
            "power_state": self.coordinator.data.get("power"),
            "input": self.coordinator.data.get("input"),
            "picture_mode": self.coordinator.data.get("picture_mode"),
            "laser_hours": self.coordinator.data.get("laser_hours"),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the projector on."""
        await self.coordinator.client.power_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the projector off."""
        await self.coordinator.client.power_off()
        await self.coordinator.async_request_refresh()
