import argparse
from bskydata.api.client import BskyApiClient
from bskydata.scrapers.search_terms import SearchTermScraper
from bskydata.storage.writers import JsonFileWriter

def main(search_term: str, limit: int = 200):
    print(f"Searching for posts with the term '{search_term}' on the BlueSky platform...")
    # Username and Password are stored in the .env file and automatically loaded
    client = BskyApiClient()

    # Scrape all posts for the search term "rstats"
    json_writer = JsonFileWriter(f"{search_term}_posts.json")
    scraper = SearchTermScraper(client, writer=json_writer)
    rstats_posts = scraper.fetch_all_posts(search_term, limit=limit)
    print(f"Scraped {len(rstats_posts['posts'])} posts for the search term '{search_term}'")
    print(f"Posts saved to {search_term}_posts.json")


if __name__ == "__main__":
    # parse arguments to pass into function
    parser = argparse.ArgumentParser(description="Search for posts on the BlueSky platform.")
    parser.add_argument("--search_term", type=str, help="The search term to use.")
    parser.add_argument("--limit", type=int, default=200, help="The maximum number of posts to fetch.")
    args = parser.parse_args()
    main(args.search_term, args.limit)
    # Example usage: python examples/store_search_term_posts.py --search_term "rstats" --limit 200
