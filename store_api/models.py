from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class XingUser(AbstractUser):
    mobile = models.CharField(max_length=12,unique=True)

    class Meta:
        db_table = 'xing_user'
        ordering = ['last_login']  
