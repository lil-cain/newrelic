#!/usr/bin/python
import requests, dateutil.parser
import json, datetime


class NewRelicError(Exception):
    pass


class NewRelicBadRequest(NewRelicError):
    pass


class NewRelicAuthError(NewRelicError):
    pass


class NewRelicRequestFailed(NewRelicError):
    pass


class NewRelicNotFoundError(NewRelicError):
    pass


class NewRelicApi(object):

    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.headers = {'X-Api-Key': api_key}
        self.endpoint = 'https://api.newrelic.com/v2'
        self.api_key = api_key

    def _request(self, method, path, data=None):
        url = '%s/%s' % (self.endpoint, path)
        method = method.lower()
        if method == 'get':
            response = self.session.get(url)
        elif method == 'post':
            reponse = self.session.post(url, data=data)
        elif method == 'put':
            reponse = self.session.put(url, data=data)
        elif method == 'delete':
            reponse = self.session.delete(url)
        else:
            raise RuntimeError("Method %s is not supported" % method)

        if response.status_code >= 200 and response.status_code < 300:
            return response
        elif response.status_code == 400:
            raise NewRelicBadRequest
        elif response.status_code == 401:
            raise NewRelicAuthError
        elif reponse.status_code == 402:
            raise NewRelicRequestFailed
        elif reponse.status_code == 404:
            raise NewRelicNotFoundError
        else:
            raise NewRelicError

    def get(self, path):
        return self._request('get', path)

    def post(self, path, data=None):
        return self._request('post', path, data)

    def put(self, path, data=None):
        return self._request('put', path, data)

    def delete(self, path):
        return self._request('delete', path)

    def _paginated_get(self, path):
        more_data = True
        while more_data is True:
            response = self._request('get', path)
            yield response.content
            if 'next' not in response.links:
                more_data = False

    def list_applications(self):
        for response in self._paginated_get('/applications.json'):
            applications = json.loads(response)['applications']
            for application in applications:
                yield application

    def get_application(self, app_id):
        response = self._request('get', 'applications/%d' % app_id)
        return json.loads(response)['applications']

    def get_alert_policy(self, alert_id):
        response = self._request('get', 'alert_policies/%d.json' % alert_id)
        return json.loads(response.content)['alert_policy']

    def list_alert_policies(self):
        for response in self._paginated_get('alert_policies.json'):
            yield json.loads(response)['alert_policy']

    def get_notification_channel(self, notification_id):
        response = self._request('get',
                                 'notification_channels/%d.json'
                                 % int(notification_id))
        return json.loads(response.content)['notification_channel']

    def list_notification_channels(self):
        for response in self._paginated_get('notification_channels.json'):
            yield json.loads(response)['notification_channel']

    def list_servers(self):
        for response in self._paginated_get('servers.json'):
            servers = json.loads(response)['servers']
            for server in servers:
                server['last_reported_at'] = dateutil.parser.parse(
                    server['last_reported_at'])
                yield server
