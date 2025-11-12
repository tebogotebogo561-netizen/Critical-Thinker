import streamlit as st
import requests
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

st.title("Library Management System")

# Dashboard
st.header("Dashboard")
res_books = requests.get(f"{BASE_URL}/books/search?query=").json()
res_members = requests.get(f"{BASE_URL}/members").json()
res_transactions = requests.get(f"{BASE_URL}/transactions").json()

st.write(f"Total Books: {len(res_books)}")
st.write(f"Total Members: {len(res_members)}")
active_txns = [t for t in res_transactions if t['status'] == 'Issued']
st.write(f"Active Transactions: {len(active_txns)}")

# Issue Book Form
st.header("Issue Book")
book_map = {b["title"]: b["isbn"] for b in res_books}
member_map = {"John Doe": 1}  # Placeholder
book_choice = st.selectbox("Select Book", list(book_map.keys()))
member_choice = st.selectbox("Select Member", list(member_map.keys()))
if st.button("Issue Book"):
    payload = {
        "book_id": 1,  # Replace with actual DB ID mapping
        "member_id": 1,
        "issue_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=14))
    }
    res = requests.post(f"{BASE_URL}/transactions/issue", json=payload)
    st.write(res.json())

# ISBN Lookup
st.header("Add Book via ISBN")
isbn_input = st.text_input("Enter ISBN")
if st.button("Lookup ISBN"):
    try:
        book_data = requests.get(f"{BASE_URL}/isbn/{isbn_input}").json()
        if "detail" in book_data:
            st.error("Book not found.")
        else:
            st.write(book_data)
            if book_data.get("cover_image_url"):
                st.image(book_data["cover_image_url"], width=150)
    except Exception as e:
        st.error(f"Error fetching book info: {e}")

# Search Books
st.header("Search Books")
search_query = st.text_input("Search by title, author, ISBN, or category")
if st.button("Search"):
    results = requests.get(f"{BASE_URL}/books/search?query={search_query}").json()
    for b in results:
        st.write(f"**{b['title']}** by {b['author']}")
        if b.get("cover_image_url"):
            st.image(b["cover_image_url"], width=100)
