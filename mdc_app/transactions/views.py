from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Transaction, TransactionTest  # 👈 Import TransactionTest
from .forms import TransactionForm

@method_decorator(login_required, name='dispatch')
class TransactionListView(ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'

@method_decorator(login_required, name='dispatch')
class TransactionActiveListView(ListView):
    model = Transaction
    template_name = 'transactions/transaction_active_list.html'
    context_object_name = 'transactions'

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

@method_decorator(login_required, name='dispatch')
class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transaction_list')
    
    def form_valid(self, form):
        form.instance.transaction_status = 'Ongoing'
        if not form.instance.payment_type:
            form.instance.payment_type = 'Cash'

        # Save transaction first
        response = super().form_valid(form)

        # Create TransactionTest records
        selected_tests = form.cleaned_data.get('tests')
        for test in selected_tests:
            TransactionTest.objects.create(
                transaction=self.object,
                test=test,
                test_price=test.test_price
            )

        return response

@method_decorator(login_required, name='dispatch')
class TransactionUpdateView(UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        # Save updated transaction first
        response = super().form_valid(form)

        # Remove existing test records
        TransactionTest.objects.filter(transaction=self.object).delete()

        # Recreate TransactionTest records
        selected_tests = form.cleaned_data.get('tests')
        for test in selected_tests:
            TransactionTest.objects.create(
                transaction=self.object,
                test=test,
                test_price=test.test_price
            )

        return response

@method_decorator(login_required, name='dispatch')
class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')
