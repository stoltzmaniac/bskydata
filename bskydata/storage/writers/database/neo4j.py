import re
from bskydata.storage.writers.base import DataWriter
from neo4j import GraphDatabase


class Neo4jDataWriter(DataWriter):
    def __init__(self, 
                 connection_uri: str, 
                 username: str, 
                 password: str,
                 ):
        """
        :param connection_uri: Neo4j connection URI.
        :param username: Neo4j username.
        :param password: Neo4j password
        """
        self.driver = GraphDatabase.driver(
            connection_uri, 
            auth=(username, password)
            )
        self.session = self.driver.session()

    def write(self, data: dict, query: str, **kwargs):
        """
        Write data to a Neo4j database.
        This is a placeholder method and should be implemented by subclasses.
        """
        # Use the data dictionary to populate a query string
        self.session.run(query, data)

    @staticmethod
    def _sanitize_value(value):
        """
        Sanitizes the input to prevent SQL injection.
        - Strings: Escapes single quotes by doubling them.
        - Integers/Floats: Allowed as-is.
        - None: Returns NULL.
        - Others: Raises an exception.
        """
        if isinstance(value, str):
            sanitized_value = value.replace("'", "''")  # Escape single quotes
            return f"'{sanitized_value}'"
        elif isinstance(value, (int, float)):
            return value
        elif value is None:
            return "NULL"
        else:
            raise ValueError(f"Unsupported data type: {type(value)}")
    
    def disconnect(self):
        """
        Close the Neo4j driver session.
        """
        self.driver.close()
