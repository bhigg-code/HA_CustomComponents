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
        super().__init__(
            hass,
            _LOGGER,
            name="atlona_matrix",
            update_interval=timedelta(seconds=30),
        )

    def _parse_status(self, video_raw: str, audio_raw: str) -> dict:
        video = video_raw.replace("\r\n", "").split(",") if video_raw else []
        audio = audio_raw.replace("\r\n", "").split(",") if audio_raw else []
        out = {}
        for i in range(min(len(video), len(audio))):
            out[i + 1] = {"video": video[i], "audio": audio[i]}
        return out

    def _parse_output_power(self, power_raw: str) -> dict:
        """Parse output power states from raw response."""
        # Response format: x1$ on, x2$ off, etc.
        states = {}
        if not power_raw:
            return states
        for line in power_raw.replace("\r\n", "\n").split("\n"):
            line = line.strip()
            if not line:
                continue
            # Parse "x9$ off" or "x9$ on"
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
            status = await self.hass.async_add_executor_job(self.client.get_all_status)
            
            _LOGGER.debug(f"Atlona status received: power={repr(status.get('power'))}"            )
            
            routes = self._parse_status(status.get("video_raw", ""), status.get("audio_raw", ""))
            output_power = self._parse_output_power(status.get("output_power_raw", ""))

            return {
                "video_raw": status.get("video_raw", ""),
                "audio_raw": status.get("audio_raw", ""),
                "power": status.get("power", ""),
                "hostname": status.get("hostname", "").strip(),
                "model": status.get("model", "").strip(),
                "version": status.get("version", "").strip(),
                "routes": routes,
                "output_power_states": output_power,
            }
        except Exception as err:
            _LOGGER.error(f"Atlona update failed: {err}")
            raise UpdateFailed(err)
