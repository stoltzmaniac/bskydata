from atproto import Client
from atproto.exceptions import AtProtocolError


def requires_authentication(func):
    """Decorator to ensure the client is authenticated before executing the method."""
    def wrapper(self, *args, **kwargs):
        self.bsky_client.ensure_authenticated()
        return func(self, *args, **kwargs)
    return wrapper


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class BskyApiClient:
    def __init__(self, username:str=None, password:str=None):
        self._client = Client()
        self._authenticated = False
        if username and password:
            self.authenticate(username, password)

    def authenticate(self, username: str, password: str):
        """Authenticate using provided credentials."""
        try:
            self._client.login(username, password)
            self._authenticated = True
        except AtProtocolError as e:
            # Always raise AuthenticationError when AtProtocolError occurs during login
            raise AuthenticationError("Authentication failed") from e

    def ensure_authenticated(self):
        """Ensure the client is authenticated before making API calls."""
        if not self._authenticated:
            raise AuthenticationError("You must authenticate before making API calls.")

    @property
    def client(self):
        """Provide access to the underlying AtprotoClient."""
        self.ensure_authenticated()
        return self._client
