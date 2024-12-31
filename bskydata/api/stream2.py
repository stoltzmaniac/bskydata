import asyncio
import json
import datetime
from collections import Counter
import pandas as pd
import os
from matplotlib import pyplot as plt
import websockets
from neo4j import GraphDatabase
# Your custom BSky libraries
from bskydata.api.client import BskyApiClient
from bskydata.agents.agent import BskyAgent

###############################################################################
# Utility Function: Convert DataFrame to Image
###############################################################################
def dataframe_to_image(df, filepath, dpi=300):
    """
    Converts a pandas DataFrame to an image and saves it locally.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to convert.
        filepath (str): Filepath to save the image (e.g., 'output.png').
        dpi (int): Resolution of the saved image.
    """
    fig, ax = plt.subplots(figsize=(8, len(df) * 0.5))  # Adjust height based on rows
    ax.axis('off')  # Turn off the axis

    # Add the table to the figure
    table = plt.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        colColours=['#f4f4f4'] * df.shape[1],  # Optional: colorize the header
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(df.columns))))  # Auto-adjust column width

    # Save the image
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close(fig)

###############################################################################
# HashtagTracker
###############################################################################
class HashtagTracker:
    """
    Tracks selected hashtags in incoming Bluesky posts.
    Provides a compact text summary suitable for short posts.
    """

    def __init__(self, hashtags_of_interest):
        self.hashtags_of_interest = [tag.lower().strip() for tag in hashtags_of_interest]

        # Counters for single tags and combos
        self.tag_counts = Counter()
        self.combo_counts = Counter()

        # Store processed data for JSON output
        self.processed_data = []

    def process_post_message(self, data):
        """Extract relevant hashtags from a single post commit and update counters."""
        commit_data = data.get("commit", {})
        if commit_data.get("collection") != "app.bsky.feed.post":
            return  # Not a post

        # Extract core fields
        record = commit_data.get("record", {})
        created_at = record.get("createdAt", "")
        facets = record.get("facets", [])
        did = data.get("did", "")

        # Parse hashtags
        found_tags = set()
        for facet in facets:
            features = facet.get("features", [])
            for feature in features:
                if feature.get("$type") == "app.bsky.richtext.facet#tag":
                    raw_tag = feature.get("tag", "").strip().lower()
                    if raw_tag in self.hashtags_of_interest:
                        found_tags.add(raw_tag)

        # Update counters and processed data
        short_lived = []
        for tag in found_tags:
            self.tag_counts[tag] += 1
            data_tag = {
                "hashtag": tag,
                "created_at": created_at,
                "did": did
            }
            short_lived.append(data_tag)
            self.processed_data.append(data_tag)
            print("Streaming data")
            print(data_tag)
            # write to json file
            with open(f"data/hashtag_data_{tag}_{created_at}_{did}.json", "a") as f:
                json.dump(short_lived, f, indent=4)

        if len(found_tags) > 1:
            combo_key = frozenset(found_tags)
            self.combo_counts[combo_key] += 1
    
    def get_compact_summary(self) -> str:
        """
        Return a short text summary of hashtags and combos, formatted for a BlueSky post.
        """
        lines = []
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        lines.append(f"\U0001F31F Prior 12 Hour Hashtag Stats:  {now_str} \U0001F31F\n")

        # Add single-tag counts
        if self.tag_counts:
            lines.append("\U0001F3AF Top Tags:")
            for tag, count in self.tag_counts.most_common(3):  # Limit to top 3
                lines.append(f"  - #{tag}: {count}")
        else:
            lines.append("No tags yet!")

        # Add hashtag combo counts
        if self.combo_counts:
            lines.append("\n\U0001F91D Popular Hashtag Combos:")
            for combo, count in self.combo_counts.most_common(3):  # Limit to top 3
                combo_str = " + ".join(f"#{tag}" for tag in combo)
                lines.append(f"  - {combo_str}: {count}")
        else:
            lines.append("\nNo combos yet!")

        final_str = "\n".join(lines)[0:300]
        print(final_str)
        return final_str
    
    def get_summary_dataframe(self) -> pd.DataFrame:
        """
        Return a pandas DataFrame with hashtag and combination counts.
        """
        # Prepare data for single hashtags
        tag_data = [
            {"Hashtag": f"#{tag}", "Count": count}
            for tag, count in self.tag_counts.most_common(10)  # Limit to top 10 for the table
        ]

        # Prepare data for combos
        combo_data = [
            {"Hashtag": " + ".join(f"#{tag}" for tag in combo), "Count": count}
            for combo, count in self.combo_counts.most_common(10)  # Limit to top 10 for combos
        ]

        # Combine into a single DataFrame
        df_tags = pd.DataFrame(tag_data)
        df_combos = pd.DataFrame(combo_data)
        return pd.concat([df_tags, df_combos], ignore_index=True)

    def get_processed_data_as_json(self):
        """Return the processed data as a JSON-formatted string."""
        print("PROCESSED")
        print(self.processed_data)
        return json.dumps(self.processed_data, indent=4)

    def clear_processed_data(self):
        """Clear the processed data dictionary."""
        self.processed_data = []

    def write_to_file(self, filename="hashtag_data.json"):
        """Write the processed data to a JSON file."""
        with open(filename, "w") as f:
            json.dump(self.processed_data, f, indent=4)

