import argparse
import os
from bskydata.api.client import BskyApiClient
from bskydata.scrapers.search_terms import SearchTermScraper
from bskydata.storage.cloud.azure_writers import AzureJsonDataWriter

# Example usage: python examples/store_search_term_posts_cloud.py --search_term "rstats" --limit 200
# Username and Password are stored in a .env file and automatically loaded
# If you don't use a .env file, enter them in the BskyApiClient(USERNAME, PASSWORD)

def main(search_term: str = "rstats", limit: int = 200):
    print(f"Searching for posts with the term '{search_term}' on the BlueSky platform...")
    client = BskyApiClient()

    # Azure
    json_writer = AzureJsonDataWriter(connection_string=os.getenv("AZURE_BLOB_STORAGE_CONNECTION_STRING"), 
                                  container_name='stoltzmaniac')
    scraper = SearchTermScraper(client, writer=json_writer)
    posts = scraper.fetch_all_posts(search_term, limit=limit)
    print(f"Scraped {len(posts['posts'])} posts for the search term '{search_term}'")
    print(f"Posts saved to Azure {search_term}_posts.json")

if __name__ == "__main__":
    # parse arguments to pass into function
    parser = argparse.ArgumentParser(description="Search for posts on the BlueSky platform.")
    parser.add_argument("--search_term", type=str, help="The search term to use.")
    parser.add_argument("--limit", type=int, default=200, help="The maximum number of posts to fetch.")
    args = parser.parse_args()
    main(args.search_term, args.limit)
