# patients/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Patient
from .forms import PatientForm
from transactions.models import Transaction
from transactions.forms import TransactionForm
from tests.models import Test
from tests.forms import TestForm
from companies.models import Company
from companies.forms import CompanyForm

@method_decorator(login_required, name='dispatch')
class HomeView(ListView):
    model = Patient
    template_name = 'patients/home.html'
    context_object_name = 'patients'

@method_decorator(login_required, name='dispatch')
class PatientListView(ListView):
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    ordering = ['-created_at']

@method_decorator(login_required, name='dispatch')
class PatientDetailView(DetailView):
    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object
        context['transactions'] = Transaction.objects.filter(patient=patient)
        return context

@method_decorator(login_required, name='dispatch')
class PatientCreateView(CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'

    def form_valid(self, form):
        data = form.cleaned_data
        existing_patient = Patient.objects.filter(
            first_name__iexact=data['first_name'],
            last_name__iexact=data['last_name'],
            middle_name__iexact=data['middle_name'],
            gender=data['gender'],
            date_of_birth=data['date_of_birth'],
        ).first()

        if existing_patient:
            # Pass this info to template context
            return self.render_to_response(self.get_context_data(
                form=form,
                existing_patient=existing_patient,
                show_modal=True,
                modal_message=f"Patient already exists with ID {existing_patient.id}"
            ))
        else:
            self.object = form.save()
            return self.render_to_response(self.get_context_data(
                form=self.get_form_class()(instance=self.object),
                new_patient=self.object,
                show_modal=True,
                modal_message=f"New patient created with ID {self.object.id}"
            ))

@method_decorator(login_required, name='dispatch')
class PatientUpdateView(UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patient_list')

@method_decorator(login_required, name='dispatch')
class PatientDeleteView(DeleteView):
    model = Patient
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patient_list')