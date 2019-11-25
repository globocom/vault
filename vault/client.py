# -*- coding: utf-8 -*-

from allaccess.clients import OAuth2Client
from requests.structures import CaseInsensitiveDict


class BearerOAuth2(object):

    def __init__(self, user_token):
        self.user_token = user_token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer {0}'.format(self.user_token)
        return r


class OAuth2BearerClient(OAuth2Client):

    def request(self, method, url, **kwargs):
        user_token = kwargs.pop('token', self.token)
        token, _ = self.parse_raw_token(user_token)

        headers = CaseInsensitiveDict(kwargs.get('headers', {}))
        kwargs['headers'] = self._apply_json_as_accept_type_when_not_defined(
            headers)

        if token is not None:
            kwargs['auth'] = BearerOAuth2(user_token=token)

        return super(OAuth2BearerClient, self).request(method, url, **kwargs)

    def _apply_json_as_accept_type_when_not_defined(self, headers):
        defined_accept = headers.get('Accept')
        if not defined_accept:
            headers['Accept'] = 'application/json'
        return headers
