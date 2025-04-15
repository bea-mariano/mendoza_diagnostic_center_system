from django.db import models

# Create your models here.
# companies/models.py
from django.db import models
from django.urls import reverse
from patients.models import Patient

class Company(models.Model):
    COMMISSION_TYPE_CHOICES = [
        ('Percentage','Percentage'),
        ('Fixed Rate','Fixed Rate'),
        ('No Commission','No Commission'),
    ]
    
    company_name = models.CharField(max_length=50)
    commission_eligible = models.BooleanField(default=False)
    commission_type = models.CharField(max_length=50, choices=COMMISSION_TYPE_CHOICES)
    commission_rate = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.company_name}"

    def get_absolute_url(self):
        return reverse('company_detail', kwargs={'pk': self.pk})