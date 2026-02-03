import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .media_player import OUTPUT_NAMES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [AtlonaMasterPowerSwitch(coordinator, entry)]
    
    # Add per-output power switches
    for key in OUTPUT_NAMES.keys():
        try:
            output_num = int(key.replace("Vx", ""))
            entities.append(AtlonaOutputPowerSwitch(coordinator, entry, output_num))
        except ValueError:
            continue
    
    async_add_entities(entities)


class AtlonaMasterPowerSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Atlona Master Power"

    @property
    def unique_id(self):
        return f"atlona_master_power_{self._entry.entry_id}"

    @property
    def icon(self):
        return "mdi:power"

    @property
    def is_on(self):
        if not self.coordinator.data:
            return None
        power = self.coordinator.data.get("power", "")
        if not power:
            return None
        power_upper = power.upper()
        if any(indicator in power_upper for indicator in ["PWON", "PON", "ON", "1"]):
            return True
        elif any(indicator in power_upper for indicator in ["PWOFF", "POFF", "OFF", "0"]):
            return False
        return None

    @property
    def available(self):
        return self.coordinator.last_update_success and self.coordinator.data is not None

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(
            self.coordinator.client.send_command, "PWON"
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(
            self.coordinator.client.send_command, "PWOFF"
        )
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self.coordinator.data.get("hostname", "Atlona Matrix") if self.coordinator.data else "Atlona Matrix",
            manufacturer="Atlona",
            model=self.coordinator.data.get("model") if self.coordinator.data else None,
        )


class AtlonaOutputPowerSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, entry, output_num):
        super().__init__(coordinator)
        self._entry = entry
        self._output_num = output_num
        self._output_key = f"Vx{output_num}"

    @property
    def name(self):
        zone = OUTPUT_NAMES.get(self._output_key, f"Output {self._output_num}")
        return f"Atlona {zone} Power"

    @property
    def unique_id(self):
        return f"atlona_output_power_{self._entry.entry_id}_{self._output_num}"

    @property
    def icon(self):
        return "mdi:video"

    @property
    def is_on(self):
        if not self.coordinator.data:
            return None
        output_power = self.coordinator.data.get("output_power_states", {})
        return output_power.get(self._output_num)

    @property
    def available(self):
        return self.coordinator.last_update_success and self.coordinator.data is not None

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_output_power, self._output_num, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_output_power, self._output_num, False
        )
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self.coordinator.data.get("hostname", "Atlona Matrix") if self.coordinator.data else "Atlona Matrix",
            manufacturer="Atlona",
            model=self.coordinator.data.get("model") if self.coordinator.data else None,
        )
