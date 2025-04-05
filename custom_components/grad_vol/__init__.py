DOMAIN = "grad_vol"
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    volume_tasks = {}
    _LOGGER.debug("Setting up Gradual Volume component")

    async def async_handle_set_volume(call):
        """Handle the service call for gradually setting volume."""
        _LOGGER.debug("Gradual Volume service called")
        _LOGGER.debug(f"Service data: {call.data}")

        entity_ids = call.data.get('entity_id', [])
        target_volume = round(float(call.data.get('volume', 0)), 2)
        span = call.data.get('duration', 5)
        tasks = {}
        se = asyncio.Event()
        for entity_id in entity_ids:
            if entity_id in volume_tasks:
                volume_tasks[entity_id].cancel()
            tasks[entity_id] = hass.async_create_task(async_adjust_volume(entity_id, target_volume, span, se))
        _LOGGER.debug(f"Tasks: {tasks}")
        volume_tasks.update(tasks)
        _LOGGER.debug(f"Volume tasks: {volume_tasks}")
        _LOGGER.debug("starting tasks with start_event")
        se.set()  # Start all tasks at once
        await asyncio.gather(*tasks.values())
        _LOGGER.debug("Service_call finished")

    async def async_adjust_volume(entity_id, target_volume, span, start_event):
        """Gradually adjust volume of a media player entity."""
        _LOGGER.debug("Waiting for start signal...")
        await start_event.wait()
        _LOGGER.debug(f"Start signal received.")
        try:
            state = hass.states.get(entity_id)
            if not state or state.state == 'off':
                _LOGGER.debug(f"Entity {entity_id} is off or not found, skipping volume adjustment.")
                return
            
            volume = state.attributes.get('volume_level')
            if volume is None:
                _LOGGER.debug(f"Volume level not found for {entity_id}, skipping volume adjustment.")
                return
            
            volume = round(float(volume), 2)
            # if abs(volume - target_volume) < 0.02:
            #     return
            
            steps = abs(int((volume - target_volume) / 0.01))
            sleeptime = span / max(steps, 1)
            _LOGGER.debug(f"Gradually adjusting volume for {entity_id} from {volume} to {target_volume} in {steps} steps over {span} seconds.")

            while abs(volume - target_volume) >= 0.02:
                if entity_id not in volume_tasks:
                    _LOGGER.debug(f"Volume adjustment for {entity_id} not in tasks, cancelled...")
                    break  # Task was canceled
                
                if target_volume < volume:
                    volume -= 0.01
                else:
                    volume += 0.01
                
                # volume = round(volume, 2)
                await hass.services.async_call('media_player', 'volume_set', {'entity_id': entity_id, 'volume_level': volume})
                _LOGGER.debug(f"Setting volume for {entity_id} to {volume}, sleeping ...")
                await asyncio.sleep(sleeptime)

            _LOGGER.debug(f"Final volume for {entity_id} set to {target_volume}.")
            await hass.services.async_call('media_player', 'volume_set', {'entity_id': entity_id, 'volume_level': target_volume})
            _LOGGER.debug("finished")

        except asyncio.CancelledError:
            _LOGGER.debug(f"Volume adjustment for {entity_id} was cancelled.")
            pass  # Task was cancelled

        finally:
            volume_tasks.pop(entity_id, None)
            _LOGGER.debug(f"Volume task for {entity_id} removed from tasks.")

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
