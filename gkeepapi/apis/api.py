import requests

from .. import __version__, exception, logger


class API(object):
    """Base API wrapper"""
    RETRY_CNT = 2

    def __init__(self, base_url, auth=None):
        self._session = requests.Session()
        self._auth = auth
        self._base_url = base_url
        self._session.headers.update({'User-Agent': 'gkeepapi/' + __version__})

    def getAuth(self):
        """Get authentication details for this API.

        Args:
            auth (APIAuth): The auth object
        """
        return self._auth

    def setAuth(self, auth):
        """Set authentication details for this API.

        Args:
            auth (APIAuth): The auth object
        """
        self._auth = auth

    def send(self, **req_kwargs):
        """Send an authenticated request to a Google API.
        Automatically retries if the access token has expired.

        Args:
            **req_kwargs: Arbitrary keyword arguments to pass to Requests.

        Return:
            dict: The parsed JSON response.

        Raises:
            APIException: If the server returns an error.
            LoginException: If :py:meth:`login` has not been called.
        """
        i = 0
        while True:
            response = self._send(**req_kwargs).json()
            if 'error' not in response:
                break

            error = response['error']
            if error['code'] != 401:
                raise exception.APIException(error['code'], error)

            if i >= self.RETRY_CNT:
                raise exception.APIException(error['code'], error)

            logger.info('Refreshing access token')
            self._auth.refresh()
            i += 1

        return response

    def _send(self, **req_kwargs):
        """Send an authenticated request to a Google API.

        Args:
            **req_kwargs: Arbitrary keyword arguments to pass to Requests.

        Return:
            requests.Response: The raw response.

        Raises:
            LoginException: If :py:meth:`login` has not been called.
        """
        auth_token = self._auth.getAuthToken()
        if auth_token is None:
            raise exception.LoginException('Not logged in')

        req_kwargs.setdefault('headers', {
            'Authorization': 'OAuth ' + auth_token
        })

        return self._session.request(**req_kwargs)
