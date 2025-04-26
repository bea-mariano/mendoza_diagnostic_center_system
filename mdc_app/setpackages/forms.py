# setpackages/forms.py

from django import forms
from .models import Setpackage

class SetpackageForm(forms.ModelForm):
    class Meta:
        model = Setpackage
        fields = [
            'package_name',
            'package_transaction_purpose',
            'company',
            'package_promo_price'
        ]
