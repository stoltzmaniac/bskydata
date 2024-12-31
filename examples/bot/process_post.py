import json
import aiofiles
import os


async def parse_data(hashtags_of_interest: list, data: dict) -> dict:
    """Extract relevant hashtags from a single post commit."""
    did = data.get("did", "")
    cid = data.get("commit", {}).get("cid", "")
    record = data.get("commit", {}).get("record", {})
    created_at = record.get("createdAt", "")
    text = record.get("text", "")
    facets = record.get("facets", [])
    
    found_tags = set()
    for facet in facets:
        features = facet.get("features", [])
        for feature in features:
            if feature.get("$type") == "app.bsky.richtext.facet#tag":
                raw_tag = feature.get("tag", "").strip().lower()
                if raw_tag in hashtags_of_interest:
                    found_tags.add(raw_tag)

    return {
        "created_at": created_at,
        "cid": cid,
        "did": did,
        "text": text,
        "hashtags": list(found_tags)
    }


async def write_hashtag_data(data: dict, folder_path: str):
    """Write hashtag data to a file asynchronously in the specified folder."""
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Construct the file path
    cid = data.get("cid", "")
    did = data.get("did", "")
    file_path = os.path.join(folder_path, f"hashtag_data_{cid}_{did}.json")
    
    # Write data asynchronously
    async with aiofiles.open(file_path, "w") as f:
        await f.write(json.dumps(data, indent=4) + "\n")


async def process_post_message(hashtags_of_interest: list, data: dict, folder_path: str):
    """Process a single post commit and save data in the specified folder."""
    # Extract hashtags
    parsed_data = await parse_data(hashtags_of_interest, data)
    if not parsed_data["hashtags"]:
        return

    print(f"[INFO] Writing data to file for: {parsed_data}")
    # Write the parsed data to the specified folder
    await write_hashtag_data(parsed_data, folder_path)
