# patients/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.PatientListView.as_view(), name='patient_list'),
    path('patient/<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('patient/new/', views.PatientCreateView.as_view(), name='patient_new'),
    path('patient/<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_edit'),
    path('patient/<int:pk>/delete/', views.PatientDeleteView.as_view(), name='patient_delete'),
]