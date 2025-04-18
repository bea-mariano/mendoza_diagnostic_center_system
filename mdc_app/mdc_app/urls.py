# mdc_app/urls.py
"""
URL configuration for mdc_app project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('patients/', include('patients.urls')),
    path('transactions/', include('transactions.urls')),
    path('', include('patients.urls')),  # Redirect root to patients app
]