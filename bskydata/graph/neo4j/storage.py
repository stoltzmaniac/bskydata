from abc import ABC, abstractmethod
from neo4j import GraphDatabase
from typing import Dict, Any, List
from bskydata.graph.neo4j.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


class GraphStorage(ABC):
    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the graph database."""
        pass

    @abstractmethod
    def store_node(self, label: str, data: Dict[str, Any]) -> None:
        """Store a node in the graph."""
        pass

    @abstractmethod
    def store_relationship(self, from_node: str, to_node: str, relationship_type: str) -> None:
        """Store a relationship between two nodes."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the connection to the graph database."""
        pass


class Neo4jGraphStorage(GraphStorage):
    def __init__(self) -> None:
        self._uri = NEO4J_URI
        self._user = NEO4J_USER
        self._password = NEO4J_PASSWORD
        self._driver = None

    def connect(self) -> None:
        """Establish a connection to the Neo4j database."""
        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))

    def store_node(self, label: str, data: Dict[str, Any]) -> None:
        """Store a node in the graph."""
        with self._driver.session() as session:
            session.write_transaction(self._store_node, label, data)

    @staticmethod
    def _store_node(tx, label: str, data: Dict[str, Any]) -> None:
        """Helper function to store a node within a transaction."""
        query = f"CREATE (n:{label} $data)"
        tx.run(query, data=data)

    def store_relationship(self, from_node: Dict[str, Any], to_node: Dict[str, Any], relationship_type: str) -> None:
        """Store a relationship between two nodes."""
        with self._driver.session() as session:
            session.write_transaction(self._store_relationship, from_node, to_node, relationship_type)

    @staticmethod
    def _store_relationship(tx, from_node: Dict[str, Any], to_node: Dict[str, Any], relationship_type: str) -> None:
        """Helper function to create a relationship between two nodes."""
        query = (
            f"MATCH (a:User {{did: '{from_node['did']}'}}), (b:User {{did: '{to_node['did']}'}}) "
            f"CREATE (a)-[:{relationship_type}]->(b)"
        )
        tx.run(query)

    def close(self) -> None:
        """Close the connection to the Neo4j database."""
        if self._driver:
            self._driver.close()


class FollowHandler:
    def __init__(self, graph_storage: GraphStorage) -> None:
        self.graph_storage = graph_storage

    def store_follow_relationship(self, follower: Dict[str, Any], followed: Dict[str, Any]) -> None:
        """Store a follow relationship between two users."""
        self.graph_storage.store_relationship(follower, followed, 'FOLLOWS')

    def process_follows(self, follows: List[Dict[str, Any]], current_user_id: str) -> None:
        """Process the list of follows and store users and relationships."""
        for follow in follows:
            # Store followed user (if not already stored)
            self.store_user(follow)
            # Create follow relationship with the current user
            self.store_follow_relationship({'did': current_user_id}, follow)

    def store_user(self, user_data: Dict[str, Any]) -> None:
        """Store a user node in the graph."""
        user_properties = {
            'did': user_data['did'],
            'handle': user_data['handle'],
            'display_name': user_data['display_name'],
            'avatar': user_data['avatar'],
            'description': user_data['description'],
            'created_at': user_data['created_at'],
            'indexed_at': user_data['indexed_at']
        }
        self.graph_storage.store_node('User', user_properties)


class DataManager:
    def __init__(self, graph_storage: GraphStorage) -> None:
        self.graph_storage = graph_storage
        self.follow_handler = FollowHandler(graph_storage)

    def process_follows(self, follows: List[Dict[str, Any]], current_user_id: str) -> None:
        """Delegate the processing of follows to the FollowHandler."""
        self.follow_handler.process_follows(follows, current_user_id)

    def close(self) -> None:
        """Close the graph storage connection."""
        self.graph_storage.close()
