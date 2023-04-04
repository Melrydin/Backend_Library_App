import io

from sqlalchemy.orm import Session
from sqlalchemy import text, func, update
from sqlalchemy.sql.expression import or_, not_

from models import BookDataModel as Book
import schemas
import pandas as pd


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



def getBook(db: Session, id: id):
    result = db.query(Book).get(id)
    if result is not None:
        return result
    else:
        return {"message": "Entry not Found"}


def deleteBook(db: Session, id: id):
    book = db.query(Book).get(id)
    if book is not None:
        db.delete(book)
        db.commit()
        return {"message": "Delete Book Successful"}
    else:
        return {"message": "Entry not Found"}


def updateBook(db: Session, id: int, book: schemas.BookDataSchema):
    stmt = update(Book).where(Book.id == id).values(
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
        endDate=book.endDate)
    db.execute(stmt)
    db.commit()
    return {"message": "Update Book successful"}


def allPay(db: Session):
    """
    Calculate the total amount paid for all books in the database.
    """
    stmt = db.query(func.sum(Book.price)).filter(Book.payDate != None, Book.gift == False).all()
    return stmt[0][0]


def yearPay(db: Session, year: int):
    """
    Calculate the total amount paid for books in a specific year.
    """
    stmt = db.query(Book.price).filter(
        Book.payDate >= f"{year}-01-01",
        Book.payDate < f"{year+1}-01-01",
        Book.gift != True
    ).all()
    if stmt is not None:
        return calculator(stmt, "price")
    else:
        return 0


def yearsInTable(db: Session):
    stmt = db.query(func.YEAR(Book.payDate).label("Year")).\
            filter(Book.payDate != None, func.YEAR(Book.payDate) > 2021).\
            group_by(func.YEAR(Book.payDate)).all()
    return stmt


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
        return calculator(stmt, "price")
    else:
        return 0


def trueFalseCounter(db: Session):
    """
    Get count of books that have wishlist=True, wishlist=False, gift=True, and borrow=True
    """
    true = db.query(func.count()).filter_by(wishlist=True).scalar()
    false = db.query(func.count()).filter_by(wishlist=False).scalar()
    gift = db.query(func.count()).filter_by(wishlist=False, gift=True).scalar()
    borrow = db.query(func.count()).filter_by(borrow=True).scalar()
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
    return authors


def publisherCounter(db: Session):
    """
    Define function to count the number of books by each publisher
    """
    publishers = db.query(Book.publisher, func.count(Book.publisher).label('counter')).group_by(Book.publisher).all()
    return publishers


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
    # Gib die Ergebnisse zurück
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

def exportCsv(db: Session):
    booksList = getAllBooks(db)
    booksDictList = convertBooksToDict(booksList)
    df = pd.DataFrame.from_records(booksDictList)
    df = df.drop(columns=['id'])
    df.to_csv('books.csv', index=False)

def importCsv(db: Session, file):
    df = pd.read_csv(io.StringIO(file.decode("utf-8")))
    df.fillna('None', inplace=True)
    db_books = [Book(**book) for book in df.to_dict(orient="records")]
    for book in db_books:
        print(book.isbn)
        addNewBook(db,book)

def convertBooksToDict(booksList):
    booksDictList = []
    for book in booksList:
        bookDict = book.__dict__
        bookDict.pop('_sa_instance_state', None) # remove _sa_instance_state which is used by SQLAlchemy
        booksDictList.append(bookDict)
    return booksDictList

def calculator(stmt, str):
    counter = 0.0
    for list in stmt:
        counter += list[str]
    return counter
