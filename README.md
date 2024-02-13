# Adano lawn mower integration for Home Assistant
Home assistant integration from lawnmower using the robotic-mower connect APP.

## Tested models
  - Adano RM6

## Install
#### Manually
In Home Assistant, create a folder under *custom_components* named *adano* and copy all the content of this project to that folder.
Restart Home Assistant and go to *Devices and Services* and press *+Add integration*.
Search for *Adano robotic mower* and add it.
#### HACS Custom Repository
In HACS, add a custom repository and use https://github.com/Sdahl1234/Adano-lawn-mower
Download from HACS.
Restart Home Assistant and go to *Devices and Services* and press *+Add integration*.
Search for *Adano robotic mower* and add it.

## Configuration
You must now choose a name for the device. Email and password for the robotic-mower connect APP.

## Update of sensors
If the mower is turne off you will only reveive a minimum of updates.
Sensors are updated as they are presented by the mqtt server. You can turn off your mower and turn it on again while the integration is running to get the most of the sensors updated.


More description later
