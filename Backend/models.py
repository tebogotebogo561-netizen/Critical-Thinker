# File: models.py
# Type: Python

from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Book(Base):
    __tablename__ = "books"
    book_id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True)
    title = Column(String)
    author = Column(String)
    publisher = Column(String)
    publication_year = Column(Integer)
    category = Column(String)
    description = Column(String)
    cover_image_url = Column(String)
    page_count = Column(Integer)
    language = Column(String)
    total_copies = Column(Integer)
    available_copies = Column(Integer)
    shelf_location = Column(String)
    reviews = relationship("BookReview", back_populates="book")

class Member(Base):
    __tablename__ = "members"
    member_id = Column(Integer, primary_key=True, index=True)
    membership_number = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    address = Column(String)
    join_date = Column(Date)
    membership_type = Column(String)
    status = Column(String)
    transactions = relationship("Transaction", back_populates="member")

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))
    book_id = Column(Integer, ForeignKey("books.book_id"))
    issue_date = Column(Date)
    due_date = Column(Date)
    return_date = Column(Date, nullable=True)
    fine_amount = Column(Float, default=0.0)
    status = Column(String)
    member = relationship("Member", back_populates="transactions")
    book = relationship("Book")

class BookReview(Base):
    __tablename__ = "book_reviews"
    review_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.book_id"))
    member_id = Column(Integer, ForeignKey("members.member_id"))
    rating = Column(Integer)
    review_text = Column(String)
    review_date = Column(Date)
    book = relationship("Book", back_populates="reviews")
