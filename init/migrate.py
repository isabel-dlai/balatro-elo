# migrate_cards.py
import asyncio
from datetime import datetime
from database import connect_to_mongo, close_mongo_connection, get_database


async def migrate_existing_cards():
    """Add missing fields to existing cards imported via CSV"""
    await connect_to_mongo()
    
    try:
        db = get_database()
        
        # Count cards that need migration
        cards_without_elo = await db.Cards.count_documents({"elo_rating": {"$exists": False}})
        cards_without_created_at = await db.Cards.count_documents({"created_at": {"$exists": False}})
        
        print(f"Found {cards_without_elo} cards without elo_rating")
        print(f"Found {cards_without_created_at} cards without created_at")
        
        if cards_without_elo == 0 and cards_without_created_at == 0:
            print("No migration needed - all cards have required fields!")
            return
        
        # Add missing elo_rating field (default: 1200.0)
        if cards_without_elo > 0:
            result = await db.Cards.update_many(
                {"elo_rating": {"$exists": False}},
                {"$set": {"elo_rating": 1200.0}}
            )
            print(f"Added elo_rating to {result.modified_count} cards")
        
        # Add missing created_at field (current timestamp)
        if cards_without_created_at > 0:
            result = await db.Cards.update_many(
                {"created_at": {"$exists": False}},
                {"$set": {"created_at": datetime.utcnow()}}
            )
            print(f"Added created_at to {result.modified_count} cards")
        
        # Verify the migration
        total_cards = await db.Cards.count_documents({})
        complete_cards = await db.Cards.count_documents({
            "elo_rating": {"$exists": True},
            "created_at": {"$exists": True},
            "name": {"$exists": True},
            "image_url": {"$exists": True}
        })
        
        print(f"Migration complete! {complete_cards}/{total_cards} cards have all required fields")
        
        # Show a sample card
        sample_card = await db.Cards.find_one({})
        if sample_card:
            print(f"Sample card: {sample_card}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(migrate_existing_cards())