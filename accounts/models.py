from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('LIBRARIAN', 'Librarian'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    student_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"