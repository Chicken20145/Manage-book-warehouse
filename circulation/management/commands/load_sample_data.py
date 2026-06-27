from datetime import date, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import CustomUser
from catalog.models import Book
from circulation.models import BorrowedItem, Borrowing


BOOKS = [
    {'code': 'BK-001', 'title': 'Django for Beginners', 'author': 'William S. Vincent', 'isbn': '978-1-7354672-0-7', 'total': 6, 'available': 4},
    {'code': 'BK-002', 'title': 'Python Crash Course', 'author': 'Eric Matthes', 'isbn': '978-1-59327-928-8', 'total': 5, 'available': 3},
    {'code': 'BK-003', 'title': 'Clean Code', 'author': 'Robert C. Martin', 'isbn': '978-0-13-235088-4', 'total': 4, 'available': 2},
    {'code': 'BK-004', 'title': 'The Pragmatic Programmer', 'author': 'Andrew Hunt, David Thomas', 'isbn': '978-0-20-161622-4', 'total': 4, 'available': 3},
    {'code': 'BK-005', 'title': 'Database System Concepts', 'author': 'Abraham Silberschatz', 'isbn': '978-0-07-352332-3', 'total': 3, 'available': 2},
    {'code': 'BK-006', 'title': 'Introduction to Algorithms', 'author': 'Thomas H. Cormen', 'isbn': '978-0-26-203384-8', 'total': 3, 'available': 1},
    {'code': 'BK-007', 'title': 'Design Patterns', 'author': 'Erich Gamma', 'isbn': '978-0-20-163361-0', 'total': 3, 'available': 2},
    {'code': 'BK-008', 'title': 'Computer Networking', 'author': 'James F. Kurose', 'isbn': '978-0-13-359414-0', 'total': 4, 'available': 4},
    {'code': 'BK-009', 'title': 'Operating System Concepts', 'author': 'Abraham Silberschatz', 'isbn': '978-1-11-806333-0', 'total': 4, 'available': 3},
    {'code': 'BK-010', 'title': 'Artificial Intelligence', 'author': 'Stuart Russell, Peter Norvig', 'isbn': '978-0-13-461099-3', 'total': 3, 'available': 1},
    {'code': 'BK-011', 'title': 'Learning SQL', 'author': 'Alan Beaulieu', 'isbn': '978-1-49-205761-1', 'total': 5, 'available': 4},
    {'code': 'BK-012', 'title': 'Effective Python', 'author': 'Brett Slatkin', 'isbn': '978-0-13-485398-7', 'total': 4, 'available': 2},
    {'code': 'BK-013', 'title': 'Fluent Python', 'author': 'Luciano Ramalho', 'isbn': '978-1-49-205635-5', 'total': 3, 'available': 1},
    {'code': 'BK-014', 'title': 'Refactoring', 'author': 'Martin Fowler', 'isbn': '978-0-13-475759-9', 'total': 4, 'available': 3},
    {'code': 'BK-015', 'title': 'Web Development with Django', 'author': 'Ben Shaw', 'isbn': '978-1-83-921250-5', 'total': 5, 'available': 5},
    {'code': 'BK-016', 'title': 'Data Structures and Algorithms in Python', 'author': 'Michael T. Goodrich', 'isbn': '978-1-11-829027-9', 'total': 4, 'available': 2},
    {'code': 'BK-017', 'title': 'Head First Design Patterns', 'author': 'Eric Freeman', 'isbn': '978-1-49-207800-5', 'total': 3, 'available': 3},
    {'code': 'BK-018', 'title': "You Don't Know JS Yet", 'author': 'Kyle Simpson', 'isbn': '978-1-09-121009-2', 'total': 4, 'available': 2},
    {'code': 'BK-019', 'title': 'Git Pro', 'author': 'Scott Chacon', 'isbn': '978-1-48-420077-3', 'total': 6, 'available': 5},
    {'code': 'BK-020', 'title': 'Software Engineering', 'author': 'Ian Sommerville', 'isbn': '978-0-13-703515-1', 'total': 4, 'available': 3},
]

USERS = [
    {'username': 'librarian', 'password': 'lib123', 'role': 'LIBRARIAN', 'email': 'librarian@library.local', 'is_staff': True},
    {'username': 'admin_demo', 'password': 'admin123', 'role': 'ADMIN', 'email': 'admin@library.local', 'is_staff': True},
    {'username': 'student01', 'password': 'stu123', 'role': 'STUDENT', 'student_id': 'SV001', 'email': 'student01@library.local'},
    {'username': 'student02', 'password': 'stu123', 'role': 'STUDENT', 'student_id': 'SV002', 'email': 'student02@library.local'},
    {'username': 'student03', 'password': 'stu123', 'role': 'STUDENT', 'student_id': 'SV003', 'email': 'student03@library.local'},
    {'username': 'student04', 'password': 'stu123', 'role': 'STUDENT', 'student_id': 'SV004', 'email': 'student04@library.local'},
    {'username': 'student05', 'password': 'stu123', 'role': 'STUDENT', 'student_id': 'SV005', 'email': 'student05@library.local'},
    {'username': 'student06', 'password': 'stu123', 'role': 'STUDENT', 'student_id': 'SV006', 'email': 'student06@library.local'},
]

