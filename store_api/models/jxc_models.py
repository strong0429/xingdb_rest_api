from os import path
from django.db import models
from django.utils import timezone

from .store_models import Store
from .goods_models import Goods, Supplier
from .user_models import User

def goods_photo_file(instance, filename):
    ext = filename.split('.')[-1]
    logo_file = '.'.join(['%s'%instance.barcode, ext])
    return path.join('goods', logo_file)

class SaleRecord(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    clerk = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    goods = models.ForeignKey(Goods, to_field='barcode', on_delete=models.CASCADE)
    count = models.SmallIntegerField('数量')
    sum = models.FloatField('金额')
    discount = models.FloatField('折扣', default=1)
    sale_time = models.DateTimeField('销售日期')
    sn = models.CharField('销售流水', max_length=32)
    #支付方式，-1为退货状态；0 微信，1 支付宝，2 现金，3 银行卡，4 其它
    mode = models.SmallIntegerField('支付方式', default=0)

    class Meta:
        db_table = 'dbs_sale_record'
        unique_together = ('store', 'sn','goods')

class Purchase(models.Model):
    store = models.ForeignKey(Store, models.CASCADE)
    goods = models.ForeignKey(Goods, models.CASCADE, to_field='barcode')
    buyer = models.ForeignKey(User, models.CASCADE)
    count = models.IntegerField('采购数量')
    price = models.FloatField('采购单价')
    date = models.DateTimeField('采购日期', default=timezone.now)
    supplier = models.ForeignKey(Supplier, models.CASCADE)

    class Meta:
        db_table = 'dbs_purchase'
        #ordering = ('store', 'date')
        #unique_together = ('store', 'goods', 'date')

class Inventory(models.Model):
    store = models.ForeignKey(Store, models.CASCADE)
    goods = models.ForeignKey(Goods, models.CASCADE, to_field='barcode')
    count_h = models.FloatField('历史库存')
    count_c = models.FloatField('当前库存')
    price = models.FloatField('售价')
    discount = models.FloatField('折扣', default=1.0)
    date_ps = models.DateTimeField('促销开始时间', null=True, blank=True)
    date_pe = models.DateTimeField('促销结束时间', null=True, blank=True)
    editor = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    edit_date = models.DateTimeField('编辑时间', null=True, blank=True)
    supplier = models.ForeignKey(Supplier, models.CASCADE, null=True, blank=True)
    unit = models.CharField('单位',max_length=16, null=True, blank=True)
    photo = models.ImageField('图片', upload_to=goods_photo_file, null=True, blank=True)

    class Meta:
        db_table = 'dbs_inventory'
        #ordering = ('store', 'count_c')
        unique_together = ('store', 'goods', 'supplier')

