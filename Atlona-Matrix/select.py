from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .media_player import INPUT_NAMES, OUTPUT_NAMES
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for key in OUTPUT_NAMES.keys():
        try:
            output_num = int(key.replace("Vx", ""))
            entities.append(AtlonaSourceSelect(coordinator, entry, output_num))
        except ValueError:
            continue

    async_add_entities(entities)


class AtlonaSourceSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator, entry, output_num):
        super().__init__(coordinator)
        self._entry = entry
        self._output_num = output_num
        self._output_key = f"Vx{output_num}"
        self._attr_options = list(INPUT_NAMES.values())

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self.coordinator.data.get("hostname", "Atlona Matrix") if self.coordinator.data else "Atlona Matrix",
            manufacturer="Atlona",
            model=self.coordinator.data.get("model", "Unknown Model") if self.coordinator.data else None,
        )

    @property
    def name(self):
        zone = OUTPUT_NAMES.get(self._output_key, f"Output {self._output_num}")
        return f"Atlona {zone} Input"

    @property
    def unique_id(self):
        return f"atlona_select_{self._entry.entry_id}_{self._output_num}"

    @property
    def current_option(self):
        if not self.coordinator.data:
            return None
        routes = self.coordinator.data.get("routes", {})
        route = routes.get(self._output_num, {})
        video_input = route.get("video", "").strip()
        
        for input_code, input_name in INPUT_NAMES.items():
            if input_code.lower() in video_input.lower():
                return input_name
        return None

    async def async_select_option(self, option: str):
        input_code = None
        for code, name in INPUT_NAMES.items():
            if name == option:
                input_code = code
                break
        
        if input_code:
            await self.hass.async_add_executor_job(
                self.coordinator.client.set_route,
                self._output_num,
                input_code
            )
            await self.coordinator.async_request_refresh()
