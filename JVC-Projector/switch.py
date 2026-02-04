"""Switch entity for JVC Projector power control."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up JVC Projector switch entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([JvcPowerSwitch(coordinator, entry)])


class JvcPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for JVC Projector power control."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"jvc_projector_power_{entry.entry_id}"
        self._attr_name = "JVC Projector Power"
        self._attr_icon = "mdi:projector"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
        )

    @property
    def is_on(self) -> bool:
        """Return true if projector is on."""
        if not self.coordinator.data:
            return False
        power = self.coordinator.data.get("power")
        return power == "on"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.data:
            return False
        power = self.coordinator.data.get("power")
        # Available unless in cooling/warming transition
        return power in ("on", "off")

    async def async_turn_on(self, **kwargs):
        """Turn the projector on."""
        await self.coordinator.client.connect()
        await self.coordinator.client.power_on()
        await self.coordinator.client.disconnect()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the projector off."""
        await self.coordinator.client.connect()
        await self.coordinator.client.power_off()
        await self.coordinator.client.disconnect()
        await self.coordinator.async_request_refresh()
