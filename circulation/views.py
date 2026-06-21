from django.shortcuts import render


def loan_list_view(request):
    loans = [
        {'student': 'Nguyễn Văn A', 'book': 'Database Design Basics', 'due': '28/06/2026', 'status': 'Đang mượn'},
        {'student': 'Trần Thị B', 'book': 'Clean Python', 'due': '25/06/2026', 'status': 'Sắp đến hạn'},
    ]
    return render(request, 'circulation/loan_list.html', {'loans': loans})
