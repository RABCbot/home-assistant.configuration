import logging

from homeassistant.const import ATTR_ENTITY_ID, CONF_ICON, CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent

DOMAIN = 'hola'
ENTITY_ID_FORMAT = DOMAIN + '.{}'
_LOGGER = logging.getLogger(__name__)

def setup(hass, config):

    _LOGGER.info('epa!')

    # component = EntityComponent(_LOGGER, DOMAIN, hass)

    entities = []

    for object_id, cfg in config[DOMAIN].items():
        name = cfg.get(CONF_NAME)
        _LOGGER.info(name)

    return True

