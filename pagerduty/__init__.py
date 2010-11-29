#!/usr/bin/env python

class PagerDuty(object):
    def __init__(self, service_key, https=True):
        self.service_key = service_key
        self.api_endpoint = ("http", "https")[https] + "://events.pagerduty.com/generic/2010-04-15/create_event.json"

    def trigger(self, description, incident_key=None, details=None):
        self._request("trigger", description=description, incident_key=incident_key, details=details)

    def acknowledge(self, incident_key, description=None, details=None):
        self._request("acknowledge", description=description, incident_key=incident_key, details=details)

    def resolve(self, incident_key, description=None, details=None):
        self._request("resolve", description=description, incident_key=incident_key, details=details)

    def _request(self, event_type, **kwargs):
        event = {
            "service_key": self.service_key,
            "event_type": event_type,
        }
        for k, v in kwargs.items():
            if v is not None:
                event[k] = v
