"""Consts for plant_helper"""

from typing import Final

DOMAIN: Final = "plant_helper"

READING_MOISTURE = "moisture"
READING_BATTERY = "battery"
READING_TEMPERATURE = "temperature"
READING_CONDUCTIVITY = "conductivity"
READING_BRIGHTNESS = "brightness"

CONF_DEVICE = "device"
CONF_PLANT = "plant"
CONF_NAME = "name"

CONF_MIN_BATTERY_LEVEL = f"min_{READING_BATTERY}"
CONF_MIN_TEMPERATURE = f"min_{READING_TEMPERATURE}"
CONF_MAX_TEMPERATURE = f"max_{READING_TEMPERATURE}"
CONF_MIN_MOISTURE = f"min_{READING_MOISTURE}"
CONF_MAX_MOISTURE = f"max_{READING_MOISTURE}"
CONF_MIN_CONDUCTIVITY = f"min_{READING_CONDUCTIVITY}"
CONF_MAX_CONDUCTIVITY = f"max_{READING_CONDUCTIVITY}"
CONF_MIN_BRIGHTNESS = f"min_{READING_BRIGHTNESS}"
CONF_MAX_BRIGHTNESS = f"max_{READING_BRIGHTNESS}"

DEFAULT_MIN_BATTERY_LEVEL = 20
DEFAULT_MIN_MOISTURE = 20
DEFAULT_MAX_MOISTURE = 60
DEFAULT_MIN_CONDUCTIVITY = 500
DEFAULT_MAX_CONDUCTIVITY = 3000

NONE_PLANT = "none"


PHOTOS_URL = "/miflora_photos"

CONFIG_DETAILS = [
  "min_moisture",
  "max_moisture",
  "min_conductivity",
  "max_conductivity",
  "min_temperature",
  "max_temperature",
  "min_brightness",
  "max_brightness"
]

ATTR_PROBLEM = "problem"
ATTR_SENSORS = "sensors"
PROBLEM_NONE = "none"
ATTR_MAX_BRIGHTNESS_HISTORY = "max_brightness"
ATTR_DICT_OF_UNITS_OF_MEASUREMENT = "unit_of_measurement_dict"