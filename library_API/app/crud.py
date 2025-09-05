import io
import json
import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy import text, func, update
from sqlalchemy.sql.expression import or_, not_

from models import BookDataModel as Book
import schemas




def getAllBooks(db: Session):
	return db.query(Book).all()


def addNewBook(db: Session, book: schemas.BookDataSchema):
	if findBookByIsbn(db=db, isbn=book.isbn) is not True:
		new_book = Book(
			category=book.category,
			title=book.title,
			series=book.series,
			volume=book.volume,
			author=book.author,
			publisher=book.publisher,
			price=book.price,
			isbn=book.isbn,
			wishlist=book.wishlist,
			gift=book.gift,
			borrow=book.borrow,
			releaseDate=book.releaseDate,
			payDate=book.payDate,
			startDate=book.startDate,
			endDate=book.endDate
		)
		db.add(new_book)
		db.commit()
		db.refresh(new_book)
		return {"message": "Add Book Successful"}
	else:
		return {"message": "Book already exists"}


def getBook(db: Session, id: int):
	result = db.query(Book).get(id)
	if result is not None:
		response_model = schemas.BookDataSchema
		return result
	else:
		return {"message": "Entry not Found"}


def deleteBook(db: Session, id: int):
	book = db.query(Book).get(id)
	if book is not None:
		db.delete(book)
		db.commit()
		return {"message": "Delete Book Successful"}
	else:
		return {"message": "Entry not Found"}


def updateBook(db: Session, id: int, book_update: schemas.BookUpdateSchema):
	# Find the existing entry in the database by its ID
	book_to_update = db.query(Book).filter(Book.id == id).first()

	if book_to_update is None:
		return None

	# Create a dictionary of the submitted values, excluding any that were not set
	# (i.e., those with a value of None). This ensures only provided fields are updated.
	update_data = book_update.model_dump(exclude_unset=True)

	# Iterate through the dictionary and update the corresponding attributes of the database object
	for key, value in update_data.items():
		setattr(book_to_update, key, value)

	# Commit the changes to the database
	db.commit()
	# Refresh the object to load the latest data from the database,
	# including any default values or changes made by the database itself
	db.refresh(book_to_update)

	# Return the updated object
	return book_to_update


def allPay(db: Session):
	"""
	Calculate the total amount paid for all books in the database.
	"""
	stmt = db.query(func.sum(Book.price)).filter(Book.payDate != None, Book.gift == False).all()
	return stmt[0][0]


def yearPay(db: Session, year: int) -> float:
	"""
	Calculate the total amount paid for books in a specific year.
	"""
	stmt = db.query(Book.price).filter(
		Book.payDate >= f"{year}-01-01",
		Book.payDate < f"{year + 1}-01-01",
		Book.gift != True
	).all()
	if stmt is not None:
		return calculator(stmt)
	else:
		return 0.0


def yearsInTable(db: Session):
	stmt = db.query(func.YEAR(Book.payDate).label("Year")). \
		filter(Book.payDate != None, func.YEAR(Book.payDate) > 2021). \
		group_by(func.YEAR(Book.payDate)).all()
	return [row._asdict() for row in stmt]


def monthPay(db: Session, year: int, month: int):
	"""
	Get total pay for a specific month in a specific year
	"""
	stmt = db.query(Book.price).filter(
		Book.payDate >= f"{year}-{str(month).zfill(2)}-01",
		Book.payDate < f"{year}-{str(month + 1).zfill(2)}-01",
		Book.gift != True
	).all()
	if stmt is not None:
		return calculator(stmt)
	else:
		return 0


def trueFalseCounter(db: Session):
	"""
	Get count of books that have wishlist=True, wishlist=False, gift=True, and borrow=True
	"""
	true = db.query(func.count()).filter(Book.wishlist == True).scalar()
	false = db.query(func.count()).filter(Book.wishlist == False).scalar()
	gift = db.query(func.count()).filter(Book.wishlist == False, Book.gift == True).scalar()
	borrow = db.query(func.count()).filter(Book.borrow == True).scalar()
	return {"true": true,
			"false": false,
			"gift": gift,
			"borrow": borrow}


