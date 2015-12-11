#!/usr/bin/python
import json
import newrelic


class NewRelicPartnerApi(newrelic.NewRelicApi):

    def __init__(self, api_key, partner_id):
        super(NewRelicPartnerApi, self).__init__(api_key)
        self.endpoint = 'https://rpm.newrelic.com/api/v2/partners/%s'\
            % partner_id

    def list_accounts(self):
        for account_list in self.__paginated_get__('accounts'):
            account_list = json.loads(account_list)
            for account in account_list['accounts']:
                yield account

    def get_account_details(self, account_id):
        content = self.get('account/%s' % account_id)
        return json.loads(content)

    def delete_account(self, account_id):
        self.delete('account/%s' % account_id)
