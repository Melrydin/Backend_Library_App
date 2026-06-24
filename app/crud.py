import json
from datetime import date
from typing import List, Optional

from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import BookDataModel as Book
from app import schemas


def add_new_book(db: Session, book: schemas.BookCreate) -> dict:
    stmt = select(Book).where(Book.isbn == book.isbn)
    existing = db.scalars(stmt).first()
    if existing:
        return {"message": "Book already exists"}

    new_book = Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"message": "Add Book Successful"}


def get_book(db: Session, book_id: int) -> schemas.BookRead:
    stmt = select(Book).where(Book.id == book_id)
    book = db.scalars(stmt).first()
    if not book:
        raise HTTPException(status_code=404, detail="Entry not found")
    return book


def get_all_books(db: Session) -> List[schemas.BookRead]:
    stmt = select(Book)
    return list(db.scalars(stmt).all())


def delete_book(db: Session, book_id: int) -> dict:
    stmt = select(Book).where(Book.id == book_id)
    book = db.scalars(stmt).first()
    if not book:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(book)
    db.commit()
    return {"message": "Delete Book Successful"}


def update_book(db: Session, book_id: int, book_update: schemas.BookUpdate) -> schemas.BookRead:
    stmt = select(Book).where(Book.id == book_id)
    book = db.scalars(stmt).first()
    if not book:
        raise HTTPException(status_code=404, detail="Entry not found")

    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book


def all_pay(db: Session) -> float:
    stmt = select(func.sum(Book.price)).where(
        Book.payDate.isnot(None),
        Book.gift == False
    )
    return db.scalar(stmt) or 0.0


def year_pay(db: Session, year: int) -> float:
    start_date = date(year, 1, 1)
    end_date = date(year + 1, 1, 1)
    stmt = select(func.sum(Book.price)).where(
        Book.payDate >= start_date,
        Book.payDate < end_date,
        Book.gift == False
    )
    return db.scalar(stmt) or 0.0


def years_in_table(db: Session) -> List[dict]:
    stmt = select(func.year(Book.payDate).label("year")).where(
        Book.payDate.isnot(None),
        func.year(Book.payDate) > 2021
    ).group_by(func.year(Book.payDate))
    return [row._asdict() for row in db.scalars(stmt).all()]


def month_pay(db: Session, year: int, month: int) -> float:
    start_date = date(year, month, 1)
    end_date = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    stmt = select(func.sum(Book.price)).where(
        Book.payDate >= start_date,
        Book.payDate < end_date,
        Book.gift == False
    )
    return db.scalar(stmt) or 0.0


def true_false_counter(db: Session) -> dict:
    stmt_true = select(func.count(Book.id)).where(Book.wishlist == True)
    stmt_false = select(func.count(Book.id)).where(Book.wishlist == False)
    stmt_gift = select(func.count(Book.id)).where(Book.wishlist == False, Book.gift == True)
    stmt_borrow = select(func.count(Book.id)).where(Book.borrow == True)

    return {
        "true": db.scalar(stmt_true) or 0,
        "false": db.scalar(stmt_false) or 0,
        "gift": db.scalar(stmt_gift) or 0,
        "borrow": db.scalar(stmt_borrow) or 0
    }


def library_or_wishlist(db: Session, true_or_false: bool, category: str) -> List[schemas.BookRead]:
    stmt = select(Book).where(
        Book.wishlist == true_or_false,
        Book.category == category,
        ~Book.borrow  # SQLAlchemy 2.0 boolean negation
    ).order_by(Book.author, Book.volume)
    return list(db.scalars(stmt).all())


def borrow(db: Session, category: str) -> List[schemas.BookRead]:
    stmt = select(Book).where(
        Book.borrow == True,
        Book.category == category
    )
    return list(db.scalars(stmt).all())


def author_counter(db: Session) -> List[dict]:
    stmt = select(Book.author, func.count(Book.author).label('counter')).group_by(Book.author)
    return [row._asdict() for row in db.scalars(stmt).all()]


def publisher_counter(db: Session) -> List[dict]:
    stmt = select(Book.publisher, func.count(Book.publisher).label('counter')).group_by(Book.publisher)
    return [row._asdict() for row in db.scalars(stmt).all()]


def search(db: Session, search_term: str) -> List[schemas.BookRead]:
    pattern = f"%{search_term}%"
    stmt = select(Book).where(
        or_(
            Book.title.ilike(pattern),
            Book.author.ilike(pattern),
            Book.publisher.ilike(pattern)
        )
    )
    return list(db.scalars(stmt).all())


def find_book_by_isbn(db: Session, isbn: int) -> Optional[Book]:
    stmt = select(Book).where(Book.isbn == isbn)
    return db.scalars(stmt).first()


def export_json(db: Session) -> str:
    stmt = select(Book)
    books = db.scalars(stmt).all()
    book_dicts = [schemas.BookBase.model_validate(book).model_dump() for book in books]
    return json.dumps(book_dicts, ensure_ascii=False, indent=4)


def import_json(db: Session, file_content: bytes) -> dict:
    try:
        data = json.loads(file_content.decode('utf-8'))

        for book_data in data:
            stmt = select(Book).where(Book.isbn == book_data["isbn"])
            if db.scalars(stmt).first():
                continue

            def parse_date(val):
                if not val:
                    return None
                try:
                    return date.fromisoformat(val)
                except ValueError:
                    return None

            new_book = Book(
                category=book_data["category"],
                title=book_data["title"],
                series=book_data["series"],
                volume=book_data["volume"],
                author=book_data["author"],
                publisher=book_data["publisher"],
                price=book_data["price"],
                isbn=book_data["isbn"],
                wishlist=book_data.get("wishlist", True),
                gift=book_data.get("gift", False),
                borrow=book_data.get("borrow", False),
                releaseDate=parse_date(book_data.get("releaseDate")),
                payDate=parse_date(book_data.get("payDate")),
                startDate=parse_date(book_data.get("startDate")),
                endDate=parse_date(book_data.get("endDate"))
            )
            db.add(new_book)

        db.commit()
        return {"imported": len(data)}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
