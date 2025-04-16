from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Transaction, TransactionTest  # 👈 Import TransactionTest
from .forms import TransactionForm
from companies.models import Company
from django.http import JsonResponse

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
        response = super().form_valid(form)

        selected_tests = form.cleaned_data.get('tests')
        print("Selected tests:", selected_tests)  # Debug statement

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

    def get_initial(self):
        initial = super().get_initial()
        initial['tests'] = self.object.transaction_tests.values_list('test__pk', flat=True)
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['tests'].initial = self.object.transaction_tests.values_list('test__pk', flat=True)
        return form

    def form_valid(self, form):
        # Update transaction_status explicitly from form data
        transaction = form.save(commit=False)
        
        # Explicitly set transaction_status if it can be modified by the user
        transaction.transaction_status = form.cleaned_data.get('transaction_status', 'Ongoing')
        
        if not transaction.payment_type:
            transaction.payment_type = 'Cash'
        transaction.save()

        selected_tests = form.cleaned_data.get('tests')

        # Clear existing tests and re-add current selection
        self.object.transaction_tests.all().delete()

        for test in selected_tests:
            TransactionTest.objects.create(
                transaction=transaction,
                test=test,
                test_price=test.test_price
            )

        return redirect(self.success_url)

    def form_invalid(self, form):
        print("Form errors:", form.errors)  # Debug: helps find silent validation issues
        return super().form_invalid(form)




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