from atproto import Client
from atproto.exceptions import AtProtocolError, InvokeTimeoutError


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class BskyApiClient:
    def __init__(self, username: str = None, password: str = None):
        print("Initializing BskyApiClient")
        self._client = Client()
        self._authenticated = False
        self.did = None
        self.username = username
        self.password = password
        if username and password:
            self.authenticate()

    def authenticate(self):
        """Authenticate using provided credentials."""
        print("Authenticating")
        try:
            self._client.login(self.username, self.password)
            self.did = self._client.me.did  # Access the 'did' attribute directly
            self._authenticated = True
            print("Authentication successful")
        except AtProtocolError as e:
            raise AuthenticationError("Authentication failed") from e
        except AttributeError:
            raise AuthenticationError("Failed to retrieve user DID after authentication.")

    def ensure_authenticated(self):
        """Ensure the client is authenticated before making API calls."""
        if not self._authenticated:
            print("Authentication required:")
            for attempt in range(2):  # Try to authenticate up to 2 times
                print("Attempt; ", attempt + 1)
                try:
                    self.authenticate()
                    break
                except AuthenticationError:
                    print("Authentication failed")
                    if attempt == 1:  # On the second failure, raise the error
                        raise AuthenticationError("Failed to authenticate after multiple attempts.")

    @property
    def client(self):
        """Provide access to the underlying AtprotoClient."""
        try:
            self.ensure_authenticated()
            return self._client
        except InvokeTimeoutError:  # Handle timeout-specific errors
            print("Timeout Error occurred")
            self._authenticated = False  # Reset authentication state
            self.ensure_authenticated()  # Reauthenticate
            return self._client  # Retry and return the client
        except AtProtocolError as e:
            print("Totally failed at the AtProtocolError")
            raise e  # Re-raise other AtProtocolError exceptions
