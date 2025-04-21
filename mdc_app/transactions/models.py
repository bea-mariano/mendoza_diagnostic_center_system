from django.db import models
from django.urls import reverse
from django.utils import timezone
import pytz
from patients.models import Patient
from tests.models import Test
from companies.models import Company

def get_manila_date():
    return timezone.now().astimezone(pytz.timezone('Asia/Manila')).date()

def get_manila_time():
    return timezone.now().astimezone(pytz.timezone('Asia/Manila')).time()

class TransactionManager(models.Manager):
    def ongoing(self):
        # Returns all transactions made on the current day (Manila date)
        return self.filter(transaction_date=get_manila_date())

class Transaction(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('Cash', 'Cash'),
        ('Charged', 'Charged')
    ]

    TRANSACTION_TYPE_CHOICES = [
        ('Company', 'Company'),
        ('Walk-in', 'Walk-in')
    ]

    TRANSACTION_PURPOSE_CHOICES = [
        ('Pre-Employment Examination (PEME)', 'Pre-Employment Examination (PEME)'),
        ('Annual Physical Examination (APE)', 'Annual Physical Examination (APE)'),
        ('Other Test', 'Other Test')
    ]

    TRANSACTION_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Ongoing', 'Ongoing'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]

    DISCOUNT_TYPE_CHOICES = [
        ('Philhealth', 'Philhealth'),
        ('Senior Citizen', 'Senior Citizen'),
        ('PWD', 'PWD'),
        ('Package Exclusion', 'Package Exclusion'),
        ('No Discount', 'No Discount')
    ]

    address = models.TextField()
    contact_no = models.CharField(max_length=11)
    age = models.PositiveIntegerField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='transactions')
    payment_type = models.CharField(max_length=25, choices=PAYMENT_TYPE_CHOICES)
    transaction_type = models.CharField(max_length=25, choices=TRANSACTION_TYPE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='transactions')
    transaction_purpose = models.CharField(max_length=50, choices=TRANSACTION_PURPOSE_CHOICES)
    has_drug_test = models.BooleanField(default=False)
    custody_control_form_submitted = models.BooleanField(default=False)
    transaction_date = models.DateField(auto_now_add=True)
    transaction_time = models.TimeField(auto_now_add=True)
    transaction_status = models.CharField(max_length=50, choices=TRANSACTION_STATUS_CHOICES)
    discount_type = models.CharField(max_length=25, choices=DISCOUNT_TYPE_CHOICES, default='No Discount')
    discount_rate = models.PositiveIntegerField(default=0)
    discounted_total = models.PositiveIntegerField(default=0)
    transaction_total = models.PositiveIntegerField(default=0)

    objects = TransactionManager()

    def get_absolute_url(self):
        return reverse('transaction_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"Transaction #{self.pk} - {self.patient}"

class TransactionTest(models.Model):
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, related_name='transaction_tests')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test_transactions')
    test_price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.transaction} - {self.test.test_name} - {self.test_price}"
