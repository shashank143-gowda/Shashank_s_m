"""Library Management System: Python + SQLite.

Shows: OOP, custom exceptions, context managers, transactions,
parameterised SQL, logging, argparse CLI and type hints.

Usage:
    python library.py demo        # builds library.db with sample data and prints reports
    python library.py overdue     # lists overdue loans from library.db
"""
import argparse
import logging
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

SCHEMA_FILE = Path(__file__).with_name('schema.sql')
LOAN_DAYS = 14
MAX_ACTIVE_LOANS = 3

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('library')


# ---------- custom exceptions ----------
class LibraryError(Exception):
    """Base class for all library errors."""


class NotFound(LibraryError):
    pass


class BookUnavailable(LibraryError):
    pass


class LoanLimitReached(LibraryError):
    pass


# ---------- database wrapper ----------
class Database:
    def __init__(self, path: str = ':memory:'):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row          # access columns by name
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.conn.executescript(SCHEMA_FILE.read_text())

    @contextmanager
    def transaction(self):
        """Commit if the block succeeds, roll back if anything fails."""
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()


# ---------- business logic ----------
class LibraryService:
    def __init__(self, db: Database):
        self.db = db

    def add_book(self, title: str, author: str, year: int,
                 isbn: str | None = None, copies: int = 1) -> int:
        with self.db.transaction() as c:
            c.execute('INSERT OR IGNORE INTO authors (name) VALUES (?)', (author,))
            author_id = c.execute('SELECT author_id FROM authors WHERE name = ?',
                                  (author,)).fetchone()['author_id']
            cur = c.execute(
                '''INSERT INTO books (title, author_id, publication_year, isbn,
                                      total_copies, available_copies)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (title, author_id, year, isbn, copies, copies))
            logger.info('Added book "%s" (%d copies)', title, copies)
            return cur.lastrowid

    def register_member(self, name: str, email: str) -> int:
        with self.db.transaction() as c:
            cur = c.execute('INSERT INTO members (name, email) VALUES (?, ?)',
                            (name, email.strip().lower()))
            logger.info('Registered member %s', name)
            return cur.lastrowid

    def borrow_book(self, book_id: int, member_id: int,
                    today: date | None = None) -> int:
        today = today or date.today()
        with self.db.transaction() as c:
            if not c.execute('SELECT 1 FROM members WHERE member_id = ?',
                             (member_id,)).fetchone():
                raise NotFound(f'Member {member_id} does not exist')
            book = c.execute('SELECT title, available_copies FROM books WHERE book_id = ?',
                             (book_id,)).fetchone()
            if book is None:
                raise NotFound(f'Book {book_id} does not exist')
            if book['available_copies'] == 0:
                raise BookUnavailable(f'No copies of "{book["title"]}" are available')

            active = c.execute(
                'SELECT COUNT(*) AS n FROM loans WHERE member_id = ? AND returned_on IS NULL',
                (member_id,)).fetchone()['n']
            if active >= MAX_ACTIVE_LOANS:
                raise LoanLimitReached(
                    f'Member {member_id} already has {MAX_ACTIVE_LOANS} active loans')

            cur = c.execute(
                'INSERT INTO loans (book_id, member_id, borrowed_on, due_on) VALUES (?, ?, ?, ?)',
                (book_id, member_id, today.isoformat(),
                 (today + timedelta(days=LOAN_DAYS)).isoformat()))
            logger.info('Member %d borrowed "%s"', member_id, book['title'])
            return cur.lastrowid

    def return_book(self, loan_id: int, today: date | None = None) -> float:
        """Returns the fine amount (0.0 if the book was on time)."""
        today = today or date.today()
        with self.db.transaction() as c:
            loan = c.execute('SELECT returned_on FROM loans WHERE loan_id = ?',
                             (loan_id,)).fetchone()
            if loan is None:
                raise NotFound(f'Loan {loan_id} does not exist')
            if loan['returned_on'] is not None:
                raise LibraryError(f'Loan {loan_id} was already returned')
            c.execute('UPDATE loans SET returned_on = ? WHERE loan_id = ?',
                      (today.isoformat(), loan_id))   # triggers update stock and fines
            fine = c.execute('SELECT amount FROM fines WHERE loan_id = ?',
                             (loan_id,)).fetchone()
            amount = fine['amount'] if fine else 0.0
            logger.info('Loan %d returned, fine = %.2f', loan_id, amount)
            return amount

    # ----- reports -----
    def overdue_loans(self, today: date | None = None) -> list[sqlite3.Row]:
        today = (today or date.today()).isoformat()
        return self.db.conn.execute(
            '''SELECT loan_id, title, member, due_on,
                      CAST(julianday(?) - julianday(due_on) AS INTEGER) AS days_late
               FROM v_active_loans WHERE due_on < ? ORDER BY days_late DESC''',
            (today, today)).fetchall()

    def popular_books(self, limit: int = 3) -> list[sqlite3.Row]:
        return self.db.conn.execute(
            'SELECT title, author, times_borrowed FROM v_book_popularity '
            'ORDER BY times_borrowed DESC, title LIMIT ?', (limit,)).fetchall()


# ---------- demo + CLI ----------
def run_demo(db_path: str = 'library.db'):
    Path(db_path).unlink(missing_ok=True)
    svc = LibraryService(Database(db_path))
    b1 = svc.add_book('Clean Code', 'Robert Martin', 2008, '9780132350884', 2)
    b2 = svc.add_book('The Pragmatic Programmer', 'Andrew Hunt', 1999, '9780201616224', 1)
    b3 = svc.add_book('Fluent Python', 'Luciano Ramalho', 2015, '9781491946008', 1)
    asha = svc.register_member('Asha Rao', 'asha@example.com')
    ravi = svc.register_member('Ravi Kumar', 'ravi@example.com')

    start = date.today() - timedelta(days=30)        # borrowed 30 days ago -> overdue
    l1 = svc.borrow_book(b1, asha, today=start)
    svc.borrow_book(b2, ravi)

    try:                                              # only 1 copy exists
        svc.borrow_book(b2, asha)
    except BookUnavailable as e:
        logger.warning('Expected error: %s', e)

    print('\nOverdue loans:')
    for r in svc.overdue_loans():
        print(f'  loan {r["loan_id"]}: {r["title"]} / {r["member"]} / {r["days_late"]} days late')

    svc.return_book(l1)                               # late return -> fine created
    print('\nMost borrowed books:')
    for r in svc.popular_books():
        print(f'  {r["title"]} by {r["author"]}: {r["times_borrowed"]} loans')


def main():
    parser = argparse.ArgumentParser(description='Library Management System')
    parser.add_argument('command', choices=['demo', 'overdue'])
    parser.add_argument('--db', default='library.db')
    args = parser.parse_args()
    if args.command == 'demo':
        run_demo(args.db)
    else:
        for r in LibraryService(Database(args.db)).overdue_loans():
            print(dict(r))


if __name__ == '__main__':
    main()
