from django.db import models
from django.utils import timezone

from .store_models import Store
from .goods_models import Goods, Supplier
from .user_models import XingUser

class SaleRecord(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    clerk = models.ForeignKey(XingUser, on_delete=models.DO_NOTHING)
    count = models.SmallIntegerField('数量')
    sum = models.FloatField('金额')
    discount = models.FloatField('折扣', default=1)
    sale_time = models.DateTimeField('销售日期')
    sn = models.CharField('销售流水', max_length=32)
    #支付方式，-1为退货状态；0 微信，1 支付宝，2 现金，3 银行卡，4 其它
    mode = models.SmallIntegerField('支付方式', default=0)

    class Meta:
        db_table = 'xing_sale_record'
        unique_together = ('store', 'sn','goods')

class Purchase(models.Model):
    store = models.ForeignKey(Store, models.CASCADE)
    goods = models.ForeignKey(Goods, models.CASCADE, to_field='barcode')
    buyer = models.ForeignKey(XingUser, models.CASCADE)
    count = models.IntegerField('采购数量')
    price = models.FloatField('采购单价')
    date = models.DateTimeField('采购日期', default=timezone.now)
    supplier = models.ForeignKey(Supplier, models.CASCADE)

    class Meta:
        db_table = 'xing_purchase'
        ordering = ('store', 'date')

class Storage(models.Model):
    store = models.ForeignKey(Store, models.CASCADE)
    goods = models.ForeignKey(Goods, models.CASCADE, to_field='barcode')
    count_t = models.BigIntegerField('历史库存')
    count_c = models.IntegerField('当前库存')
    price = models.FloatField('售价')
    discount = models.FloatField('折扣', default=1.0)
    date_ps = models.DateTimeField('促销开始时间', null=True, blank=True)
    date_pe = models.DateTimeField('促销结束时间', null=True, blank=True)
    editor = models.ForeignKey(XingUser, models.CASCADE, null=True, blank=True)
    edit_date = models.DateTimeField('编辑时间', null=True, blank=True)

    class Meta:
        db_table = 'xing_storage'
        ordering = ('store', 'count_c')