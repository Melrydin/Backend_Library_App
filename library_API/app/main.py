from fastapi import FastAPI, Depends, Response, UploadFile, File
from sqlmodel import Session
from database import get_db
import crud, schemas

app = FastAPI()


@app.get("/")
async def hallo():
    return {"message": "Halo from Library API"}


@app.post("/add/")
async def addBook(book: schemas.BookDataSchema, db: Session = Depends(get_db)):
    newBook = crud.addNewBook(db=db, book=book)
    return newBook

@app.delete("/delete/{bookId}")
async def deleteBook(book_id: int, db: Session = Depends(get_db)):
    del_book = crud.deleteBook(db=db, id=book_id)
    return del_book


@app.post("/update/{bookId}")
async def updateBook(book_id: int, book: schemas.BookDataSchema, db: Session = Depends(get_db)):
    up_book = crud.updateBook(db=db, id=book_id, book=book)
    return up_book


@app.get("/getBook/{bookId}")
async def getBook(bookId: int, db: Session = Depends(get_db)):
    book = crud.getBook(db=db, id=bookId)
    return book



@app.get("/getAll/", response_model=list[schemas.BookDataSchema])
async def getAllBooks(db: Session = Depends(get_db)):
    books = crud.getAllBooks(db)
    return books


@app.get("/allPay/", response_model=float)
async def allPay(db: Session = Depends(get_db)):
    result = crud.allPay(db=db)
    return round(result, 2)


@app.get("/yearPay/{year}", response_model=float)
async def yearPay(year: int, db: Session = Depends(get_db)):
    result = crud.yearPay(db=db, year=year)
    return round(result, 2)


@app.get("/yearsInTable/")
async def yearsInTable(db: Session = Depends(get_db)):
    result = crud.yearsInTable(db=db)
    return result


@app.get("/monthpay/{year}{month}", response_model=float)
async def monthPay(year: int, month: int, db: Session = Depends(get_db)):
    month = crud.monthPay(db=db, year=year, month=month)
    return month


@app.get("/trueAndFalseCounter/")
async def trueFasleCounter(db: Session = Depends(get_db)):
    counter = crud.trueFalseCounter(db=db)
    return counter


@app.get("/libraryOrWishlist/{value}&{category}", response_model=list[schemas.BookDataSchema])
async def libraryOrWishlist(db: Session = Depends(get_db), value: bool = True, category: str = 'Manga'):
    libraryOrWishlist = crud.libraryOrWishlist(db=db, trueOrFalse=value, category=category)
    return libraryOrWishlist


@app.get("/borrow/{category}", response_model=list[schemas.BookDataSchema])
async def borrow(db: Session = Depends(get_db), category: str = 'Manga'):
    borrow = crud.borrow(db=db, category=category)
    return borrow


@app.get("/authorCounter/")
async def authorCounter(db: Session = Depends(get_db)):
    author = crud.authorCounter(db=db)
    return author


@app.get("/publisherCounter/")
async def publisherCounter(db: Session = Depends(get_db)):
    publisher = crud.publisherCounter(db=db)
    return publisher


@app.get("/searche/", response_model=list[schemas.BookDataSchema])
async def searchLibrary(db: Session = Depends(get_db), search: str = "%",):
    searchResult = crud.search(db=db, search=search)
    return searchResult

@app.get("/findBookByIsbn/")
async def findBookByIsbn(db: Session = Depends(get_db), isbn: int = 0):
    result = crud.findBookByIsbn(db=db, isbn=isbn)
    return result

@app.get("/downloadBooks", response_model=None)
async def downloadBooks(db: Session = Depends((get_db))):
    csvData = crud.exportCsv(db)
    return Response(content=csvData, media_type='text/csv', headers={'Content-Disposition': 'attachment; filename="books.csv"'})

@app.post("/uploadBooks")
async def uploadBook(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    crud.importCsv(db=db, file=content)
    return {"message": "Books uploaded successfully."}
