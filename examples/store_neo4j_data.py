from bskydata.builders import BuildNetworkSearchAndFollowsNeo4j
import os
from dotenv import load_dotenv
load_dotenv()


SEARCH_TERMS = ["python"]
for search_term in SEARCH_TERMS:
    print(f"Searching for {search_term}")
    builder = BuildNetworkSearchAndFollowsNeo4j(
        bsky_username=os.getenv('BSKY_USERNAME'),
        bsky_password=os.getenv('BSKY_PASSWORD'),
        neo4j_uri=os.getenv('NEO4J_URI'),
        neo4j_username=os.getenv('NEO4J_USERNAME'),
        neo4j_password=os.getenv('NEO4J_PASSWORD')
    )
    data = builder.run(search_term)

