import asyncio
import websockets
import json
import curses


class BlueskyStream:
    def __init__(self, uri, follow_parser, like_parser, post_parser):
        self.uri = uri
        self.follow_parser = follow_parser
        self.like_parser = like_parser
        self.post_parser = post_parser
        # For simple visualization, keep counters
        self.post_count = 0
        self.like_count = 0
        self.follow_count = 0
        # Keep a short text snippet from the last event
        self.last_snippet = ""

    async def connect_and_read(self, stdscr):
        """
        Main loop that connects to the WebSocket and receives messages.
        We'll update a curses-based UI on each message.
        """
        # Turn off cursor blinking
        curses.curs_set(0)
        # Make getch() non-blocking
        stdscr.nodelay(True)

        async with websockets.connect(self.uri) as websocket:
            while True:
                try:
                    raw_message = await websocket.recv()
                    self.handle_message(raw_message)
                except websockets.ConnectionClosed:
                    break

                self.render_screen(stdscr)

    def handle_message(self, raw_message: str):
        """
        Determine which parser to use based on the message content,
        then update counters and snippet accordingly.
        """
        data = json.loads(raw_message)
        kind = data.get("kind")
        commit_data = data.get("commit", {})
        collection = commit_data.get("collection")

        if kind == "account":
            # Follow/Account
            parsed = self.follow_parser.parse(raw_message)
            self.follow_count += 1
            self.last_snippet = f"Follow event from DID {parsed.get('did')}"
        elif kind == "commit":
            if collection == "app.bsky.feed.like":
                parsed = self.like_parser.parse(raw_message)
                self.like_count += 1
                self.last_snippet = f"Like event from DID {parsed.get('did')}"
            elif collection == "app.bsky.feed.post":
                parsed = self.post_parser.parse(raw_message)
                self.post_count += 1
                # Try to extract some short text from the record
                record = parsed.get("commit", {}).get("record", {})
                text = record.get("text", "<No Text>")
                # Grab just the first line or so for display
                self.last_snippet = text.split("\n")[0][:60]
            else:
                self.last_snippet = f"Unknown commit type: {collection}"
        else:
            self.last_snippet = "Unknown message kind"

    def render_screen(self, stdscr):
        """
        Update the curses UI.
        """
        stdscr.clear()

        stdscr.addstr(0, 0, "Bluesky Stream Visualization (curses)")
        stdscr.addstr(2, 0, f"Posts  : {self.post_count}")
        stdscr.addstr(3, 0, f"Likes  : {self.like_count}")
        stdscr.addstr(4, 0, f"Follows: {self.follow_count}")
        stdscr.addstr(6, 0, "Last Snippet:")
        stdscr.addstr(7, 2, f"{self.last_snippet}")

        # Refresh the screen
        stdscr.refresh()


class SimpleParser:
    """
    A basic parser that demonstrates how one might handle or transform
    incoming messages. This class follows the Open/Closed principle by
    allowing extension through subclasses or composition without modifying
    the existing code.
    """
    
    def parse(self, message):
        """
        For now, this simple parser just returns the message as-is.
        In a real-world scenario, you'd parse JSON, filter or transform data, etc.
        """
        return message


class FollowParser:
    """
    Parses JSON data for a 'follow' (or 'account') record.
    Expects a JSON payload such as:

    {
      "did": "did:plc:r5bxxbs27h5tnsrri26opxwo",
      "time_us": 1734785130896682,
      "kind": "account",
      "account": {
        "active": true,
        "did": "did:plc:r5bxxbs27h5tnsrri26opxwo",
        "seq": 2085572775,
        "time": "2024-12-21T12:45:30.537Z"
      }
    }
    """

    def parse(self, message: str) -> dict:
        """
        :param message: A JSON string containing follow/account information.
        :return: A dictionary of relevant fields.
        """
        data = json.loads(message)

        # Extract top-level fields
        did = data.get("did")
        time_us = data.get("time_us")
        kind = data.get("kind")

        # Extract nested account fields
        account_data = data.get("account", {})
        account_did = account_data.get("did")
        account_seq = account_data.get("seq")
        account_time = account_data.get("time")
        account_active = account_data.get("active")

        # Return a cleaned-up dictionary
        return {
            "did": did,
            "time_us": time_us,
            "kind": kind,
            "account_did": account_did,
            "account_seq": account_seq,
            "account_time": account_time,
            "account_active": account_active,
        }


