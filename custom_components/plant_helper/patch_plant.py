
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_component import EntityComponent, DATA_INSTANCES

from homeassistant.components import plant

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    component: EntityComponent[plant.Plant] = hass.data[DATA_INSTANCES][plant.DOMAIN]
    return await component.async_setup_entry(entry)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    component: EntityComponent[plant.Plant] = hass.data[DATA_INSTANCES][plant.DOMAIN]
    return await component.async_unload_entry(entry)

if not hasattr(plant, "async_setup_entry"):
    plant.async_setup_entry = async_setup_entry
if not hasattr(plant, "async_unload_entry"):
    plant.async_unload_entry = async_unload_entry