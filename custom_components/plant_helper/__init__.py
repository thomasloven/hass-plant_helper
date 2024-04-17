import logging
import os

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.frontend import add_extra_js_url

from . import patch_plant
from .const import PHOTOS_URL
from .plant_data import get_photo_path

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, _) -> bool:
    JS_PATCH_URL = "/patch_plant_card.js"
    js_patch_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "patch_plant_card.js")
    hass.http.register_static_path(JS_PATCH_URL, js_patch_path)
    add_extra_js_url(hass, JS_PATCH_URL)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    await hass.config_entries.async_forward_entry_setups(entry, ("plant","binary_sensor"))

    photopath = get_photo_path(hass)
    if photopath and os.path.isdir(photopath):
        hass.http.register_static_path(PHOTOS_URL, photopath)

    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))

    return True

async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_result = await hass.config_entries.async_unload_platforms(entry, ("plant",))
    return unload_result
