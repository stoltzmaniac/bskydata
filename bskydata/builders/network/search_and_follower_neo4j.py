from neo4j.exceptions import SessionExpired
from bskydata.storage.writers.database.neo4j import Neo4jDataWriter
from bskydata.api import BskyApiClient
from bskydata.scrapers import FollowsScraper, SearchTermScraper, ProfilesScraper
from bskydata.storage.writers import LocalJsonFileWriter
from bskydata.parsers import BasicFollowsParser, BasicSearchTermsParser, BasicProfilesParser


class BuildNetworkSearchAndFollowsNeo4j:
    def __init__(self,
                 bsky_username:str,
                 bsky_password:str,
                 neo4j_uri:str,
                 neo4j_username:str,
                 neo4j_password:str):
        
        self.client = BskyApiClient(
            username=bsky_username,
            password=bsky_password
        )

        self.writer = Neo4jDataWriter(
            connection_uri=neo4j_uri,
            username=neo4j_username,
            password=neo4j_password
        )
    
    def _scrape_profiles(self, actors: list):
        scraper = ProfilesScraper(self.client)
        profiles = scraper.fetch(actors, destination="profiles.json")
        return profiles
    
    def _scrape_follows(self, actor:str, limit: int = 2000):
        if not actor.startswith("did:"):
            profiles = self._scrape_profiles([actor])
            actor = profiles['profiles'][0]['did']

        json_writer = LocalJsonFileWriter()
        basic_parser = BasicFollowsParser()
        scraper = FollowsScraper(self.client, 
                                writer=json_writer, 
                                parser=basic_parser)

        follows = scraper.fetch(actor, 
                                destination=f"follows.json",
                                limit=limit)
        
        return follows
    
    def _scrape_search_posts(self, search_term:str, limit:int = 2000):
        json_writer = LocalJsonFileWriter()
        parser = BasicSearchTermsParser()
        scraper = SearchTermScraper(self.client, 
                                    writer=json_writer, 
                                    parser=parser)
        
        posts = scraper.fetch(
            search_term, 
            destination=f"posts.json",
            limit=limit
            )        
        return posts

    def _insert_follows(self, data):
        query = """
        MERGE (actor:Author {did: $actor_did})
        ON CREATE SET actor.display_name = $actor_display_name, 
                      actor.handle = $actor_handle

        WITH actor
        UNWIND $follows AS follow
        MERGE (followed:Author {did: follow.did})
        ON CREATE SET followed.display_name = follow.display_name, 
                      followed.handle = follow.handle

        MERGE (actor)-[r:FOLLOWS]->(followed)
        ON CREATE SET r.created_at = follow.created_at
        """
        try:
            self.writer.session.run(query, 
                        actor_did=data["actor"],
                        actor_display_name=data.get("actor_display_name", ""),
                        actor_handle=data.get("actor_handle", ""),
                        follows=data["follows"])
        except SessionExpired:
            self.writer.session.close()
            self.writer.session = self.writer.driver.session()

    def _insert_posts_bulk(self, posts):
        query = """
        UNWIND $posts AS post_data
        
        // Merge Author
        MERGE (author:Author {did: post_data.author_did})
        ON CREATE SET author.display_name = post_data.author_display_name,
                    author.handle = post_data.author_handle

        // Merge Post
        MERGE (post:Post {created_at: post_data.post_created_at})
        ON CREATE SET post.text = post_data.post_text

        // Create Relationship between Author and Post
        MERGE (author)-[:CREATED]->(post)

        // Merge Tags and Relationships (convert tag names to lowercase)
        FOREACH (tag_name IN post_data.tags | 
            MERGE (tag:Tag {name: toLower(tag_name)})
            MERGE (post)-[:HAS_TAG]->(tag)
        )
        """
        try:
            self.writer.session.run(query, posts=posts)
        except SessionExpired:
            self.writer.session.close()
            self.writer.session = self.writer.driver.session()

    def run(self, search_term: str):
        search_data = self._scrape_search_posts(search_term)
        self._insert_posts_bulk(search_data["posts"])
        unique_actors = list(set([p['author_did'] for p in search_data["posts"]]))
        n = 0
        for actor in unique_actors:
            n += 1
            print(f"Store follows for the following profiles: {actor}. {n}/{len(unique_actors)}")
            follows = self._scrape_follows(actor)
            self._insert_follows(follows)
        self.writer.disconnect()
        print("Data stored successfully.")
