import logging
import requests
import json
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.entity import Entity
from homeassistant.components.image_processing import DOMAIN
from homeassistant.const import CONF_NAME, CONF_API_KEY, CONF_TIMEOUT, ATTR_NAME, ATTR_ENTITY_ID
from homeassistant.components.microsoft_face import CONF_AZURE_REGION, ATTR_CAMERA_ENTITY
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

VISION_API_URL = "api.cognitive.microsoft.com/vision/v2.0/analyze?visualFeatures=Categories,Description"
ATTR_DESCRIPTION = 'description'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_AZURE_REGION, default="eastus2"): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

SCHEMA_CALL_SERVICE = vol.Schema({
    vol.Required(ATTR_CAMERA_ENTITY): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the platform."""
    device = MicrosoftVisionDevice(
        config.get(CONF_NAME), 
        config.get(CONF_AZURE_REGION), 
        config.get(CONF_API_KEY))
    add_devices([device])

    def call_api(service):
        device.call_api()

    hass.services.register(
        DOMAIN, 'call_api', call_api)

    return True

class MicrosoftVisionDevice(Entity):
    """Representation of a platform."""

    def __init__(self, name, server_loc, api_key):
        """Initialize the platform."""
        self._state = None
        self._name = name
        self._url = "https://{0}.{1}".format(server_loc, VISION_API_URL)
        self._description = "this is the description"
        self._api_key = api_key

    @property
    def name(self):
        """Return the name of the platform."""
        return self._name

    @property
    def description(self):
        """Return the description of the platform."""
        return self._description

    @property
    def state(self):
        """Return the state of the platform."""
        return self._state

    @property
    def state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_DESCRIPTION: self._description,
        }
        return attrs

    def call_api(self):
        image_path = "/config/camera/front.jpg"
        image = open(image_path, "rb").read()

        try:
            headers = {"Ocp-Apim-Subscription-Key": self._api_key,
                       "Content-Type": "application/octet-stream"}
            response = requests.post(self._url, headers=headers, data=image)
            self._description = response.json()["description"]["captions"][0]["text"]
            self.schedule_update_ha_state()        
        except HomeAssistantError as err:
            _LOGGER.error("Failed to call Microsoft API with error: %s", err)

