import logging
from homeassistant.components.zwave import (
    ATTR_NODE_ID, ATTR_VALUE_ID, ZWaveDeviceEntity)
from homeassistant.components import zwave

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'Trane'
ATTR_NAME = 'Temp'
DEFAULT_NAME = ''

def setup_platform(hass, config, add_devices, discovery_info=None):
    node = zwave.NETWORK.nodes[discovery_info[ATTR_NODE_ID]]
    value = node.values[discovery_info[ATTR_VALUE_ID]]
    value.set_change_verified(False)
    
    _LOGGER.info("discovery_info=%s and zwave.NETWORK=%s",
                  discovery_info, zwave.NETWORK)

    add_devices([Trane(value)])

    return True

class Trane(ZWaveDeviceEntity):
  def __init_(self, value):
    ZWaveDeviceEntity.__init__(self, value, DOMAIN)


