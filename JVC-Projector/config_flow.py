"""Config flow for JVC Projector integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_PASSWORD
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_PORT
from .client import JvcProjectorClient

_LOGGER = logging.getLogger(__name__)


class JvcProjectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JVC Projector."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return JvcProjectorOptionsFlow(config_entry)

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


class JvcProjectorOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for JVC Projector."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            password = user_input.get(CONF_PASSWORD, "")

            # Test connection with new settings
            client = JvcProjectorClient(host, port, password=password)
            if await client.connect():
                await client.disconnect()
                
                # Update the config entry data
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_PASSWORD: password,
                    },
                )
                return self.async_create_entry(title="", data={})
            else:
                errors["base"] = "cannot_connect"

        # Get current values
        current_host = self.config_entry.data.get(CONF_HOST, "")
        current_port = self.config_entry.data.get(CONF_PORT, DEFAULT_PORT)
        current_password = self.config_entry.data.get(CONF_PASSWORD, "")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=current_host): str,
                vol.Optional(CONF_PORT, default=current_port): int,
                vol.Optional(CONF_PASSWORD, default=current_password): str,
            }),
            errors=errors,
        )
