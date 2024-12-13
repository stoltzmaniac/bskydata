from typing import Dict, Any, List
from bskydata.parsers.base import DataParser


class BasicFollowersParser(DataParser):
    def parse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        actor = data.get("actor", "")
        created_at = data.get("created_at", "")
        followers = [
            {
                "did": follower.get("did"),
                "display_name": follower.get("display_name"),
                "handle": follower.get("handle"),
                "description": follower.get("description"),
                "avatar_url": follower.get("avatar"),
                "created_at": follower.get("created_at"),
            }
            for follower in data.get("followers", [])
        ]
        return {
            "actor": actor,
            "created_at": created_at,
            "followers": followers
        }


class BasicFollowsParser(DataParser):
    """
    Concrete parser class for 'follows' data.
    Parses a dictionary containing follows data into a structured format.
    """

    def parse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the follows data.

        Args:
            data (Dict[str, Any]): The input data dictionary for follows.

        Returns:
            Dict[str, Any]: Parsed follows data in a structured format.
        """
        actor = data.get("actor", "")
        created_at = data.get("created_at", "")
        follows = self._extract_follows(data.get("follows", []))
        
        return {
            "actor": actor,
            "follows_created_at": created_at,
            "follows": follows
        }

    def _extract_follows(self, follows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract and structure individual follow details.

        Args:
            follows (List[Dict[str, Any]]): List of raw follow dictionaries.

        Returns:
            List[Dict[str, Any]]: Structured list of follow details.
        """
        return [
            {
                "did": follow.get("did", ""),
                "display_name": follow.get("display_name", ""),
                "handle": follow.get("handle", ""),
                "description": follow.get("description", ""),
                "avatar_url": follow.get("avatar", ""),
                "created_at": follow.get("created_at", "")
            }
            for follow in follows
        ]


class BasicProfilesParser(DataParser):
    """
    Concrete parser class for 'profiles' data.
    Parses a dictionary containing profile data into a structured format.
    """

    def parse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the profiles data.

        Args:
            data (Dict[str, Any]): The input data dictionary for profiles.

        Returns:
            Dict[str, Any]: Parsed profiles data in a structured format.
        """
        actors = data.get("actors", [])
        profiles_created_at = data.get("created_at", "")
        profiles = self._extract_profiles(data.get("profiles", []))
        
        return {
            "actors": actors,
            "profiles_created_at": profiles_created_at,
            "profiles": profiles
        }

    def _extract_profiles(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract and structure individual profile details.

        Args:
            profiles (List[Dict[str, Any]]): List of raw profile dictionaries.

        Returns:
            List[Dict[str, Any]]: Structured list of profile details.
        """
        return [
            {
                "did": profile.get("did", ""),
                "display_name": profile.get("display_name", ""),
                "handle": profile.get("handle", ""),
                "followers_count": profile.get("followers_count", 0),
                "follows_count": profile.get("follows_count", 0),
                "posts_count": profile.get("posts_count", 0),
                "description": profile.get("description", ""),
                "avatar_url": profile.get("avatar", ""),
                "banner_url": profile.get("banner", ""),
                "created_at": profile.get("created_at", ""),
                "labels": profile.get("labels", []),
                "pinned_post_uri": profile.get("pinned_post", {}).get("uri", "")
            }
            for profile in profiles
        ]
