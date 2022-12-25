from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.sql import text
import models, schemas


def getAllBooks(db: Session):
    return db.query(models.BookDataModel).all()


def addNewBook(db: Session, book: schemas.BookDataSchema):
    new_book = models.BookDataModel(
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


def getBook(db: Session, id: id):
    res = db.query(models.BookDataModel).get(id)
    if res is not None:
        return res
    else:
        return {"message": "Entry not Found"}


def deleteBook(db: Session, id: id):
    book = db.query(models.BookDataModel).get(id)
    if book is not None:
        db.delete(book)
        db.commit()
        return {"message": "Delete Book Successful"}
    else:
        return {"message": "Entry not Found"}


def updateBook(db: Session, id: int, book: schemas.BookDataSchema):
    stmt = update(models.BookDataModel).where(models.BookDataModel.id == id).values(
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
    stmt = db.execute(
        text(f"SELECT b.price FROM books b WHERE b.payDate IS NOT NULL AND b.gift IS NOT TRUE")).fetchall()
    return calculator(stmt, "price")


def yearPay(db: Session, year: int):
    stmt = db.execute(text(
        f"SELECT b.price FROM books b WHERE b.payDate BETWEEN '{year}-01-01' AND '{year + 1}-01-01' AND b.gift IS NOT TRUE")).fetchall()
    return calculator(stmt, "price")


def yearsInTable(db: Session):
    stmt = db.execute(text(
        "SELECT YEAR(b.payDate) AS Year FROM books b WHERE (b.payDate IS NOT NULL AND YEAR(b.payDate) > 2021) GROUP BY YEAR(b.payDate)")).fetchall()
    return stmt


def monthPay(db: Session, year: int, month: int):
    stmt = db.execute(text(
        f"SELECT b.price FROM books b WHERE b.payDate BETWEEN '{year}-{str(month).zfill(2)}-01' AND '{year}-{str(month + 1).zfill(2)}-01' AND b.gift IS NOT TRUE")).fetchall()
    return calculator(stmt, "price")


def trueFasleCounter(db: Session):
    true = db.execute(text("SELECT COUNT(b.wishlist) FROM books b WHERE b.wishlist = TRUE")).fetchall()
    false = db.execute(text("SELECT COUNT(b.wishlist) FROM books b WHERE b.wishlist = FALSE")).fetchall()
    gift = db.execute(
        text("SELECT COUNT(b.wishlist) FROM books b WHERE b.wishlist = FALSE AND b.gift = TRUE")).fetchall()
    borrow = db.execute(text("SELECT COUNT(b.borrow) FROM books b WHERE b.borrow = TRUE")).fetchall()
    true = true[0]["COUNT(b.wishlist)"]
    false = false[0]["COUNT(b.wishlist)"]
    gift = gift[0]["COUNT(b.wishlist)"]
    borrow = borrow[0]["COUNT(b.borrow)"]
    return {"true": true,
            "false": false,
            "gift": gift,
            "borrow": borrow}


def librayOrWishlist(db: Session, trueOrFalse: bool, category: str):
    list = db.execute(text(
        f"SELECT * FROM books b WHERE (b.wishlist = {trueOrFalse} AND b.category = '{category}' AND NOT b.borrow) ORDER BY b.author")).fetchall()
    return list


def borrow(db: Session, category: str):
    list = db.execute(text(f"SELECT * FROM books b WHERE (b.borrow = TRUE AND b.category = '{category}')")).fetchall()
    return list


def authorCounter(db: Session):
    author = db.execute(
        text("SELECT b.author , COUNT(b.author) AS counter FROM books b GROUP BY b.author")).fetchall()
    return author


def publisherCounter(db: Session):
    publisher = db.execute(
        text("SELECT b.publisher , COUNT(b.publisher) AS counter FROM books b GROUP BY b.publisher")).fetchall()
    return publisher


def search(db: Session, titleOrAuthor: str, trueOrFalse: bool):
    titleOrAuthor = f"%{titleOrAuthor}%"
    result = db.execute(text(
        f"SELECT * FROM books b WHERE (b.title LIKE '{titleOrAuthor}' OR b.author LIKE '{titleOrAuthor}' AND b.wishlist = {trueOrFalse})")).fetchall()
    return result


def calculator(stmt, str):
    counter = 0.0
    for list in stmt:
        counter += list[str]
    return counter
