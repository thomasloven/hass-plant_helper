import csv
import os
from collections import namedtuple
import base64
import urllib.parse
import glob

from homeassistant.core import HomeAssistant

from .const import PHOTOS_URL, NONE_PLANT

import logging
_LOGGER = logging.getLogger(__name__)

plant_data = {}
plant_options = []

PlantData = namedtuple("PlantData", [
    "pid",
    "display_pid",
    "alias",
    "image",
    "floral_language",
    "origin",
    "production",
    "category",
    "blooming",
    "color",
    "size",
    "soil",
    "sunlight",
    "watering",
    "fertilization",
    "pruning",
    "max_light_mmol",
    "min_light_mmol",
    "max_light_lux",
    "min_light_lux",
    "max_temp",
    "min_temp",
    "max_end_humid",
    "min_env_humin",
    "max_soil_moist",
    "min_soil_moist",
    "max_soil_ec",
    "min_soil_ec",
    ])

def async_load_data(hass: HomeAssistant) -> bool:

    if plant_data:
        return True
    csvpath = get_db_path(hass)
    if csvpath is None:
        return False
    try:
        with open(csvpath, "r") as csvfile:
            reader = csv.reader(csvfile)
            for ln, line in enumerate(reader):
                if ln == 0: continue
                flower = PlantData(*line)
                plant_data[flower.pid] = flower
                plant_options.append({
                    "label": flower.display_pid,
                    "value": flower.pid})
            return True
    except FileNotFoundError:
        return False


def get_plant(hass: HomeAssistant, pid: str) -> PlantData:
    if not async_load_data(hass):
        return None
    return plant_data.get(pid)

def get_plant_options(hass: HomeAssistant, ) -> list[dict] | None:
    if not async_load_data(hass):
        return None
    return plant_options

def get_photo(hass: HomeAssistant, pid: str) -> str | None:
    if (photopath := get_photo_path(hass)) is None:
        return None
    photo = os.path.join(photopath, f"{pid}.jpg")
    if os.path.exists(photo):
        return urllib.parse.quote(f"{PHOTOS_URL}/{pid}.jpg")
    return None

def get_db_path(hass: HomeAssistant) -> str | None:
    files = glob.glob("PlantDB*.csv", root_dir=hass.config.config_dir)
    if files: return os.path.join(hass.config.config_dir, files[0])
    return None

def get_photo_path(hass: HomeAssistant) -> str | None:
    path = glob.glob("plant_photos", root_dir=hass.config.config_dir)
    if path: return os.path.join(hass.config.config_dir, path[0])
    return None