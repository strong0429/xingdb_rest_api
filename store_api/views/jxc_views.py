import pytz
from django.utils import timezone
from django.db.models import F
from django.db.models import Sum, Count, Avg

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions, permissions
from rest_framework.settings import api_settings
from rest_framework.serializers import ValidationError

from public.utils import PublicView
from xingdb_proj.settings import TIME_ZONE
from ..models import SaleRecord, StoreStaff, Purchase, Inventory
from ..serializers import (
    SaleRecordSerializer, 
    PurchaseSerializer, 
    StockSerializer)

class JXC_Permission(permissions.BasePermission):
    def has_permission(self, request, view):
        # 获取path中的参数
        store_id = view.kwargs.get('store_id', None)
        if store_id is None:
            return False
        try:
            StoreStaff.objects.get(store=store_id, staff=request.user.id)
        except:
            return False
        return True

#销售记录增、改、查视图，查询时可以给出时间段查询
class SaleRecordView(PublicView):
    permission_classes = (JXC_Permission, )

    def get(self, request, store_id, format=None):
        if 'start_time' and 'end_time' in request.data:
            srs = SaleRecord.objects.filter(store=store_id, 
                sale_time__gte=request.data['start_time'],
                sale_time__lte=request.data['end_time'])
        elif 'start_time' in request.data:
            srs = SaleRecord.objects.filter(store=store_id,\
                sale_time__gte=request.data['start_time'])
        elif 'end_time' in request.data:
            srs = SaleRecord.objects.filter(store=store_id,\
                sale_time__lte=request.data['end_time'])
        else:
            srs = SaleRecord.objects.filter(store=store_id)
        if 'sn' in request.data:
            srs = srs.filter(sn=request.data['sn'])
        srs = srs.order_by('sn')
        srs = self.paginator.paginate_queryset(srs, request, self)
        serializer = SaleRecordSerializer(srs, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def post(self, request, store_id, format=None):
        data = request.data.copy()
        data['store'] = store_id
        data['clerk'] = request.user.id
        serializer = SaleRecordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, store_id, format=None):
        if 'sn' not in request.data:
            raise ValidationError({'sn':['该项目为必填项。']}, 'required')

        if 'barcode' in request.data:
            srs = SaleRecord.objects.filter(store=store_id, sn=request.data['sn'], 
                goods__barcode=request.data['barcode'])
        else:
            srs = SaleRecord.objects.filter(store=store_id, sn=request.data['sn'])
        srs.update(mode=-1)

        serializer = SaleRecordSerializer(srs, many=True)
        return Response(serializer.data)

