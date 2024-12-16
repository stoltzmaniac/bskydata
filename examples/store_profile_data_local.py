import argparse
import os
from dotenv import load_dotenv
load_dotenv()
from bskydata.api import BskyApiClient
from bskydata.scrapers import ProfilesScraper
from bskydata.storage.writers import LocalJsonFileWriter
from bskydata.parsers import BasicProfilesParser


# Example usage: # Example usage: python examples/store_profile_data_local.py --profiles "stoltzmaniac.bsky.social" "bsky.app" --destination "profile_posts.json"
# Username and Password are stored in a .env file and automatically loaded
# If you don't use a .env file, enter them in the BskyApiClient(USERNAME, PASSWORD)


def main(profiles: list, destination: str):
    
    profiles = [profile.replace('"', "") for profile in profiles]
    print(f"Store profile data for the following profiles: {profiles}")
    
    client = BskyApiClient(
        username=os.getenv("BSKY_USERNAME"),
        password=os.getenv("BSKY_PASSWORD")
    )

    # Scrape all posts for the search_term
    json_writer = LocalJsonFileWriter()
    basic_parser = BasicProfilesParser()
    scraper = ProfilesScraper(client, 
                              writer=json_writer, 
                              parser=basic_parser)
    profiles = scraper.fetch(profiles, 
                             destination=destination)
    
    print(f"Scraped profiles: {profiles}")
    print("Posts saved to profile_posts_posts.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for profiles on the BlueSky platform.")
    parser.add_argument("--profiles", nargs="+", required=True, help="List of profiles to process.")
    parser.add_argument("--destination", required=True, help="Destination file name to store the profiles.")
    args = parser.parse_args()
    main(args.profiles, args.destination)
