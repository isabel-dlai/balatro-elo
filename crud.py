# crud.py
import random
import math
from typing import List, Optional, Tuple
from bson import ObjectId
from models import Card, Comparison, CardResponse
from database import get_database


async def create_card(name: str, image_url: str) -> Card:
    """Create a new card in the database"""
    db = get_database()
    card = Card(name=name, image_url=image_url)
    result = await db.cards.insert_one(card.dict(by_alias=True))
    card.id = result.inserted_id
    return card


async def get_card_by_id(card_id: str) -> Optional[Card]:
    """Get a card by its ID"""
    db = get_database()
    card_data = await db.cards.find_one({"_id": ObjectId(card_id)})
    if card_data:
        return Card(**card_data)
    return None


async def get_all_cards() -> List[CardResponse]:
    """Get all cards from the database"""
    db = get_database()
    cards = []
    async for card_data in db.cards.find():
        card = Card(**card_data)
        cards.append(CardResponse(
            id=str(card.id),
            name=card.name,
            image_url=card.image_url,
            elo_rating=card.elo_rating,
            created_at=card.created_at
        ))
    return cards


async def get_random_card_pair() -> Tuple[CardResponse, CardResponse]:
    """Get two random cards for comparison"""
    db = get_database()
    cards = await db.cards.aggregate([{"$sample": {"size": 2}}]).to_list(length=2)
    
    if len(cards) < 2:
        raise ValueError("Not enough cards in database for comparison")
    
    card1 = Card(**cards[0])
    card2 = Card(**cards[1])
    
    return (
        CardResponse(
            id=str(card1.id),
            name=card1.name,
            image_url=card1.image_url,
            elo_rating=card1.elo_rating,
            created_at=card1.created_at
        ),
        CardResponse(
            id=str(card2.id),
            name=card2.name,
            image_url=card2.image_url,
            elo_rating=card2.elo_rating,
            created_at=card2.created_at
        )
    )


async def get_leaderboard(limit: int = 20) -> List[CardResponse]:
    """Get cards sorted by ELO rating"""
    db = get_database()
    cards = []
    async for card_data in db.cards.find().sort("elo_rating", -1).limit(limit):
        card = Card(**card_data)
        cards.append(CardResponse(
            id=str(card.id),
            name=card.name,
            image_url=card.image_url,
            elo_rating=card.elo_rating,
            created_at=card.created_at
        ))
    return cards


def calculate_elo_ratings(winner_rating: float, loser_rating: float, k_factor: int = 32) -> Tuple[float, float]:
    """Calculate new ELO ratings based on comparison result"""
    expected_winner = 1 / (1 + math.pow(10, (loser_rating - winner_rating) / 400))
    expected_loser = 1 / (1 + math.pow(10, (winner_rating - loser_rating) / 400))
    
    new_winner_rating = winner_rating + k_factor * (1 - expected_winner)
    new_loser_rating = loser_rating + k_factor * (0 - expected_loser)
    
    return new_winner_rating, new_loser_rating


async def update_card_ratings(winner_id: str, loser_id: str) -> Comparison:
    """Update ELO ratings after a comparison and record the comparison"""
    db = get_database()
    
    # Get both cards
    winner = await get_card_by_id(winner_id)
    loser = await get_card_by_id(loser_id)
    
    if not winner or not loser:
        raise ValueError("One or both cards not found")
    
    # Calculate new ratings
    old_winner_rating = winner.elo_rating
    old_loser_rating = loser.elo_rating
    
    new_winner_rating, new_loser_rating = calculate_elo_ratings(
        old_winner_rating, old_loser_rating
    )
    
    # Update cards in database
    await db.cards.update_one(
        {"_id": ObjectId(winner_id)},
        {"$set": {"elo_rating": new_winner_rating}}
    )
    
    await db.cards.update_one(
        {"_id": ObjectId(loser_id)},
        {"$set": {"elo_rating": new_loser_rating}}
    )
    
    # Record the comparison
    comparison = Comparison(
        winner_id=ObjectId(winner_id),
        loser_id=ObjectId(loser_id),
        winner_old_elo=old_winner_rating,
        loser_old_elo=old_loser_rating,
        winner_new_elo=new_winner_rating,
        loser_new_elo=new_loser_rating
    )
    
    result = await db.comparisons.insert_one(comparison.dict(by_alias=True))
    comparison.id = result.inserted_id
    
    return comparison


async def get_card_count() -> int:
    """Get the total number of cards in the database"""
    db = get_database()
    return await db.cards.count_documents({})