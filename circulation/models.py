from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Borrowing(models.Model):
    STATUS_CHOICES = [
        ('BORROWED', 'Đang mượn'),
        ('RETURNED', 'Đã trả'),
        ('OVERDUE', 'Quá hạn'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowings')
    borrow_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='BORROWED')
    fine = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_fine_paid = models.BooleanField(default=False)
    extended = models.BooleanField(default=False)  # Đã gia hạn chưa

    def save(self, *args, **kwargs):
        if not self.due_date and self.borrow_date:
            self.due_date = self.borrow_date + timedelta(days=14)
        if not self.returned_date and self.due_date < timezone.now().date():
            self.status = 'OVERDUE'
        super().save(*args, **kwargs)

    def calculate_fine(self):
        if not self.returned_date or self.returned_date <= self.due_date:
            return 0
        late_days = (self.returned_date - self.due_date).days
        return late_days * 1000  # 1000 VND/ngày

    def __str__(self):
        return f"Borrowing #{self.id} - {self.user.username}"

class BorrowedItem(models.Model):
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE)  # giả sử app catalog có model Book
    is_returned = models.BooleanField(default=False)
    returned_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} - {self.borrowing.user.username}"