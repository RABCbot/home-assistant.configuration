import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'textbox'
CONF_TEXT = 'text'
DEFAULT_TEXT = 'Hello World!'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
      vol.Required(CONF_TEXT): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

def setup(hass, config):
    entity_id = 'textbox.hola'
    text = config[DOMAIN].get(CONF_TEXT, DEFAULT_TEXT)
    hass.states.set(entity_id, text)

    def set_text_call(call):
        hass.states.set(entity_id, call.data.get(CONF_TEXT, DEFAULT_TEXT))

    hass.services.register(DOMAIN, 'set_text', set_text_call)

    return True

