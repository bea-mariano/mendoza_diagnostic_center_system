from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Transaction, TransactionTest  # 👈 Import TransactionTest
from .forms import TransactionForm
from companies.models import Company
from django.http import JsonResponse
from django.db.models import Q
from setpackages.models import Setpackage



@method_decorator(login_required, name='dispatch')
class TransactionListView(ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    ordering = ['-transaction_date', '-transaction_time']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            if q.isdigit():
                # search by Txn ID, or by Patient ID or name
                qs = qs.filter(
                    Q(id=int(q)) |
                    Q(patient__id=int(q)) |
                    Q(patient__first_name__icontains=q) |
                    Q(patient__last_name__icontains=q)
                )
            else:
                # search only by patient name
                qs = qs.filter(
                    Q(patient__first_name__icontains=q) |
                    Q(patient__last_name__icontains=q)
                )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx

@method_decorator(login_required, name='dispatch')
class TransactionActiveListView(ListView):
    model = Transaction
    template_name = 'transactions/transaction_active_list.html'
    context_object_name = 'transactions'
    ordering = ['-transaction_date', '-transaction_time']

    def get_queryset(self):
        return Transaction.objects.ongoing()

@method_decorator(login_required, name='dispatch')
class TransactionDetailView(DetailView):
    model = Transaction
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        context['tests'] = self.object.transaction_tests.all()  # 👈 Add test details
        return context

class TransactionCreateView(CreateView):
    model         = Transaction
    form_class    = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url   = reverse_lazy('transaction_list')

    def form_valid(self, form):
        # 1. Build but don’t save yet
        self.object = form.save(commit=False)

        # 2. Ensure transaction_purpose is taken from POST (or cleaned_data)
        tp = self.request.POST.get('transaction_purpose') \
             or form.cleaned_data.get('transaction_purpose')
        self.object.transaction_purpose = tp.strip() if tp else None

        # 3. Lookup the matching Setpackage
        if self.object.company_id and self.object.transaction_purpose:
            pkg = Setpackage.objects.filter(
                company=self.object.company,
                package_transaction_purpose__iexact=self.object.transaction_purpose
            ).first()
        else:
            pkg = None
        self.object.setpackage = pkg

        # 4. Set your defaults
        self.object.transaction_status = 'Ongoing'
        if not self.object.payment_type:
            self.object.payment_type = 'Cash'

        # 5. Save the instance and m2m
        self.object.save()
        form.save_m2m()

        # 6. Create the TransactionTest rows
        selected_tests = form.cleaned_data.get('tests', [])
        for test in selected_tests:
            TransactionTest.objects.create(
                transaction=self.object,
                test=test,
                test_price=test.test_price
            )

        # 7. Finally redirect
        return redirect(self.success_url)

class TransactionUpdateView(UpdateView):
    model         = Transaction
    form_class    = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url   = reverse_lazy('transaction_list')

    def form_valid(self, form):
        # build but don’t save
        transaction = form.save(commit=False)

        # re-bind purpose
        tp = self.request.POST.get('transaction_purpose') \
             or form.cleaned_data.get('transaction_purpose')
        transaction.transaction_purpose = tp.strip() if tp else None

        # re-lookup package
        if transaction.company_id and transaction.transaction_purpose:
            pkg = Setpackage.objects.filter(
                company=transaction.company,
                package_transaction_purpose__iexact=transaction.transaction_purpose
            ).first()
        else:
            pkg = None
        transaction.setpackage = pkg

        # default values
        transaction.transaction_status = form.cleaned_data.get('transaction_status', 'Ongoing')
        if not transaction.payment_type:
            transaction.payment_type = 'Cash'

        # save and refresh tests
        transaction.save()
        form.save_m2m()
        self.object.transaction_tests.all().delete()
        for test in form.cleaned_data.get('tests', []):
            TransactionTest.objects.create(
                transaction=transaction,
                test=test,
                test_price=test.test_price
            )

        return redirect(self.success_url)



@method_decorator(login_required, name='dispatch')
class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')


@login_required
def complete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.transaction_status = 'Completed'
    transaction.save()
    return redirect('transaction_detail', pk=pk)

@login_required
def revert_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.transaction_status = 'Ongoing'
    transaction.save()
    return redirect('transaction_detail', pk=pk)

def get_company_peme_rate(request, company_id):
    try:
        company = Company.objects.get(pk=company_id)
        return JsonResponse({'peme_rate': company.company_peme_rate})
    except Company.DoesNotExist:
        return JsonResponse({'peme_rate': 0})