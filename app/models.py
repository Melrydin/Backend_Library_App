from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import date

from app.database import Base


class BookDataModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    category: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    series: Mapped[bool] = mapped_column(default=False)
    volume: Mapped[int] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(String(150), nullable=False)
    publisher: Mapped[str] = mapped_column(String(150), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    isbn: Mapped[int] = mapped_column(unique=True, nullable=False)

    wishlist: Mapped[bool] = mapped_column(default=True)
    gift: Mapped[bool] = mapped_column(default=False)
    borrow: Mapped[bool] = mapped_column(default=False)

    releaseDate: Mapped[Optional[date]] = mapped_column(nullable=True)
    payDate: Mapped[Optional[date]] = mapped_column(nullable=True)
    startDate: Mapped[Optional[date]] = mapped_column(nullable=True)
    endDate: Mapped[Optional[date]] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint('isbn', name='uq_isbn'),
    )
