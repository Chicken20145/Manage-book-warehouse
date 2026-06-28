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
        self.admin = User.objects.create_user(
            username='admin_catalog',
            password='pass12345',
            role='ADMIN',
        )
        self.book = Book.objects.create(
            code='BK-CAT-001',
            title='Catalog Safety',
            author='Safety Author',
            total_copies=2,
            available_copies=1,
        )

    def test_catalog_root_redirects_student_to_opac(self):
        self.client.force_login(self.student)
        response = self.client.get('/catalog/')

        self.assertRedirects(response, reverse('opac'))

    def test_catalog_root_redirects_librarian_to_book_list(self):
        self.client.force_login(self.librarian)
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
        self.book.refresh_from_db()
        self.assertFalse(self.book.is_active)

    def test_librarian_can_create_book(self):
        self.client.force_login(self.librarian)
        response = self.client.post(reverse('book-create'), {
            'code': 'BK-CAT-002',
            'title': 'Created By Librarian',
            'author': 'Catalog Team',
            'isbn': '978-0-00-000000-2',
            'total_copies': 5,
            'available_copies': 5,
            'is_active': 'on',
        })

        self.assertRedirects(response, reverse('book-list'))
        self.assertTrue(Book.objects.filter(code='BK-CAT-002').exists())

    def test_admin_can_create_book(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('book-create'), {
            'code': 'BK-CAT-003',
            'title': 'Created By Admin',
            'author': 'Admin Team',
            'isbn': '',
            'total_copies': 3,
            'available_copies': 2,
            'is_active': 'on',
        })

        self.assertRedirects(response, reverse('book-list'))
        self.assertTrue(Book.objects.filter(code='BK-CAT-003').exists())

    def test_student_cannot_create_update_or_delete_book(self):
        self.client.force_login(self.student)
        create_response = self.client.post(reverse('book-create'), {
            'code': 'BK-STUDENT',
            'title': 'Student Should Not Create',
            'total_copies': 1,
            'available_copies': 1,
            'is_active': 'on',
        })
        update_response = self.client.post(reverse('book-update', args=[self.book.pk]), {
            'code': self.book.code,
            'title': 'Student Should Not Update',
            'total_copies': 1,
            'available_copies': 1,
            'is_active': 'on',
        })
        delete_response = self.client.post(reverse('book-delete', args=[self.book.pk]))

        self.assertEqual(create_response.status_code, 302)
        self.assertEqual(update_response.status_code, 302)
        self.assertEqual(delete_response.status_code, 302)
        self.assertTrue(create_response['Location'].startswith(reverse('dashboard')))
        self.assertTrue(update_response['Location'].startswith(reverse('dashboard')))
        self.assertTrue(delete_response['Location'].startswith(reverse('dashboard')))
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Catalog Safety')
        self.assertTrue(self.book.is_active)

    def test_librarian_searches_books_by_title_author_or_code(self):
        Book.objects.create(
            code='BK-SEARCH-002',
            title='Algorithms Handbook',
            author='Special Writer',
            total_copies=1,
            available_copies=1,
        )
        self.client.force_login(self.librarian)

        for query in ['Algorithms', 'Special Writer', 'BK-SEARCH-002']:
            response = self.client.get(reverse('book-list'), {'q': query})
            self.assertContains(response, 'Algorithms Handbook')
            self.assertNotContains(response, 'Catalog Safety')

    def test_can_delete_book_without_borrowing_history(self):
        removable = Book.objects.create(
            code='BK-REMOVE',
            title='Removable Book',
            total_copies=1,
            available_copies=1,
        )
        self.client.force_login(self.librarian)
        response = self.client.post(reverse('book-delete', args=[removable.pk]))

        self.assertRedirects(response, reverse('book-list'))
        self.assertFalse(Book.objects.filter(pk=removable.pk).exists())

    def test_student_does_not_see_inactive_books(self):
        self.book.is_active = False
        self.book.save(update_fields=['is_active'])

        self.client.force_login(self.student)
        response = self.client.get(reverse('opac'))

        self.assertNotContains(response, 'Catalog Safety')

    def test_student_book_list_redirects_to_opac(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('book-list'))

        self.assertRedirects(response, reverse('opac'))
