from django.db import models

# Create your models here.
class CustomerProfile(models.Model):
    account_number=models.CharField(max_length=8)
    userid=models.CharField(max_length=6)
    account_encrypted=models.BinaryField(max_length=4096)
