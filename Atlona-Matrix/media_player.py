from homeassistant.components.media_player import (MediaPlayerEntity,
    MediaPlayerEntityFeature)
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

# Map input codes to source names
INPUT_NAMES = {
    "x1V": "nVidiaShield4k",
    "x2V": "Kaleidescape Strato C",
    "x3V": "Media Room Computer",
    "x4V": "nVidiaShield4k-2",
    "x5V": "Roku 4k Player",
    "x6V": "Amcrest NVR",
    "x7V": "AppleTV 4K",
    "x8V": "Undefined",
}

# Map output codes to zone names
OUTPUT_NAMES = {
    "Vx1": "Master Bedroom",
    "Vx2": "Gameroom",
    "Vx3": "Patio Front Wall",
    "Vx4": "Small Garage",
    "Vx5": "Patio Mantle",
    "Vx6": "Living Room",
    "Vx7": "Jakes Room",
    "Vx8": "Parkers Room",
    "Vx9": "Media Room",
    "Vx10": "Undefined",
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # Iterate over the KNOWN physical outputs (OUTPUT_NAMES)
    # instead of waiting for coordinator data.
    for key in OUTPUT_NAMES.keys():
        try:
            # Convert "Vx1" -> 1 so it matches the integer keys in coordinator.data['routes']
            output_num = int(key.replace("Vx", ""))
            entities.append(AtlonaMatrixPlayer(coordinator, entry, output_num))
        except ValueError:
            continue

    async_add_entities(entities)


class AtlonaMatrixPlayer(CoordinatorEntity, MediaPlayerEntity):
    def __init__(self, coordinator, entry, output_num):
        super().__init__(coordinator)
        self._entry = entry
        self._output_num = output_num
        self._output_key = f"Vx{output_num}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return info for the device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self.coordinator.data.get("hostname", "Atlona Matrix") if self.coordinator.data else "Atlona Matrix",
            manufacturer="Atlona",
            model=self.coordinator.data.get("model", "Unknown Model") if self.coordinator.data else None,
            sw_version=self.coordinator.data.get("version") if self.coordinator.data else None,
            configuration_url=f"http://{self._entry.data.get('host')}",
        )

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )
    
    @property
    def name(self):
        zone = OUTPUT_NAMES.get(self._output_key, f"Output {self._output_num}")
        return f"Atlona {zone}"

    @property
    def unique_id(self):
        return f"atlona_output_{self._entry.entry_id}_{self._output_num}"

    @property
    def state(self):
        if not self.coordinator.data:
            return STATE_OFF
        power = self.coordinator.data.get("power", "").upper()
        return STATE_ON if "PWON" in power else STATE_OFF
   
    @property
    def source_list(self):
        return list(INPUT_NAMES.values())

    @property
    def source(self):
        if not self.coordinator.data:
            return None
        routes = self.coordinator.data.get("routes", {})
        # Route keys are integers (1, 2, 3), not strings
        route = routes.get(self._output_num, {})
        video_input = route.get("video", "").strip()
        
        # Extract input code from the route (e.g., "x1V" from "x1V")
        for input_code, input_name in INPUT_NAMES.items():
            if input_code.lower() in video_input.lower():
                return input_name
        return video_input

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {
            "model": self.coordinator.data.get("model"),
            "version": self.coordinator.data.get("version"),
            "hostname": self.coordinator.data.get("hostname"),
        }


    async def async_select_source(self, source):
        """Select input source."""
        # 1. Find the input key (e.g., "x1V")
        input_code = None
        for code, name in INPUT_NAMES.items():
            if name == source:
                input_code = code
                break
        
        if input_code:
            # 2. Use the client helper we defined above
            # We pass the raw output number (self._output_num)
            await self.hass.async_add_executor_job(
                self.coordinator.client.set_route, 
                self._output_num,
                input_code
            )
            await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        """Turn the specific output on."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_output_power, 
            self._output_num, 
            True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the specific output off."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_output_power, 
            self._output_num, 
            False
        )
        await self.coordinator.async_request_refresh()

    @property
    def is_on(self):
        """Return true if this specific output zone is powered on."""
        if not self.coordinator.data:
            return False
        # FIX: Use self._output_num (not _output_id)
        return self.coordinator.data["output_power_states"].get(self._output_num)