from datetime import date, timedelta

from django.core.management.base import BaseCommand

from accounts.models import CustomUser
from catalog.models import Book
from circulation.models import BorrowedItem, Borrowing


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho module mượn/trả'

    def handle(self, *args, **kwargs):
        lib, _ = CustomUser.objects.get_or_create(
            username='librarian',
            defaults={'role': 'LIBRARIAN', 'is_staff': True},
        )
        lib.set_password('lib123')
        lib.save()

        member, _ = CustomUser.objects.get_or_create(
            username='member01',
            defaults={'role': 'STUDENT'},
        )
        member.set_password('mem123')
        member.save()

        books_data = [
            {'title': 'Django for Beginners', 'available_copies': 3},
            {'title': 'Python Crash Course', 'available_copies': 2},
        ]
        books = []
        for index, book_data in enumerate(books_data, start=1):
            book, _ = Book.objects.get_or_create(
                code=f'BK-{index:03d}',
                defaults={
                    'title': book_data['title'],
                    'available_copies': book_data['available_copies'],
                    'total_copies': book_data['available_copies'],
                },
            )
            books.append(book)

        borrow1 = Borrowing.objects.create(user=member, borrow_date=date.today(), due_date=date.today() + timedelta(days=14))
        for book in books:
            BorrowedItem.objects.create(borrowing=borrow1, book=book)
            book.borrow_copy()

        past_date = date.today() - timedelta(days=20)
        borrow2 = Borrowing.objects.create(user=member, borrow_date=past_date, due_date=past_date + timedelta(days=14))
        BorrowedItem.objects.create(borrowing=borrow2, book=books[0])
        books[0].borrow_copy()

        self.stdout.write(self.style.SUCCESS('Dữ liệu mẫu đã được tạo!'))
