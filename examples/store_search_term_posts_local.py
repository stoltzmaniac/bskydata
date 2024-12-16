import argparse
import os
from bskydata.api.client import BskyApiClient
from bskydata.scrapers.search_terms import SearchTermScraper
from bskydata.storage.writers import LocalJsonFileWriter
from dotenv import load_dotenv
load_dotenv()


# Example usage: 
# python examples/store_search_term_posts_cloud.py --search_term "rstats" --limit 2000 --destination "rstats_posts.json"
# Username and Password are stored in a .env file and automatically loaded
# If you don't use a .env file, enter them in the BskyApiClient(USERNAME, PASSWORD)

def main(search_term: str, limit: int):
    
    print(f"Searching for posts with the term '{search_term}' on the BlueSky platform...")
    client = BskyApiClient(
        username=os.getenv("BSKY_USERNAME"),
        password=os.getenv("BSKY_PASSWORD")
    )

    json_writer = LocalJsonFileWriter()
    scraper = SearchTermScraper(client, writer=json_writer)
    
    posts = scraper.fetch(search_term, 
                          limit=limit,
                          destination=f"s3_{search_term}_posts.json"
                          )

    # print(f"Scraped {len(posts['posts'])} posts for the search term '{search_term}'")
    print(f"{len(posts)} Posts saved to  local_{search_term}_posts.json")


if __name__ == "__main__":
    # parse arguments to pass into function
    parser = argparse.ArgumentParser(description="Search for posts on the BlueSky platform.")
    parser.add_argument("--search_term", type=str, help="The search term to use.")
    parser.add_argument("--limit", type=int, default=200, help="The maximum number of posts to fetch.")
    parser.add_argument("--destination", type=str, help="Destination file name to store the posts.")
    args = parser.parse_args()
    main(args.search_term, args.limit)
