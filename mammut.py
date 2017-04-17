# -*- coding: utf-8 -*-
import json
from urllib.parse import urljoin

import requests

__version__ = '0.0.1'


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
