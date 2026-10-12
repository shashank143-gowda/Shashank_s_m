# Library Management System (Python + SQLite)

A small command-line library system that tracks books, members, loans and late fines.
Built to demonstrate clean Python design and non-trivial SQLite database design.

## Features

- Add books (with authors and multiple copies) and register members
- Borrow and return books with business rules:
  - a book cannot be borrowed when no copy is available
  - a member can have at most 3 active loans
  - loans are due after 14 days
- Late returns automatically create a fine (2.00 per late day)
- Reports: overdue loans and most borrowed books
- Unit tests covering the main rules

## Project structure

| File | Purpose |
|---|---|
| `library.py` | Python application: database wrapper, business logic, CLI and demo |
| `schema.sql` | Database schema: tables, constraints, indexes, triggers and views |
| `queries.sql` | Analytical SQL queries (CTE, window functions, joins, aggregation) |
| `test_library.py` | Unit tests (`unittest`) |

## Requirements

- Python 3.10 or newer (uses `X | None` type hints)
- No third-party packages. SQLite is included with Python.

## How to run

```bash
# 1. Run the tests
python test_library.py

# 2. Run the demo (creates library.db with sample data and prints reports)
python library.py demo

# 3. List overdue loans from an existing database
python library.py overdue --db library.db
```

Expected demo output (dates vary):

```
Overdue loans:
  loan 1: Clean Code / Asha Rao / 16 days late

Most borrowed books:
  Clean Code by Robert Martin: 1 loans
  The Pragmatic Programmer by Andrew Hunt: 1 loans
  Fluent Python by Luciano Ramalho: 0 loans
```

To run the analytical queries, open `library.db` in any SQLite client
(for example DB Browser for SQLite, or `sqlite3 library.db < queries.sql`).

## Database design

Five tables with foreign keys:

```
authors 1---* books 1---* loans *---1 members
                           |
                           1
                           |
                          0..1 fines
```

Key design decisions:

- **Constraints in the database, not only in Python.** `CHECK` constraints keep
  `available_copies` between 0 and `total_copies`, so invalid data is rejected
  even if the application has a bug.
- **Triggers keep stock and fines consistent.**
  `trg_loan_created` reduces available copies when a loan is inserted.
  `trg_loan_returned` restores the copy and creates a fine if the book is late.
- **Views** (`v_active_loans`, `v_book_popularity`) simplify reporting queries.
- **Indexes** on foreign keys, plus a partial index on active loans, speed up common lookups.
- **Parameterised queries (`?`)** everywhere to prevent SQL injection.
- **Transactions**: each operation runs inside a context manager that commits on
  success and rolls back on any error.

## Assumptions

- Fine rate and loan length are constants at the top of `library.py` and can be changed.
- Dates are stored as ISO text (`YYYY-MM-DD`), which SQLite date functions understand.
- This is a single-user local application, so concurrency is not handled.

## Possible improvements

- Reservation queue for books with no available copies
- Fine payment workflow and a REST API (for example with FastAPI)
- Migration to PostgreSQL for multi-user use

## References

- Python `sqlite3`: https://docs.python.org/3/library/sqlite3.html
- Python `contextlib`: https://docs.python.org/3/library/contextlib.html
- Python `unittest`: https://docs.python.org/3/library/unittest.html
- SQLite foreign keys: https://www.sqlite.org/foreignkeys.html
- SQLite triggers: https://www.sqlite.org/lang_createtrigger.html
- SQLite window functions: https://www.sqlite.org/windowfunctions.html
- SQLite date functions: https://www.sqlite.org/lang_datefunc.html

## Author

Shashank S M | shashanksmv511Agmail.com | GitHub: shashank143-gowda
