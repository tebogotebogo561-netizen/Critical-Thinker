# File: schemas.py
# Type: Python

from pydantic import BaseModel
from typing import Optional
from datetime import date

class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: Optional[str]
    publication_year: Optional[int]
    category: Optional[str]
    description: Optional[str]
    cover_image_url: Optional[str]
    page_count: Optional[int]
    language: Optional[str]
    total_copies: int
    available_copies: int
    shelf_location: Optional[str]

class BookCreate(BookBase):
    pass

class MemberBase(BaseModel):
    membership_number: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    join_date: Optional[date]
    membership_type: str
    status: str

class MemberCreate(MemberBase):
    pass

class TransactionBase(BaseModel):
    member_id: int
    book_id: int
    issue_date: date
    due_date: date
