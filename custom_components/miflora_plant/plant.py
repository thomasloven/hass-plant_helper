import logging

from homeassistant.components import plant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .plant_data import get_plant, get_photo

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):

    registry = er.async_get(hass)
    device_id = entry.options["device"]
    entities = er.async_entries_for_device(registry, device_id)

    configuration = {"sensors": {}}
    for e in entities:
        if e.original_device_class == "moisture":
            configuration["sensors"]["moisture"] = e.entity_id
        if e.original_device_class == "battery":
            configuration["sensors"]["battery"] = e.entity_id
        if e.original_device_class == "temperature":
            configuration["sensors"]["temperature"] = e.entity_id
        if e.original_name == "Conductivity":
            configuration["sensors"]["conductivity"] = e.entity_id
        if e.original_device_class == "illuminance":
            configuration["sensors"]["brightness"] = e.entity_id

    entity = MiFloraPlant(hass, entry.options["name"], configuration, entry.options.get("plant"), device_id, entry.entry_id)

    async_add_entities([entity])

    return True


class MiFloraPlant(plant.Plant):

    def __init__(self, hass, name, configuration, pid, device_id, unique_id):
        self._plant = None
        if pid is not None and pid != "none" and (plant := get_plant(pid)) is not None:
            self._plant = plant
            configuration["min_moisture"] = int(plant.min_soil_moist)
            configuration["max_moisture"] = int(plant.max_soil_moist)
            configuration["min_conductivity"] = int(plant.min_soil_ec)
            configuration["max_conductivity"] = int(plant.max_soil_ec)
            configuration["min_temperature"] = int(plant.min_temp)
            configuration["max_temperature"] = int(plant.max_temp)
            configuration["min_brightness"] = int(plant.min_light_lux)
            configuration["max_brightness"] = int(plant.max_light_lux)

            self._attr_entity_picture = get_photo(pid)

        super().__init__(name, configuration)
        self._attr_unique_id = unique_id

        device_registry = dr.async_get(hass)
        device = device_registry.async_get(device_id)

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



