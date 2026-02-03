"""Config flow for JVC Projector integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_PASSWORD

from .const import DOMAIN, DEFAULT_PORT
from .client import JvcProjectorClient

_LOGGER = logging.getLogger(__name__)


class JvcProjectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JVC Projector."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            password = user_input.get(CONF_PASSWORD, "")

            # Test connection
            client = JvcProjectorClient(host, port, password=password)
            if await client.connect():
                model = await client.get_model()
                await client.disconnect()
                
                return self.async_create_entry(
                    title=f"JVC {model or 'Projector'}",
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_PASSWORD: password,
                    },
                )
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_PASSWORD, default=""): str,
            }),
            errors=errors,
        )
