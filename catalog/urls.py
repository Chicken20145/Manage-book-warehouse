from django.urls import path

from . import views

urlpatterns = [
    path('', views.book_list_view, name='book-list'),
]
