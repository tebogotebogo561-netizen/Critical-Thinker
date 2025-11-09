
# File: main.py
# Type: Python
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas
from datetime import date, timedelta
import requests
import smtplib
from email.mime.text import MIMEText

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Library Management System API")

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD for Books
@app.post("/api/books")
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# Search Books
@app.get("/api/books/search")
def search_books(query: str = "", db: Session = Depends(get_db)):
    results = db.query(models.Book).filter(
        (models.Book.title.ilike(f"%{query}%")) |
        (models.Book.author.ilike(f"%{query}%")) |
        (models.Book.isbn.ilike(f"%{query}%")) |
        (models.Book.category.ilike(f"%{query}%"))
    ).all()
    return results

# Issue Book
@app.post("/api/transactions/issue")
def issue_book(payload: schemas.TransactionBase, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.book_id == payload.book_id).first()
    if not book or book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book unavailable")
    book.available_copies -= 1
    txn = models.Transaction(**payload.dict(), status="Issued")
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn

# Return Book
@app.post("/api/transactions/return/{txn_id}")
def return_book(txn_id: int, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).filter(models.Transaction.transaction_id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    txn.return_date = date.today()
    txn.status = "Returned"
    txn.book.available_copies += 1
    # Fine calculation
    if txn.due_date < date.today():
        txn.fine_amount = (date.today() - txn.due_date).days * 5  # R5 per day
    db.commit()
    return txn

# Google Books + Open Library API
GOOGLE_API_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:{}"
OPENLIBRARY_URL = "https://openlibrary.org/isbn/{}.json"

@app.get("/api/isbn/{isbn}")
def lookup_isbn(isbn: str):
    g_response = requests.get(GOOGLE_API_URL.format(isbn))
    if g_response.status_code == 200 and g_response.json().get("items"):
        item = g_response.json()["items"][0]["volumeInfo"]
        return {
            "isbn": isbn,
            "title": item.get("title"),
            "author": ", ".join(item.get("authors", [])),
            "publisher": item.get("publisher"),
            "publication_year": item.get("publishedDate", "").split("-")[0],
            "description": item.get("description"),
            "cover_image_url": item.get("imageLinks", {}).get("thumbnail"),
            "page_count": item.get("pageCount"),
            "language": item.get("language")
        }
    o_response = requests.get(OPENLIBRARY_URL.format(isbn))
    if o_response.status_code == 200:
        data = o_response.json()
        return {
            "isbn": isbn,
            "title": data.get("title"),
            "author": ", ".join([a["name"] for a in data.get("authors", [])]),
            "publisher": data.get("publishers", [""])[0],
            "publication_year": data.get("publish_date", "").split()[-1],
            "description": data.get("notes", ""),
            "cover_image_url": f"http://covers.openlibrary.org/b/isbn/{isbn}-M.jpg",
            "page_count": data.get("number_of_pages"),
            "language": data.get("languages", [""])[0].split("/")[-1]
        }
    raise HTTPException(status_code=404, detail="Book not found")

# Email Notifications
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "<your-email@gmail.com>"
EMAIL_PASSWORD = "<your-app-password>"

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

@app.post("/api/notify/due")
def notify_due_books(db: Session = Depends(get_db)):
    today = date.today()
    due_txns = db.query(models.Transaction).filter(models.Transaction.due_date == today).all()
    for txn in due_txns:
        send_email(
            txn.member.email,
            "Book Due Reminder",
            f"Dear {txn.member.first_name}, your book '{txn.book.title}' is due today."
        )
    return {"notified": len(due_txns)}

