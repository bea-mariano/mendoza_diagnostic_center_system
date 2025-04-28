from django import forms
from .models import Transaction
from tests.models import Test
from patients.models import Patient
from companies.models import Company

class TransactionForm(forms.ModelForm):
    # This field is not part of the Transaction model anymore, but we use it for selection UI
    tests = forms.ModelMultipleChoiceField(
        queryset=Test.objects.all().order_by('test_name'),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Select Tests'
    )

    transaction_purpose = forms.CharField(required=False)

    class Meta:
        model = Transaction
        exclude = ['discount_type']  # remove the old dropdown
        fields = [
            'patient', 
            'address', 
            'contact_no', 
            'age', 
            'transaction_type', 
            'company', 
            'payment_type', 
            # 'transaction_purpose', 
            'has_drug_test', 
            'custody_control_form_submitted', 
            'transaction_status', 
            'discount_type', 
            'discount_rate',
            'discounted_total', 
            'transaction_total'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.all().order_by('last_name', 'first_name')
        self.fields['company'].queryset = Company.objects.all().order_by('company_name')

        # Prepopulate `tests` field if updating an instance
        if self.instance.pk:
            self.fields['tests'].initial = self.instance.transaction_tests.values_list('test_id', flat=True)
