from sqlmodel import Field
from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum


class BookTyps(str, Enum):
    manga = "Manga"
    Novel = "Novel"
    Technical = "Technical"


class BookDataSchema(BaseModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: BookTyps
    title: str
    series: bool
    volume: int
    author: str
    publisher: str
    price: float
    isbn: int
    wishlist: Optional[bool] = Field(default=True)
    gift: Optional[bool] = Field(default=False)
    borrow: Optional[bool] = Field(default=False)
    releaseDate: Optional[date] = Field(default=None)
    payDate: Optional[date] = Field(default=None)
    startDate: Optional[date] = Field(default=None)
    endDate: Optional[date] = Field(default=None)

    class Config:
        orm_mode = True
