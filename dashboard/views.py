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
    active_books = Book.objects.filter(is_active=True)
    active_agg = active_books.aggregate(
        total=Sum('total_copies'),
        available=Sum('available_copies'),
    )
    borrowed_count = Borrowing.objects.filter(status=Borrowing.Status.BORROWED).count()
    overdue_count = Borrowing.objects.filter(status=Borrowing.Status.OVERDUE).count()
    cards = [
        {
            'label': 'Đầu sách hoạt động',
            'value': active_books.count(),
            'tone': 'primary',
            'note': 'Đầu sách đang được hiển thị và phục vụ mượn trả.',
        },
        {
            'label': 'Bản sách sẵn có',
            'value': active_agg['available'] or 0,
            'tone': 'success',
            'note': f"Tổng số bản có thể cho mượn trên {active_agg['total'] or 0} bản.",
        },
        {
            'label': 'Phiếu đang mượn',
            'value': borrowed_count,
            'tone': 'warning',
            'note': 'Phiếu đang mở và chưa được xác nhận trả.',
        },
        {
            'label': 'Quá hạn',
            'value': overdue_count,
            'tone': 'danger',
            'note': 'Phiếu cần thủ thư theo dõi và nhắc trả sách.',
        },
    ]
    actions_by_role = {
        'ADMIN': [
            'Rà soát tài khoản và phân quyền người dùng.',
            'Kiểm tra phiếu quá hạn và tình trạng bản sách.',
            'Xem báo cáo thống kê trước khi bàn giao dữ liệu.',
        ],
        'LIBRARIAN': [
            'Tạo phiếu mượn cho sinh viên tại quầy.',
            'Xác nhận trả sách và ghi nhận tiền phạt nếu có.',
            'Cập nhật số lượng sách còn khả dụng trong kho.',
        ],
        'STUDENT': [
            'Tra cứu sách còn trong kho trước khi mượn.',
            'Theo dõi phiếu đang mượn và hạn trả.',
            'Cập nhật thông tin tài khoản khi cần.',
        ],
    }
    primary_links_by_role = {
        'ADMIN': [
            {'label': 'Quản trị tài khoản', 'url_name': 'admin-panel', 'style': 'btn-brand'},
            {'label': 'Báo cáo thống kê', 'url_name': 'statistics', 'style': 'btn-outline-secondary'},
            {'label': 'Mượn trả', 'url_name': 'loan-list', 'style': 'btn-outline-secondary'},
        ],
        'LIBRARIAN': [
            {'label': 'Tạo phiếu mượn', 'url_name': 'loan-list', 'style': 'btn-brand'},
            {'label': 'Danh mục sách', 'url_name': 'book-list', 'style': 'btn-outline-secondary'},
            {'label': 'Thống kê', 'url_name': 'statistics', 'style': 'btn-outline-secondary'},
        ],
        'STUDENT': [
            {'label': 'Tra cứu sách', 'url_name': 'opac', 'style': 'btn-brand'},
            {'label': 'Phiếu của tôi', 'url_name': 'loan-list', 'style': 'btn-outline-secondary'},
            {'label': 'Cài đặt tài khoản', 'url_name': 'account-settings', 'style': 'btn-outline-secondary'},
        ],
    }
    context = {
        'role': ROLE_LABELS.get(role, role),
        'role_code': role,
        'cards': cards,
        'actions': actions_by_role.get(role, actions_by_role['STUDENT']),
        'primary_links': primary_links_by_role.get(role, primary_links_by_role['STUDENT']),
        'student_count': student_count,
        'borrowed_count': borrowed_count,
        'overdue_count': overdue_count,
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
