import gpsoauth

from .. import exception


class APIAuth(object):
    """Authentication token manager"""

    def __init__(self, scopes):
        self._master_token = None
        self._auth_token = None
        self._email = None
        self._android_id = None
        self._scopes = scopes

    def login(self, email, password, android_id):
        """Authenticate to Google with the provided credentials.

        Args:
            email (str): The account to use.
            password (str): The account password.
            android_id (str): An identifier for this client.

        Raises:
            LoginException: If there was a problem logging in.
        """
        self._email = email
        self._android_id = android_id
        res = gpsoauth.perform_master_login(self._email, password, self._android_id)
        if 'Token' not in res:
            raise exception.LoginException(res.get('Error'), res.get('ErrorDetail'))
        self._master_token = res['Token']

        self.refresh()
        return True

    def load(self, email, master_token, android_id):
        """Authenticate to Google with the provided master token.

        Args:
            email (str): The account to use.
            master_token (str): The master token.
            android_id (str): An identifier for this client.

        Raises:
            LoginException: If there was a problem logging in.
        """
        self._email = email
        self._android_id = android_id
        self._master_token = master_token

        self.refresh()
        return True

    def getMasterToken(self):
        """Gets the master token.

        Returns:
            str: The account master token.
        """
        return self._master_token

    def setMasterToken(self, master_token):
        """Sets the master token. This is useful if you'd like to authenticate
        with the API without providing your username & password.
        Do note that the master token has full access to your account.

        Args:
            master_token (str): The account master token.
        """
        self._master_token = master_token

    def getEmail(self):
        """Gets the account email.

        Returns:
            str: The account email.
        """
        return self._email

    def setEmail(self, email):
        """Gets the account email.

        Args:
            email (str): The account email.
        """
        self._email = email

    def getAndroidId(self):
        """Gets the device id.

        Returns:
            str: The device id.
        """
        return self._android_id

    def setAndroidId(self, android_id):
        """Sets the device id.

        Args:
            android_id (str): The device id.
        """
        self._android_id = android_id

    def getAuthToken(self):
        """Gets the auth token.

        Returns:
            Union[str, None]: The auth token.
        """
        return self._auth_token

    def refresh(self):
        """Refresh the OAuth token.

        Returns:
            string: The auth token.

        Raises:
            LoginException: If there was a problem refreshing the OAuth token.
        """
        res = gpsoauth.perform_oauth(
            self._email, self._master_token, self._android_id,
            service=self._scopes,
            app='com.google.android.keep',
            client_sig='38918a453d07199354f8b19af05ec6562ced5788'
        )
        if 'Auth' not in res:
            if 'Token' not in res:
                raise exception.LoginException(res.get('Error'))

        self._auth_token = res['Auth']
        return self._auth_token

    def logout(self):
        """Log out of the account."""
        self._master_token = None
        self._auth_token = None
        self._email = None
        self._android_id = None
