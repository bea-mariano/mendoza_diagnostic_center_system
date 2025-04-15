# companies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('company/list/', views.CompanyListView.as_view(), name='company_list'),
    path('company/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('company/new/', views.CompanyCreateView.as_view(), name='company_new'),
    path('company/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_edit'),
    path('company/<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
]