BORROWINGS = [
    {'code': 'BR-001', 'student': 'student01', 'book': 'BK-001', 'borrow_date': '2026-06-12', 'due_date': '2026-06-26', 'status': Borrowing.Status.OVERDUE, 'confirmed_by': 'librarian', 'notes': 'Quá hạn, cần nhắc trả sách'},
    {'code': 'BR-002', 'student': 'student02', 'book': 'BK-002', 'borrow_date': '2026-06-20', 'due_date': '2026-07-04', 'status': Borrowing.Status.BORROWED, 'confirmed_by': 'librarian', 'notes': 'Đang mượn'},
    {'code': 'BR-003', 'student': 'student03', 'book': 'BK-003', 'borrow_date': '2026-06-03', 'due_date': '2026-06-17', 'returned_date': '2026-06-15', 'status': Borrowing.Status.RETURNED, 'confirmed_by': 'librarian', 'notes': 'Trả đúng hạn'},
    {'code': 'BR-004', 'student': 'student04', 'book': 'BK-005', 'borrow_date': '2026-06-18', 'due_date': '2026-07-02', 'status': Borrowing.Status.BORROWED, 'confirmed_by': 'librarian', 'notes': 'Mượn phục vụ môn CSDL'},
    {'code': 'BR-005', 'student': 'student05', 'book': 'BK-010', 'borrow_date': '2026-05-30', 'due_date': '2026-06-13', 'status': Borrowing.Status.OVERDUE, 'confirmed_by': 'admin_demo', 'notes': 'Quá hạn 2 tuần'},
    {'code': 'BR-006', 'student': 'student06', 'book': 'BK-014', 'borrow_date': '2026-06-08', 'due_date': '2026-06-22', 'returned_date': '2026-06-21', 'status': Borrowing.Status.RETURNED, 'confirmed_by': 'admin_demo', 'notes': 'Đã trả'},
    {'code': 'BR-007', 'student': 'student01', 'book': 'BK-012', 'borrow_date': '2026-06-24', 'due_date': '2026-07-08', 'status': Borrowing.Status.BORROWED, 'confirmed_by': 'librarian', 'notes': 'Mượn thêm Python'},
    {'code': 'BR-008', 'student': 'student02', 'book': 'BK-016', 'borrow_date': '2026-06-10', 'due_date': '2026-06-24', 'status': Borrowing.Status.OVERDUE, 'confirmed_by': 'librarian', 'notes': 'Quá hạn nhẹ'},
    {'code': 'BR-009', 'student': 'student03', 'book': 'BK-019', 'borrow_date': '2026-06-26', 'due_date': '2026-07-10', 'status': Borrowing.Status.BORROWED, 'confirmed_by': 'admin_demo', 'notes': 'Mượn Git Pro'},
    {'code': 'BR-010', 'student': 'student04', 'book': 'BK-008', 'borrow_date': '2026-06-01', 'due_date': '2026-06-15', 'returned_date': '2026-06-16', 'status': Borrowing.Status.RETURNED, 'confirmed_by': 'librarian', 'notes': 'Trả muộn 1 ngày'},
]


def parse_day(value):
    return date.fromisoformat(value) if value else None


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu phong phú cho danh mục sách và module mượn/trả'

    def handle(self, *args, **kwargs):
        Borrowing.objects.filter(notes__startswith='[sample:').delete()

        users = {}
        for data in USERS:
            user, _ = CustomUser.objects.get_or_create(username=data['username'])
            user.role = data['role']
            user.email = data.get('email', '')
            user.student_id = data.get('student_id')
            user.is_staff = data.get('is_staff', False)
            user.set_password(data['password'])
            user.save()
            users[user.username] = user

        books = {}
        for data in BOOKS:
            book, _ = Book.objects.get_or_create(code=data['code'])
            book.title = data['title']
            book.author = data['author']
            book.isbn = data['isbn']
            book.total_copies = data['total']
            book.available_copies = data['available']
            book.save()
            books[book.code] = book

        for data in BORROWINGS:
            borrowing = Borrowing.objects.create(
                user=users[data['student']],
                borrow_date=parse_day(data['borrow_date']),
                due_date=parse_day(data['due_date']),
                returned_date=parse_day(data.get('returned_date')),
                status=data['status'],
                confirmed_by=users[data['confirmed_by']],
                confirmed_at=timezone.make_aware(datetime.combine(parse_day(data['borrow_date']), datetime.min.time())),
                notes=f"[sample:{data['code']}] {data['notes']}",
            )
            borrowing.fine = Decimal(borrowing.calculate_fine())
            borrowing.save(update_fields=['fine', 'updated_at'])
            BorrowedItem.objects.create(
                borrowing=borrowing,
                book=books[data['book']],
                quantity=1,
                is_returned=data['status'] == Borrowing.Status.RETURNED,
                returned_date=parse_day(data.get('returned_date')),
            )

        self.stdout.write(self.style.SUCCESS(
            f"Created {len(BOOKS)} books, {len(USERS)} demo users and {len(BORROWINGS)} sample borrowings."
        ))
