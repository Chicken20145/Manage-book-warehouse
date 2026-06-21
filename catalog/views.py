from django.shortcuts import render

from .models import Book


def book_list_view(request):
    books = Book.objects.all()
    return render(request, 'catalog/book_list.html', {'books': books})