def libraryOrWishlist(db: Session, trueOrFalse: bool, category: str):
	"""
	Get list of books that either are in the library or on the wishlist
	"""
	result_list = db.query(Book).filter(Book.wishlist == trueOrFalse,
										Book.category == category,
										not_(Book.borrow)).order_by(Book.author, Book.volume).all()
	return result_list


def borrow(db: Session, category: str):
	"""
	Define function to find borrowed books of a specific category
	"""
	result_list = db.query(Book).filter(Book.borrow == True, Book.category == category).all()
	return result_list


def authorCounter(db: Session):
	"""
	Define function to count the number of books by each author
	"""
	authors = db.query(Book.author, func.count(Book.author).label('counter')).group_by(Book.author).all()
	return [row._asdict() for row in authors]


def publisherCounter(db: Session):
	"""
	Define function to count the number of books by each publisher
	"""
	publishers = db.query(Book.publisher, func.count(Book.publisher).label('counter')).group_by(Book.publisher).all()
	return [row._asdict() for row in publishers]


def search(db: Session, search: str):
	"""
	Perform a query on the database that returns all records where one or more columns contain the search term
	"""
	results = db.query(Book).filter(
		or_(Book.title.ilike(f"%{search}%"),
			Book.author.ilike(f"%{search}%"),
			Book.publisher.ilike(f"%{search}%"),
			Book.isbn.ilike(f"%{search}%"))
	).all()
	return results


def findBookByIsbn(db: Session, isbn: int):
	"""
	Define function to find a book by its ISBN
	"""
	result = db.query(Book).filter_by(isbn=isbn).first()
	db.close()
	if result:
		return True
	else:
		return False


def exportJson(db: Session):
	"""
	Export all books from the database as a JSON file
	"""
	books = db.query(Book).all()
	# Convert SQLAlchemy objects to dictionaries
	book_list = []
	for book in books:
		book_dict = {
			"id": book.id,
			"category": book.category,
			"title": book.title,
			"series": book.series,
			"volume": book.volume,
			"author": book.author,
			"publisher": book.publisher,
			"price": book.price,
			"isbn": book.isbn,
			"wishlist": book.wishlist,
			"gift": book.gift,
			"borrow": book.borrow,
			"releaseDate": str(book.releaseDate) if book.releaseDate else None,
			"payDate": str(book.payDate) if book.payDate else None,
			"startDate": str(book.startDate) if book.startDate else None,
			"endDate": str(book.endDate) if book.endDate else None
		}
		book_list.append(book_dict)

	# Convert to JSON
	json_data = json.dumps(book_list, ensure_ascii=False, indent=4)
	return json_data


def importJson(db: Session, file):
	"""
	Import books from a JSON file into the database
	"""
	try:
		# Parse JSON from bytes to Python objects
		data = json.loads(file.decode('utf-8'))

		# Process each book in the JSON
		for book_data in data:
			# Check if book with this ISBN already exists
			existing_book = db.query(Book).filter(Book.isbn == book_data["isbn"]).first()

			if not existing_book:
				# Convert date strings back to date objects if they exist
				releaseDate = pd.to_datetime(book_data["releaseDate"]).date() if book_data["releaseDate"] else None
				payDate = pd.to_datetime(book_data["payDate"]).date() if book_data["payDate"] else None
				startDate = pd.to_datetime(book_data["startDate"]).date() if book_data["startDate"] else None
				endDate = pd.to_datetime(book_data["endDate"]).date() if book_data["endDate"] else None

				# Create new book
				new_book = Book(
					category=book_data["category"],
					title=book_data["title"],
					series=book_data["series"],
					volume=book_data["volume"],
					author=book_data["author"],
					publisher=book_data["publisher"],
					price=book_data["price"],
					isbn=book_data["isbn"],
					wishlist=book_data["wishlist"],
					gift=book_data["gift"],
					borrow=book_data["borrow"],
					releaseDate=releaseDate,
					payDate=payDate,
					startDate=startDate,
					endDate=endDate
				)
				db.add(new_book)

		# Commit all changes at once
		db.commit()
		return {"imported": len(data)}
	except Exception as e:
		db.rollback()
		return {"error": str(e)}


def calculator(stmt):
	counter = 0.0
	for row in stmt:
		counter += row[0]
	return counter
