"""
2020.02.19
    实现店铺注册、查询、更新等API接口
"""
import os
from rest_framework import status
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

#from django.http import FileResponse

from ..models import Store, StoreStaff
from ..serializers import StoreSerializer
from public.utils import PublicView

#店铺查询、注册API
class StoreListView(PublicView):
    def get(self, request, format=None):
        stores = Store.objects.filter(staffs__id = request.user.id)
            #storestaff__position = 'O')
        
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = StoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        store = serializer.save()

        #更新store_staff表
        store_staff = StoreStaff(store=store, staff=request.user, position='O')
        store_staff.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)

#店铺查询、更新、注销API
class StoreDetailView(PublicView):
    def get_object(self, pk, owner):
        #只有店主才可以更改店铺信息
        try:
            store = Store.objects.get(pk=pk, 
                    staffs__id=owner.id, storestaff__position='O')
        except:
            raise exceptions.PermissionDenied
        return store

    def get(self, request, pk, format=None):
        try:
            store = Store.objects.get(pk=pk, staffs__id=request.user.id)
        except:
            raise exceptions.PermissionDenied

        serializer = StoreSerializer(store)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        store = self.get_object(pk, request.user)
        logo = store.logo
        #partial=True, 只更新部分字段；若不设置，则data中必须包含模型的关键字段；
        serializer = StoreSerializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #若更新了logo文件，删除旧的logo文件
        if 'logo' in request.data:
            os.remove(logo.path)
            
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        store = self.get_object(pk, request.user)
        store.delete()
        return Response(status=status.HTTP_200_OK)
        
