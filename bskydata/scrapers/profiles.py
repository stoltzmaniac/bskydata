import time
from atproto_client.exceptions import InvokeTimeoutError
from bskydata.api.client import BskyApiClient
from bskydata.storage.writers.base import DataWriter
from bskydata.parsers.base import DataParser


class ProfilesScraper:
    def __init__(self, 
                 bsky_client: BskyApiClient, 
                 writer: DataWriter = None, 
                 parser: DataParser = None):
        self.bsky_client = bsky_client
        self.writer = writer
        self.parser = parser
    
    def fetch(self, actors: list, destination: str) -> dict:
        try:
            profiles = self.bsky_client.client.get_profiles(actors).model_dump()
            profiles['actors'] = actors
            profiles["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            if self.parser:
                profiles = self.parser.parse(profiles)
            if self.writer:
                self.writer.write(profiles, destination=destination)
            return profiles
        except InvokeTimeoutError as e:
            self.bsky_client._timed_out = True
