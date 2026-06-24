import json
from app import crud
from fastapi import FastAPI, Depends, Response, UploadFile, File, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas
from typing import List

app = FastAPI(
	title="Library Management API",
	description="API for managing a personal library with financial tracking",
	version="1.0.0",
	docs_url="/docs",
	redoc_url="/redoc"
)


@app.get("/", tags=["Health"])
async def root():
	return {"message": "Hello from Library API"}


@app.get("/books/{book_id}", response_model=schemas.BookRead, tags=["Books"])
async def get_book(book_id: int, db: Session = Depends(get_db)):
	return crud.get_book(db, book_id)


@app.put("/books/{book_id}", response_model=schemas.BookRead, tags=["Books"])
async def update_book(book_id: int, book_update: schemas.BookUpdate, db: Session = Depends(get_db)):
	return crud.update_book(db, book_id, book_update)


@app.post("/books/", tags=["Books"])
async def add_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
	result = crud.add_new_book(db, book)
	if "message" in result and "already exists" in result["message"]:
		raise HTTPException(status_code=409, detail=result["message"])
	return result


@app.delete("/books/{book_id}", status_code=204, tags=["Books"])
async def delete_book(book_id: int, db: Session = Depends(get_db)):
	crud.delete_book(db, book_id)


@app.get("/books/", response_model=List[schemas.BookRead], tags=["Books"])
async def get_all_books(
	skip: int = Query(default=0, ge=0),
	limit: int = Query(default=100, ge=1, le=500),
	db: Session = Depends(get_db)
):
	return crud.get_all_books(db, skip=skip, limit=limit)


@app.get("/stats/all-pay/", response_model=float, tags=["Stats"])
async def all_pay(db: Session = Depends(get_db)):
	return round(crud.all_pay(db), 2)


@app.get("/stats/year-pay/{year}", response_model=float, tags=["Stats"])
async def year_pay(year: int, db: Session = Depends(get_db)):
	return round(crud.year_pay(db, year), 2)


@app.get("/stats/month-pay/{year}/{month}", response_model=float, tags=["Stats"])
async def month_pay(
	year: int = Path(ge=2000, le=2100),
	month: int = Path(ge=1, le=12),
	db: Session = Depends(get_db)
):
	return round(crud.month_pay(db, year, month), 2)


@app.get("/stats/years-in-table/", tags=["Stats"])
async def years_in_table(db: Session = Depends(get_db)):
	return crud.years_in_table(db)


@app.get("/stats/true-false-counter/", tags=["Stats"])
async def true_false_counter(db: Session = Depends(get_db)):
	return crud.true_false_counter(db)


@app.get("/books/library-or-wishlist/{true_or_false}/{category}", response_model=List[schemas.BookRead], tags=["Filters"])
async def library_or_wishlist(true_or_false: bool, category: str, db: Session = Depends(get_db)):
	return crud.library_or_wishlist(db, true_or_false, category)


@app.get("/books/borrowed/{category}", response_model=List[schemas.BookRead], tags=["Filters"])
async def get_borrowed_books(category: str, db: Session = Depends(get_db)):
	return crud.borrow(db, category)


@app.get("/books/search/", response_model=List[schemas.BookRead], tags=["Search"])
async def search_books(search_term: str = Query(default="%", min_length=1), db: Session = Depends(get_db)):
	return crud.search(db, search_term)


@app.get("/books/isbn/{isbn}", response_model=schemas.BookRead, tags=["Search"])
async def find_book_by_isbn(isbn: int, db: Session = Depends(get_db)):
	book = crud.find_book_by_isbn(db, isbn)
	if not book:
		raise HTTPException(status_code=404, detail="Book not found")
	return book


@app.get("/stats/author-counter/", tags=["Stats"])
async def author_counter(db: Session = Depends(get_db)):
	return crud.author_counter(db)


@app.get("/stats/publisher-counter/", tags=["Stats"])
async def publisher_counter(db: Session = Depends(get_db)):
	return crud.publisher_counter(db)


@app.get("/export/books/", tags=["Import/Export"])
async def export_books(db: Session = Depends(get_db)):
	json_data = crud.export_json(db)
	return Response(
		content=json_data,
		media_type="application/json",
		headers={"Content-Disposition": 'attachment; filename="books.json"'}
	)


@app.post("/import/books/", tags=["Import/Export"])
async def import_books(file: UploadFile = File(...), db: Session = Depends(get_db)):
	if file.content_type not in ("application/json", "text/plain"):
		raise HTTPException(status_code=400, detail="Only JSON files are accepted.")

	content = await file.read()
	if len(content) > 10 * 1024 * 1024:  # 10 MB
		raise HTTPException(status_code=413, detail="File too large (max 10 MB).")

	result = crud.import_json(db, content)
	if "error" in result:
		raise HTTPException(status_code=400, detail=result["error"])
	return {"message": "Books uploaded successfully.", **result}
