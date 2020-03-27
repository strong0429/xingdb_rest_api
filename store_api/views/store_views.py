"""
2020.02.19
    实现店铺注册、查询、更新等API接口
"""
from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

#from django.http import FileResponse

from ..models import Store, StoreStaff
from ..serializers import StoreSerializer
from public.utils import handle_api_exception

#店铺查询、注册API
class StoreListView(APIView):
    def handle_exception(self, exc):
        response = handle_api_exception(exc)
        return Response(response, status=exc.status_code)
    
    def get(self, request, format=None):
        #stores = request.user.store_set.all()
        #只有店主才可以查询店铺信息
        stores = Store.objects.filter(
            staffs__id = request.user.id,
            storestaff__position = 'OW')
        
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = StoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        store = serializer.save()

        #更新store_staff表
        store_staff = StoreStaff(store=store, staff=request.user, position='OW')
        store_staff.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

#店铺查询、更新、注销API
class StoreDetailView(APIView):
    def handle_exception(self, exc):
        response = handle_api_exception(exc)
        return Response(response, status=exc.status_code)
    
    def get_object(self, pk, owner):
        try:
            store = Store.objects.get(pk=pk, 
                    staffs__id=owner.id,
                    storestaff__position='OW')
        except Store.DoesNotExist:
            raise serializers.ValidationError({'store': ['对象不存在。']}, 'does_not_exit')
        return store

    def get(self, request, pk, format=None):
        store = self.get_object(pk, request.user)
        serializer = StoreSerializer(store)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        store = self.get_object(pk, request.user)
        #partial=True, 只更新部分字段；若不设置，则data中必须包含模型的关键字段；
        serializer = StoreSerializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        store = self.get_object(pk, request.user)
        store.delete()
        return Response(status=status.HTTP_200_OK)
        
