# init_data.py
import asyncio
import csv
import os
from database import connect_to_mongo, close_mongo_connection
from crud import create_card, get_card_count


async def load_cards_from_csv(csv_file="jokers.csv"):
    """Load cards from CSV file"""
    cards = []
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please ensure the file exists in the current directory.")
        return cards
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Verify required columns exist
            if 'name' not in reader.fieldnames or 'image_url' not in reader.fieldnames:
                print(f"Error: {csv_file} must contain 'name' and 'image_url' columns")
                print(f"Found columns: {reader.fieldnames}")
                return cards
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 since row 1 is headers
                # Strip whitespace from values
                name = row['name'].strip() if row['name'] else ""
                image_url = row['image_url'].strip() if row['image_url'] else ""
                
                # Skip rows with empty name or image_url
                if not name or not image_url:
                    print(f"Warning: Skipping row {row_num} - missing name or image_url")
                    continue
                
                cards.append({
                    "name": name,
                    "image_url": image_url
                })
        
        print(f"Successfully loaded {len(cards)} cards from {csv_file}")
        
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
    
    return cards


async def initialize_data_from_csv():
    """Initialize the database with cards from jokers.csv"""
    await connect_to_mongo()
    
    try:
        # Check if we already have cards
        card_count = await get_card_count()
        
        if card_count > 0:
            print(f"Database already has {card_count} cards. Skipping initialization.")
            return
        
        # Load cards from CSV
        cards_data = await load_cards_from_csv()
        
        if not cards_data:
            print("No valid cards found in CSV file. Database initialization aborted.")
            return
        
        print("Initializing database with cards from jokers.csv...")
        
        success_count = 0
        for card_data in cards_data:
            try:
                card = await create_card(card_data["name"], card_data["image_url"])
                print(f"Created card: {card.name}")
                success_count += 1
            except Exception as e:
                print(f"Error creating card '{card_data['name']}': {e}")
        
        print(f"Successfully initialized {success_count} out of {len(cards_data)} cards!")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(initialize_data_from_csv())