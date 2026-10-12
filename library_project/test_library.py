import unittest
from datetime import date, timedelta
from library import (Database, LibraryService, BookUnavailable,
                      LoanLimitReached, NotFound)


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.svc = LibraryService(Database(':memory:'))
        self.book = self.svc.add_book('Test Book', 'Some Author', 2020, copies=1)
        self.member = self.svc.register_member('Tester', 'T@Example.com')

    def stock(self, book_id):
        return self.svc.db.conn.execute(
            'SELECT available_copies FROM books WHERE book_id=?', (book_id,)).fetchone()[0]

    def test_borrow_reduces_stock(self):
        self.svc.borrow_book(self.book, self.member)
        self.assertEqual(self.stock(self.book), 0)

    def test_no_copy_left(self):
        self.svc.borrow_book(self.book, self.member)
        with self.assertRaises(BookUnavailable):
            self.svc.borrow_book(self.book, self.member)

    def test_unknown_member(self):
        with self.assertRaises(NotFound):
            self.svc.borrow_book(self.book, 999)

    def test_loan_limit(self):
        for i in range(3):
            b = self.svc.add_book(f'Book {i}', 'Author', 2000)
            self.svc.borrow_book(b, self.member)
        extra = self.svc.add_book('Extra', 'Author', 2001)
        with self.assertRaises(LoanLimitReached):
            self.svc.borrow_book(extra, self.member)

    def test_on_time_return_has_no_fine(self):
        loan = self.svc.borrow_book(self.book, self.member)
        self.assertEqual(self.svc.return_book(loan), 0.0)
        self.assertEqual(self.stock(self.book), 1)

    def test_late_return_creates_fine(self):
        loan = self.svc.borrow_book(self.book, self.member,
                                    today=date.today() - timedelta(days=20))
        # due after 14 days, returned on day 20 -> 6 days late * 2.0
        self.assertEqual(self.svc.return_book(loan), 12.0)


if __name__ == '__main__':
    unittest.main()