class PostParser:
    """
    Parses JSON data for a 'post' record from the Bluesky protocol,
    including optional or variable-length fields such as facets, embeds,
    images, replies, mentions, etc.

    This parser demonstrates handling different types of "embed":
      - app.bsky.embed.images
      - app.bsky.embed.external
      - And easily extendable to more types (e.g. record, recordWithMedia)

    It also parses facets to handle:
      - app.bsky.richtext.facet#tag
      - app.bsky.richtext.facet#link
      - app.bsky.richtext.facet#mention

    Example for a mention facet:
    {
      "$type": "app.bsky.richtext.facet#mention",
      "did": "did:plc:sliywhmsq6ieplltfkm6zltw"
    }
    """

    def parse(self, message: str) -> dict:
        """
        :param message: A JSON string containing a 'post' commit record.
        :return: A nested dictionary of parsed data.
        """
        data = json.loads(message)

        # ----------------------
        # 1. Top-Level Fields
        # ----------------------
        did = data.get("did")
        time_us = data.get("time_us")
        kind = data.get("kind")

        # ----------------------
        # 2. Commit-Level Fields
        # ----------------------
        commit_data = data.get("commit", {})
        commit_rev = commit_data.get("rev")
        commit_operation = commit_data.get("operation")
        commit_collection = commit_data.get("collection")
        commit_rkey = commit_data.get("rkey")
        commit_cid = commit_data.get("cid")

        # ----------------------
        # 3. Record-Level Fields
        # ----------------------
        record = commit_data.get("record", {})
        record_type = record.get("$type")
        record_created_at = record.get("createdAt")
        text = record.get("text", "")
        langs = record.get("langs", [])

        # ----------------------
        # 4. Reply (If Present)
        # ----------------------
        reply_data = record.get("reply")
        parsed_reply = None
        if reply_data:
            parent_data = reply_data.get("parent", {})
            root_data = reply_data.get("root", {})
            parsed_reply = {
                "parent": {
                    "cid": parent_data.get("cid"),
                    "uri": parent_data.get("uri"),
                },
                "root": {
                    "cid": root_data.get("cid"),
                    "uri": root_data.get("uri"),
                }
            }

        # ----------------------
        # 5. Embed Handling
        # ----------------------
        embed = record.get("embed", {})
        embed_type = embed.get("$type")
        # Default structure for embed
        parsed_embed = {"type": embed_type}

        if embed_type == "app.bsky.embed.images":
            # Handle image embed
            images = []
            for image_data in embed.get("images", []):
                alt_text = image_data.get("alt", "")
                aspect = image_data.get("aspectRatio", {})
                height = aspect.get("height")
                width = aspect.get("width")

                image_blob = image_data.get("image", {})
                mime_type = image_blob.get("mimeType")
                size = image_blob.get("size")
                link_ref = image_blob.get("ref", {}).get("$link")

                images.append({
                    "alt": alt_text,
                    "height": height,
                    "width": width,
                    "mimeType": mime_type,
                    "size": size,
                    "linkRef": link_ref
                })

            parsed_embed["images"] = images

        elif embed_type == "app.bsky.embed.external":
            # Handle external embed
            external = embed.get("external", {})
            thumb = external.get("thumb", {})
            parsed_embed["external"] = {
                "description": external.get("description"),
                "title": external.get("title"),
                "uri": external.get("uri"),
                "thumb": {
                    "mimeType": thumb.get("mimeType"),
                    "size": thumb.get("size"),
                    "linkRef": thumb.get("ref", {}).get("$link"),
                }
            }

        else:
            # Catch-all for unrecognized embed types or if embed is empty
            parsed_embed["raw"] = embed

        # ----------------------
        # 6. Facets (Tags, Links, Mentions, etc.) - Optional
        # ----------------------
        facets = record.get("facets", [])
        parsed_facets = []
        for facet in facets:
            index_info = facet.get("index", {})
            features = facet.get("features", [])
            parsed_features = []

            for feature in features:
                feature_type = feature.get("$type")
                if feature_type == "app.bsky.richtext.facet#link":
                    parsed_features.append({
                        "type": "link",
                        "uri": feature.get("uri"),
                    })
                elif feature_type == "app.bsky.richtext.facet#tag":
                    parsed_features.append({
                        "type": "tag",
                        "tag": feature.get("tag"),
                    })
                elif feature_type == "app.bsky.richtext.facet#mention":
                    parsed_features.append({
                        "type": "mention",
                        "did": feature.get("did"),
                    })
                else:
                    # Catch-all for unrecognized feature types
                    parsed_features.append({
                        "type": feature_type,
                        "data": feature
                    })

            parsed_facets.append({
                "byteStart": index_info.get("byteStart"),
                "byteEnd": index_info.get("byteEnd"),
                "features": parsed_features
            })

        # ----------------------
        # 7. Return Structured Data
        # ----------------------
        return {
            "did": did,
            "time_us": time_us,
            "kind": kind,
            "commit": {
                "rev": commit_rev,
                "operation": commit_operation,
                "collection": commit_collection,
                "rkey": commit_rkey,
                "cid": commit_cid,
                "record": {
                    "type": record_type,
                    "createdAt": record_created_at,
                    "text": text,
                    "langs": langs,
                    "reply": parsed_reply,
                    "embed": parsed_embed,
                    "facets": parsed_facets,
                }
            }
        }



