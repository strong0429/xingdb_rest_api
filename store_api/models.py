from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.

#用户表，继承auth.models.AbstractUser
class XingUser(AbstractUser):
    mobile = models.CharField('手机号码', max_length=12,unique=True)
    id_card = models.CharField('身份证', max_length=18, unique=True, null=True, blank=True)

    class Meta:
        db_table = 'xing_user'
        ordering = ['last_login']  
    
    def __str__(self):
        return '%s %s' % (self.username, self.mobile)

#店铺类别表
class StoreCategory(models.Model):
    name = models.CharField('类别名称', max_length=45, unique=True)
    class Meta:
        db_table = 'xing_store_category'

#付费模式
class PayMode(models.Model):
    mode = models.CharField('付费模式', max_length=45)
    amount = models.FloatField('付费金额')

    class Meta:
        db_table = 'xing_pay_mode'

#注册店铺信息表
class Store(models.Model):
    name = models.CharField('店铺名称', max_length=45)
    reg_date = models.DateTimeField('注册日期', auto_now_add=True)
    owner = models.ForeignKey(XingUser, related_name='stores', on_delete=models.CASCADE)
    category = models.ForeignKey(StoreCategory, on_delete=models.PROTECT, related_name='stores', blank=True)
    addr_province = models.CharField('省', max_length=16, null=True, blank=True)
    addr_city = models.CharField('市/县', max_length=16, null=True, blank=True)
    addr_district = models.CharField('区/镇', max_length=16, null=True, blank=True)
    addr_street = models.CharField('街道/村', max_length=16, null=True, blank=True)
    addr_detail = models.CharField('具体', max_length=45, null=True, blank=True)
    phone = models.CharField('联系电话', max_length=12, null=True, blank=True)
    photo_name = models.CharField('图片名称', max_length=45, null=True, blank=True)

    class Meta:
        db_table = 'xing_store'
        unique_together = ['owner', 'name']
        ordering = ['addr_province', 'addr_city', 'reg_date']

    def __str__(self):
        return '%d:%s' % (self.id, self.name)

#店铺付费记录表
class PayRecord(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    pay_mode = models.ForeignKey(PayMode, on_delete=models.PROTECT)
    pay_date = models.DateTimeField('付费日期', auto_now_add=True)
    pay_amount = models.FloatField('付费金额', default=0.0)

    class Meta:
        db_table = 'xing_pay_record'
        ordering = ['store_id', 'pay_date']

#店铺职员信息表
class Staff(models.Model):
    CLERK = 'CL'
    MANAGER = 'MA'
    POSITION_CHOICES = (
        (CLERK, '店员'),
        (MANAGER, '经理'),
    )
    store = models.ForeignKey(Store, related_name='staffs', on_delete=models.CASCADE)
    staff = models.ForeignKey(XingUser, related_name='staffs', on_delete=models.CASCADE)
    position = models.CharField(max_length=16, choices=POSITION_CHOICES, default=CLERK)
    date_joined = models.DateTimeField('入职日期', auto_now_add=True)
    is_active = models.BooleanField(default=True)
