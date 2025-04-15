# companies/forms.py
from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'company_name', 
            'commission_eligible',
            'commission_type', 
            'commission_rate'
            ]
        widgets = {
        }