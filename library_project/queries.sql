-- queries.sql : analytical queries on the library database

-- 1. Rank books by popularity inside each author (CTE + window function)
WITH popularity AS (
    SELECT author, title, times_borrowed FROM v_book_popularity
)
SELECT author, title, times_borrowed,
       RANK() OVER (PARTITION BY author ORDER BY times_borrowed DESC) AS rank_in_author
FROM popularity
ORDER BY author, rank_in_author;

-- 2. Members who have borrowed 2 or more books (GROUP BY + HAVING)
SELECT m.name, COUNT(*) AS total_loans
FROM loans l JOIN members m ON m.member_id = l.member_id
GROUP BY m.member_id
HAVING COUNT(*) >= 2
ORDER BY total_loans DESC;

-- 3. Unpaid fines per member (multi-table JOIN + aggregate)
SELECT m.name, ROUND(SUM(f.amount), 2) AS unpaid_fines
FROM fines f
JOIN loans   l ON l.loan_id   = f.loan_id
JOIN members m ON m.member_id = l.member_id
WHERE f.paid = 0
GROUP BY m.member_id
ORDER BY unpaid_fines DESC;

-- 4. Books that were never borrowed (anti-join with NOT EXISTS)
SELECT b.title FROM books b
WHERE NOT EXISTS (SELECT 1 FROM loans l WHERE l.book_id = b.book_id);

-- 5. Running count of loans per month (window function)
SELECT strftime('%Y-%m', borrowed_on) AS month,
       COUNT(*) AS loans_in_month,
       SUM(COUNT(*)) OVER (ORDER BY strftime('%Y-%m', borrowed_on)) AS running_total
FROM loans
GROUP BY month;
