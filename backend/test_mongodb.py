#!/usr/bin/env python3
"""
MongoDB Connection Test Script
Verifies that MongoDB is properly configured and working with your Travel Planner app.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_mongodb_connection():
    """Test MongoDB connection and basic operations."""
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)
    
    try:
        from mongodb_persistence import build_mongodb_persistence
        print("✓ Successfully imported mongodb_persistence module")
    except ImportError as e:
        print(f"✗ Failed to import mongodb_persistence: {e}")
        print("  Run: pip install -r requirements.txt")
        return False
    
    try:
        print("\nAttempting to connect to MongoDB...")
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        print(f"  Connection URI: {mongo_uri}")
        
        db = build_mongodb_persistence()
        print("✓ Connected to MongoDB successfully!")
        
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        print("\nPossible solutions:")
        print("1. Ensure MongoDB is running:")
        print("   - Local: verify mongod service is started")
        print("   - Docker: run 'docker-compose up -d mongo'")
        print("   - Atlas: check internet connection and firewall")
        print("2. Check MONGO_URI in .env file:")
        print("   - Local: mongodb://localhost:27017")
        print("   - Atlas: mongodb+srv://user:pass@cluster.mongodb.net")
        return False
    
    try:
        print("\nTesting database operations...")
        
        # Test write
        print("  Writing test document...")
        test_collection = db.get_collection("test")
        test_collection.insert_one({"_id": "test_doc", "message": "Hello MongoDB!"})
        print("  ✓ Write successful")
        
        # Test read
        print("  Reading test document...")
        doc = test_collection.find_one({"_id": "test_doc"})
        if doc and doc.get("message") == "Hello MongoDB!":
            print("  ✓ Read successful")
        else:
            print("  ✗ Read failed - document not found or corrupted")
            return False
        
        # Cleanup
        print("  Cleaning up test document...")
        test_collection.delete_one({"_id": "test_doc"})
        print("  ✓ Cleanup successful")
        
    except Exception as e:
        print(f"✗ Database operation failed: {e}")
        return False
    
    try:
        print("\nChecking collections...")
        collections = {
            "destinations": "destinations",
            "users": "users",
            "cost_rates": "cost_rates"
        }
        
        for display_name, collection_name in collections.items():
            collection = db.get_collection(collection_name)
            count = collection.count_documents({})
            if count > 0:
                print(f"  ✓ {collection_name}: {count} document(s)")
            else:
                print(f"  - {collection_name}: empty (will be seeded on app startup)")
        
    except Exception as e:
        print(f"✗ Failed to check collections: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed! MongoDB is working correctly.")
    print("=" * 60)
    print("\nYou can now start the app with: python app.py")
    return True


if __name__ == "__main__":
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)
