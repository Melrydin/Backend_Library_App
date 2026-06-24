from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date
from typing import Optional
from enum import Enum


class BookCategory(str, Enum):
	manga = "Manga"
	novel = "Novel"
	technical = "Technical"


class BookBase(BaseModel):
	category: BookCategory
	title: str = Field(min_length=1, max_length=255)
	author: str = Field(min_length=1, max_length=150)
	publisher: str = Field(min_length=1, max_length=150)
	volume: int = Field(ge=0, le=9999)
	price: float = Field(ge=0.0, le=99999.99)
	isbn: int = Field(gt=0)
	series: bool = False
	wishlist: bool = True
	gift: bool = False
	borrow: bool = False
	releaseDate: Optional[date] = None
	payDate: Optional[date] = None
	startDate: Optional[date] = None
	endDate: Optional[date] = None

	@field_validator("isbn")
	@classmethod
	def validate_isbn(cls, v: int) -> int:
		isbn_str = str(v)
		if len(isbn_str) not in (10, 13):
			raise ValueError("ISBN must be 10 or 13 digits")
		if len(isbn_str) == 13:
			total = sum(
				int(d) * (1 if i % 2 == 0 else 3)
				for i, d in enumerate(isbn_str)
			)
			if total % 10 != 0:
				raise ValueError("Invalid ISBN-13 checksum")
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
