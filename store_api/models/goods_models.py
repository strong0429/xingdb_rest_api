from os import path
from django.db import models

from .store_models import Store
from .user_models import User

class GoodsCategoryL1(models.Model):
    name = models.CharField('商品类别I', max_length=64, unique=True)

    class Meta:
        db_table = 'dbs_goods_category_l1'

class GoodsCategoryL2(models.Model):
    category_l1 = models.ForeignKey(GoodsCategoryL1, on_delete=models.PROTECT)
    name = models.CharField('商品类别II', max_length=64, unique=True)

    class Meta:
        db_table = 'dbs_goods_category_l2'

class Goods(models.Model):
    barcode = models.CharField('条码', max_length=16, unique=True)
    name = models.CharField('名称', max_length=32)
    spec = models.CharField('规格', max_length=32)
    category = models.ForeignKey(GoodsCategoryL2, on_delete=models.CASCADE)

    class Meta:
        db_table = 'dbs_goods'
        #ordering = ('category', 'name')

    def __str__(self):
        return "%s %s" % (self.barcode, self.name)

class Supplier(models.Model):
    name = models.CharField('名称', max_length=45)
    contactor = models.CharField('联系人', max_length=45)
    phone = models.CharField('联系电话', max_length=45, unique=True)
    addr = models.CharField('地址', max_length=128, null=True, blank=True)
    store = models.ManyToManyField(Store, null=True, blank=True)

    class Meta:
        db_table = 'dbs_supplier'

    def __str__(self):
        return '%s %s' % (self.name, self.phone)