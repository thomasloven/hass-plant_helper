import csv
import os
from collections import namedtuple
import base64
import urllib.parse

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

def async_load_data() -> bool:
    if plant_data:
        return True
    dir = os.path.dirname(os.path.realpath(__file__))
    csvpath = os.path.join(dir, "database.csv")
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


def get_plant(pid: str) -> PlantData:
    if not async_load_data():
        return None
    return plant_data.get(pid)

def get_plant_options() -> list[dict]:
    if not async_load_data():
        return [{"value": "none", "label": "database.csv not found..."}]
    return plant_options

def get_photo(pid: str) -> str:
    dir = os.path.dirname(os.path.realpath(__file__))
    photopath = os.path.join(dir, "photos", f"{pid}.jpg")
    if os.path.exists(photopath):
        return urllib.parse.quote(f"/miflora_photos/{pid}.jpg")
    return None