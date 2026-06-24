from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date
from typing import Optional
from enum import Enum


class BookCategory(str, Enum):
    manga = "Manga"
    novel = "Novel"
    technical = "Technical"


class BookBase(BaseModel):
    category: BookCategory
    title: str
    series: bool
    volume: int
    author: str
    publisher: str
    price: float
    isbn: int
    wishlist: bool = True
    gift: bool = False
    borrow: bool = False
    releaseDate: Optional[date] = None
    payDate: Optional[date] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Price must be a positive value')
        return v


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    category: Optional[BookCategory] = None
    title: Optional[str] = None
    series: Optional[bool] = None
    volume: Optional[int] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    price: Optional[float] = None
    isbn: Optional[int] = None
    wishlist: Optional[bool] = None
    gift: Optional[bool] = None
    borrow: Optional[bool] = None
    releaseDate: Optional[date] = None
    payDate: Optional[date] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None


class BookRead(BookBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
