# -*- coding: utf-8 -*-
import json
from urllib.parse import urljoin

import requests
from requests_oauthlib import OAuth2Session

__version__ = '0.0.2'


def register_app(client_name, base_url, redirect_uris='urn:ietf:wg:oauth:2.0:oob',
                 scopes='read write follow', website=None, file_path=None):
    """Register application
    
    :param client_name: Name of your application
    :param base_url: Specify the base URL of the Mastodon instance you want to connect. Example: https://mstdn.jp
    :param redirect_uris: Where the user should be redirected after authorization
        (for no redirect, `use urn:ietf:wg:oauth:2.0:oob`)
    :param scopes: This can be a space-separated list of the following items: "read", "write" and "follow"
    :param website: (optional) URL to the homepage of your app
    :param file_path: (optional) Specify the file path if you want to save the acquired information in a JSON file.
    :return: Returns `id`, `client_id` and `client_secret`
    :rtype: dict
    
    Usage::
    
        >>> register_app('myapp', 'https://mstdn.jp')
        {'id': 1234, 'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob', 'client_id': '...', 'client_secret': '...'}
    
    """
    data = {
        'client_name': client_name,
        'redirect_uris': redirect_uris,
        'scopes': scopes,
        'website': website,
    }
    url = urljoin(base_url, '/api/v1/apps')
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    data = resp.json()
    if file_path:
        with open(file_path, 'w') as fp:
            json.dump(data, fp, indent=2, sort_keys=True)
    return data


class OAuth2Handler:
    """OAuth2 authentication handler

    :param client_id: Your Client ID
    :param client_secret: Your Client Secret
    :param base_url: Specify the base URL of the Mastodon instance you want to connect. Example: https://mstdn.jp
    :param scope: This can be a space-separated list of the following items: "read", "write" and "follow"
    :type scope: list of str
    :param redirect_uri: Where the user should be redirected after authorization
        (for no redirect, `use urn:ietf:wg:oauth:2.0:oob`)

    """
    def __init__(self, client_id, client_secret, base_url, scope=('read',), redirect_uri='urn:ietf:wg:oauth:2.0:oob'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url,
        self.redirect_uri = redirect_uri
        self.scope = scope
        self._oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scope)

    def get_authorization_url(self):
        """Get authorization URL
        
        :return: Authorization URL and state
        :rtype: tuple

        """
        url = urljoin(self.base_url, '/oauth/authorize')
        authorization_url, state = self._oauth.authorization_url(url)
        return authorization_url, state

    def fetch_token(self, code, file_path=None):
        """Fetch token
        
        :param code: Authorization code
        :param file_path: (optional) Specify the file path if you want to save the acquired information in a JSON file.
        :return: Returns `access_token`, `token_type`, `scope` and `created_at`.
        :rtype: dict

        """
        token_url = urljoin(self.base_url, '/oauth/token')
        token = self._oauth.fetch_token(token_url, authorization_response=code, client_id=self.client_id,
                                        client_secret=self.client_secret, code=code)
        if file_path:
            with open(file_path, 'w') as fp:
                json.dump(token, fp, indent=2, sort_keys=True)
        return token
