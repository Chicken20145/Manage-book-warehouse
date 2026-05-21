from django.urls import path
from . import views

urlpatterns = [
    path('sach/', views.DanhSachSachView.as_view(), name='danh-sach-sach'),
    path('sach/them/', views.SachCreateView.as_view(), name='them-sach'),
    path('sach/<int:pk>/sua/', views.SachUpdateView.as_view(), name='sua-sach'),   # URL sửa sách
    path('sach/<int:pk>/xoa/', views.SachDeleteView.as_view(), name='xoa-sach'),   # URL xóa sách
]