###############################################################################
# BlueskyStream (Listen to Jetstream)
###############################################################################
class BlueskyStream:
    def __init__(self, uri, tracker: HashtagTracker):
        self.uri = uri
        self.tracker = tracker

    async def connect_and_read(self):
        print(f"[INFO] Connecting to Jetstream at {self.uri} ...")
        async with websockets.connect(self.uri) as websocket:
            print("[INFO] Connected. Listening for posts...")
            while True:
                try:
                    raw_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                    self.handle_message(raw_msg)
                except asyncio.TimeoutError:
                    # If no message within 5s, loop again
                    continue
                except websockets.ConnectionClosed:
                    print("[INFO] WebSocket closed.")
                    break

    def handle_message(self, raw_msg: str):
        data = json.loads(raw_msg)
        kind = data.get("kind")
        if kind == "commit":
            # Potentially check if it's a post, if you only want to track post commits
            commit_data = data.get("commit", {})
            collection = commit_data.get("collection")
            if collection == "app.bsky.feed.post":
                self.tracker.process_post_message(data)
                

###############################################################################
# Periodic Tasks
###############################################################################
async def post_summary_periodically(tracker: HashtagTracker, agent: BskyAgent):
    """
    Every x_seconds:
      1) Generate a compact text summary
      2) Generate an image of the summary
      3) Post both to BlueSky
    """
    x_seconds = 60 * 60 * 12  # Example interval
    while True:
        await asyncio.sleep(x_seconds)
        if not tracker.processed_data:
            print("[INFO] No new data to process.")
            continue
        print("[INFO] Generating compact text summary for posting...")
        compact_summary = tracker.get_compact_summary()

        print("[INFO] Generating hashtag stats image...")
        # Get the summary as a DataFrame and convert to image
        summary_df = tracker.get_summary_dataframe()
        image_path = "hashtag_stats.png"
        dataframe_to_image(summary_df, image_path)

        print("[INFO] Creating a new post via BskyAgent...")
        # Create a new post
        agent.new_post()\
            .add_text(compact_summary)\
            .add_image(image_path, image_path)\
            .send_post()
        if tracker.processed_data: 
            tracker.write_to_file(f"all_hashtag_data_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json")
        tracker.clear_processed_data()

        print(f"[INFO] Post sent with text and image. Check your feed!")


