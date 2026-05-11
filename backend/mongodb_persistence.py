"""MongoDB persistence module for Travel Planner.

This module provides direct MongoDB connection and operations
instead of using an abstraction layer.
"""

import os
import json
from typing import Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import certifi
from dotenv import load_dotenv

load_dotenv()


class MongoDBPersistence:
    """Direct MongoDB connection handler."""
    
    def __init__(self, uri: Optional[str] = None, db_name: str = "travelplanner"):
        """Initialize MongoDB connection.
        
        Args:
            uri: MongoDB connection string (from MONGO_URI env var if not provided)
            db_name: Database name to use
        """
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            ca_file = os.getenv("MONGO_TLS_CA_FILE", certifi.where())
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000,
                tlsCAFile=ca_file,
            )
            # Verify connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            print(f"[OK] Connected to MongoDB: {self.db_name}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(
                "[ERROR] Failed to connect to MongoDB: "
                f"{e}\n"
                "[HINT] If using MongoDB Atlas, ensure TLS certificates are "
                "available and your system clock is correct."
            )
            raise
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
    
    def get_collection(self, collection_name: str):
        """Get a MongoDB collection."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call _connect() first.")
        return self.db[collection_name]
    
    def load_json(self, collection_name: str, key: str) -> Optional[Any]:
        """Load JSON data from MongoDB collection.
        
        Args:
            collection_name: Name of the MongoDB collection
            key: Document key/ID to retrieve
            
        Returns:
            Parsed JSON data or None if not found
        """
        try:
            collection = self.get_collection(collection_name)
            doc = collection.find_one({"_id": key})
            if doc:
                return doc.get("payload")
            return None
        except Exception as e:
            print(f"Error loading from MongoDB: {e}")
            return None
    
    def save_json(self, collection_name: str, key: str, data: Any) -> bool:
        """Save JSON data to MongoDB collection.
        
        Args:
            collection_name: Name of the MongoDB collection
            key: Document key/ID
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.get_collection(collection_name)
            payload = data if isinstance(data, dict) else json.loads(json.dumps(data))
            
            result = collection.update_one(
                {"_id": key},
                {"$set": {"payload": payload}},
                upsert=True
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            return False
    
    def delete(self, collection_name: str, key: str) -> bool:
        """Delete a document from MongoDB collection.
        
        Args:
            collection_name: Name of the MongoDB collection
            key: Document key/ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one({"_id": key})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting from MongoDB: {e}")
            return False
    
    def find_all(self, collection_name: str) -> list:
        """Retrieve all documents from a collection.
        
        Args:
            collection_name: Name of the MongoDB collection
            
        Returns:
            List of documents (without MongoDB _id)
        """
        try:
            collection = self.get_collection(collection_name)
            docs = list(collection.find())
            for doc in docs:
                doc.pop("_id", None)
            return docs
        except Exception as e:
            print(f"Error finding documents in MongoDB: {e}")
            return []


def build_mongodb_persistence(uri: Optional[str] = None) -> MongoDBPersistence:
    """Factory function to build MongoDB persistence."""
    return MongoDBPersistence(uri=uri)
