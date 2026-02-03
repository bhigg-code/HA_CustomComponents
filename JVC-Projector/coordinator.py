"""Data coordinator for JVC Projector."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import JvcProjectorClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class JvcProjectorCoordinator(DataUpdateCoordinator):
    """Coordinator for JVC Projector data updates."""

    def __init__(self, hass: HomeAssistant, host: str, port: int, password: str = ""):
        self.host = host
        self.port = port
        self.client = JvcProjectorClient(host, port, password=password)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from the projector."""
        try:
            data = await self.client.get_all_status()
            _LOGGER.debug(f"JVC Projector data: {data}")
            return data
        except Exception as err:
            _LOGGER.error(f"Error updating JVC Projector: {err}")
            raise UpdateFailed(err)
