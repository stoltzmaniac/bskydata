
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
