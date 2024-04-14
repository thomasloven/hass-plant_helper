from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol
import logging

from homeassistant.helpers import selector
from homeassistant.config_entries import ConfigFlow, ConfigEntry, OptionsFlowWithConfigEntry

from .plant_data import get_plant_options
from .const import DOMAIN, CONFIG_DEVICE, CONFIG_PLANT, CONFIG_NAME

_LOGGER = logging.getLogger(__name__)

class MiFloraOptionsFlow(OptionsFlowWithConfigEntry):

    @staticmethod
    def generate_options_schema(self, default=None):
        plant_options = get_plant_options(self.hass)
        return vol.Schema(
            {
                vol.Required(CONFIG_DEVICE,
                             default=default.get(CONFIG_DEVICE) if default else None
                            ): selector.DeviceSelector(
                    selector.DeviceSelectorConfig(
                        entity=selector.EntityFilterSelectorConfig(
                            device_class=["moisture"]
                        ),
                        multiple=False,
                    ),
                ),
                vol.Optional(CONFIG_PLANT,
                             default=default.get(CONFIG_PLANT) if default else None
                            ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=plant_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    ),
                ),
            }
        )

    async def async_step_init(self, user_input: dict[str, Any]|None = None):
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(data=user_input)
        return self.async_show_form(step_id="init", data_schema=self.generate_options_schema(self, self.config_entry.options))


class MiFloraConfigFlow(ConfigFlow, domain=DOMAIN):
    def generate_config_schema(self):
        options_schema = MiFloraOptionsFlow.generate_options_schema(self)
        return vol.Schema(
            {
                vol.Required(CONFIG_NAME): selector.TextSelector(),
            }
        ).extend(options_schema.schema)

    async def async_step_user(self, user_input: dict[str, Any]|None = None):
        if user_input is not None:
            title = cast(str, user_input[CONFIG_NAME]) if CONFIG_NAME in user_input else "New plant"
            return self.async_create_entry(title=title, data={}, options=user_input)

        return self.async_show_form(step_id="user", data_schema=self.generate_config_schema())

    def async_get_options_flow(entry: ConfigEntry):
        return MiFloraOptionsFlow(entry)
