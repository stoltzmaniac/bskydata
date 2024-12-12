import time
import typing as t
from bskydata.api.client import BskyApiClient
from atproto import models
from bskydata.storage.base_writers import DataWriter


class ProfileScraper:
    def __init__(self, bsky_client: BskyApiClient, writer: DataWriter = None):
        self.bsky_client = bsky_client
        self.writer = writer
    
    def _fetch_follows(self, actor: str, cursor: t.Union[str, None] = None) -> models.AppBskyGraphGetFollows.Response:
        params = models.AppBskyGraphGetFollows.Params(actor=actor, limit=100)
        if cursor:
            params.cursor = cursor
        return self.bsky_client.client.app.bsky.graph.get_follows(params)

    def _fetch_followers(self, actor: str, cursor: t.Union[str, None] = None) -> models.AppBskyGraphGetFollowers.Response:
        params = models.AppBskyGraphGetFollowers.Params(actor=actor, limit=100)
        if cursor:
            params.cursor = cursor
        return self.bsky_client.client.app.bsky.graph.get_followers(params)

    def fetch_all_profiles(self, actors: list, output_file: str = "profiles.json") -> dict:
        profiles = self.bsky_client.client.get_profiles(actors).model_dump()
        if self.writer:
            self.writer.write(profiles, destination=output_file)
        return profiles

    def fetch_all_follows(self, actor: str, limit: int = 1000, output_file: str = "follows.json") -> dict:
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
            "follows": all_follows
        }
        if self.writer:
            self.writer.write(all_follows_final, destination=output_file)
        return all_follows_final

    def fetch_all_followers(self, actor: str, limit: int = 1000, output_file: str = "followers.json") -> dict:
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
            "followers": all_followers
        }
        if self.writer:
            self.writer.write(all_followers_final, destination=output_file)
        return all_followers_final
