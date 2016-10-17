import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'hola'
ATTR_NAME = 'quien'
DEFAULT_NAME = 'Nadie'

def setup(hass, config):
    entity_id = 'hola.tipo'
    hass.states.set(entity_id, DEFAULT_NAME)

    _LOGGER.error("Hola que tal!")

    def set_text_call(call):
        hass.states.set(entity_id, call.data.get(ATTR_NAME, DEFAULT_NAME))

    hass.services.register(DOMAIN, 'action', set_text_call)

    return True
