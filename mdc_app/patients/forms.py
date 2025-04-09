# patients/forms.py
from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 
            'middle_name',
            'last_name', 
            'gender', 
            'date_of_birth'
            ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }