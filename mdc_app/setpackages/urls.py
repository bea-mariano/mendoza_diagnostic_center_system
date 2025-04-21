# setpackages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('setpackages/list/', views.SetpackageListView.as_view(), name='setpackage_list'),
    path('setpackages/<int:pk>/', views.SetpackageDetailView.as_view(), name='setpackage_detail'),
    path('setpackages/new/', views.SetpackageCreateView.as_view(), name='setpackage_new'),
    path('setpackages/<int:pk>/edit/', views.SetpackageUpdateView.as_view(), name='setpackage_edit'),
    path('setpackages/<int:pk>/delete/', views.SetpackageDeleteView.as_view(), name='setpackage_delete'),
]