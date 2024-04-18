from typing import TypedDict, Any, Callable
from collections import defaultdict, deque
from contextlib import suppress
import logging
import datetime

from homeassistant.core import HomeAssistant, callback, Event, State
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE, CONDUCTIVITY
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event, EventStateChangedData
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.util import dt as dt_util
from homeassistant.components.recorder import history, get_instance
from homeassistant.components.sensor import SensorDeviceClass

from .plant_data import get_plant, get_photo, PlantData

from .const import *

_LOGGER = logging.getLogger(__name__)

class PlantRule(TypedDict):
    entity: str | None = None
    min: float | None = None
    max: float | None = None
    unit: str | None = None
    listener: Callable|None = None

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    pid = entry.options.get(CONF_PLANT)
    device_id = entry.options.get(CONF_DEVICE)

    if pid is not None:
        entity = MiFloraPlantBinarySensor(hass, entry.options.get(CONF_NAME), entry.options, pid)
    else:
        entity = CustomPlantBinarySensor(hass, entry.options.get(CONF_NAME), entry.options)

    entity._attr_unique_id = entry.entry_id
    # Connect to original device
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)
    if device:
        entity._attr_device_info = dr.DeviceInfo(connections=device.connections, identifiers=device.identifiers,)


    async_add_entities([entity])
    return True


class PlantBinarySensor(BinarySensorEntity):

    _attr_device_class = "plant" #BinarySensorDeviceClass.PROBLEM
    _attr_supported_features = 1
    _attr_translation_key = "plant"

    def __init__(self, hass: HomeAssistant, name: str, rules: dict[str: PlantRule]):
        super().__init__()
        self.hass = hass
        self._attr_name: str = name

        self.rules: dict[str, PlantRule] = rules

        self.values: dict[str, float|str] = {reading: STATE_UNKNOWN for reading in rules}
        self.problems: dict[str, str|None] = {reading: False for reading in rules}

        self._check_days = 3
        self._brightness_history = DailyHistory(self._check_days)
        self._actual_brightness = None


    def _check_state(self) -> None:
        problems = self.problems
        for reading, rule in self.rules.items():
            if (value := self.values.get(reading)) is None:
                continue
            if value == STATE_UNAVAILABLE:
                problems[reading] = "unavailable"
            if value == STATE_UNKNOWN:
                problems[reading] = "unknown"
            elif (min_val := rule.get("min")) is not None and value < min_val:
                problems[reading] = "low"
            elif (max_val := rule.get("max")) is not None and value > max_val:
                problems[reading] = "high"
            else:
                problems[reading] = PROBLEM_NONE

        self.async_write_ha_state()

    @property
    def is_on(self):
        return any((v is not PROBLEM_NONE for v in self.problems.values()))

    @property
    def extra_state_attributes(self):

        problems = ", ".join([f"{reading} {problem}" for reading, problem in self.problems.items() if problem is not PROBLEM_NONE])

        attrib = {
            ATTR_PROBLEM: problems,
            ATTR_SENSORS: {reading: rule.get("entity") for reading, rule in self.rules.items()},
            ATTR_DICT_OF_UNITS_OF_MEASUREMENT: {reading: rule["unit"] for reading, rule in self.rules.items()},
            **self.values
        }

        # TODO: Remove when card has been fixed
        if self._actual_brightness is not None:
            attrib["brightness"] = self._actual_brightness

        if self._brightness_history.max is not None:
            attrib[ATTR_MAX_BRIGHTNESS_HISTORY] = self._brightness_history.max

        attrib["problems"] = self.problems

        return attrib

    def _state_changed(self, entity: str, new_state: State|None):
        if new_state is None:
            return

        reading = [measure for measure, rule in self.rules.items() if rule.get("entity") == entity][0]

        value: str|float = new_state.state


        if value not in [STATE_UNKNOWN, STATE_UNAVAILABLE]:
            value = int(float(value))

        if reading == READING_BRIGHTNESS:
            # For brightness, continue with the maximum value over the past few days
            self._brightness_history.add_measurement(value, new_state.last_updated)
            self._actual_brightness = value
            value = self._brightness_history.max

        self.values[reading] = value

        self._check_state()

    def _state_changed_event(self, event: Event[EventStateChangedData]):
        return self._state_changed(event.data["entity_id"], event.data["new_state"])

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        for reading, rule in self.rules.items():
            if rule.get("entity") is None:
                continue

            if reading == READING_BRIGHTNESS:
                # Load historical data for brightness
                await get_instance(self.hass).async_add_executor_job(
                    self._load_history_from_db,
                    rule["entity"]
                )

            rule["listener"] = async_track_state_change_event(self.hass, rule["entity"], self._state_changed_event)
            self._state_changed(rule["entity"], self.hass.states.get(rule["entity"]))

    async def will_remove_from_hass(self) -> None:
        """When entity is removed from hass."""
        for rule in self.rules:
            rule.get("listener", lambda: None)()
        return await super().async_will_remove_from_hass()

    def _load_history_from_db(self, entity_id: str):
        """Load the history of the brightness values from the database.

        This only needs to be done once during startup.
        """

        start_date = dt_util.utcnow() - datetime.timedelta(days=self._check_days)
        _LOGGER.debug(f"Initializing values for {self._attr_name} from the database")
        history_list = history.state_changes_during_period(
            self.hass,
            start_date,
            entity_id=entity_id.lower(),
            no_attributes=True
        )

        for state in history_list.get(entity_id.lower(), []):
            with suppress(ValueError):
                self._brightness_history.add_measurement(int(state.state), state.last_updated)

        _LOGGER.debug("Initializing from database completed")

