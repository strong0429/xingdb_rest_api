from django.utils import timezone
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions, permissions
from rest_framework.serializers import ValidationError
from rest_framework.settings import api_settings

from public.utils import PublicView
from ..models import SaleRecord, StoreStaff, Purchase, Storage
from ..serializers import SaleRecordSerializer, PurchaseSerializer, StorageSerializer

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
        #serializer = SaleRecordSerializer(srs, many=True)
        #return Response(serializer.data)

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
            storage = Storage.objects.get(store=purchase.store, 
                goods=purchase.goods, supplier=purchase.supplier)
            storage.count_h = F('count_h') + purchase.count
            storage.count_c = F('count_c') + purchase.count
        except:
            storage = Storage(store=purchase.store, goods=purchase.goods, supplier=purchase.supplier, 
                count_h=purchase.count, count_c=purchase.count)
        storage.price = request.data['sale_price']
        storage.save()

        return Response(serializer.data)

class StorageView(PublicView):
    permission_classes = (JXC_Permission, )

    def get(self, request, store_id, format=None):
        records = Storage.objects.filter(store=store_id).order_by('count_c')
        records = self.paginator.paginate_queryset(records, request, self)
        serializer = StorageSerializer(records, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    def put(self, request, store_id, format=None):
        if 'goods' and 'supplier' in request.data:
            record = Storage.objects.get(store=store_id, 
                goods=request.data['goods'], supplier=request.data['supplier'])
        elif 'goods' in request.data:
            record = Storage.objects.get(store=store_id, goods=request.data['goods'])
        else:
            raise ValidationError({'goods': ['该字段是必填项。']}, 'required')
        record.editor = request.user
        record.edit_date = timezone.now()

        serializer = StorageSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
