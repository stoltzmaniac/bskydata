from dotenv import load_dotenv
load_dotenv()
import json
import os
from bskydata.storage.writers.database.neo4j import Neo4jDataWriter
from bskydata.api import BskyApiClient
from bskydata.scrapers import FollowsScraper
from bskydata.storage.writers import LocalJsonFileWriter
from bskydata.parsers import BasicFollowsParser



def insert_follows(session, data):
    query = """
    MERGE (actor:Author {did: $actor_did})
    ON CREATE SET actor.display_name = $actor_display_name, 
                  actor.handle = $actor_handle

    WITH actor
    UNWIND $follows AS follow
    MERGE (followed:Author {did: follow.handle})
    ON CREATE SET followed.display_name = follow.display_name, 
                  followed.handle = follow.handle

    MERGE (actor)-[r:FOLLOWS]->(followed)
    ON CREATE SET r.created_at = follow.created_at
    """
    session.run(query, 
                actor_did=data["actor_did"],
                actor_display_name=data.get("actor_display_name", data["actor_did"]),
                actor_handle=data.get("actor_handle", ""),
                follows=data["follows"])


def insert_posts_bulk(session, posts):
    query = """
    UNWIND $posts AS post_data
    
    // Merge Author
    MERGE (author:Author {did: post_data.author_handle})
    ON CREATE SET author.display_name = post_data.author_display_name,
                  author.handle = post_data.author_handle

    // Merge Post
    MERGE (post:Post {created_at: post_data.post_created_at})
    ON CREATE SET post.text = post_data.post_text

    // Create Relationship between Author and Post
    MERGE (author)-[:CREATED]->(post)

    // Merge Tags and Relationships
    FOREACH (tag_name IN post_data.tags | 
        MERGE (tag:Tag {name: tag_name})
        MERGE (post)-[:HAS_TAG]->(tag)
    )
    """
    session.run(query, posts=posts)


posts = json.load(open("local_rstats_posts.json"))["posts"]
authors = list(set([p['author_handle'] for p in posts]))

client = BskyApiClient(
    username=os.getenv("BSKY_USERNAME"),
    password=os.getenv("BSKY_PASSWORD")
)

writer = Neo4jDataWriter(
        connection_uri=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )

for actor in authors:    

    print(f"Store follows for the following profiles: {actor}")
    
    json_writer = LocalJsonFileWriter()
    basic_parser = BasicFollowsParser()
    scraper = FollowsScraper(client, 
                            writer=json_writer, 
                            parser=basic_parser)

    followers = scraper.fetch(actor, 
                              destination="follows.json",
                              limit=500)

    follows = json.load(open("follows.json"))
    follows['actor_did'] = follows['actor']

    insert_posts_bulk(writer.session, posts)
    insert_follows(writer.session, follows)

writer.disconnect()
