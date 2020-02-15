from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.

#用户表，继承auth.models.AbstractUser
class XingUser(AbstractUser):
    mobile = models.CharField(max_length=12,unique=True)

    class Meta:
        db_table = 'xing_user'
        ordering = ['last_login']  

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
    name = models.CharField('店铺名称', max_length=45,unique=True)
    reg_date = models.DateTimeField('注册日期', auto_now_add=True)
    owner_id = models.ForeignKey(XingUser, on_delete=models.CASCADE, db_column='owner_id')
    category_id = models.ForeignKey(StoreCategory, db_column='catagory_id', on_delete=models.PROTECT, blank=True)
    addr_province = models.CharField('省', max_length=16, null=True, blank=True)
    addr_city = models.CharField('市/县', max_length=16, null=True, blank=True)
    addr_district = models.CharField('区/镇', max_length=16, null=True, blank=True)
    addr_street = models.CharField('街道/村', max_length=16, null=True, blank=True)
    addr_detail = models.CharField('具体', max_length=45, null=True, blank=True)
    phone = models.CharField('联系电话', max_length=12, null=True, blank=True)
    photo_name = models.CharField('图片名称', max_length=45, null=True, blank=True)

    class Meta:
        db_table = 'xing_store'
        ordering = ['addr_province', 'addr_city', 'reg_date']

#店铺付费记录表
class PayList(models.Model):
    store_id = models.ForeignKey(Store, db_column='store_id', on_delete=models.CASCADE)
    pay_mode_id = models.ForeignKey(PayMode, db_column='pay_mode_id', on_delete=models.PROTECT)
    pay_date = models.DateTimeField('付费日期', default=timezone.now)
    pay_amount = models.FloatField('付费金额', default=0.0)

    class Meta:
        db_table = 'xing_pay_list'
        ordering = ['store_id', 'pay_date']

