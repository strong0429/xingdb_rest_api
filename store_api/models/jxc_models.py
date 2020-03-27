from django.db import models

from .store_models import Store
from .goods_models import Goods
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

