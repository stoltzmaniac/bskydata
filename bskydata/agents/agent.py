import requests
from bskydata.api.client import BskyApiClient
from atproto import models, client_utils


class BskyAgent:
    def __init__(self, client: BskyApiClient):
        self.client = client
    
    def new_post(self):
        self.post = None
        self.images = None
        self.images_alt = None
        self.post_response = None
        self.post = client_utils.TextBuilder()
        return self
    
    def add_text(self, text: str):
        self.post.text(text)
        return self
    
    def add_mention(self, username: str, did: str = None):
        if did is None:
            profile = self.client.client.get_profile(username)
            self.post.mention(username, profile.did)
        else:
            self.post.mention(username, did)
        return self
    
    def add_tag(self, text: str, label: str):
        self.post.tag(text, label)
        return self
    
    def add_link(self, text: str, url: str):
        self.post.link(text, url)
        return self
    
    def add_image(self, image: str, image_alt: str):
        if image.startswith('http://') or image.startswith('https://'):
            # Download image from URL
            response = requests.get(image)
            if response.status_code == 200:
                img_data = response.content
            else:
                raise ValueError(f"Failed to download image from URL: {image}")
        else:
            # Read local file
            with open(image, 'rb') as f:
                img_data = f.read()
        if self.images is None:
            self.images = []
            self.images_alt = []
        self.images.append(img_data)
        self.images_alt.append(image_alt)
        return self

    def send_post(self):
        if self.images is not None:
            response = self.client.client.send_images(self.post, self.images, self.images_alt)
        elif self.post is not None:
            response = self.client.client.send_post(self.post)
        else:
            raise ValueError("No post content provided.")
        self.post_response = response
        self.post = None
        print("Post created successfully!")
