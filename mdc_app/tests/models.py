# tests/models.py
from django.db import models
from django.urls import reverse
from patients.models import Patient

class Test(models.Model):
    TEST_CATEGORY_CHOICES = [
        ('Hematology', 'Hematology'),
        ('Clinical Microscopy', 'Clinical Microscopy'),
        ('Pregnancy Test', 'Pregnancy Test'),
        ('Blood Chemistry', 'Blood Chemistry'),
        ('Liver Function', 'Liver Function'),
        ('Electrolytes', 'Electrolytes'),
        ('Tumor Markers', 'Tumor Markers'),
        ('Serology', 'Serology'),
        ('Immunology', 'Immunology'),
        ('Hormone', 'Hormone'),
        ('Hepatitis', 'Hepatitis'),
        ('Xray', 'Xray'),
        ('Ultrasound', 'Ultrasound'),
        ('Xray', 'Xray'),
        ('Others', 'Others')
    ]
    
    test_name = models.CharField(max_length=50)
    test_price = models.PositiveIntegerField()
    test_package_exclusion_rate = models.PositiveIntegerField()
    test_category = models.CharField(max_length=50, choices=TEST_CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.test_name}"
    

    def get_absolute_url(self):
        return reverse('test_detail', kwargs={'pk': self.pk})