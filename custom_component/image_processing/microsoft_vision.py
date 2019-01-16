import asyncio
import logging
import requests
import json
import time
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.entity import Entity
from homeassistant.components.image_processing import DOMAIN
from homeassistant.const import CONF_NAME, CONF_API_KEY, CONF_TIMEOUT, ATTR_NAME, ATTR_ENTITY_ID
from homeassistant.components.microsoft_face import CONF_AZURE_REGION, ATTR_CAMERA_ENTITY
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

VISION_URL = "api.cognitive.microsoft.com/vision/v2.0"
ANALIZE_URL = 'analyze'
DESCRIBE_URL = 'describe'
DETECT_URL = 'detect'
RECOGNIZE_URL = 'recognizeText'

CONF_SERVICES = 'services'
CONF_VISUAL_FEATURES = 'visualFeatures'
CONF_RECOGNIZETEXT_MODE = 'mode'
CONF_VISUAL_FEATURES_DEFAULT = 'Description,Faces'
CONF_RECOGNIZETEXT_MODE_DEFAULT = 'Printed'
ATTR_DESCRIPTION = 'description'
ATTR_JSON = 'json'

DATA_VISION = 'microsoft_vision'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_SERVICES): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_AZURE_REGION, default="eastus2"): cv.string,
        vol.Optional(CONF_VISUAL_FEATURES, default=CONF_VISUAL_FEATURES_DEFAULT): cv.string,
        vol.Optional(CONF_RECOGNIZETEXT_MODE, default=CONF_RECOGNIZETEXT_MODE_DEFAULT): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

SCHEMA_CALL_SERVICE = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.string,
    vol.Required(ATTR_CAMERA_ENTITY): cv.string,
})

async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the platform."""
    if DATA_VISION not in hass.data:
        hass.data[DATA_VISION] = []

    devices = []
    services = config.get(CONF_SERVICES)

    for service in services:
        device = MicrosoftVisionDevice(
            service, 
            config.get(CONF_AZURE_REGION), 
            config.get(CONF_API_KEY),
            {CONF_VISUAL_FEATURES:config.get(CONF_VISUAL_FEATURES, CONF_VISUAL_FEATURES_DEFAULT),
            CONF_RECOGNIZETEXT_MODE:config.get(CONF_RECOGNIZETEXT_MODE, CONF_RECOGNIZETEXT_MODE_DEFAULT)})
        devices.append(device)
        hass.data[DATA_VISION].append(device)

    add_devices(devices)

    async def call_api(service):
        entity_id = service.data.get(ATTR_ENTITY_ID)
        camera_entity = service.data.get(ATTR_CAMERA_ENTITY)
        devices = hass.data[DATA_VISION]
        for device in devices:
            if entity_id == device.entity_id:
                camera = hass.components.camera
                image = None
                try:
                    image = await camera.async_get_image(camera_entity)
                    device.call_api(image.content)
                except HomeAssistantError as err:
                    _LOGGER.error("Error on receive image from entity: %s", err)


    hass.services.async_register(DOMAIN, 'call_api', call_api, schema=SCHEMA_CALL_SERVICE)

    return True

class MicrosoftVisionDevice(Entity):
    """Representation of a platform."""

    def __init__(self, operation, server_loc, api_key, params=None):
        """Initialize the platform."""
        self._state = None
        self._name = operation
        self._url = "https://{0}.{1}/{2}".format(server_loc, VISION_URL, operation)
        self._params = params
        self._api_key = api_key
        self._description = None
        self._json = None

    @property
    def name(self):
        """Return the name of the platform."""
        return self._name

    @property
    def description(self):
        """Return the description of the platform."""
        return self._description

    @property
    def json(self):
        """Return the JSON of the platform."""
        return self._json

    @property
    def state(self):
        """Return the state of the platform."""
        return self._state

    @property
    def state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_DESCRIPTION: self._description,
            ATTR_JSON: self._json,
        }
        return attrs

    def call_api(self, image):
        try:
            headers = {"Ocp-Apim-Subscription-Key": self._api_key,
                       "Content-Type": "application/octet-stream"}
            response = requests.post(self._url, headers=headers, params=self._params, data=image)
            response.raise_for_status()

            self._json = None
            self._description = None
            self.async_schedule_update_ha_state()

            if self._name == DESCRIBE_URL:
                self._json = response.json()
                self._description = self._json["description"]["captions"][0]["text"]

            if self._name == ANALIZE_URL or self._name == DETECT_URL:
                self._json = response.json()

            if response.status_code == 202:
                url = response.headers["Operation-Location"]
                time.sleep(4)
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                self._description = None
                self._json = response.json()

                if self._json["status"] == "Succeeded":
                    for line in self._json["recognitionResult"]["lines"]:
                        if line["text"] != "888":
                            self._description = line["text"]

            self.async_schedule_update_ha_state()

        except HomeAssistantError as err:
            _LOGGER.error("Failed to call Microsoft API with error: %s", err)

