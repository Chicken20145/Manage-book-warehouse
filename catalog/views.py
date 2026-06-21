from django.shortcuts import render


def book_list_view(request):
    books = [
        {'title': 'Django for Library Systems', 'code': 'BK-001', 'status': 'Còn sách'},
        {'title': 'Database Design Basics', 'code': 'BK-002', 'status': 'Đang mượn'},
        {'title': 'Clean Python', 'code': 'BK-003', 'status': 'Còn sách'},
    ]
    return render(request, 'catalog/book_list.html', {'books': books})