class LikeParser:
    """
    Parses JSON data for a 'like' record, which appears under the 'commit' key.
    Expects a JSON payload such as:

    {
      "did": "did:plc:jgtdylrh7i3tte6sphdyx4ob",
      "time_us": 1734785182311121,
      "kind": "commit",
      "commit": {
        "rev": "3ldswncqhpd27",
        "operation": "create",
        "collection": "app.bsky.feed.like",
        "rkey": "3ldswncq3yd27",
        "record": {
          "$type": "app.bsky.feed.like",
          "createdAt": "2024-12-21T12:46:20.728Z",
          "subject": {
            "cid": "bafyreiahnesznth7evfcljbxuuaiz4epskcwemjgz3qvjcg3fmhhu6lq2y",
            "uri": "at://did:plc:5v5wzh74fqfu6w3bsk2mfjhw/app.bsky.feed.post/3ldrqlh4f2s2t"
          }
        },
        "cid": "bafyreiexbyp7vtxxmyruqerkwfdlu2btuvtjoib5hv463kqrvjl5wi7uye"
      }
    }
    """

    def parse(self, message: str) -> dict:
        """
        :param message: A JSON string containing a 'like' commit record.
        :return: A dictionary of relevant fields extracted from the JSON.
        """
        # Convert the incoming JSON string to a Python dictionary
        data = json.loads(message)

        # Extract top-level fields
        did = data.get("did")
        time_us = data.get("time_us")
        kind = data.get("kind")

        # Extract 'commit' fields
        commit_data = data.get("commit", {})
        commit_rev = commit_data.get("rev")
        commit_operation = commit_data.get("operation")
        commit_collection = commit_data.get("collection")
        commit_rkey = commit_data.get("rkey")
        commit_cid = commit_data.get("cid")

        # Extract 'record' from within 'commit'
        record = commit_data.get("record", {})
        record_type = record.get("$type")
        record_created_at = record.get("createdAt")

        # Extract 'subject' from within 'record'
        subject_data = record.get("subject", {})
        subject_cid = subject_data.get("cid")
        subject_uri = subject_data.get("uri")

        # Return a structured dictionary
        return {
            "did": did,
            "time_us": time_us,
            "kind": kind,
            "commit": {
                "rev": commit_rev,
                "operation": commit_operation,
                "collection": commit_collection,
                "rkey": commit_rkey,
                "cid": commit_cid,
                "record": {
                    "type": record_type,
                    "createdAt": record_created_at,
                    "subject": {
                        "cid": subject_cid,
                        "uri": subject_uri
                    }
                }
            }
        }


async def run_curses_stream(stdscr):
    # Instantiate parsers
    follow_parser = FollowParser()
    like_parser = LikeParser()
    post_parser = PostParser()

    # Bluesky Jetstream endpoint
    uri = (
        "wss://jetstream2.us-east.bsky.network/subscribe"
        "?wantedCollections=app.bsky.feed.post"
        "&wantedCollections=app.bsky.feed.like"
        "&wantedCollections=app.bsky.feed.follow"
    )

    # Create the stream object
    stream = BlueskyStream(uri, follow_parser, like_parser, post_parser)

    await stream.connect_and_read(stdscr)


def main():
    curses.wrapper(lambda stdscr: asyncio.run(run_curses_stream(stdscr)))

if __name__ == "__main__":
    main()