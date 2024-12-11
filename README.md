# BlueSky API Data Wrapper

This is built as a wrapper for the `atproto` package. While that package is fantastic, it can be a bit tricky to navigate. This package will **hopefully** give a productive user experience.

### Installation
```
pip install bskydata
```

### Example usage

```python
import os
from dotenv import load_dotenv
from bskydata.api.client import BskyApiClient
from bskydata.scrapers.search_terms import SearchTermScraper
from bskydata.scrapers.profiles import ProfileScraper
from bskydata.storage.writers import JsonFileWriter
load_dotenv()

BSKY_USERNAME = os.getenv('BSKY_USERNAME')
BSKY_PASSWORD = os.getenv('BSKY_PASSWORD')

# Create a client -- reuse this across your code rather than instantiating a new one each time
# If you run this frequently, you will be rate limited
client = BskyApiClient(username = BSKY_USERNAME, 
                       password = BSKY_PASSWORD)

# Scrape all posts for the search term "rstats"
st_scraper = SearchTermScraper(client)
rstats_posts = st_scraper.fetch_all_posts("rstats", limit=200)

# Scrape user: follows, followers, profiles
pf_scraper = ProfileScraper(client)
profiles = pf_scraper.fetch_all_profiles(["stoltzmaniac.bsky.social", "bsky.app"])
profile_follows = pf_scraper.fetch_all_follows("stoltzmaniac.bsky.social", limit=200)
profile_followers = pf_scraper.fetch_all_followers("stoltzmaniac.bsky.social", limit=200)

# Add output files -- you can specify different file names within each method if you prefer not to use the defaults
json_writer = JsonFileWriter()
scraper = SearchTermScraper(client, writer=json_writer)
data = scraper.fetch_all_posts("rstats", limit=200)

pf_scraper = ProfileScraper(client, writer=json_writer)
profiles = pf_scraper.fetch_all_profiles(["stoltzmaniac.bsky.social"])
profile_follows = pf_scraper.fetch_all_follows("stoltzmaniac.bsky.social", limit=200)
profile_followers = pf_scraper.fetch_all_followers("stoltzmaniac.bsky.social", limit=200)
```

