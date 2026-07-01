from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Borrowing(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Chờ duyệt'
        BORROWED = 'BORROWED', 'Đang mượn'
        RETURNED = 'RETURNED', 'Đã trả'
        OVERDUE = 'OVERDUE', 'Quá hạn'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrowings')
    borrow_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BORROWED)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_fine_paid = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_borrowings',
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.due_date and self.borrow_date:
            self.due_date = self.borrow_date + timedelta(days=14)
        if self.status == self.Status.BORROWED and self.returned_date:
            self.status = self.Status.RETURNED
        elif self.status == self.Status.BORROWED and self.due_date and self.due_date < timezone.localdate() and not self.returned_date:
            self.status = self.Status.OVERDUE
        super().save(*args, **kwargs)

    def calculate_fine(self):
        end_date = self.returned_date or timezone.localdate()
        if end_date <= self.due_date:
            return 0
        late_days = (end_date - self.due_date).days
        return late_days * 1000

    @property
    def current_fine(self):
        if self.status == self.Status.RETURNED:
            return self.fine
        return self.calculate_fine()

    @property
    def is_overdue(self):
        return self.status == self.Status.OVERDUE

    def __str__(self):
        return f"Borrowing #{self.id} - {self.user}"


class BorrowedItem(models.Model):
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='borrowed_items')
    quantity = models.PositiveIntegerField(default=1)
    is_returned = models.BooleanField(default=False)
    returned_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('borrowing', 'book')

    def __str__(self):
        return f"{self.book.title} - {self.borrowing.user}"
