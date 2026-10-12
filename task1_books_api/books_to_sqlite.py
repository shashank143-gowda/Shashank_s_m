"""Task 1: fetch books from a REST API, store them in SQLite, display them.

API used: Open Library search API (free, no key needed).
If the API cannot be reached (no internet), sample data is used so the script still runs.
"""
import sqlite3
import requests

API_URL = 'https://openlibrary.org/search.json'
DB_NAME = 'books.db'

SAMPLE_BOOKS = [
    ('Clean Code', 'Robert C. Martin', 2008),
    ('Fluent Python', 'Luciano Ramalho', 2015),
    ('The Pragmatic Programmer', 'Andrew Hunt, David Thomas', 1999),
]


def fetch_books(query='python', limit=20):
    """Call the API and return a list of (title, author, year) tuples."""
    try:
        params = {'q': query, 'limit': limit,
                  'fields': 'title,author_name,first_publish_year'}
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        books = []
        for item in response.json().get('docs', []):
            books.append((item.get('title', 'Unknown'),
                          ', '.join(item.get('author_name', ['Unknown'])),
                          item.get('first_publish_year')))
        return books
    except requests.RequestException as e:
        print(f'API request failed ({e}). Using sample data instead.')
        return SAMPLE_BOOKS


def save_books(books):
    """Create the table if needed and insert the books (duplicates ignored)."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            year INTEGER,
            UNIQUE(title, author))''')
        conn.executemany(
            'INSERT OR IGNORE INTO books (title, author, year) VALUES (?, ?, ?)',
            books)


def show_books():
    """Read the books back from the database and print them as a table."""
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute(
            'SELECT id, title, author, year FROM books ORDER BY year').fetchall()
    print(f"{'ID':<4}{'Title':<45}{'Author':<30}{'Year'}")
    print('-' * 90)
    for r in rows:
        print(f'{r[0]:<4}{r[1][:43]:<45}{str(r[2])[:28]:<30}{r[3]}')
    print(f'\nTotal books in database: {len(rows)}')


if __name__ == '__main__':
    save_books(fetch_books())
    show_books()
