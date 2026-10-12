-- schema.sql : Library Management System (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS books (
    book_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    author_id        INTEGER NOT NULL REFERENCES authors(author_id) ON DELETE RESTRICT,
    publication_year INTEGER CHECK (publication_year BETWEEN 1000 AND 2100),
    isbn             TEXT UNIQUE,
    total_copies     INTEGER NOT NULL DEFAULT 1 CHECK (total_copies >= 0),
    available_copies INTEGER NOT NULL DEFAULT 1 CHECK (available_copies >= 0),
    CHECK (available_copies <= total_copies)
);

CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE,
    joined_on DATE NOT NULL DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id     INTEGER NOT NULL REFERENCES books(book_id),
    member_id   INTEGER NOT NULL REFERENCES members(member_id),
    borrowed_on DATE NOT NULL DEFAULT (date('now')),
    due_on      DATE NOT NULL,
    returned_on DATE,
    CHECK (due_on >= borrowed_on)
);

CREATE TABLE IF NOT EXISTS fines (
    fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL UNIQUE REFERENCES loans(loan_id),
    amount  REAL NOT NULL CHECK (amount > 0),
    paid    INTEGER NOT NULL DEFAULT 0 CHECK (paid IN (0, 1))
);

-- Indexes for the most common lookups
CREATE INDEX IF NOT EXISTS idx_books_author   ON books(author_id);
CREATE INDEX IF NOT EXISTS idx_loans_member   ON loans(member_id);
CREATE INDEX IF NOT EXISTS idx_loans_book     ON loans(book_id);
CREATE INDEX IF NOT EXISTS idx_loans_active   ON loans(due_on) WHERE returned_on IS NULL;

-- Trigger 1: borrowing a book reduces available copies.
-- The CHECK (available_copies >= 0) makes the insert fail if no copy is left.
CREATE TRIGGER IF NOT EXISTS trg_loan_created
AFTER INSERT ON loans
BEGIN
    UPDATE books SET available_copies = available_copies - 1
    WHERE book_id = NEW.book_id;
END;

-- Trigger 2: returning a book restores the copy and creates a fine
-- (2.00 per late day) when it is returned after the due date.
CREATE TRIGGER IF NOT EXISTS trg_loan_returned
AFTER UPDATE OF returned_on ON loans
WHEN OLD.returned_on IS NULL AND NEW.returned_on IS NOT NULL
BEGIN
    UPDATE books SET available_copies = available_copies + 1
    WHERE book_id = NEW.book_id;

    INSERT INTO fines (loan_id, amount)
    SELECT NEW.loan_id,
           (julianday(NEW.returned_on) - julianday(NEW.due_on)) * 2.0
    WHERE NEW.returned_on > NEW.due_on;
END;

-- View: every book currently out on loan
CREATE VIEW IF NOT EXISTS v_active_loans AS
SELECT l.loan_id, b.title, m.name AS member, l.borrowed_on, l.due_on
FROM loans l
JOIN books   b ON b.book_id   = l.book_id
JOIN members m ON m.member_id = l.member_id
WHERE l.returned_on IS NULL;

-- View: how often each book has been borrowed
CREATE VIEW IF NOT EXISTS v_book_popularity AS
SELECT b.book_id, b.title, a.name AS author, COUNT(l.loan_id) AS times_borrowed
FROM books b
JOIN authors a      ON a.author_id = b.author_id
LEFT JOIN loans l   ON l.book_id   = b.book_id
GROUP BY b.book_id;
