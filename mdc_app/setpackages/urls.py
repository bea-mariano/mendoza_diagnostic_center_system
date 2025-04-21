# setpackages/urls.py
from django.urls import path
from . import views
from .views import (
    SetpackageListView,
    SetpackageDetailView,
    SetpackageCreateView,
    SetpackageUpdateView,
    SetpackageDeleteView,
    get_available_transaction_purposes,
    get_tests_by_transaction_purpose,
    get_package_price,
)


urlpatterns = [
    path('setpackages/list/', views.SetpackageListView.as_view(), name='setpackage_list'),
    path('setpackages/<int:pk>/', views.SetpackageDetailView.as_view(), name='setpackage_detail'),
    path('setpackages/new/', views.SetpackageCreateView.as_view(), name='setpackage_new'),
    path('setpackages/<int:pk>/edit/', views.SetpackageUpdateView.as_view(), name='setpackage_edit'),
    path('setpackages/<int:pk>/delete/', views.SetpackageDeleteView.as_view(), name='setpackage_delete'),
    path('ajax/get-available-transaction-purposes/', get_available_transaction_purposes, name='get_available_transaction_purposes'),
    path('ajax/get-tests-by-purpose/<str:purpose>/', get_tests_by_transaction_purpose, name='get_tests_by_transaction_purpose'),
    path('ajax/get-package-price/', get_package_price, name='get_package_price'),
]