import argparse
import os
from dotenv import load_dotenv
load_dotenv()
from bskydata.api import BskyApiClient
from bskydata.scrapers import FollowersScraper
from bskydata.storage.writers import LocalJsonFileWriter
from bskydata.parsers import BasicFollowersParser

# Example usage:
# python examples/store_profile_followers_data_local.py --actor="stoltzmaniac.bsky.social" --limit=20 --destination "profile_followers.json"
# Username and Password are stored in a .env file and automatically loaded
# If you don't use a .env file, enter them in the BskyApiClient(USERNAME, PASSWORD)

def main(actor: list, limit: int, destination: str):
    print(f"Store followers for the following profiles: {actor}")
    client = BskyApiClient(
        username=os.getenv("BSKY_USERNAME"),
        password=os.getenv("BSKY_PASSWORD")
    )
    
    json_writer = LocalJsonFileWriter()
    basic_parser = BasicFollowersParser()
    scraper = FollowersScraper(client, 
                              writer=json_writer, 
                              parser=basic_parser)
    
    followers = scraper.fetch(actor, 
                              destination=destination,
                              limit=limit)
    print(f"Scraped followers: {followers}")
    print("Posts saved to profile_posts_posts.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for followers on the BlueSky platform.")
    parser.add_argument("--actor", type=str, help="Search for actor by handle or did.")
    parser.add_argument("--limit", type=int, default=200, help="The maximum number of followers to fetch.")
    parser.add_argument("--destination", required=True, help="Destination file name to store the profiles.")
    args = parser.parse_args()
    main(args.actor, args.limit, args.destination)
