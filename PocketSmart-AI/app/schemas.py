from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=80)
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    rooms: list[str] = Field(min_length=1, max_length=10)
    style: str = Field(default="modern", max_length=80)
    priorities: list[str] = Field(default_factory=list, max_length=12)
class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    guests: int = Field(gt=0, le=5000)
    event_type: str = Field(min_length=2, max_length=80)
    venue: str = Field(default="", max_length=120)
class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=80)
    style: str = Field(default="classic", max_length=80)
    outfit_description: str = Field(default="", max_length=500)
