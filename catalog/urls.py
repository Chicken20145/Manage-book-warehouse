from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='book-list', permanent=False), name='catalog-home'),

    # Xem danh sách
    path('books/', views.book_list_view, name='book-list'),
    
    # Thêm sách
    path('books/add/', views.book_create_view, name='book-create'),
    
    # Sửa sách (yêu cầu truyền ID - pk vào)
    path('books/<int:pk>/edit/', views.book_update_view, name='book-update'),
    
    # Xóa sách (yêu cầu truyền ID - pk vào)
    path('books/<int:pk>/delete/', views.book_delete_view, name='book-delete'),
]
