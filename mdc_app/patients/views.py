# patients/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin 
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
import logging
from django.forms.models import model_to_dict
from django.db.models import Q
from django.utils import timezone
import pytz
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count
from transactions.models import Transaction, TransactionTest

logger = logging.getLogger('mdc_app')

@method_decorator(login_required, name='dispatch')
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'patients/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # 1. Compute “today” in Manila
        manila_tz = pytz.timezone('Asia/Manila')
        today = timezone.now().astimezone(manila_tz).date()

        # 2. All transactions for today
        todays = Transaction.objects.filter(transaction_date=today)

        # a) How many
        ctx['daily_count'] = todays.count()

        # b) Total of transaction_total
        ctx['daily_total'] = todays.aggregate(total=Sum('transaction_total'))['total'] or 0

        # c) Total of discounted_total
        ctx['daily_discounted_total'] = todays.aggregate(total=Sum('discounted_total'))['total'] or 0

        # d) Discounts given = gross – discounted
        ctx['daily_discounts'] = ctx['daily_total'] - ctx['daily_discounted_total']

        # 3. Summary of test counts
        ctx['tests_summary'] = (
            TransactionTest.objects
            .filter(transaction__transaction_date=today)
            .values('test__test_name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return ctx

@method_decorator(login_required, name='dispatch')
class PatientListView(ListView):
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            if q.isdigit():
                # search by numeric ID OR by name
                qs = qs.filter(
                    Q(id=int(q)) |
                    Q(first_name__icontains=q) |
                    Q(last_name__icontains=q)
                )
            else:
                # search only by name
                qs = qs.filter(
                    Q(first_name__icontains=q) |
                    Q(last_name__icontains=q)
                )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # so your template can pre‑fill the search box
        context['q'] = self.request.GET.get('q', '')
        return context

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
            logger.info(
                f"Patient CREATED by user={self.request.user.username!r}: "
                f"Patient already exists with ID {existing_patient.id}, name={self.object.first_name} {self.object.last_name}"
            )
            return self.render_to_response(self.get_context_data(
                form=form,
                existing_patient=existing_patient,
                show_modal=True,
                modal_message=f"Patient already exists with ID {existing_patient.id}"
            ))
        else:
            self.object = form.save()

            logger.info(
                f"Patient CREATED by user={self.request.user.username!r}: "
                f"id={self.object.pk}, name={self.object.first_name} {self.object.last_name}"
            )

            return self.render_to_response(self.get_context_data(
                form=self.get_form_class()(instance=self.object),
                new_patient=self.object,
                show_modal=True,
                modal_message=f"New patient created with ID {self.object.id}"
            ))

@method_decorator(login_required, name='dispatch')
class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patient_list')

    def dispatch(self, request, *args, **kwargs):
        # capture a snapshot of the object *before* any edits
        self._original = model_to_dict(self.get_object())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        changed = form.changed_data  # list of field names that were modified
        
        if changed:
            # build a “field: old → new” string
            diffs = []
            for field in changed:
                old = self._original.get(field)
                new = getattr(self.object, field)
                diffs.append(f"{field!r}: {old!r} → {new!r}")
            
            logger.info(
                f"Patient UPDATED by user={self.request.user.username!r} "
                f"(id={self.object.pk}): " + "; ".join(diffs)
            )
        else:
            # you can still log “no changes” if you like
            logger.info(
                f"Patient UPDATE attempted by user={self.request.user.username!r} "
                f"(id={self.object.pk}) but no fields changed"
            )

        return response

@method_decorator(login_required, name='dispatch')
class PatientDeleteView(DeleteView):
    model = Patient
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patient_list')