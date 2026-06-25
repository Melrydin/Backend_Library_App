import re

from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date
from typing import Optional
from enum import Enum


class BookCategory(str, Enum):
	manga = "Manga"
	novel = "Novel"
	technical = "Technical"


_ISBN_PATTERN = re.compile(r"^\d{9}[\dXx]$|^\d{13}$")


def validate_isbn(v: str) -> str:
	if not isinstance(v, str):
		raise ValueError("ISBN must be a string")

	if not _ISBN_PATTERN.match(v):
		raise ValueError(
			"ISBN must be exactly 10 digits (last may be 'X') or exactly 13 digits, "
			"with no hyphens or spaces"
		)

	isbn = v.upper()

	if len(isbn) == 10:
		total = sum(
			(10 - i) * (10 if ch == "X" else int(ch))
			for i, ch in enumerate(isbn)
		)
		if total % 11 != 0:
			raise ValueError("Invalid ISBN-10 checksum")
	else:
		total = sum(
			int(d) * (1 if i % 2 == 0 else 3)
			for i, d in enumerate(isbn)
		)
		if total % 10 != 0:
			raise ValueError("Invalid ISBN-13 checksum")

	return isbn


class BookBase(BaseModel):
	category: BookCategory
	title: str = Field(min_length=1, max_length=255)
	author: str = Field(min_length=1, max_length=150)
	publisher: str = Field(min_length=1, max_length=150)
	volume: int = Field(ge=0, le=9999)
	price: float = Field(ge=0.0, le=99999.99)
	isbn: str = Field(min_length=10, max_length=13)
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
	def check_isbn(cls, v: str) -> str:
		return validate_isbn(v)


class BookCreate(BookBase):
	pass


class BookUpdate(BaseModel):
	category: Optional[BookCategory] = None
	title: Optional[str] = Field(default=None, min_length=1, max_length=255)
	series: Optional[bool] = None
	volume: Optional[int] = Field(default=None, ge=0, le=9999)
	author: Optional[str] = Field(default=None, min_length=1, max_length=150)
	publisher: Optional[str] = Field(default=None, min_length=1, max_length=150)
	price: Optional[float] = Field(default=None, ge=0.0, le=99999.99)
	isbn: Optional[str] = Field(default=None, min_length=10, max_length=13)
	wishlist: Optional[bool] = None
	gift: Optional[bool] = None
	borrow: Optional[bool] = None
	releaseDate: Optional[date] = None
	payDate: Optional[date] = None
	startDate: Optional[date] = None
	endDate: Optional[date] = None

	@field_validator("isbn")
	@classmethod
	def check_isbn(cls, v: Optional[str]) -> Optional[str]:
		if v is None:
			return v
		return validate_isbn(v)


class BookRead(BookBase):
	id: int
	model_config = ConfigDict(from_attributes=True)
