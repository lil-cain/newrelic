#!/usr/bin/python

import newrelic.account

class Alert_Policy(newrelic.account.Account):

    def __init__(self, policy_details, api_key):
        super(Alert_Policy, self).__init__(api_key)
        self.name = policy_details['name']
        self.enabled = policy_details['enabled']
        self.conditions = policy_details['conditions']
        self.id = policy_details['id']
        self.links = policy_details['links']
