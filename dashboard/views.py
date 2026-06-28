from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q
from django.shortcuts import render

from accounts.decorators import role_required
from catalog.models import Book
from circulation.models import Borrowing, BorrowedItem


ROLE_LABELS = {
    'ADMIN': 'Quản trị viên',
    'LIBRARIAN': 'Thủ thư',
    'STUDENT': 'Sinh viên',
}


@login_required
def dashboard_view(request):
    role = getattr(request.user, 'role', 'STUDENT')
    student_count = get_user_model().objects.filter(role='STUDENT').count()
    cards = [
        {
            'label': 'Sách trong kho',
            'value': Book.objects.count(),
            'tone': 'primary',
            'note': 'Tổng số đầu sách đang được quản lý trong kho.',
        },
        {
            'label': 'Đang cho mượn',
            'value': Borrowing.objects.filter(status=Borrowing.Status.BORROWED).count(),
            'tone': 'warning',
            'note': 'Phiếu mượn đang mở và chưa xác nhận trả.',
        },
        {
            'label': 'Sinh viên',
            'value': student_count,
            'tone': 'success',
            'note': 'Tài khoản sinh viên có thể mượn sách trong hệ thống.',
        },
        {
            'label': 'Quá hạn',
            'value': Borrowing.objects.filter(status=Borrowing.Status.OVERDUE).count(),
            'tone': 'danger',
            'note': 'Phiếu cần thủ thư theo dõi và nhắc trả sách.',
        },
    ]
    actions_by_role = {
        'ADMIN': [
            'Kiểm tra tài khoản mới và phân quyền.',
            'Kiểm tra cấu hình hệ thống và quyền truy cập.',
            'Theo dõi trạng thái các phân hệ trong dashboard.',
        ],
        'LIBRARIAN': [
            'Cập nhật danh mục sách và tình trạng tồn kho.',
            'Xác nhận phiếu mượn/trả sách.',
            'Theo dõi sách quá hạn cần nhắc sinh viên.',
        ],
        'STUDENT': [
            'Tìm sách trong kho.',
            'Theo dõi sách đang mượn.',
            'Xem lịch sử mượn/trả của bản thân.',
        ],
    }
    context = {
        'role': ROLE_LABELS.get(role, role),
        'role_code': role,
        'cards': cards,
        'actions': actions_by_role.get(role, actions_by_role['STUDENT']),
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def opac_view(request):
    query = request.GET.get('q', '').strip()
    books = Book.objects.filter(is_active=True)
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(code__icontains=query)
        )
    return render(request, 'dashboard/opac.html', {'books': books, 'query': query})


@role_required('ADMIN', 'LIBRARIAN')
def statistics_view(request):
    # 1. Thống kê phân phối bản sách (Doughnut Chart)
    active_agg = Book.objects.filter(is_active=True).aggregate(
        total=Sum('total_copies'),
        available=Sum('available_copies')
    )
    total_copies = active_agg['total'] or 0
    available_copies = active_agg['available'] or 0
    borrowed_copies = total_copies - available_copies

    inactive_copies = Book.objects.filter(is_active=False).aggregate(total=Sum('total_copies'))['total'] or 0

    # 2. Thống kê xu hướng mượn sách 7 ngày gần đây (Line Chart)
    today = date.today()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    borrowings_by_day = Borrowing.objects.filter(
        borrow_date__range=[today - timedelta(days=6), today]
    ).values('borrow_date').annotate(count=Count('id'))

    day_labels = [d.strftime('%d/%m') for d in last_7_days]
    day_data = [0] * 7
    borrow_map = {b['borrow_date']: b['count'] for b in borrowings_by_day}
    for i, d in enumerate(last_7_days):
        day_data[i] = borrow_map.get(d, 0)

    # 3. Top 5 sách mượn nhiều nhất
    top_books = BorrowedItem.objects.values('book__title', 'book__code')\
        .annotate(borrow_count=Count('id'))\
        .order_by('-borrow_count')[:5]

    # 4. Top 5 sinh viên mượn sách nhiều nhất
    top_renters = Borrowing.objects.values('user__username', 'user__student_id')\
        .annotate(borrow_count=Count('id'))\
        .order_by('-borrow_count')[:5]

    context = {
        'book_stats': {
            'available': available_copies,
            'borrowed': borrowed_copies,
            'inactive': inactive_copies,
        },
        'chart_trend': {
            'labels': day_labels,
            'data': day_data,
        },
        'top_books': top_books,
        'top_renters': top_renters,
    }
    return render(request, 'dashboard/statistics.html', context)
