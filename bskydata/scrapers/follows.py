import time
import typing as t
from bskydata.api.client import BskyApiClient
from atproto import models
from bskydata.storage.writers.base import DataWriter
from bskydata.parsers.base import DataParser


class FollowsScraper:
    def __init__(self, 
                 bsky_client: BskyApiClient, 
                 writer: DataWriter = None, 
                 parser: DataParser = None):
        self.bsky_client = bsky_client
        self.writer = writer
        self.parser = parser
    
    def _fetch_follows(self, actor: str, cursor: t.Union[str, None] = None) -> models.AppBskyGraphGetFollows.Response:
        params = models.AppBskyGraphGetFollows.Params(actor=actor, limit=100)
        if cursor:
            params.cursor = cursor
        return self.bsky_client.client.app.bsky.graph.get_follows(params)

    def fetch(self, actor: str, destination: str, limit: int = 1000) -> dict:
        all_follows = []
        cursor = None
        limit_check = 0
        while True:
            limit_check += 100
            response = self._fetch_follows(actor, cursor)
            cursor = response.cursor
            follows = response.model_dump()['follows']
            all_follows.extend(follows)
            if not cursor or limit_check > limit:
                break
            time.sleep(2)
        all_follows_final = {
            "actor": actor,
            "created_at":  time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "follows": all_follows
        }
        if self.parser:
            all_follows_final = self.parser.parse(all_follows_final)
        if self.writer:
            self.writer.write(all_follows_final, destination=destination)
        return all_follows_final
