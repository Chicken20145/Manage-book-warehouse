from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('dashboard.urls')),
    path('catalog/', include('catalog.urls')),
    path('circulation/', include('circulation.urls')),
]
