import time
import typing as t
from bskydata.api.client import BskyApiClient
from bskydata.storage.writers.base import DataWriter
from bskydata.parsers.base import DataParser
from atproto import models


class SearchTermScraper:
    def __init__(self, bsky_client: BskyApiClient, writer: DataWriter = None, parser: DataParser = None):
        """
        :param bsky_client: Instance of BskyApiClient.
        :param writer: Writer instance for outputting fetched posts.
        """
        self.bsky_client = bsky_client
        self.writer = writer
        self.parser = parser

    def _fetch(self, search_term: str, cursor: t.Union[int, None] = None) -> models.AppBskyFeedSearchPosts.Response:
        params = {"q": search_term, 'limit': 100}
        if cursor:
            params['cursor'] = cursor
        return self.bsky_client.client.app.bsky.feed.search_posts(params=params)

    def fetch(
        self, 
        search_term: str, 
        destination: str,
        limit: int = 1000, 
    ) -> dict:
        all_posts = []
        cursor = None
        while True:
            response = self._fetch(search_term, cursor)
            cursor = response.cursor
            posts = response.model_dump()['posts']
            all_posts.extend(posts)
            if not cursor:
                break
            if int(cursor) > limit:
                break
            time.sleep(1)
        all_posts_final = {
            "search_term": search_term,
            "created_at":  time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "posts": all_posts
        }
        if self.parser:
            all_posts_final = self.parser.parse(all_posts_final)
        # Write the fetched posts using the writer
        if self.writer:
            self.writer.write(all_posts_final, destination=destination)

        return all_posts_final