class CustomPlantBinarySensor(PlantBinarySensor):
    def __init__(self, hass: HomeAssistant, name: str, config: dict[str, Any]):
        device_id = config.get(CONF_DEVICE)
        rules = defaultdict(PlantRule)

        registry = er.async_get(hass)
        entities = er.async_entries_for_device(registry, device_id)
        for e in entities:
            if e.original_device_class == SensorDeviceClass.MOISTURE:
                rules[READING_MOISTURE] = {
                    "entity": e.entity_id,
                    "min": config.get(CONF_MIN_MOISTURE),
                    "max": config.get(CONF_MAX_MOISTURE),
                    "unit": e.unit_of_measurement,
                }
            if e.original_device_class == SensorDeviceClass.BATTERY:
                rules[READING_BATTERY] = {
                    "entity": e.entity_id,
                    "min": config.get(CONF_MIN_BATTERY_LEVEL),
                    "unit": e.unit_of_measurement,
                }
            if e.original_device_class == SensorDeviceClass.TEMPERATURE:
                rules[READING_TEMPERATURE] = {
                    "entity": e.entity_id,
                    "min": config.get(CONF_MIN_TEMPERATURE),
                    "max": config.get(CONF_MAX_TEMPERATURE),
                    "unit": e.unit_of_measurement,
                }
            if e.unit_of_measurement == CONDUCTIVITY:
                rules[READING_CONDUCTIVITY] = {
                    "entity": e.entity_id,
                    "min": config.get(CONF_MIN_CONDUCTIVITY),
                    "max": config.get(CONF_MAX_CONDUCTIVITY),
                    "unit": e.unit_of_measurement,
                }
            if e.original_device_class == SensorDeviceClass.ILLUMINANCE:
                rules[READING_BRIGHTNESS] = {
                    "entity": e.entity_id,
                    "min": config.get(CONF_MIN_BRIGHTNESS),
                    "max": config.get(CONF_MAX_BRIGHTNESS),
                    "unit": e.unit_of_measurement,
                }

        super().__init__(hass, name, rules)

class MiFloraPlantBinarySensor(PlantBinarySensor):
    def __init__(self, hass: HomeAssistant, name: str, config: dict[str, Any], pid: str):
        device_id = config.get(CONF_DEVICE)
        rules = defaultdict(PlantRule)

        self.plant = plant = get_plant(hass, pid)
        if plant is None:
            pass

        registry = er.async_get(hass)
        entities = er.async_entries_for_device(registry, device_id)
        for e in entities:
            if e.original_device_class == SensorDeviceClass.MOISTURE:
                rules[READING_MOISTURE] = {
                    "entity": e.entity_id,
                    "min": int(plant.min_soil_moist),
                    "max": int(plant.max_soil_moist),
                    "unit": e.unit_of_measurement,
                }
            if e.original_device_class == SensorDeviceClass.BATTERY:
                rules[READING_BATTERY] = {
                    "entity": e.entity_id,
                    "min": config.get(CONF_MIN_BATTERY_LEVEL, DEFAULT_MIN_BATTERY_LEVEL),
                    "unit": e.unit_of_measurement,
                }
            if e.original_device_class == SensorDeviceClass.TEMPERATURE:
                rules[READING_TEMPERATURE] = {
                    "entity": e.entity_id,
                    "min": int(plant.min_temp),
                    "max": int(plant.max_temp),
                    "unit": e.unit_of_measurement,
                }
            if e.unit_of_measurement == CONDUCTIVITY:
                rules[READING_CONDUCTIVITY] = {
                    "entity": e.entity_id,
                    "min": int(plant.min_soil_ec),
                    "max": int(plant.max_soil_ec),
                    "unit": e.unit_of_measurement,
                }
            if e.original_device_class == SensorDeviceClass.ILLUMINANCE:
                rules[READING_BRIGHTNESS] = {
                    "entity": e.entity_id,
                    "min": int(plant.min_light_lux),
                    "max": int(plant.max_light_lux),
                    "unit": e.unit_of_measurement,
                }

        super().__init__(hass, name, rules)

        self._attr_entity_picture = get_photo(hass, pid)

    @property
    def extra_state_attributes(self):
        attrib = super().extra_state_attributes

        if (plant := self.plant) is not None:
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

class DailyHistory:
    """Stores one measurement per day for a maximum number of days.

    At the moment only the maximum value per day is kept.
    """

    def __init__(self, max_length: int):
        """Create new DailyHistory with a maximum length of the history."""
        self.max_length = max_length
        self._days = None
        self._max_dict = {}

    def add_measurement(self, value:Any, timestamp:datetime.datetime=None):
        """Add a new measurement for a certain day."""
        day = (timestamp or datetime.datetime.now()).date()
        if not isinstance(value, (int, float)):
            return
        if self._days is None:
            self._days = deque()
            self._add_day(day, value)
        else:
            current_day = self._days[-1]
            if day == current_day:
                self._max_dict[day] = max(value, self._max_dict[day])
            elif day > current_day:
                self._add_day(day, value)
            else:
                _LOGGER.warning("Received old value, not storing it")

    @property
    def max(self):
        """Return the maximum value in the history."""
        if self._max_dict:
            return max(self._max_dict.values())
        return 0

    def _add_day(self, day:datetime.date, value:int|float):
        """Add a new day to the history.

        Deletes the oldest day, if the queue becomes too long.
        """
        if len(self._days) == self.max_length:
            oldest = self._days.popleft()
            del self._max_dict[oldest]
        self._days.append(day)
        self._max_dict[day] = value