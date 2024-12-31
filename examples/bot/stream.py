from dotenv import load_dotenv
import asyncio
import json
import websockets
from examples.bot.process_post import process_post_message
from examples.bot.uploader import schedule_bulk_upload

load_dotenv()

async def process_stream(hashtags_of_interest: list, folder_path: str):
    """
    Connect to Jetstream WebSocket and process incoming data stream.
    """
    URI = "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"
    message_count = 0
    print("[INFO] Connecting to Jetstream...")
    async with websockets.connect(URI) as websocket:
        print("[INFO] Connected. Listening for posts...")
        while True:
            try:
                raw_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(raw_msg)
                kind = data.get("kind")
                if kind == "commit":
                    # Check if it's a post
                    commit_data = data.get("commit", {})
                    collection = commit_data.get("collection")
                    if collection == "app.bsky.feed.post":
                        message_count += 1
                        if message_count % 100 == 0:
                            print(f"[INFO] Processed message count: {message_count}")
                        # Process the message and save it locally
                        await process_post_message(
                            hashtags_of_interest=hashtags_of_interest,
                            data=data,
                            folder_path=folder_path,
                        )
            except asyncio.TimeoutError:
                # If no message within 5 seconds, loop again
                continue
            except websockets.ConnectionClosed:
                print("[INFO] WebSocket closed.")
                break


async def main():
    """
    Run both the data processing stream and periodic uploads concurrently.
    """
    hashtags_to_track = [
        "rstats", "python", "stata", "sql", "html", "css", "javascript", "golang", "java", "csharp", "cplusplus"
    ]
    bucket_name = "stoltzmaniac"
    folder_path = "data"
    upload_interval = 60  # 1 minute

    # Start the WebSocket data stream processor
    stream_task = asyncio.create_task(process_stream(hashtags_to_track, folder_path))
    
    # Start the periodic bulk uploader to GCS
    upload_task = asyncio.create_task(schedule_bulk_upload(bucket_name, folder_path, upload_interval))
    
    # Run both tasks concurrently
    await asyncio.gather(stream_task, upload_task)


if __name__ == "__main__":
    # Run the main coroutine
    asyncio.run(main())
