import argparse
from bskydata.api.client import BskyApiClient
from bskydata.scrapers.profiles import ProfileScraper
from bskydata.storage.local.local_writers import LocalJsonFileWriter
from bskydata.parsers.profiles.profiles import BasicFollowersParser

# Example usage: # Example usage: python examples/store_profile_followers_data_local.py --actor="stoltzmaniac.bsky.social" --limit=2
# Username and Password are stored in a .env file and automatically loaded
# If you don't use a .env file, enter them in the BskyApiClient(USERNAME, PASSWORD)

def main(actor: list, limit: int):
    print(f"Store followers for the following profiles: {actor}")
    client = BskyApiClient()

    # Scrape all posts for the search_term
    json_writer = LocalJsonFileWriter("followers.json")
    followers_parser = BasicFollowersParser()
    scraper = ProfileScraper(client, writer=json_writer, parser=followers_parser)
    followers = scraper.fetch_all_followers(actor, limit)
    print(f"Scraped followers: {followers}")
    print("Posts saved to profile_posts_posts.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for followers on the BlueSky platform.")
    parser.add_argument("--actor", type=str, help="Search for actor by handle or did.")
    parser.add_argument("--limit", type=int, default=200, help="The maximum number of followers to fetch.")
    args = parser.parse_args()
    main(args.actor, args.limit)
