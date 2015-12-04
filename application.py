#!/usr/bin/python

import datetime
import newrelic.account

class Application(newrelic.account.Account):

    def __init__(self, app_details, api_key):
        super(Application, self).__init__(api_key)
        self.name = app_details['name']
        self.application_summary = app_details['application_summary']
        self.health_status = app_details['health_status']
        self.id = app_details['id']
        self.language = app_details['language']
        self.links = app_details['links']
        self.reporting = app_details['reporting']
        self.settings = app_details['settings']
        self.last_report = datetime.datetime.strptime(
            app_details['last_reported_at'],
            '%Y-%m-%dT%H:%M:%S%z')
