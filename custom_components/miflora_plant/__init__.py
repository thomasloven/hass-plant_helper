import logging
import os

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from . import patch_plant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "miflora_plant"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    await hass.config_entries.async_forward_entry_setups(entry, ("plant",))

    dir = os.path.dirname(os.path.realpath(__file__))
    photopath = os.path.join(dir, "photos")
    if os.path.isdir(photopath):
        hass.http.register_static_path("/miflora_photos", photopath)

    return True

async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True