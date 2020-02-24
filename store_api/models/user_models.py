from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

#App版本记录表
class AppVersion(models.Model):
    app_name = models.CharField('APP名称', max_length=32, unique=True)
    ver_code = models.PositiveIntegerField('版本号')
    ver_txt = models.CharField('版本描述', max_length=8)
    date_pub = models.DateTimeField('发布日期', auto_now_add=True)
    detail = models.TextField('版本描述', null=True, blank=True)

    class Meta:
        db_table = 'xing_app_version'
        ordering = ['app_name', 'date_pub']

    def __str__(self):
        return '%s: V%s' % (self.app_name, self.ver_txt)

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
