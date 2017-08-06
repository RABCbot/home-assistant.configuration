import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'textbox'
ATTR_NAME = 'text'
DEFAULT_NAME = 'Hello World!'

def setup(hass, config):
    entity_id = 'textbox.hola'
    hass.states.set(entity_id, DEFAULT_NAME)

    def set_text_call(call):
        hass.states.set(entity_id, call.data.get(ATTR_NAME, DEFAULT_NAME))

    hass.services.register(DOMAIN, 'set_text', set_text_call)

    return True

