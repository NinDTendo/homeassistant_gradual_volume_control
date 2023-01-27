# homeassistant_gradual_volume_control
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
 This integration provides a service to gradually change the volume of a mediaplayer over a given timespan
## Installation (with HACS)

1. Go to Home Assistant > HACS > Integrations > Click on tree dot (on top right corner) > Custom repositories \
and fill :
   * **Repository** :  `NinDTendo/homeassistant_gradual_volume_control`
   * **Category** : `Integration` 

2. Click on `ADD`, restart HA.

## Installation (manual)
1. Download last release.
2. Unzip `grad_vol` folder into your HomeAssistant : `custom_components`
3. Restart HA

## Configuration

Edit your Home Assistant `configuration.yaml` and set :

``` YAML
grad_vol:
```
to use this integration.

## Usage

Using a service-call, you can gradually change the volume to a target volume over a given timespan

example:
``` YAML
service: grad_vol.set_volume
data:
  volume: <target volume [0.00; 1.00], required>
  duration: <timespan in seconds, optional>
target:
  entity_id: <entity_id, required>
``` 
