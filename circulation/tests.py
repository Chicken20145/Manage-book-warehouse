from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Book
from circulation.models import BorrowedItem, Borrowing


User = get_user_model()


class CirculationFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin01',
            password='pass12345',
            role='ADMIN',
        )
        self.librarian = User.objects.create_user(
            username='lib01',
            password='pass12345',
            role='LIBRARIAN',
        )
        self.student = User.objects.create_user(
            username='student01',
            password='pass12345',
            role='STUDENT',
        )
        self.book = Book.objects.create(
            code='BK-001',
            title='Django for Beginners',
            author='Someone',
            total_copies=3,
            available_copies=3,
        )

    def test_admin_can_create_borrowing_and_decrease_stock(self):
        self.client.force_login(self.admin)
        payload = {
            'user': self.student.pk,
            'borrow_date': date.today().isoformat(),
            'due_date': (date.today() + timedelta(days=14)).isoformat(),
            'notes': 'Test borrow',
            'books': [self.book.pk],
        }
        response = self.client.post(reverse('borrow-create'), payload)

        self.assertRedirects(response, reverse('loan-list'))
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)
        borrowing = Borrowing.objects.get(user=self.student)
        self.assertEqual(borrowing.status, Borrowing.Status.BORROWED)
        self.assertEqual(borrowing.confirmed_by, self.admin)
        self.assertEqual(borrowing.items.count(), 1)
        self.assertEqual(BorrowedItem.objects.get(borrowing=borrowing).book, self.book)

    def test_student_cannot_create_borrowing(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse('borrow-create'), {
            'user': self.student.pk,
            'borrow_date': date.today().isoformat(),
            'due_date': (date.today() + timedelta(days=14)).isoformat(),
            'notes': 'Not allowed',
            'books': [self.book.pk],
        })

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Borrowing.objects.exists())

    def test_librarian_can_confirm_return_and_restore_stock(self):
        borrowing = Borrowing.objects.create(
            user=self.student,
            borrow_date=date.today() - timedelta(days=10),
            due_date=date.today() + timedelta(days=4),
            status=Borrowing.Status.BORROWED,
            confirmed_by=self.admin,
        )
        BorrowedItem.objects.create(borrowing=borrowing, book=self.book, quantity=1)
        self.book.available_copies = 2
        self.book.save(update_fields=['available_copies', 'updated_at'])

        self.client.force_login(self.librarian)
        response = self.client.post(
            reverse('return-confirm', args=[borrowing.pk]),
            {'returned_date': date.today().isoformat()},
        )

        self.assertRedirects(response, reverse('loan-list'))
        borrowing.refresh_from_db()
        self.book.refresh_from_db()
        self.assertEqual(borrowing.status, Borrowing.Status.RETURNED)
        self.assertEqual(borrowing.confirmed_by, self.librarian)
        self.assertEqual(self.book.available_copies, 3)
        self.assertTrue(borrowing.items.first().is_returned)

    def test_student_cannot_confirm_return(self):
        borrowing = Borrowing.objects.create(
            user=self.student,
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=14),
            status=Borrowing.Status.BORROWED,
        )
        self.client.force_login(self.student)
        response = self.client.post(reverse('return-confirm', args=[borrowing.pk]), {'returned_date': date.today().isoformat()})

        self.assertEqual(response.status_code, 403)

    def test_overdue_status_is_marked_on_list_view(self):
        borrowing = Borrowing.objects.create(
            user=self.student,
            borrow_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6),
            status=Borrowing.Status.BORROWED,
        )
        self.client.force_login(self.student)
        response = self.client.get(reverse('loan-list'))

        self.assertEqual(response.status_code, 200)
        borrowing.refresh_from_db()
        self.assertEqual(borrowing.status, Borrowing.Status.OVERDUE)

    def test_confirm_borrowing_does_not_reopen_returned_loan(self):
        borrowing = Borrowing.objects.create(
            user=self.student,
            borrow_date=date.today() - timedelta(days=5),
            due_date=date.today() + timedelta(days=9),
            returned_date=date.today(),
            status=Borrowing.Status.RETURNED,
            confirmed_by=self.admin,
        )

        self.client.force_login(self.librarian)
        response = self.client.post(reverse('borrow-confirm', args=[borrowing.pk]))

        self.assertRedirects(response, reverse('loan-list'))
        borrowing.refresh_from_db()
        self.assertEqual(borrowing.status, Borrowing.Status.RETURNED)
        self.assertEqual(borrowing.confirmed_by, self.admin)

    def test_return_button_is_hidden_for_returned_loan(self):
        Borrowing.objects.create(
            user=self.student,
            borrow_date=date.today() - timedelta(days=5),
            due_date=date.today() + timedelta(days=9),
            returned_date=date.today(),
            status=Borrowing.Status.RETURNED,
            confirmed_by=self.admin,
        )

        self.client.force_login(self.librarian)
        response = self.client.get(reverse('loan-list'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Xác nhận trả')

    def test_inactive_books_are_not_available_for_new_borrowing(self):
        self.book.is_active = False
        self.book.save(update_fields=['is_active'])

        self.client.force_login(self.librarian)
        response = self.client.get(reverse('loan-list'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.book.title)

    def test_student_does_not_see_fine_payment_action(self):
        borrowing = Borrowing.objects.create(
            user=self.student,
            borrow_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6),
            status=Borrowing.Status.OVERDUE,
            fine=30000,
            is_fine_paid=False,
        )

        self.client.force_login(self.student)
        response = self.client.get(reverse('loan-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chưa thanh toán')
        self.assertNotContains(response, reverse('fine-confirm', args=[borrowing.pk]))
        self.assertNotContains(response, 'Ghi nhận thu phạt')

    def test_librarian_sees_fine_payment_action(self):
        borrowing = Borrowing.objects.create(
            user=self.student,
            borrow_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6),
            status=Borrowing.Status.OVERDUE,
            fine=30000,
            is_fine_paid=False,
        )

        self.client.force_login(self.librarian)
        response = self.client.get(reverse('loan-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('fine-confirm', args=[borrowing.pk]))
        self.assertContains(response, 'Ghi nhận thu phạt')
