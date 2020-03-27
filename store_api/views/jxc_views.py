from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions, permissions
from rest_framework.serializers import ValidationError
from rest_framework.settings import api_settings

from public.utils import handle_api_exception
from ..serializers import SaleRecordSerializer, PurchaseSerializer
from ..models import SaleRecord, StoreStaff, Purchase

class JXC_Pagination(api_settings.DEFAULT_PAGINATION_CLASS):
    #每页显示多少个
    #page_size = 10
    #默认每页显示3个，可以通过传入pager1/?page=2&size=4,改变默认每页显示的个数
    page_size_query_param = "size"
    #最大页数不超过100
    max_page_size = 100
    #获取页码数的
    #page_query_param = "page"

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

class JXC_View(APIView):
    permission_classes = (JXC_Permission, )
    pagination_class = JXC_Pagination

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def handle_exception(self, exc):
        response = handle_api_exception(exc)
        return Response(response, status=exc.status_code)

class SaleRecordView(JXC_View):
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

class PurchaseView(JXC_View):
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
        serializer.save()
        return Response(serializer.data)