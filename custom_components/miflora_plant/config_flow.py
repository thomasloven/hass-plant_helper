from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol
import logging

from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import SchemaFlowFormStep, SchemaConfigFlowHandler
from homeassistant.config_entries import ConfigFlow

from .plant_data import get_plant_options

_LOGGER = logging.getLogger(__name__)

DOMAIN = "miflora_plant"

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required("device"): selector.DeviceSelector(
            selector.DeviceSelectorConfig(
                entity=selector.EntityFilterSelectorConfig(device_class=["moisture"]),
                multiple=False
            )
        ),
        vol.Optional("plant"): selector.SelectSelector(
            selector.SelectSelectorConfig(options=get_plant_options(), mode="dropdown")
        ),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("name"): selector.TextSelector(),
    }
).extend(OPTIONS_SCHEMA.schema)

CONFIG_FLOW = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA),
}

OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(OPTIONS_SCHEMA),
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        return cast(str, options["name"]) if "name" in options else ""