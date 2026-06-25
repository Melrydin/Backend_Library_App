import json
from datetime import date
from typing import List, Optional

from sqlalchemy import select, func, or_, extract
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

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


def get_all_books(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.BookRead]:
	stmt = select(Book).offset(skip).limit(limit)
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

	new_isbn = update_data.get("isbn")
	if new_isbn is not None and new_isbn != book.isbn:
		conflict_stmt = select(Book).where(Book.isbn == new_isbn, Book.id != book_id)
		conflict = db.scalars(conflict_stmt).first()
		if conflict:
			raise HTTPException(
				status_code=409,
				detail=f"ISBN {new_isbn} is already used by another book (id={conflict.id})",
			)

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


def years_pay_in_table(db: Session) -> List[dict]:
	current_year = date.today().year

	stmt = (
		select(
			extract("year", Book.payDate).label("year"),
			func.sum(Book.price).label("total")
		)
		.where(
			Book.payDate.isnot(None),
			Book.gift == False,
			extract("year", Book.payDate) < current_year  # nur vergangene Jahre
		)
		.group_by(extract("year", Book.payDate))
		.order_by(extract("year", Book.payDate))
	)

	result = db.execute(stmt)
	return [
		{
			"year": int(row.year),
			"total": round(float(row.total), 2)
		}
		for row in result]


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
	stmt = (
		select(Book.author, func.count(Book.author).label("counter"))
		.where(Book.author.isnot(None))
		.group_by(Book.author)
		.order_by(func.count(Book.author).desc())
	)
	result = db.execute(stmt)
	return [{"author": row.author, "counter": row.counter} for row in result]


def publisher_counter(db: Session) -> List[dict]:
	stmt = (
		select(Book.publisher, func.count(Book.publisher).label("counter"))
		.where(Book.publisher.isnot(None))
		.group_by(Book.publisher)
		.order_by(func.count(Book.publisher).desc())
	)
	result = db.execute(stmt)
	return [{"publisher": row.publisher, "counter": row.counter} for row in result]


def search(db: Session, search_term: str) -> List[schemas.BookRead]:
	escaped = search_term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
	pattern = f"%{escaped}%"
	stmt = select(Book).where(
		or_(
			Book.title.ilike(pattern, escape="\\"),
			Book.author.ilike(pattern, escape="\\"),
			Book.publisher.ilike(pattern, escape="\\"),
		)
	).limit(100)
	return list(db.scalars(stmt).all())


def find_book_by_isbn(db: Session, isbn: str) -> Optional[Book]:
	stmt = select(Book).where(Book.isbn == isbn)
	return db.scalars(stmt).first()


def export_json(db: Session) -> str:
	stmt = select(Book)
	books = db.scalars(stmt).all()
	book_dicts = [schemas.BookBase.model_validate(book, from_attributes=True).model_dump() for book in books]
	data = jsonable_encoder(book_dicts)
	return json.dumps(data, ensure_ascii=False, indent=4)


def import_json(db: Session, file_content: bytes) -> dict:
	try:
		data = json.loads(file_content.decode("utf-8"))

		if not isinstance(data, list):
			return {"error": "JSON must be a list of books"}

		if len(data) > 10_000:
			return {"error": "Too many entries (max 10.000)"}

		imported = 0
		errors = []

		for i, book_data in enumerate(data):
			try:
				validated = schemas.BookCreate.model_validate(book_data)
			except Exception as e:
				errors.append({"index": i, "error": str(e)})
				continue

			stmt = select(Book).where(Book.isbn == validated.isbn)
			if db.scalars(stmt).first():
				continue

			db.add(Book(**validated.model_dump()))
			imported += 1

		db.commit()
		return {"imported": imported, "errors": errors}

	except json.JSONDecodeError as e:
		db.rollback()
		return {"error": f"Invalid JSON: {e.msg}"}
	except Exception as e:
		db.rollback()
		return {"error": "Import failed"}
