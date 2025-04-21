from django.db import models
from companies.models import Company
from tests.models import Test

class Setpackage(models.Model):
    package_name = models.CharField(max_length=100)
    package_transaction_purpose = models.CharField(max_length=100)  # e.g., "PEME", "APE"
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    package_promo_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.company.name} - {self.package_name} ({self.package_transaction_purpose})"


class SetpackageTest(models.Model):
    package = models.ForeignKey(Setpackage, related_name='tests', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    exclusion_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.package.package_name} - {self.test.name} (-₱{self.exclusion_amount})"
