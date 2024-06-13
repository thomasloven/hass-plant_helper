# Plant Helper

# WARNING: This is considered a beta version - expect significant functional and breaking changes

Helper for monitoring plant health using MiFlora devices

## Summary

| Go from this                                                                                                                     | To this                                                                                                                    |
| -------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| ![default device entities](https://github.com/thomasloven/hass-plant_helper/assets/1299821/5c031db8-a9bf-471d-8230-6195ed71d89a) | ![plant status card](https://github.com/thomasloven/hass-plant_helper/assets/1299821/64e5d969-1fff-43e6-b4d3-818051cabb2d) |

## Description

Home Assistant normally registers MiFlora plant monitors through [Xiaomi BLE](https://www.home-assistant.io/integrations/xiaomi_ble) as five separate entities.

This integration adds a new Helper which lets you combine those entities into a single binary sensor to indicate you plants health.

If you have installed the Plant Database it will also automatically set the environmental limits for your plant and select a picture for it.

## Installation

- Download the `custom_components/plant_helper` directory and place in your `custom_components` directory
- Or: add this repo (`thomasloven/hass-plant_helper`) as a custom repository in HACS and install the integration from there.

### Plant database

Xiaomi has created an extensive database of suitable conditions for a large variety of plants to use with their Flower Care apps. Unfortunately, those are very limited in functionality - which is why many choose to use Home Assistant for plant monitoring instead.

For copyright reasons, I cannot include the database in this repository, but it's easy to import this "MiFloraDB" yourself.

- Find and download the file `PlantDB_*.csv` and place directly in your Home Assistant configuration directory.
  The `*` in the name can be anything, but the filename _must_ start with `PlantDB` and end with `.csv`.
- Optional: Download the plant photos and extract to a folder named exactly `plant_photos` which is placed directly in your Home Assistant configuration directory.

## Usage:

- Make sure you have at least one MiFlora Device set up and working. Going to the device settings you should see something like this:

![default device entities](https://github.com/thomasloven/hass-plant_helper/assets/1299821/5c031db8-a9bf-471d-8230-6195ed71d89a)

- Go to "Settings" -> "Devices & Services" -> "Helpers" [![Open your Home Assistant instance and show your helper entities.](https://my.home-assistant.io/badges/helpers.svg)](https://my.home-assistant.io/redirect/helpers/)

- Click "Create Helper"

- Select "Plant" from the list

- Name your plant, select the MiFlora device, and (optionally) select the special of your plant.

![plant helper configuration](https://github.com/thomasloven/hass-plant_helper/assets/1299821/fb5ed20c-afba-4546-9c1a-f5e1288a3884)

- You should now have a new `binary_sensor` entity which can be used in automations to e.g. alert you as soon as anything is wrong with your clorophyl babies. When the sensor is `off` everything is fine. If the sensor is `on`, the attributes of the sensor will tell you the problem.

- This integration also patches the [Plant Status card](https://www.home-assistant.io/dashboards/plant-status/) such that it accepts the newly created `binary_sensor` as an entity:

![plant status card](https://github.com/thomasloven/hass-plant_helper/assets/1299821/64e5d969-1fff-43e6-b4d3-818051cabb2d)

## Customization

If you have a plant that is not included in the database, or don't have the database installed. You can set max and min limits for any of the monitored conditions manually by going to the options for the new entity and deselecting the Species.

From the options, you will also be able to select which measures to include in the compound status check - if e.g. you want to ignore the brightness measurement.

![custom settings](https://github.com/thomasloven/hass-plant_helper/assets/1299821/537d6b52-1290-4a47-8eb6-482fc60bd70e)

![custom settings 2](https://github.com/thomasloven/hass-plant_helper/assets/1299821/706e9d40-a610-47c8-9314-b4483cb7176f)
