import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import AtlonaClient

_LOGGER = logging.getLogger(__name__)


class AtlonaDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, host: str, port: int):
        self.host = host
        self.port = port
        self.client = AtlonaClient(host, port)
        
        # Cache for static device info (fetched once)
        self._static_info = None
        
        # Counter for less frequent polling of output power
        self._poll_count = 0
        
        super().__init__(
            hass,
            _LOGGER,
            name="atlona_matrix",
            update_interval=timedelta(seconds=60),  # Increased from 30s
        )

    def _parse_status(self, status_raw: str) -> dict:
        """Parse combined Status response (returns both video and audio lines)."""
        lines = status_raw.replace("\r\n", "\n").strip().split("\n")
        video = []
        audio = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Video line contains 'V', audio line contains 'A'
            if "V" in line and "A" not in line:
                video = line.split(",")
            elif "A" in line:
                audio = line.split(",")
        
        out = {}
        for i in range(min(len(video), len(audio))):
            out[i + 1] = {"video": video[i], "audio": audio[i]}
        return out

    def _parse_output_power(self, power_raw: str) -> dict:
        """Parse output power states from raw response."""
        states = {}
        if not power_raw:
            return states
        for line in power_raw.replace("\r\n", "\n").split("\n"):
            line = line.strip()
            if not line:
                continue
            if "$" in line:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        num = int(parts[0].replace("x", "").replace("$", ""))
                        state = parts[1].lower() == "on"
                        states[num] = state
                    except (ValueError, IndexError):
                        continue
        return states

    async def _async_update_data(self):
        try:
            # Fetch static info only once
            if self._static_info is None:
                self._static_info = await self.hass.async_add_executor_job(
                    self.client.get_static_info
                )
                _LOGGER.debug(f"Fetched static info: {self._static_info}")
            
            # Always fetch routing status (this is the core data)
            status = await self.hass.async_add_executor_job(
                self.client.get_routing_status
            )
            
            routes = self._parse_status(status.get("status_raw", ""))
            
            # Fetch output power states every 3rd poll (every 3 minutes)
            # or if we don't have any cached data yet
            self._poll_count += 1
            output_power = self.data.get("output_power_states", {}) if self.data else {}
            
            if self._poll_count >= 3 or not output_power:
                self._poll_count = 0
                power_raw = await self.hass.async_add_executor_job(
                    self.client.get_output_power_states
                )
                output_power = self._parse_output_power(power_raw)
                _LOGGER.debug(f"Refreshed output power states")
            
            return {
                "status_raw": status.get("status_raw", ""),
                "video_raw": status.get("status_raw", "").split("\n")[0] if status.get("status_raw") else "",
                "audio_raw": status.get("status_raw", "").split("\n")[1] if status.get("status_raw") and "\n" in status.get("status_raw", "") else "",
                "power": status.get("power", ""),
                "hostname": self._static_info.get("hostname", "").strip(),
                "model": self._static_info.get("model", "").strip(),
                "version": self._static_info.get("version", "").strip(),
                "routes": routes,
                "output_power_states": output_power,
            }
        except Exception as err:
            _LOGGER.error(f"Atlona update failed: {err}")
            raise UpdateFailed(err)
