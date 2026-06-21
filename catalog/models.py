from django.db import models
from django.utils.text import slugify


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=50, unique=True)
    isbn = models.CharField(max_length=20, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.code:
            base_code = slugify(self.title).upper().replace('-', '')[:20] or 'BOOK'
            self.code = f"{base_code}-{self.pk or ''}".strip('-')
        if self.total_copies < 0:
            self.total_copies = 0
        if isinstance(self.available_copies, int) and self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)

    def borrow_copy(self, quantity=1):
        if self.available_copies < quantity:
            raise ValueError('Không đủ sách trong kho.')
        self.available_copies -= quantity
        self.save(update_fields=['available_copies', 'updated_at'])

    def return_copy(self, quantity=1):
        self.available_copies = min(self.total_copies, self.available_copies + quantity)
        self.save(update_fields=['available_copies', 'updated_at'])

    @property
    def is_available(self):
        return self.available_copies > 0

    def __str__(self):
        return f"{self.code} - {self.title}"
