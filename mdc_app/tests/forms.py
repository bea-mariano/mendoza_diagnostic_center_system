# tests/forms.py
from django import forms
from .models import Test

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = [
            'test_name', 
            'test_price',
            'test_package_exclusion_rate', 
            'test_category'
            ]
        widgets = {
        }