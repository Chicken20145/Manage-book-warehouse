from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from circulation.models import BorrowedItem, Borrowing
from .models import Book


User = get_user_model()


class CatalogViewsTests(TestCase):
    def setUp(self):
        self.librarian = User.objects.create_user(
            username='lib_catalog',
            password='pass12345',
            role='LIBRARIAN',
        )
        self.student = User.objects.create_user(
            username='student_catalog',
            password='pass12345',
            role='STUDENT',
        )
        self.book = Book.objects.create(
            code='BK-CAT-001',
            title='Catalog Safety',
            total_copies=2,
            available_copies=1,
        )

    def test_catalog_root_redirects_to_book_list(self):
        self.client.force_login(self.student)
        response = self.client.get('/catalog/')

        self.assertRedirects(response, reverse('book-list'))

    def test_cannot_delete_book_with_borrowing_history(self):
        borrowing = Borrowing.objects.create(
            user=self.student,
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=14),
            status=Borrowing.Status.BORROWED,
        )
        BorrowedItem.objects.create(borrowing=borrowing, book=self.book)

        self.client.force_login(self.librarian)
        response = self.client.post(reverse('book-delete', args=[self.book.pk]))

        self.assertRedirects(response, reverse('book-list'))
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())
