# transactions/forms.py
from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'patient'
            , 'transaction_type'
            , 'company_id'
            , 'payment_type'
            , 'transaction_purpose'
            , 'age' # SHOULD BE AUTO COMPUTE!
            , 'address'
            , 'contact_no'
            , 'has_drug_test'
            , 'custody_control_form_submitted'
            , 'tests'
            , 'transaction_status'
            ]
        widgets = {
            
        }