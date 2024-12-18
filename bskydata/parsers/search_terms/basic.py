from typing import Dict, Any, List
from bskydata.parsers.base import DataParser


class BasicSearchTermsParser(DataParser):
    """
    Concrete parser class for 'search terms' data.
    Parses a dictionary containing search term data into a structured format.
    """

    def parse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the search terms data.

        Args:
            data (Dict[str, Any]): The input data dictionary for search terms.

        Returns:
            Dict[str, Any]: Parsed search terms data in a structured format.
        """
        search_term = data.get("search_term", "")
        created_at = data.get("created_at", "")
        posts = self._extract_posts(data.get("posts", []))
        
        return {
            "search_term": search_term,
            "created_at": created_at,
            "posts": posts
        }

    def _extract_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract and structure individual post details.

        Args:
            posts (List[Dict[str, Any]]): List of raw post dictionaries.

        Returns:
            List[Dict[str, Any]]: Structured list of post details.
        """
        return [
            {
                "author_display_name": post.get("author", {}).get("display_name", ""),
                "author_did": post.get("author", {}).get("did", ""),
                "author_handle": post.get("author", {}).get("handle", ""),
                "post_text": post.get("record", {}).get("text", ""),
                "tags": self._extract_tags(post.get("record", {}).get("facets", [])),
                "mentions": self._extract_mentions(post.get("record", {}).get("facets", [])),
                "post_created_at": post.get("record", {}).get("created_at", "")
            }
            for post in posts
        ]

    def _extract_tags(self, facets: List[Dict[str, Any]]) -> List[str]:
        """
        Extract tags from post facets.

        Args:
            facets (List[Dict[str, Any]]): List of facet dictionaries.

        Returns:
            List[str]: List of extracted tags.
        """
        tags = []
        if facets is not None:
            for facet in facets:
                # Check if 'features' is in the facet and is a non-empty list
                features = facet.get("features", [])
                if features and isinstance(features, list):
                    for feature in features:
                        # Look for features with type 'mention' and a valid handle
                        if feature.get("py_type") == "app.bsky.richtext.facet#tag":
                            tags.append(feature["tag"])
        return tags
    
    def _extract_mentions(self, facets: List[Dict[str, Any]]) -> List[str]:
        """
        Extract mentions of other users from post facets.

        Args:
            facets (List[Dict[str, Any]]): List of facet dictionaries.

        Returns:
            List[str]: List of extracted mention handles.
        """
        mentions = []
        if facets is not None:
            for facet in facets:
                # Check if 'features' is in the facet and is a non-empty list
                features = facet.get("features", [])
                if features and isinstance(features, list):
                    for feature in features:
                        # Look for features with type 'mention' and a valid handle
                        if feature.get("py_type") == "app.bsky.richtext.facet#mention":
                            mentions.append(feature["did"])
        return mentions
