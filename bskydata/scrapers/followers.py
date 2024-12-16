import time
import typing as t
from bskydata.api.client import BskyApiClient
from atproto import models
from bskydata.storage.writers.base import DataWriter
from bskydata.parsers.base import DataParser


class FollowersScraper:
    def __init__(self, 
                 bsky_client: BskyApiClient, 
                 writer: DataWriter = None, 
                 parser: DataParser = None):
        self.bsky_client = bsky_client
        self.writer = writer
        self.parser = parser
    
    def _fetch_followers(self, actor: str, cursor: t.Union[str, None] = None) -> models.AppBskyGraphGetFollowers.Response:
        params = models.AppBskyGraphGetFollowers.Params(actor=actor, limit=100)
        if cursor:
            params.cursor = cursor
        return self.bsky_client.client.app.bsky.graph.get_followers(params)


    def fetch(self, actor: str, destination: str, limit: int = 1000) -> dict:
        all_followers = []
        cursor = None
        limit_check = 0
        while True:
            limit_check += 100
            response = self._fetch_followers(actor, cursor)
            cursor = response.cursor
            followers = response.model_dump()['followers']
            all_followers.extend(followers)
            if not cursor or limit_check > limit:
                break
            time.sleep(2)
        all_followers_final = {
            "actor": actor,
            "created_at":  time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "followers": all_followers
        }
        if self.parser:
            all_followers_final = self.parser.parse(all_followers_final)
        if self.writer:
            self.writer.write(all_followers_final, destination=destination)
        return all_followers_final
