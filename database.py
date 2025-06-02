# database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = "JokerELO"

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
        print(f"Using database: {DATABASE_NAME}")
        
        # Create indexes
        await database.Cards.create_index("name", unique=True)
        await database.Cards.create_index("elo_rating")
        await database.Comparisons.create_index("created_at")
        
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        database = None
        raise


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


def get_database():
    """Get the database instance"""
    if database is None:
        raise Exception("Database not initialized. Make sure MongoDB connection is established.")
    return database