from fastapi import FastAPI, Depends
from sqlmodel import Session
from database import get_db
import crud, schemas

app = FastAPI()


@app.get("/")
async def hallo():
    return {"message": "Halo from Library API"}


@app.post("/add/")
async def add_Book(book: schemas.BookDataSchema, db: Session = Depends(get_db)):
    new_book = crud.addNewBook(db=db, book=book)
    return new_book


@app.delete("/delete/{bookId}")
async def delete_Book(book_id: int, db: Session = Depends(get_db)):
    del_book = crud.deleteBook(db=db, id=book_id)
    return del_book


@app.post("/update/{bookId}")
async def update_Book(book_id: int, book: schemas.BookDataSchema, db: Session = Depends(get_db)):
    up_book = crud.updateBook(db=db, id=book_id, book=book)
    return up_book


@app.get("/get_book/{bookId}", response_model=schemas.BookDataSchema)
async def get_Book(bookId: int, db: Session = Depends(get_db)):
    book = crud.getBook(db=db, id=bookId)
    return book


@app.get("/get_all_books/", response_model=list[schemas.BookDataSchema])
async def get_All_Books(db: Session = Depends(get_db)):
    books = crud.getAllBooks(db)
    return books


@app.get("/all_pay/", response_model=float)
async def all_Pay(db: Session = Depends(get_db)):
    result = crud.allPay(db=db)
    return round(result, 2)


@app.get("/year_pay/{year}", response_model=float)
async def year_Pay(year: int, db: Session = Depends(get_db)):
    result = crud.yearPay(db=db, year=year)
    return round(result, 2)


@app.get("/years_in_Table/")
async def years_In_Table(db: Session = Depends(get_db)):
    result = crud.yearsInTable(db=db)
    return result


@app.get("/month_pay/{year}{month}", response_model=float)
async def month_Pay(year: int, month: int, db: Session = Depends(get_db)):
    month = crud.monthPay(db=db, year=year, month=month)
    return month


@app.get("/true_and_false_counter/")
async def true_Fasle_Counter(db: Session = Depends(get_db)):
    counter = crud.trueFasleCounter(db=db)
    return counter


@app.get("/library_Or_wishlist/{value}&{category}", response_model=list[schemas.BookDataSchema])
async def library_Or_Wishlist(db: Session = Depends(get_db), value: bool = True, category: str = 'Manga'):
    librayOrWishlist = crud.librayOrWishlist(db=db, trueOrFalse=value, category=category)
    return librayOrWishlist


@app.get("/borrow/{category}", response_model=list[schemas.BookDataSchema])
async def borrow(db: Session = Depends(get_db), category: str = 'Manga'):
    borrow = crud.borrow(db=db, category=category)
    return borrow


@app.get("/author_Counter/")
async def author_Counter(db: Session = Depends(get_db)):
    author = crud.authorCounter(db=db)
    return author


@app.get("/publisher_Counter/")
async def publisher_Counter(db: Session = Depends(get_db)):
    publisher = crud.publisherCounter(db=db)
    return publisher


@app.get("/searche/", response_model=list[schemas.BookDataSchema])
async def search_Library(db: Session = Depends(get_db), titleOrAuthor: str = "%", trueOrFalse: bool = True):
    searchResult = crud.search(db=db, titleOrAuthor=titleOrAuthor, trueOrFalse=trueOrFalse)
    return searchResult
