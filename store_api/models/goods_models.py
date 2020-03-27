from os import path
from django.db import models

from .store_models import Store
from .user_models import XingUser

def goods_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    logo_file = '.'.join(['%s'%instance.barcode, ext])
    return path.join('goods', logo_file)

class GoodsCategoryL1(models.Model):
    name = models.CharField('商品类别I', max_length=16, unique=True)

    class Meta:
        db_table = 'xing_goods_category_l1'

class GoodsCategoryL2(models.Model):
    category_l1 = models.ForeignKey(GoodsCategoryL1, on_delete=models.PROTECT)
    name = models.CharField('商品类别II', max_length=16, unique=True)

    class Meta:
        db_table = 'xing_goods_category_l2'

class Goods(models.Model):
    barcode = models.CharField('条码', max_length=16, unique=True)
    name = models.CharField('名称', max_length=32)
    spec = models.CharField('规格', max_length=32)
    category = models.ForeignKey(GoodsCategoryL2, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ImageField('图片', upload_to=goods_upload_to, null=True, blank=True)

    class Meta:
        db_table = 'xing_goods'
        ordering = ('category', 'name')

    def __str__(self):
        return "%s %s" % (self.barcode, self.name)

class Supplier(models.Model):
    name = models.CharField('名称', max_length=45)
    contactor = models.CharField('联系人', max_length=45)
    phone = models.CharField('联系电话', max_length=45)
    addr = models.CharField('地址', max_length=128, null=True, blank=True)

    class Meta:
        db_table = 'xing_supplier'
        unique_together = ('name', 'phone')

    def __str__(self):
        return '%s %s' % (self.name, self.phone)