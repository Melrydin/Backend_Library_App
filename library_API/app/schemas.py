from sqlmodel import Field
from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List
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

	model_config = ConfigDict(from_attributes=True)


# Scheme for updating books
class BookUpdateSchema(BaseModel):
	# All fields are optional and have no default value.
	category: Optional[BookTyps] = None
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
