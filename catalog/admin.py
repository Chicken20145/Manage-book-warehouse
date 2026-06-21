from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'author', 'total_copies', 'available_copies')
    search_fields = ('title', 'code', 'author', 'isbn')
    list_filter = ('created_at',)
