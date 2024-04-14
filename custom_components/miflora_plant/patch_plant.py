
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_component import EntityComponent, DATA_INSTANCES

from homeassistant.components import plant

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    component: EntityComponent[plant.Plant] = hass.data[DATA_INSTANCES][plant.DOMAIN]
    return await component.async_setup_entry(entry)

plant.async_setup_entry = async_setup_entry
