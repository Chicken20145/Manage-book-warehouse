from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    path('', views.BorrowingListView.as_view(), name='list'),
    path('create/', views.BorrowingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.BorrowingDetailView.as_view(), name='detail'),
    path('<int:pk>/renew/', views.renew_borrowing, name='renew'),
    path('return/<int:item_id>/', views.return_book_item, name='return_item'),
]