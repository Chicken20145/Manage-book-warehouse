from django.urls import path

from . import views

urlpatterns = [
    path('', views.loan_list_view, name='loan-list'),
    path('create/', views.create_borrowing_view, name='borrow-create'),
    path('<int:borrowing_id>/confirm-borrow/', views.confirm_borrowing_view, name='borrow-confirm'),
    path('<int:borrowing_id>/confirm-return/', views.confirm_return_view, name='return-confirm'),
    path('<int:borrowing_id>/confirm-fine/', views.confirm_fine_payment_view, name='fine-confirm'),
]
