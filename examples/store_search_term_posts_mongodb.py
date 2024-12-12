import argparse
import os
from bskydata.api.client import BskyApiClient
from bskydata.scrapers.search_terms import SearchTermScraper
from bskydata.storage.database.mongodb import MongoDBDataWriter


# Example usage: python examples/store_search_term_posts_mongodb.py --search_term "rstats" --limit 200
# Username and Password are stored in a .env file and automatically loaded
# If you don't use a .env file, enter them in the BskyApiClient(USERNAME, PASSWORD)

def main(search_term: str = "rstats", limit: int = 200):
    
    print(f"Searching for posts with the term '{search_term}' on the BlueSky platform...")
    client = BskyApiClient()

    # AWS
    json_writer = MongoDBDataWriter(
        connection_uri=os.getenv("MONGODB_CONNECTION_STRING"), 
        database_name='stoltzmaniac',
        collection = 'stoltzmaniac')
    
    scraper = SearchTermScraper(client, writer=json_writer)
    posts = scraper.fetch_all_posts(search_term, limit=limit)
    print(f"Scraped {len(posts['posts'])} posts for the search term '{search_term}'")
    print(f"Posts saved to AWS {search_term}_posts.json")


if __name__ == "__main__":
    # parse arguments to pass into function
    parser = argparse.ArgumentParser(description="Search for posts on the BlueSky platform.")
    parser.add_argument("--search_term", type=str, help="The search term to use.")
    parser.add_argument("--limit", type=int, default=200, help="The maximum number of posts to fetch.")
    args = parser.parse_args()
    main(args.search_term, args.limit)
