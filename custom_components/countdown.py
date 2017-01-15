import logging
from datetime import date

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'Countdown'

def setup(hass, config):
    entity_id = 'Countdown.Christmas'

    def DaysLeft():
      d1 = date.today()
      d2 = date(2016,12,25)
      d = d2.toordinal() - d1.toordinal()
      s = '%s days' % d
      return s


    hass.states.set(entity_id, DaysLeft())

    def set_text_call(call):
        hass.states.set(entity_id, DaysLeft())

    hass.services.register(DOMAIN, 'update', set_text_call)

    return True
