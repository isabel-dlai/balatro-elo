# models.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Card(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    image_url: str
    elo_rating: float = Field(default=1200.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Comparison(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    winner_id: PyObjectId
    loser_id: PyObjectId
    winner_old_elo: float
    loser_old_elo: float
    winner_new_elo: float
    loser_new_elo: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CardResponse(BaseModel):
    id: str
    name: str
    image_url: str
    elo_rating: float
    created_at: datetime