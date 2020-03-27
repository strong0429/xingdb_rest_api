from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions, permissions
from rest_framework.serializers import ValidationError

from public.utils import handle_api_exception
from ..serializers import SaleRecordSerializer
from ..models import SaleRecord, StoreStaff

class SalePermission(permissions.BasePermission):
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

class SaleRecordView(APIView):
    permission_classes = (SalePermission, )

    def handle_exception(self, exc):
        response = handle_api_exception(exc)
        return Response(response, status=exc.status_code)

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

        serializer = SaleRecordSerializer(srs, many=True)
        return Response(serializer.data)

    def post(self, request, store_id, format=None):
        data = request.data.copy()
        data['store'] = store_id
        data['clerk'] = request.user.id
        '''
        data['sale_time'] = timezone.datetime.now()
        data['sn'] = '{0:0>6}{1:0>10}'.format(data['clerk'], 
                    int(data['sale_time'].timestamp()))
        '''
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