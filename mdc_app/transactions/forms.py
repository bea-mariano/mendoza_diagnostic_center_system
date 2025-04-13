from django import forms
from .models import Transaction
from tests.models import Test
from patients.models import Patient

class TransactionForm(forms.ModelForm):
    tests = forms.ModelMultipleChoiceField(
        queryset=Test.objects.all().order_by('test_name'),  # Using test_name instead of name
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Transaction
        fields = [
            'patient', 
            'address', 
            'contact_no', 
            'age', 
            'transaction_type', 
            'company_id', 
            'payment_type', 
            'transaction_purpose', 
            'has_drug_test', 
            'custody_control_form_submitted', 
            'tests', 
            'transaction_status', 
            'discount_type', 
            'discount_rate',
            'discounted_total', 
            'transaction_total'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.all().order_by('last_name', 'first_name')
