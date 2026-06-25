from decimal import Decimal

from sqlalchemy import String, UniqueConstraint, Index, Numeric
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import date

from app.database import Base
from app.schemas import BookCategory


class BookDataModel(Base):
	__tablename__ = "books"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)

	category: Mapped[BookCategory] = mapped_column(
		SAEnum(
			BookCategory,
			name="book_category",
			native_enum=True,
			length=50,
			values_callable=lambda enum_cls: [member.value for member in enum_cls],
		),
		nullable=False,
	)
	title: Mapped[str] = mapped_column(String(255), nullable=False)
	series: Mapped[bool] = mapped_column(default=False)
	volume: Mapped[int] = mapped_column(nullable=False)
	author: Mapped[str] = mapped_column(String(150), nullable=False)
	publisher: Mapped[str] = mapped_column(String(150), nullable=False)
	price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
	isbn: Mapped[str] = mapped_column(String(13), nullable=False)

	wishlist: Mapped[bool] = mapped_column(default=True)
	gift: Mapped[bool] = mapped_column(default=False)
	borrow: Mapped[bool] = mapped_column(default=False)

	releaseDate: Mapped[Optional[date]] = mapped_column(nullable=True)
	payDate: Mapped[Optional[date]] = mapped_column(nullable=True)
	startDate: Mapped[Optional[date]] = mapped_column(nullable=True)
	endDate: Mapped[Optional[date]] = mapped_column(nullable=True)

	__table_args__ = (
		UniqueConstraint('isbn', name='uq_isbn'),
		Index('idx_category', 'category'),
		Index('idx_author', 'author'),
		Index('idx_paydate', 'payDate'),
	)
