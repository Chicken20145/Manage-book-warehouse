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

    my_borrowings = Borrowing.objects.filter(user=request.user)
    my_borrowed_count = my_borrowings.filter(status=Borrowing.Status.BORROWED).count()
    my_overdue_count = my_borrowings.filter(status=Borrowing.Status.OVERDUE).count()
    my_returned_count = my_borrowings.filter(status=Borrowing.Status.RETURNED).count()

    common_library_cards = [
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
    cards_by_role = {
        'ADMIN': common_library_cards,
        'LIBRARIAN': common_library_cards,
        'STUDENT': [
            {
                'label': 'Sách có thể tra cứu',
                'value': active_books.count(),
                'tone': 'primary',
                'note': 'Đầu sách đang mở trong OPAC để bạn tìm kiếm.',
            },
            {
                'label': 'Bản sách sẵn có',
                'value': active_agg['available'] or 0,
                'tone': 'success',
                'note': 'Số bản sách còn có thể mượn tại thư viện.',
            },
            {
                'label': 'Phiếu của tôi',
                'value': my_borrowed_count,
                'tone': 'warning',
                'note': 'Phiếu mượn của bạn đang chờ trả.',
            },
            {
                'label': 'Quá hạn của tôi',
                'value': my_overdue_count,
                'tone': 'danger',
                'note': 'Phiếu cần trả sớm để tránh phát sinh thêm phí.',
            },
        ],
    }
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
    dashboard_meta_by_role = {
        'ADMIN': {
            'title': 'Bảng quản trị hệ thống',
            'intro': 'Theo dõi toàn bộ thư viện: kho sách, phiếu mượn trả, quá hạn, báo cáo và phân quyền tài khoản.',
            'summary_title': 'Tình hình toàn hệ thống',
            'summary_text': f'Có {borrowed_count} phiếu đang mượn, {overdue_count} phiếu quá hạn và {student_count} tài khoản sinh viên trong hệ thống.',
        },
        'LIBRARIAN': {
            'title': 'Bảng làm việc thủ thư',
            'intro': 'Tập trung vào nghiệp vụ hằng ngày: tạo phiếu mượn, xác nhận trả sách, theo dõi quá hạn và cập nhật kho.',
            'summary_title': 'Tình hình mượn trả',
            'summary_text': f'Có {borrowed_count} phiếu đang mượn và {overdue_count} phiếu quá hạn cần theo dõi.',
        },
        'STUDENT': {
            'title': 'Trang cá nhân sinh viên',
            'intro': 'Tra cứu sách trong thư viện, theo dõi phiếu đang mượn của bạn và cập nhật thông tin tài khoản.',
            'summary_title': 'Tình hình mượn sách của tôi',
            'summary_text': f'Bạn có {my_borrowed_count} phiếu đang mượn, {my_overdue_count} phiếu quá hạn và {my_returned_count} phiếu đã trả.',
        },
    }
    dashboard_meta = dashboard_meta_by_role.get(role, dashboard_meta_by_role['STUDENT'])
    context = {
        'role': ROLE_LABELS.get(role, role),
        'role_code': role,
        'cards': cards_by_role.get(role, cards_by_role['STUDENT']),
        'actions': actions_by_role.get(role, actions_by_role['STUDENT']),
        'primary_links': primary_links_by_role.get(role, primary_links_by_role['STUDENT']),
        'dashboard_title': dashboard_meta['title'],
        'dashboard_intro': dashboard_meta['intro'],
        'summary_title': dashboard_meta['summary_title'],
        'summary_text': dashboard_meta['summary_text'],
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
