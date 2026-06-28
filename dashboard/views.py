from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render

from catalog.models import Book
from circulation.models import Borrowing


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
            'Duyệt thay đổi model trước khi chạy migration.',
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
