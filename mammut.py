# -*- coding: utf-8 -*-
import json
from urllib.parse import urljoin

import requests
from requests_oauthlib import OAuth2Session

__version__ = '0.1.0'


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
        self.base_url = base_url
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


class Mammut:
    """Mammut: Mastodon API for Python
    
    :params token: Token information include `access_token`.
    :params base_url: Specify the base URL of the Mastodon instance you want to connect. Example: https://mstdn.jp
    
    """
    def __init__(self, token, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer ' + token['access_token']})

    def _build_url(self, path):
        """Build URL
        
        :param path: URL path
        :return: Endpoint URL
        :rtype: str

        """
        return urljoin(self.base_url, path)

    def _build_parameters(self, params, ignores=None):
        """Build a suitable parameters for request.
        
        :param params: dict of arguments given to Mammut's methods.
        :param ignores: Ignore keys.
        :return: Parameters for request.
        :rtype: dict

        """
        if ignores is None:
            ignores = ('self',)
        return {k: v for k, v in params.items() if k not in ignores and v}

    def _request(self, method, url, data=None, params=None, files=None):
        """Talk to API server
        
        :param method: HTTP method
        :param url: Endpoint URL
        :param data: Form data
        :param params: query parameter
        :return: `requests.Response`
        :rtype: `requests.Response`
        
        """
        kwargs = {
            'data': data or {},
            'params': params or {},
            'files': files or {},
        }
        resp = self.session.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp

    #
    # Media - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#media
    #
    def upload_media(self, filename):
        """Uploading a media attachment

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#media
        :param filename: Media to be uploaded
        :return: Returns an Attachment that can be used when creating a status.
        :rtype: dict

        """
        url = self._build_url('/api/v1/media')
        with open(filename, 'rb') as file:
            files = {'file': file}
            return self._request('post', url, files=files)

    #
    # Statuses - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#statuses
    #
    def get_status(self, id_):
        """Fetching a status
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#fetching-a-status
        :param id_: Target Status ID
        :return: Returns a Status.
        :rtype: dict

        """
        url = self._build_url('/api/v1/statuses/{id}'.format(id=id_))
        return self._request('get', url)

    def post_status(self, status, in_reply_to_id=None, media_ids=None, sensitive=None, spoiler_text=None,
                      visibility=None):
        """Posting a new status
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#posting-a-new-status
        :param status:  The text of the status
        :param in_reply_to_id: (optional): local ID of the status you want to reply to
        :param media_ids: (optional): array of media IDs to attach to the status (maximum 4)
        :param sensitive: (optional): set this to mark the media of the status as NSFW
        :param spoiler_text: (optional): text to be shown as a warning before the actual content
        :param visibility: (optional): either "direct", "private", "unlisted" or "public"
        :return: Returns the new Status
        :rtype: dict

        """
        data = self._build_parameters(locals())
        data['media_ids[]'] = data.pop('media_ids')
        url = self._build_url('/api/v1/statuses')
        return self._request('post', url, data=data)

    def delete_status(self, id_):
        """Deleting a status:
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#deleting-a-status
        :param id_: Target status ID

        """
        url = self._build_url('/api/v1/statuses/{id}'.format(id=id_))
        return self._request('delete', url)
