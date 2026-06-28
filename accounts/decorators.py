from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def role_required(*allowed_roles):
    """
    Hàm bọc kiểm tra quyền của người dùng.
    Nhận vào danh sách các role được phép (vd: 'ADMIN', 'LIBRARIAN')
    """
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            # 1. Nếu chưa đăng nhập -> Đẩy về trang Login
            if not request.user.is_authenticated:
                return redirect('login')
                
            # 2. Nếu đã đăng nhập và role nằm trong danh sách cho phép -> Cho đi tiếp
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
                
            # 3. Nếu sai quyền -> Báo lỗi 403 (Hoặc có thể redirect về trang báo lỗi riêng)
            raise PermissionDenied
        return wrap
    return decorator
