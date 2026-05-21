from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalog.models import Book
from circulation.models import Borrowing, BorrowedItem
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho module mượn/trả'

    def handle(self, *args, **kwargs):
        # Tạo user
        lib, _ = User.objects.get_or_create(username='librarian', is_staff=True)
        lib.set_password('lib123')
        lib.save()
        member, _ = User.objects.get_or_create(username='member01')
        member.set_password('mem123')
        member.save()

        # Tạo sách (nếu chưa có)
        books_data = [
            {'title': 'Django for Beginners', 'available_copies': 3},
            {'title': 'Python Crash Course', 'available_copies': 2},
        ]
        books = []
        for b in books_data:
            book, _ = Book.objects.get_or_create(title=b['title'], defaults={'available_copies': b['available_copies']})
            books.append(book)

        # Tạo phiếu mượn đang mượn
        borrow1 = Borrowing.objects.create(user=member, borrow_date=date.today(), due_date=date.today() + timedelta(days=14))
        for book in books:
            BorrowedItem.objects.create(borrowing=borrow1, book=book)
            book.borrow_copy()

        # Tạo phiếu quá hạn
        past_date = date.today() - timedelta(days=20)
        borrow2 = Borrowing.objects.create(user=member, borrow_date=past_date, due_date=past_date + timedelta(days=14))
        BorrowedItem.objects.create(borrowing=borrow2, book=books[0])
        books[0].borrow_copy()

        self.stdout.write(self.style.SUCCESS('Dữ liệu mẫu đã được tạo!'))