# -*- coding: utf-8 -*-
import json
from urllib.parse import urljoin

import requests
from requests_oauthlib import OAuth2Session

from .utils import bundle_media_description


#
# Register apps - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#apps
#
def register_app(client_name, base_url, redirect_uris='urn:ietf:wg:oauth:2.0:oob',
                 scopes='read write follow', website=None, file_path=None):
    """Register application
    
    :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#registering-an-application
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


#
# OAuth - https://github.com/tootsuite/documentation/blob/master/Using-the-API/OAuth-details.md
#
class OAuth2Handler:
    """OAuth2 authentication handler

    :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/OAuth-details.md
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
        :return: Response JSON
        :rtype: dict
        
        """
        kwargs = {
            'data': data or {},
            'params': params or {},
            'files': files or {},
        }
        resp = self.session.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp.json()

    #
    # Accounts - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#accounts
    #
    def get_account(self, id_):
        """Fetching an account

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#fetching-a-status
        :param id_: Target Account ID
        :return: Returns an Account.
        :rtype: dict

        """
        url = self._build_url('/api/v1/accounts/{id}'.format(id=id_))
        return self._request('get', url)

    def verify_credentials(self):
        """Getting the current user

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#getting-the-current-user
        :return: Returns the authenticated user's Account.
        :rtype: dict

        """
        url = self._build_url('/api/v1/accounts/verify_credentials')
        return self._request('get', url)

    def update_credentials(self, display_name=None, note=None, avatar=None, header=None):
        """Updating the current user
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#updating-the-current-user
        :param display_name: (optional) The name to display in the user's profile
        :param note: (optional) A new biography for the user
        :param avatar:  (optional) Image to display as the user's avatar file path.
        :param header: (optional) Image to display as the user's header image file path.
        :return: 
        :rtype: dict

        """
        data = {'display_name': display_name, 'note': note}

        files = []
        if avatar:
            files.append(bundle_media_description('avatar', avatar))
        if header:
            files.append(bundle_media_description('header', header))

        url = self._build_url('/api/v1/accounts/update_credentials')
        return self._request('patch', url, data=data, files=files)

    def get_followers(self, id_):
        """Getting an account's followers:
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#getting-an-accounts-followers
        :param id_: Target Account ID
        :return: Returns a list of Accounts.
        :rtype: list

        """
        url = self._build_url('/api/v1/accounts/{id}/followers'.format(id=id_))
        return self._request('get', url)

    def get_following(self, id_):
        """Getting who account is following

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#getting-who-account-is-following
        :param id_: Target Account ID
        :return: Returns an array of Accounts.
        :rtype: list

        """
        url = self._build_url('/api/v1/accounts/{id}/following'.format(id=id_))
        return self._request('get', url)

    def get_account_statuses(self, id_, only_media=False, exclude_replies=False):
        """Getting an account's statuses

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#getting-an-accounts-statuses
        :param id_: Target Account ID
        :param only_media: (optional): Only return statuses that have media attachments
        :param exclude_replies: (optional): Skip statuses that reply to other statuses
        :return: Returns an array of Statuses.
        :rtype: list

        """
        params = self._build_parameters(locals())
        url = self._build_url('/api/v1/accounts/{id}/statuses'.format(id=id_))
        return self._request('get', url, params=params)

    def follow(self, id_):
        """Following an account
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#followingunfollowing-an-account
        :param id_: Target Account ID
        :return: Returns the target account's Relationship.
        :rtype: dict

        """
        url = self._build_url('/api/v1/accounts/{id}/follow'.format(id=id_))
        return self._request('post', url)

    def unfollow(self, id_):
        """Unfollowing an account

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#followingunfollowing-an-account
        :param id_: Target Account ID
        :return: Returns the target account's Relationship.
        :rtype: dict

        """
        url = self._build_url('/api/v1/accounts/{id}/unfollow'.format(id=id_))
        return self._request('post', url)

    def block(self, id_):
        """Blocking an account

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#blockingunblocking-an-account
        :param id_: Target Account ID
        :return: Returns the target account's Relationship.
        :rtype: dict

        """
        url = self._build_url('/api/v1/accounts/{id}/block'.format(id=id_))
        return self._request('post', url)

    def unblock(self, id_):
        """Unblocking an account

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#blockingunblocking-an-account
        :param id_: Target Account ID
        :return: Returns the target account's Relationship.
        :rtype: dict

        """
        url = self._build_url('/api/v1/accounts/{id}/unblock'.format(id=id_))
        return self._request('post', url)

    def mute(self, id_):
        """Muting an account

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#mutingunmuting-an-account
        :param id_: Target Account ID
        :return: Returns the target account's Relationship.
        :rtype: dict

        """
        url = self._build_url('/api/v1/accounts/{id}/mute'.format(id=id_))
        return self._request('post', url)

    def unmute(self, id_):
        """Unmuting an account

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#mutingunmuting-an-account
        :param id_: Target Account ID
        :return: Returns the target account's Relationship.
        :rtype: dict

        """
        url = self._build_url('/api/v1/accounts/{id}/unmute'.format(id=id_))
        return self._request('post', url)

    def get_relationships(self, id_):
        """Getting an account's relationships
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#getting-an-accounts-relationships
        :param id_: Account IDs
        :type id_: list or int
        :return: Returns an list of Relationships of the current user to a list of given accounts.
        :rtype: list

        """
        params = {'id': id_}
        url = self._build_url('/api/v1/accounts/relationships')
        return self._request('get', url, params=params)

    def search_accounts(self, q, limit=40):
        """Searching for accounts
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#searching-for-accounts
        :param q: What to search for
        :param limit: (optional) Maximum number of matching accounts to return (default: 40)
        :return: Returns an array of matching Accounts.
            Will lookup an account remotely if the search term is in the username@domain format
            and not yet in the database.
        :rtype: list

        """
        params = self._build_parameters(locals())
        url = self._build_url('/api/v1/accounts/search')
        return self._request('get', url, params=params)

    #
    # Blocks - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#blocks
    #
    def list_blocks(self):
        """Fetching a user's blocks
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#fetching-a-users-blocks
        :return: Returns a list of Accounts blocked by the authenticated user.
        :rtype: list

        """
        url = self._build_url('/api/v1/blocks')
        return self._request('get', url)

    #
    # Favourites - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#favourites
    #
    def get_favourites(self):
        """Fetching a user's favourites
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#fetching-a-users-favourites
        :return: Returns a list of Statuses favored by the authenticated user.
        :rtype: list

        """
        url = self._build_url('/api/v1/favourites')
        return self._request('get', url)

    #
    # Follows - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#follows
    #
    def remote_follow(self, uri):
        """Following a remote user
        
        :reference:https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#following-a-remote-user
        :param uri: `username@domain` of the person you want to follow
        :return: Returns the local representation of the followed account, as an Account.
        :rtype: dict

        """
        data = {'uri': uri}
        url = self._build_url('/api/v1/follows')
        return self._request('post', url, data=data)

    #
    # Media - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#media
    #
    def upload_media(self, filename):
        """Uploading a media attachment

        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#uploading-a-media-attachment
        :param filename: Media to be uploaded
        :return: Returns an Attachment that can be used when creating a status.
        :rtype: dict

        """
        url = self._build_url('/api/v1/media')
        with open(filename, 'rb') as file:
            files = {'file': file}
            return self._request('post', url, files=files)

    #
    # Mutes - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#mutes
    #
    def list_mutes(self):
        """Fetching a user's mutes
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#fetching-a-users-mutes
        :return: 
        """
        url = self._build_url('/api/v1/mutes')
        return self._request('get', url)

    #
    # Notifications - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#notifications
    #
    def notifications(self):
        """Fetching a user's notifications
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#fetching-a-users-notifications
        :return: Returns a list of Notifications for the authenticated user.
        :rtype: list

        """
        url = self._build_url('/api/v1/notifications')
        return self._request('get', url)

    def get_notification(self, id_):
        """Getting a single notification
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#getting-a-single-notification
        :param id_: Target notification ID
        :return: Returns the Notification.
        :rtype: dict

        """
        url = self._build_url('/api/v1/notifications/{id}'.format(id=id_))
        return self._request('get', url)

    def clear_notifications(self):
        """Clearing notifications
        
        Deletes all notifications from the Mastodon server for the authenticated user. 
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#clearing-notifications
        :return: Returns an empty dict
        :rtype: dict

        """
        url = self._build_url('/api/v1/notifications/clear')
        return self._request('post', url)

    #
    # Search - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#search
    #
    def search(self, q, resolve=False):
        """Searching for content
        
        :param q: The search query
        :param resolve: Whether to resolve non-local accounts
        :return: Returns Results. If q is a URL, Mastodon will attempt to fetch the provided account
            or status. Otherwise, it will do a local account and hashtag search.
        :rtype: dict

        """
        params = self._build_parameters(locals())
        url = self._build_url('/api/v1/search')
        return self._request('get', url, params=params)

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
        data['media_ids[]'] = data.pop('media_ids', None)
        url = self._build_url('/api/v1/statuses')
        return self._request('post', url, data=data)

    def delete_status(self, id_):
        """Deleting a status:
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#deleting-a-status
        :param id_: Target status ID

        """
        url = self._build_url('/api/v1/statuses/{id}'.format(id=id_))
        return self._request('delete', url)

    def reblog(self, id_):
        """Reblogging a status
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#rebloggingunreblogging-a-status
        :param id_: Target status ID
        :return: Returns the target Status.

        """
        url = self._build_url('/api/v1/statuses/{id}/reblog'.format(id=id_))
        return self._request('post', url)

    def unreblog(self, id_):
        """Unreblogging a status
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#rebloggingunreblogging-a-status
        :param id_: Target status ID
        :return: Returns the target Status.

        """
        url = self._build_url('/api/v1/statuses/{id}/unreblog'.format(id=id_))
        return self._request('post', url)

    def create_favourite(self, id_):
        """Favouriting a status
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#favouritingunfavouriting-a-status
        :param id_: Target status ID
        :return: Returns the target Status.

        """
        url = self._build_url('/api/v1/statuses/{id}/favourite'.format(id=id_))
        return self._request('post', url)

    def delete_unfavourite(self, id_):
        """Unfavouriting a status
        
        :reference: https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#favouritingunfavouriting-a-status
        :param id_: Target status ID
        :return: Returns the target Status.

        """
        url = self._build_url('/api/v1/statuses/{id}/unfavourite'.format(id=id_))
        return self._request('post', url)

    #
    # Timelines - https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#timelines
    #
    def home_timeline(self, max_id=None, since_id=None, limit=None):
        """Retrieving a home timeline
        
        :param max_id: (optional)  Returns only statuses with an ID less than (that is, older than)
            or equal to the specified ID.
        :param since_id: (optional) Returns only statuses with an ID greater than (that is, more recent than)
            the specified ID.
        :param limit: (optional) Specifies the number of statuses to retrieve.
        :return: Returns an array of Statuses, most recent ones first.

        """
        params = self._build_parameters(locals())
        url = self._build_url('/api/v1/timelines/home')
        return self._request('get', url, params=params)

    def public_timeline(self, max_id=None, since_id=None, limit=None, local=False):
        """Retrieving a public timeline
        
        :param max_id: (optional)  Returns only statuses with an ID less than (that is, older than)
            or equal to the specified ID.
        :param since_id: (optional) Returns only statuses with an ID greater than (that is, more recent than)
            the specified ID.
        :param limit: (optional) Specifies the number of statuses to retrieve.
        :param local: (optional) If `True` then fetch local statuses only.
        :return: Returns an array of Statuses, most recent ones first.

        """
        params = self._build_parameters(locals())
        url = self._build_url('/api/v1/timelines/public')
        return self._request('get', url, params=params)

    def hashtag_timeline(self, hashtag, max_id=None, since_id=None, limit=None, local=False):
        """Retrieving a hashtag timeline
        
        :param hashtag: Hashtag's name
        :param max_id: (optional)  Returns only statuses with an ID less than (that is, older than)
            or equal to the specified ID.
        :param since_id: (optional) Returns only statuses with an ID greater than (that is, more recent than)
            the specified ID.
        :param limit: (optional) Specifies the number of statuses to retrieve.
        :param local: (optional) If `True` then fetch local statuses only.
        :return: Returns an array of Statuses, most recent ones first.

        """
        params = self._build_parameters(locals())
        url = self._build_url('/api/v1/timelines/tag/{hashtag}'.format(hashtag=hashtag))
        return self._request('get', url, params=params)
