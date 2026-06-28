from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('opac/', views.opac_view, name='opac'),
    path('statistics/', views.statistics_view, name='statistics'),
]
