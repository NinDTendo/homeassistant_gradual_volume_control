DOMAIN = "grad_vol"
import asyncio

async def async_setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    volume_tasks = {}

    async def async_handle_set_volume(call):
        """Handle the service call for gradually setting volume."""
        entity_ids = call.data.get('entity_id', [])
        target_volume = round(float(call.data.get('volume', 0)), 2)
        span = call.data.get('duration', 5)
        
        for entity_id in entity_ids:
            if entity_id in volume_tasks:
                volume_tasks[entity_id].cancel()
            
            volume_tasks[entity_id] = hass.async_create_task(async_adjust_volume(entity_id, target_volume, span))

    async def async_adjust_volume(entity_id, target_volume, span):
        """Gradually adjust volume of a media player entity."""
        try:
            state = hass.states.get(entity_id)
            if not state or state.state == 'off':
                return
            
            volume = state.attributes.get('volume_level')
            if volume is None:
                return
            
            volume = round(float(volume), 2)
            if abs(volume - target_volume) < 0.02:
                return
            
            steps = abs(int((volume - target_volume) / 0.01))
            sleeptime = span / max(steps, 1)
            
            while abs(volume - target_volume) > 0.02:
                if entity_id not in volume_tasks:
                    break  # Task was canceled
                
                if target_volume < volume:
                    volume -= 0.01
                else:
                    volume += 0.01
                
                # volume = round(volume, 2)
                await hass.services.async_call('media_player', 'volume_set', {'entity_id': entity_id, 'volume_level': volume})
                await asyncio.sleep(sleeptime)
            
            await hass.services.async_call('media_player', 'volume_set', {'entity_id': entity_id, 'volume_level': target_volume})
        except asyncio.CancelledError:
            pass  # Task was cancelled
        finally:
            volume_tasks.pop(entity_id, None)

    async def async_cancel(call):
        """Cancel the volume adjustment for a specific entity or all."""
        entity_ids = call.data.get('entity_id', [])
        if not entity_ids:
            for task in volume_tasks.values():
                task.cancel()
            volume_tasks.clear()
        else:
            for entity_id in entity_ids:
                if entity_id in volume_tasks:
                    volume_tasks[entity_id].cancel()
                    volume_tasks.pop(entity_id, None)

    hass.services.async_register(DOMAIN, "set_volume", async_handle_set_volume)
    hass.services.async_register(DOMAIN, "cancel_all", async_cancel)
    
    return True
