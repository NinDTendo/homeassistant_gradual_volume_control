DOMAIN = "grad_vol"
import time

def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""

    def handle_set_volume(call):
        """Handle the service call."""
        entity_ids = call.data.get('entity_id')
        target_volume= round(float(call.data.get('volume')),2)
        span = call.data.get('duration',5)
        for entity_id in entity_ids:
            volume = round(float(hass.states.get(entity_id).attributes.get('volume_level')),2)
            if volume == None or abs(volume-target_volume) < 0.02: continue
            sleeptime = span/(abs(volume - target_volume)/0.01)
            while abs(volume-target_volume) > 0.02:
                if target_volume < volume:
                    volume -= 0.01
                else:
                    volume += 0.01
                hass.services.call('media_player', 'volume_set', {'entity_id': entity_id, 'volume_level': volume})
                time.sleep(sleeptime)
            hass.services.call('media_player', 'volume_set', {'entity_id': entity_id, 'volume_level': target_volume})
        return

    hass.services.register(DOMAIN, "set_volume", handle_set_volume)

    # Return boolean to indicate that initialization was successful.
    return True