class Neo4jHandler:
    """
    Handles operations for writing hashtag and user data to a Neo4j database.
    """

    def write_hashtag_data(self, driver, hashtag_data, client):
        """
        Write hashtag data to the Neo4j database.

        Parameters:
        - driver (neo4j.Driver): Neo4j driver instance.
        - hashtag_data (list): List of dictionaries with keys 'hashtag', 'created_at', and 'did'.
        - client (BskyApiClient): An authenticated BskyApiClient instance for fetching user metadata.
        """
        with driver.session() as session:
            unique_dids = list({record['did'] for record in hashtag_data})
            user_metadata_map = self._fetch_user_metadata_batch(client, unique_dids)

            for record in hashtag_data:
                user_metadata = user_metadata_map.get(record['did'], {"handle": "unknown", "display_name": "unknown"})
                session.execute_write(self._create_user_and_tag, record, user_metadata)

    @staticmethod
    def _create_user_and_tag(tx, record, user_metadata):
        """
        Create a user and a hashtag node with a relationship between them.
        """
        query = """
        MERGE (u:User {did: $did})
        ON CREATE SET u.handle = $handle, u.display_name = $display_name
        MERGE (t:Tag {name: $hashtag})
        MERGE (u)-[:USED_TAG]->(t)
        """
        tx.run(query, 
               did=record['did'], 
               handle=user_metadata.get('handle', 'unknown'), 
               display_name=user_metadata.get('display_name', 'unknown'), 
               hashtag=record['hashtag'], 
               created_at=record['created_at'])

    @staticmethod
    def _fetch_user_metadata_batch(client: BskyApiClient, dids):
        """Fetch user metadata for a batch of DIDs using the BskyApiClient."""
        print("Fetching metadata for DIDs...")
        print(dids)
        user_metadata_map = {}
        try:
            for i in range(0, len(dids), 25):  # Process in batches of 25
                batch = dids[i:i+25]
                if batch:
                    users_data = client.client.get_profiles(actors=batch)  # Use the atproto.Client from BskyApiClient
                    for user_data in users_data['profiles']:
                        did = user_data.did
                        user_metadata_map[did] = {
                            "handle": user_data.handle,
                            "display_name": user_data.display_name
                        }
                        print(f"Fetched metadata for DID: {user_data.handle}")
                    del batch
        except Exception as e:
            print(f"Error fetching metadata for DIDs: {e}")
        return user_metadata_map

async def write_to_neo4j_task(client, uri, username, password):
    """Task to periodically write data from JSON files in the 'data' folder to Neo4j."""
    data_folder = "data"
    x_seconds = 60

    try:
        while True:
            await asyncio.sleep(x_seconds)
            print("Checking data folder for new files.")

            # Check for JSON files in the data folder
            for filename in os.listdir(data_folder):
                if filename.endswith(".json"):
                    filepath = os.path.join(data_folder, filename)
                    
                    with open(filepath, "r") as f:
                        hashtag_data = json.load(f)

                    try:
                        driver = GraphDatabase.driver(uri, auth=(username, password))
                        n4j = Neo4jHandler()
                        n4j.write_hashtag_data(driver, hashtag_data, client)
                        del hashtag_data
                        os.remove(filepath)
                        print(f"Processed and deleted {filepath}.")
                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")
                    finally:
                        driver.close()
    except Exception as e:
        print(f"Error in write_to_neo4j_task: {e}")

###############################################################################
# main()
###############################################################################
async def main():
    # 1) Choose the hashtags we track
    hashtags_to_track = ["rstats", "python", "stata", "sql", "html", "css", "javascript"]
    tracker = HashtagTracker(hashtags_to_track)

    # 2) Jetstream endpoint
    uri = (
        "wss://jetstream2.us-east.bsky.network/subscribe"
        "?wantedCollections=app.bsky.feed.post"
    )
    bluesky_stream = BlueskyStream(uri, tracker)

    # 3) Initialize your Bsky client & agent
    client = BskyApiClient(
        username="stoltzmaniacbot.bsky.social",
        password="PwssDD2PPZ7864W"
    )
    agent = BskyAgent(client)

    # Neo4j connection details
    neo4j_uri = "neo4j+s://2308f04a.databases.neo4j.io"
    neo4j_username = "neo4j"
    neo4j_password = "9AswVZiSyBoCBoJqoFCB7XcX6p_MwMkbAiEOo148x3I"

    # Start tasks in parallel
    read_task = asyncio.create_task(bluesky_stream.connect_and_read())
    post_task = asyncio.create_task(post_summary_periodically(tracker, agent))
    write_task = asyncio.create_task(write_to_neo4j_task(client, neo4j_uri, neo4j_username, neo4j_password))

    try:
        await read_task
    except asyncio.CancelledError:
        pass
    finally:
        post_task.cancel()
        await asyncio.gather(post_task, write_task, return_exceptions=True)  # Ensure tasks finish gracefully


if __name__ == "__main__":
    asyncio.run(main())
