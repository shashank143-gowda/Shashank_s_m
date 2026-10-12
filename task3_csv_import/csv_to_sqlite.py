"""Task 3: read users from a CSV file and insert them into a SQLite database."""
import csv
import sqlite3

CSV_FILE = 'users.csv'
DB_NAME = 'users.db'


def import_users():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE)''')

        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            rows = [(r['name'].strip(), r['email'].strip().lower())
                    for r in csv.DictReader(f)]

        before = conn.total_changes
        conn.executemany('INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)', rows)
        print(f'Inserted {conn.total_changes - before} of {len(rows)} rows '
              f'(duplicates skipped).')

        print('\nUsers in database:')
        for row in conn.execute('SELECT id, name, email FROM users'):
            print(row)


if __name__ == '__main__':
    import_users()
