from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

#用户表，继承auth.models.AbstractUser
class XingUser(AbstractUser):
    mobile = models.CharField('手机号码', max_length=12,unique=True)
    wechat = models.CharField('微信', max_length=256, unique=True, null=True, blank=True)
    id_card = models.CharField('身份证', max_length=18, unique=True, null=True, blank=True)

    class Meta:
        db_table = 'xing_user'
        ordering = ['last_login']  
    
    def __str__(self):
        return '%s %s' % (self.username, self.mobile)
