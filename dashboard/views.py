from django.contrib.auth.decorators import login_required
from django.shortcuts import render


ROLE_LABELS = {
    'ADMIN': 'Quản trị viên',
    'LIBRARIAN': 'Thủ thư',
    'STUDENT': 'Sinh viên',
}


@login_required
def dashboard_view(request):
    role = getattr(request.user, 'role', 'STUDENT')
    cards = [
        {
            'label': 'Sach trong kho',
            'value': '1,250',
            'tone': 'primary',
            'note': 'Catalog sẽ thay số liệu thật sau khi hoàn thành model Book.',
        },
        {
            'label': 'Đang cho mượn',
            'value': '45',
            'tone': 'warning',
            'note': 'Circulation sẽ cập nhật theo phiếu mượn/trả.',
        },
        {
            'label': 'Người dùng',
            'value': '320',
            'tone': 'success',
            'note': 'Admin theo dõi tài khoản và phân quyền.',
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
