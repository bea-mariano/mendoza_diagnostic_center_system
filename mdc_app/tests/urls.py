# tests/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('test/list/', views.TestListView.as_view(), name='test_list'),
    path('test/<int:pk>/', views.TestDetailView.as_view(), name='test_detail'),
    path('test/new/', views.TestCreateView.as_view(), name='test_new'),
    path('test/<int:pk>/edit/', views.TestUpdateView.as_view(), name='test_edit'),
    path('test/<int:pk>/delete/', views.TestDeleteView.as_view(), name='test_delete'),
]