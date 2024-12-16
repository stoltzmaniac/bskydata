import typing as t
from bskydata.storage.writers.base import DataWriter
from pymongo import MongoClient


class MongoDBDataWriter(DataWriter):
    def __init__(self, connection_uri: str, database_name: str, collection: str):
        """
        :param connection_uri: MongoDB connection URI.
        :param database_name: Name of the MongoDB database to write to.
        """
        self.client = MongoClient(connection_uri)
        self.database = self.client[database_name]
        self.destination = collection

    def write(self, data: t.Any, destination: str = None, **kwargs):
        """
        Write data to a MongoDB collection.
        
        :param data: The data to write (dictionary or list of dictionaries).
        :param destination: MongoDB collection name.
        :param kwargs: Additional options for the insert operation.
        """
        if self.destination is not None:
            self.destination = destination

        if not destination:
            raise ValueError("No destination (collection name) specified for MongoDBDataWriter.")

        collection = self.database[self.destination]

        # Handle insertion of single or multiple documents
        if isinstance(data, list):
            collection.insert_many(data, **kwargs)
        else:
            collection.insert_one(data, **kwargs)
