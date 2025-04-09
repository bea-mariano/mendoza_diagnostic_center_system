# transactions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('transaction/list/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transaction/active_list/', views.TransactionActiveListView.as_view(), name='transaction_active_list'),
    path('transaction/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transaction/new/', views.TransactionCreateView.as_view(), name='transaction_new'),
    path('transaction/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_edit'),
    path('transaction/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
]