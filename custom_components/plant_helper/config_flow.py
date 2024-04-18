from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol
import logging

from homeassistant.helpers import selector
from homeassistant.config_entries import ConfigFlow, ConfigEntry, OptionsFlowWithConfigEntry

from .plant_data import get_plant_options
from .const import DOMAIN, CONF_DEVICE, CONF_PLANT, CONF_NAME, CONFIG_DETAILS, NONE_PLANT
from .const import *

_LOGGER = logging.getLogger(__name__)

class MiFloraOptionsFlow(OptionsFlowWithConfigEntry):

    @staticmethod
    def generate_options_schema(self):
        plant_options = get_plant_options(self.hass)
        if not plant_options:
            plant_options = [{
                "value": NONE_PLANT,
                "label": "PlantDB.csv not found..."
            }]

        return vol.Schema(
            {
                vol.Required(CONF_DEVICE): selector.DeviceSelector(
                    selector.DeviceSelectorConfig(
                        entity=selector.EntityFilterSelectorConfig(
                            device_class=["moisture"]
                        ),
                        multiple=False,
                    ),
                ),
                vol.Optional(CONF_PLANT): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=plant_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    ),
                ),
            }
        )

    @staticmethod
    def generate_details_schema(self):

        def _key(option: str) -> vol.Optional:
            return vol.Optional(option)

        def _value() -> selector.NumberSelector:
            return selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=100000,
                    mode="box",
                )
            )

        return vol.Schema(
            { _key(o): _value() for o in CONFIG_DETAILS}
        )

    async def async_step_init(self, user_input: dict[str, Any]|None = None):
        data_schema = self.add_suggested_values_to_schema(
            self.generate_options_schema(self),
            self.config_entry.options
        )

        if user_input is not None:
            self.options.update(user_input)
            if user_input.get(CONF_PLANT, NONE_PLANT) == NONE_PLANT:
                self.options.pop(CONF_PLANT, None)
                return await self.async_step_details()

            return self.async_create_entry(data=self.options)

        return self.async_show_form(step_id="init", data_schema=data_schema)

    async def async_step_details(self, user_input: dict[str, Any]|None = None):
        """Options for custom limits"""
        details_schema = self.add_suggested_values_to_schema(
            self.generate_details_schema(self),
            self.config_entry.options
        )

        if user_input is not None:
            self.options.update(user_input)
            for key in details_schema.schema:
                if isinstance(key, vol.Optional) and key not in user_input:
                    self.options.pop(key, None)
            return self.async_create_entry(data=self.options)

        return self.async_show_form(step_id="details", data_schema=details_schema)


class MiFloraConfigFlow(ConfigFlow, domain=DOMAIN):
    def generate_config_schema(self):
        options_schema = MiFloraOptionsFlow.generate_options_schema(self)
        return vol.Schema(
            {
                vol.Required(CONF_NAME): selector.TextSelector(),
            }
        ).extend(options_schema.schema)

    async def async_step_user(self, user_input: dict[str, Any]|None = None):
        if user_input is not None:
            self.options = user_input
            if user_input.get(CONF_PLANT, NONE_PLANT) == NONE_PLANT:
                self.options.pop(CONF_PLANT, None)
                return await self.async_step_details()

            return self.async_create_entry(
                title=cast(str, self.options.get(CONF_NAME, "New Plant")),
                data={},
                options=user_input
                )

        return self.async_show_form(step_id="user", data_schema=self.generate_config_schema())

    async def async_step_details(self, user_input: dict[str, Any]|None = None):
        """Config for custom limits"""
        details_schema = MiFloraOptionsFlow.generate_details_schema(self)
        details_schema = self.add_suggested_values_to_schema(
            MiFloraOptionsFlow.generate_details_schema(self),
            {
                CONF_MIN_MOISTURE: DEFAULT_MIN_MOISTURE,
                CONF_MAX_MOISTURE: DEFAULT_MAX_MOISTURE,
                CONF_MIN_CONDUCTIVITY: DEFAULT_MIN_CONDUCTIVITY,
                CONF_MAX_CONDUCTIVITY: DEFAULT_MAX_CONDUCTIVITY,
                CONF_MIN_BATTERY_LEVEL: DEFAULT_MIN_BATTERY_LEVEL,
            }
        )

        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(
                title=cast(str, self.options.get(CONF_NAME, "New Plant")),
                data={},
                options=self.options
                )

        return self.async_show_form(step_id="details", data_schema=details_schema)

    def async_get_options_flow(entry: ConfigEntry):
        return MiFloraOptionsFlow(entry)
