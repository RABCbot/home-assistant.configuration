import asyncio
import logging
import requests
import json
import time
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.entity import Entity
from homeassistant.components.image_processing import DOMAIN
from homeassistant.const import CONF_NAME, CONF_API_KEY, CONF_TIMEOUT, ATTR_NAME, ATTR_ENTITY_ID, HTTP_BAD_REQUEST, HTTP_OK, HTTP_UNAUTHORIZED
from homeassistant.components.microsoft_face import CONF_AZURE_REGION, ATTR_CAMERA_ENTITY
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

VISION_URL = "api.cognitive.microsoft.com/vision/v2.0"
ANALIZE_URL = 'analyze'
DESCRIBE_URL = 'describe'
DETECT_URL = 'detect'
RECOGNIZE_URL = 'recognizeText'
SNAPSHOT_SERVICE = 'snapshot'

CONF_VISUAL_FEATURES = 'visualFeatures'
CONF_RECOGNIZETEXT_MODE = 'mode'
CONF_VISUAL_FEATURES_DEFAULT = 'Description,Faces'
CONF_RECOGNIZETEXT_MODE_DEFAULT = 'Printed'
ATTR_DESCRIPTION = 'description'
ATTR_JSON = 'json'
ATTR_OPERATION = 'operation'
ATTR_CONFIDENCE = 'confidence'

DATA_VISION = 'microsoft_vision'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_AZURE_REGION, default="eastus2"): cv.string,
        vol.Optional(CONF_VISUAL_FEATURES, default=CONF_VISUAL_FEATURES_DEFAULT): cv.string,
        vol.Optional(CONF_RECOGNIZETEXT_MODE, default=CONF_RECOGNIZETEXT_MODE_DEFAULT): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

SCHEMA_CALL_SERVICE = vol.Schema({
    vol.Required(ATTR_CAMERA_ENTITY): cv.string,
})

async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the platform."""
    if DATA_VISION not in hass.data:
        hass.data[DATA_VISION] = None

    devices = []
    device = MicrosoftVisionDevice(
        config.get(CONF_AZURE_REGION), 
        config.get(CONF_API_KEY),
        {CONF_VISUAL_FEATURES:config.get(CONF_VISUAL_FEATURES, CONF_VISUAL_FEATURES_DEFAULT),
        CONF_RECOGNIZETEXT_MODE:config.get(CONF_RECOGNIZETEXT_MODE, CONF_RECOGNIZETEXT_MODE_DEFAULT)})
    devices.append(device)
    hass.data[DATA_VISION] = device
    add_devices(devices)

    async def analize(service):
        device = hass.data[DATA_VISION]
        try:
            device.call_api(ANALIZE_URL)
        except HomeAssistantError as err:
            _LOGGER.error("Error on receive image from entity: %s", err)

    hass.services.async_register(DOMAIN, ANALIZE_URL, analize)

    async def describe(service):
        device = hass.data[DATA_VISION]
        try:
            device.call_api(DESCRIBE_URL)
        except HomeAssistantError as err:
            _LOGGER.error("Error calling describe: %s", err)

    hass.services.async_register(DOMAIN, DESCRIBE_URL, describe)

    async def detect(service):
        device = hass.data[DATA_VISION]
        try:
            device.call_api(DETECT_URL)
        except HomeAssistantError as err:
            _LOGGER.error("Error on receive image from entity: %s", err)

    hass.services.async_register(DOMAIN, DETECT_URL, detect)

    async def recognizeText(service):
        device = hass.data[DATA_VISION]
        try:
            device.call_api(RECOGNIZE_URL)
        except HomeAssistantError as err:
            _LOGGER.error("Error on receive image from entity: %s", err)

    hass.services.async_register(DOMAIN, RECOGNIZE_URL, recognizeText)

    async def snapshot(service):
        camera_entity = service.data.get(ATTR_CAMERA_ENTITY)
        camera = hass.components.camera
        device = hass.data[DATA_VISION]
        image = None
        try:
            image = await camera.async_get_image(camera_entity)
            device.set_image(image)
        except HomeAssistantError as err:
            _LOGGER.error("Error on receive image from entity: %s", err)

    hass.services.async_register(DOMAIN, SNAPSHOT_SERVICE, snapshot, schema=SCHEMA_CALL_SERVICE)

    return True

class MicrosoftVisionDevice(Entity):
    """Representation of a platform."""

    def __init__(self, server_loc, api_key, params=None):
        """Initialize the platform."""
        self._state = None
        self._name = DATA_VISION
        self._azure_location = server_loc
        self._params = params
        self._api_key = api_key
        self._description = None
        self._json = None
        self._image = None
        self._operation = None
        self._confidence = None

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
    def operation(self):
        """Return the Operation of the platform."""
        return self._operation

    @property
    def confidence(self):
        """Return the Operation of the platform."""
        return self._confidence

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
            ATTR_OPERATION: self._operation,
            ATTR_CONFIDENCE: self._confidence,
        }
        return attrs

    def call_api(self, operation):
        try:
            self._operation = operation
            url = "https://{0}.{1}/{2}".format(self._azure_location, VISION_URL, operation)

            headers = {"Ocp-Apim-Subscription-Key": self._api_key,
                       "Content-Type": "application/octet-stream"}
            response = requests.post(url, headers=headers, params=self._params, data=self._image.content)
            response.raise_for_status()

            self._json = None
            self._description = None
            self._confidence = None
            self.async_schedule_update_ha_state()

            if operation == DESCRIBE_URL:
                self._json = response.json()
                self._description = self._json["description"]["captions"][0]["text"]
                self._confidence = round(100 * self._json["description"]["captions"][0]["confidence"])

            if operation == ANALIZE_URL or operation == DETECT_URL:
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

    def set_image(self, image):
        self._image = image
