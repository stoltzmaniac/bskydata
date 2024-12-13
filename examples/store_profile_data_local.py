import argparse
from bskydata.api.client import BskyApiClient
from bskydata.scrapers.profiles import ProfileScraper
from bskydata.storage.local.local_writers import LocalJsonFileWriter
from bskydata.parsers.profiles.profiles import BasicProfilesParser
# Example usage: # Example usage: python examples/store_profile_data_local.py --profiles "stoltzmaniac.bsky.social" "bsky.app"
# Username and Password are stored in a .env file and automatically loaded
# If you don't use a .env file, enter them in the BskyApiClient(USERNAME, PASSWORD)

def main(profiles: list):
    profiles = [profile.replace('"', "") for profile in profiles]
    print(f"Store profile data for the following profiles: {profiles}")
    client = BskyApiClient()

    # Scrape all posts for the search_term
    json_writer = LocalJsonFileWriter("profiles.json")
    basic_parser = BasicProfilesParser()
    scraper = ProfileScraper(client, writer=json_writer, parser=basic_parser)
    profiles = scraper.fetch_all_profiles(profiles)
    print(f"Scraped profiles: {profiles}")
    print("Posts saved to profile_posts_posts.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for profiles on the BlueSky platform.")
    parser.add_argument("--profiles", nargs="+", required=True, help="List of profiles to process.")
    args = parser.parse_args()
    main(args.profiles)
