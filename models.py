# models.py
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: Dict[str, Any]) -> Dict[str, Any]:
        field_schema.update(type="string")
        return field_schema

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_wrap_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def _validate(cls, v, handler):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class Card(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    image_url: str
    description: str = Field(default="No description available")
    elo_rating: float = Field(default=1200.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('id', mode='before')
    @classmethod
    def validate_object_id(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        return v


class Comparison(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    winner_id: PyObjectId
    loser_id: PyObjectId
    winner_old_elo: float
    loser_old_elo: float
    winner_new_elo: float
    loser_new_elo: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('id', 'winner_id', 'loser_id', mode='before')
    @classmethod
    def validate_object_id(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        return v


class CardResponse(BaseModel):
    id: str
    name: str
    image_url: str
    description: str
    elo_rating: float
    created_at: datetime