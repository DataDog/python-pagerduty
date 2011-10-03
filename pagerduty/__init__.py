#!/usr/bin/env python

try:
    import json
except ImportError:
    import simplejson as json
import urllib2
import urllib
import base64

from pagerduty.version import *

__version__ = VERSION

class SchedulesError(urllib2.HTTPError):
    def __init__(self, http_error):
        urllib2.HTTPError.__init__(self, http_error.filename, http_error.code, http_error.msg, http_error.hdrs, http_error.fp)

        data = self.read()

        j = json.loads(data)
        error = j['error']
        self.statuscode = error['code']
        self.statusdesc = ' | '.join(error['errors'])
        self.errormessage = error['message']

    def __repr__(self):
        return 'Pagerduty Schedules Error: HTTP {0} {1} returned with message, "{3}"' % (self.statuscode, self.statusdesc, self.errormessage)

    def __str__(self):
        return self.__repr__()

class SchedulesRequest(urllib2.Request):
    def __init__(self, connection, resource, params):
        """Representation of a Pagerduty Schedules API HTTP request.
        
        :type connection: :class:`Schedules`
        :param connection: Schedules connection object populated with a username, password and base URL
        
        :type resource: string
        :param resource: Pagerduty resource to query (lowercase)
        
        :type params: dict
        :param params: Params to be sent with a GET request
        
        """

        encoded_params = urllib.urlencode(params)
        url = connection.base_url + resource + '?' + encoded_params
        urllib2.Request.__init__(self, url)

        # Add auth header
        base64string = base64.encodestring('%s:%s' % (connection.username, connection.password)).replace('\n','')
        self.add_header("Authorization", "Basic %s" % base64string)

    
    def __repr__(self):
        return 'SchedulesRequest: {0} {1}' % (self.get_method(), self.get_full_url())
        
        
    def fetch(self):
        """Execute the request."""
        try:
            response = urllib2.urlopen(self)
        except urllib2.HTTPError, e:
            raise SchedulesError(e)
        else:
            return SchedulesResponse(response)
        

class SchedulesResponse(object):
    def __init__(self, response):
        """Representation of a Pagerduty Schedules API HTTP response."""
        self.data = response.read()

        self.headers = response.headers
        self.content = json.loads(self.data)
        
        if 'error' in self.content:
            raise SchedulesError(self.content)


    def __repr__(self):
        return 'SchedulesResponse: {0}'.format(self.content.items())

class Schedules(object):
    """ Interface to Pagerduty Schedule API.
    """
    def __init__(self, subdomain, schedule_id, username, password):

        self.username = username
        self.password = password

        self.base_url = 'https://{0}.pagerduty.com/api/v1/schedules/{1}/'.format(subdomain, schedule_id)

    def entries(self, since, until):
        """ Query schedule entries.
        """
        params = {'since' : since, 'until' : until}
        response = SchedulesRequest(self, 'entries', params).fetch()
        for e in response.content['entries']:
            print e['user']['name'], ' ', e['start'], ' ', e['end']


class PagerDutyException(Exception):
    def __init__(self, status, message, errors):
        super(PagerDutyException, self).__init__(message)
        self.msg = message
        self.status = status
        self.errors = errors
    
    def __repr__(self):
        return "%s(%r, %r, %r)" % (self.__class__.__name__, self.status, self.msg, self.errors)
    
    def __str__(self):
        txt = "%s: %s" % (self.status, self.msg)
        if self.errors:
            txt += "\n" + "\n".join("* %s" % x for x in self.errors)
        return txt

class PagerDuty(object):
    def __init__(self, service_key, https=True, timeout=15):
        self.service_key = service_key
        self.api_endpoint = ("http", "https")[https] + "://events.pagerduty.com/generic/2010-04-15/create_event.json"
        self.timeout = timeout
    
    def trigger(self, description, incident_key=None, details=None):
        return self._request("trigger", description=description, incident_key=incident_key, details=details)
    
    def acknowledge(self, incident_key, description=None, details=None):
        return self._request("acknowledge", description=description, incident_key=incident_key, details=details)
    
    def resolve(self, incident_key, description=None, details=None):
        return self._request("resolve", description=description, incident_key=incident_key, details=details)
    
    def _request(self, event_type, **kwargs):
        event = {
            "service_key": self.service_key,
            "event_type": event_type,
        }
        for k, v in kwargs.items():
            if v is not None:
                event[k] = v
        encoded_event = json.dumps(event)
        try:
            res = urllib2.urlopen(self.api_endpoint, encoded_event, self.timeout)
        except urllib2.HTTPError, exc:
            if exc.code != 400:
                raise
            res = exc
        
        result = json.loads(res.read())
        
        if result['status'] != "success":
            raise PagerDutyException(result['status'], result['message'], result['errors'])
        
        # if result['warnings]: ...
        
        return result.get('incident_key')
