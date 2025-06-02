# database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "card_comparison"

client = None
database = None


async def connect_to_mongo():
    global client, database
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        database = client[DATABASE_NAME]
        # Test the connection
        await client.admin.command('ping')
        print("Connected to MongoDB successfully!")
        
        # Create indexes
        await database.cards.create_index("name", unique=True)
        await database.cards.create_index("elo_rating")
        await database.comparisons.create_index("created_at")
        
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


def get_database():
    return database