# Python Assignment

Solutions for Problem Statement 1 (Python + SQLite tasks).

| Task | Folder / file | What it does |
|---|---|---|
| 1. API data retrieval and storage | `task1_books_api/books_to_sqlite.py` | Fetches books (title, author, year) from the Open Library REST API, stores them in SQLite, and displays them |
| 2. Data processing and visualization | `task2_student_scores/student_scores.py` | Fetches student scores from an API, calculates the average, and draws a bar chart (`scores_chart.png`) |
| 3. CSV import to a database | `task3_csv_import/csv_to_sqlite.py` | Reads `users.csv` and inserts users into SQLite, skipping duplicate emails |
| 4. Most complex Python code | `library_project/library.py` | Library management system: OOP, custom exceptions, transactions, logging, CLI, unit tests |
| 5. Most complex database code | `library_project/schema.sql` | 5 related tables, constraints, triggers, views, indexes, plus analytical queries in `queries.sql` |

## Requirements

- Python 3.10+
- `pip install requests matplotlib` (Tasks 1 and 2 only; Tasks 3 to 5 use the standard library)

## How to run

```bash
cd task1_books_api       && python books_to_sqlite.py
cd task2_student_scores  && python student_scores.py
cd task3_csv_import      && python csv_to_sqlite.py
cd library_project       && python test_library.py && python library.py demo
```

Run each command from the repository root (use `cd ..` between them).

## Assumptions

- Task 1 uses the free Open Library API (no API key). If the network is unavailable, the script falls back to sample data and says so.
- No specific students API was given for Task 2, so `API_URL` in `student_scores.py` is a placeholder. The script expects JSON like `[{"name": "Asha", "score": 78}]`; change `API_URL`, `NAME_KEY` and `SCORE_KEY` to match your API. Without a reachable API it uses sample data (average 78.20).
- Duplicate records are ignored using `UNIQUE` constraints and `INSERT OR IGNORE`.
- All SQL uses parameterised queries (`?`) to prevent SQL injection.

## Author

Your Name | shashanksmv511@gmail.com | GitHub: shashank143-gowda