#销售记录概要统计：上月、当月、上周、本周、昨天、当日的销售额；
class SalesSummaryView(PublicView):
    permission_classes = (JXC_Permission,)

    def get(self, request, store_id, format=None):
        try:
            StoreStaff.objects.get(store=store_id, staff=request.user.id, position__in='OM')
        except:
            raise exceptions.PermissionDenied

        now_dt = timezone.now()
        month = 12 if now_dt.month == 1 else (now_dt.month - 1)
        year = now_dt.year - 1 if now_dt.month == 12 else now_dt.year
        start_dt = timezone.datetime(year, month, 1, 0, 0, 0, tzinfo=pytz.timezone(TIME_ZONE))

        #查询上月一号至今的所有销售数据
        sales = SaleRecord.objects.filter(store=store_id, sale_time__gte=start_dt)\
            .exclude(mode=-1).values_list('goods', 'count', 'sum', 'sale_time')
        #统计上月单个商品的销售额
        lm_sales = sales.filter(sale_time__month=start_dt.month).values_list('goods')\
            .annotate(Sum('sum'), Sum('count'))
        #统计当月单个商品的销售额
        cm_sales = sales.filter(sale_time__month=now_dt.month).values_list('goods')\
            .annotate(Sum('sum'), Sum('count'))
        #统计上周单个商品的销售额
        lw = now_dt.isocalendar()[1] - 1 #(year, weeks, weekday)
        lw_sales = sales.filter(sale_time__week=lw).values_list('goods')\
            .annotate(Sum('sum'), Sum('count'))
        #统计本周单个商品的销售额
        cw_sales = sales.filter(sale_time__week=(lw+1)).values_list('goods')\
            .annotate(Sum('sum'), Sum('count'))
        #统计昨天单个商品的销售额
        yd = (now_dt - timezone.timedelta(days=1)).date()
        yd_sales = sales.filter(sale_time__date=yd).values_list('goods')\
            .annotate(Sum('sum'), Sum('count'))
        #统计当天单个商品的销售额
        td_sales = sales.filter(sale_time__date=now_dt.date()).values_list('goods')\
            .annotate(Sum('sum'), Sum('count'))
        
        #统计总的销售额
        lm_sum = sum(sale[1] for sale in lm_sales)
        cm_sum = sum(sale[1] for sale in cm_sales)
        lw_sum = sum(sale[1] for sale in lw_sales)
        cw_sum = sum(sale[1] for sale in cw_sales)
        yd_sum = sum(sale[1] for sale in yd_sales)
        td_sum = sum(sale[1] for sale in td_sales)

        #获取每种商品的采购价格（统计周期内的平均价格）
        goods_price = Purchase.objects.filter(store=store_id, date__gte=start_dt)\
            .values_list('goods').annotate(Avg('price'))
        #转换为字典数据
        goods_price = dict(goods_price)
        
        #计算利润, 没有采购价格的商品不计算利润
        lm_profit = lm_sum - sum(data[2] * goods_price[data[0]]\
            for data in lm_sales if data[0] in goods_price)
        cm_profit = cm_sum - sum(data[2] * goods_price[data[0]]\
            for data in cm_sales if data[0] in goods_price)
        lw_profit = lw_sum - sum(data[2] * goods_price[data[0]]\
            for data in lw_sales if data[0] in goods_price)
        cw_profit = cw_sum - sum(data[2] * goods_price[data[0]]\
            for data in cw_sales if data[0] in goods_price)
        yd_profit = yd_sum - sum(data[2] * goods_price[data[0]]\
            for data in yd_sales if data[0] in goods_price)
        td_profit = td_sum - sum(data[2] * goods_price[data[0]]\
            for data in td_sales if data[0] in goods_price)

        response = {'lm_sum':lm_sum, 'lm_pro':lm_profit, 'cm_sum':cm_sum, 'cm_pro':cm_profit,
                    'lw_sum':lw_sum, 'lw_pro':lw_profit, 'cw_sum':cw_sum, 'cw_pro':cw_profit,
                    'yd_sum':yd_sum, 'yd_pro':yd_profit, 'td_sum':td_sum, 'td_pro':td_profit}
        return Response(response)


class PurchaseView(PublicView):
    permission_classes = (JXC_Permission, )

    def get(self, request, store_id, format=None):
        if 'start_time' and 'end_time' in request.data:
            records = Purchase.objects.filter(store=store_id, 
                    date__gte=request.data['start_time'],
                    date__lte=request.data['end_time']).order_by('date')
        elif 'start_time' in request.data:
            records = Purchase.objects.filter(store=store_id, 
                    date__gte=request.data['start_time']).order_by('date')
        elif 'end_time' in request.data:
            records = Purchase.objects.filter(store=store_id, 
                    date__lte=request.data['end_time']).order_by('date')
        else:
            records = Purchase.objects.filter(store=store_id).order_by('date')

        records = self.paginator.paginate_queryset(records, request, self)
        serializer = PurchaseSerializer(records, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def post(self, request, store_id, format=None):
        data = request.data.copy()
        data['store'] = store_id
        data['buyer'] = request.user.id

        serializer = PurchaseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        purchase = serializer.save()

        #对应更新 storage 表
        try:
            storage = Inventory.objects.get(store=purchase.store, 
                goods=purchase.goods, supplier=purchase.supplier)
            storage.count_h = F('count_h') + purchase.count
            storage.count_c = F('count_c') + purchase.count
        except:
            storage = Inventory(store=purchase.store, goods=purchase.goods, supplier=purchase.supplier, 
                count_h=purchase.count, count_c=purchase.count)
        storage.price = request.data['sale_price']
        storage.save()

        return Response(serializer.data)


#获取库存详细信息、更新库存信息视图
class StockView(PublicView):
    permission_classes = (JXC_Permission, )

    def get(self, request, store_id, format=None):
        records = Inventory.objects.filter(store=store_id).order_by('count_c')
        records = self.paginator.paginate_queryset(records, request, self)
        serializer = StockSerializer(records, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def put(self, request, store_id, format=None):
        if 'goods' and 'supplier' in request.data:
            record = Inventory.objects.get(store=store_id, 
                goods=request.data['goods'], supplier=request.data['supplier'])
        elif 'goods' in request.data:
            record = Inventory.objects.get(store=store_id, goods=request.data['goods'])
        else:
            raise ValidationError({'goods': ['该字段是必填项。']}, 'required')
        record.editor = request.user
        record.edit_date = timezone.now()

        serializer = StockSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
