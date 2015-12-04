#!/usr/bin/python
import requests
import json
from newrelic.application import Application
from newrelic.alert_policy import Alert_policy


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


class Account(object):

    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.headers = {'X-Api-Key': api_key}
        self.endpoint = 'https://api.newrelic.com/v2'
        self.api_key = api_key

    def __request__(self, method, path, data=None):
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
        return self.__request__('get', path)

    def post(self, path, data=None):
        return self.__request__('post', path, data)

    def put(self, path, data=None):
        return self.__request('put', path, data)

    def delete(self, path):
        return self.__request__('delete', path)

    def __paginated_get__(self, path):
        more_data = True
        while more_data is True:
            response = self.__request__('get', path)
            yield response.content
            if 'next' not in response.links:
                more_data = False

    def list_applications(self):
        for response in self.__paginated_get__('/applications.json'):
            applications = json.loads(response)['applications']
            for application in applications:
                yield Application(application,
                                           self.session.headers['X-Api-Key'])

    def get_application(self, app_id):
        response = self.__request__('get', 'applications/%d' % app_id)
        application = json.loads(response)['applications']
        return Application(application,
                                    self.session.headers['X-Api-Key'])

    def get_alert_policy(self, alert_id):
        response = self.__request__('get', 'alert_policies/%d.json' % alert_id)
        data = json.loads(response.content)['alert_policy']
        return Alert_policy(self, data,
                                     self.session.headers['X-Api-Key'])

    def list_alert_policies(self):
        for response in self.__paginated_get__('alert_policies.json'):
            data = json.loads(response.content)['alert_policy']
            yield Alert_policy(self, data,
                                        self.session.headers['X-Api-Key'])

    def __get_attr__(self, name):
        if name == 'applications':
            self.applications = []
            try:
                for app_id in self.links['application']:
                    self.applications.append(self.get_application(app_id))
            except AttributeError:
                self.applications = [ application for application in self.list_applications() ] 
        elif name == 'alert_policies':
            try:
                self.alert_policies = []
                for alert_id in self.links['alert_policies']:
                    self.alert_policies.append(self.get_alert_policy(alert_id))
            except AttributeError:
                self.alert_policies = [ alert_policy for alert_policy in self.list_alert_policies() ]
