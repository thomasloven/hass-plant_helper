import logging

from homeassistant.components import plant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .plant_data import get_plant, get_photo
from .const import CONF_DEVICE, CONF_PLANT, CONF_NAME, CONFIG_DETAILS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    registry = er.async_get(hass)
    device_id = entry.options.get(CONF_DEVICE)
    entities = er.async_entries_for_device(registry, device_id)

    sensors = {}
    configuration = {plant.ATTR_SENSORS: sensors}

    for e in entities:
        if e.original_device_class == "moisture":
            sensors[plant.CONF_SENSOR_MOISTURE] = e.entity_id
        if e.original_device_class == "battery":
            sensors[plant.CONF_SENSOR_BATTERY_LEVEL] = e.entity_id
        if e.original_device_class == "temperature":
            sensors[plant.CONF_SENSOR_TEMPERATURE] = e.entity_id
        if e.original_name == "Conductivity":
            sensors[plant.CONF_SENSOR_CONDUCTIVITY] = e.entity_id
        if e.original_device_class == "illuminance":
            sensors[plant.CONF_SENSOR_BRIGHTNESS] = e.entity_id

    _plant = None
    plant_picture = None
    if (pid:=entry.options.get(CONF_PLANT)) and (_plant := get_plant(hass, pid)):
        configuration[plant.CONF_MIN_MOISTURE] = int(_plant.min_soil_moist)
        configuration[plant.CONF_MAX_MOISTURE] = int(_plant.max_soil_moist)
        configuration[plant.CONF_MIN_CONDUCTIVITY] = int(_plant.min_soil_ec)
        configuration[plant.CONF_MAX_CONDUCTIVITY] = int(_plant.max_soil_ec)
        configuration[plant.CONF_MIN_TEMPERATURE] = int(_plant.min_temp)
        configuration[plant.CONF_MAX_TEMPERATURE] = int(_plant.max_temp)
        configuration[plant.CONF_MIN_BRIGHTNESS] = int(_plant.min_light_lux)
        configuration[plant.CONF_MAX_BRIGHTNESS] = int(_plant.max_light_lux)
        plant_picture = get_photo(hass, pid)
    else:
        for key in CONFIG_DETAILS:
            if (value := entry.options.get(key)) is not None:
                configuration[key] = value


    entity = MiFloraPlant(
        hass,
        entry.options.get(CONF_NAME),
        configuration,
        _plant,
        plant_picture,
        device_id,
        entry.entry_id
    )

    async_add_entities([entity])

    return True


class MiFloraPlant(plant.Plant):

    def __init__(self, hass, name, configuration, _plant, picture, device_id, unique_id):
        super().__init__(name, configuration)

        self._plant = _plant
        self._attr_entity_picture = picture
        self._attr_unique_id = unique_id

        device_registry = dr.async_get(hass)
        device = device_registry.async_get(device_id)

        if device:
            self._attr_device_info = dr.DeviceInfo(connections=device.connections, identifiers=device.identifiers,)

    @property
    def extra_state_attributes(self):
        attrib = super().extra_state_attributes

        if (plant:=self._plant) is not None:
            attrib["species"] = plant.display_pid
            attrib["description"] = plant.floral_language
            attrib["origin"] = plant.origin
            attrib["production"] = plant.production
            attrib["category"] = plant.category
            attrib["blooming"] = plant.blooming
            attrib["color"] = plant.color
            attrib["size"] = plant.size
            attrib["soil"] = plant.soil
            attrib["sunlight"] = plant.sunlight
            attrib["watering"] = plant.watering
            attrib["fertilization"] = plant.fertilization
            attrib["pruning"] = plant.pruning

        return attrib



