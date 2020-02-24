"""
2020.02.19
    实现店铺注册、查询、更新等API接口
"""
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from store_api.models import Store, StoreStaff
from store_api.serializers import StoreSerializer

#店铺查询、注册API
class StoreListView(APIView):
    def get(self, request, format=None):
        #以下两种查询方式都可以
        #stores = Store.objects.filter(staffs__id=request.user.id)
        #stores = request.user.store_set.all()
        #只有店主才可以查询店铺信息
        stores = Store.objects.filter(
            staffs__id = request.user.id,
            storestaff__position = 'OW')
        
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        #request.data['owner'] = request.user.id
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            store = serializer.save()
            #更新store_staff表
            store_staff = StoreStaff(store=store, staff=request.user, position='OW')
            store_staff.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#店铺查询、更新、注销API
class StoreDetailView(APIView):
    def get_object(self, pk):
        try:
            return Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            raise Http404

    def has_permission(self, store, owner):
        if store.owner.id != owner.id and not owner.is_superuser:
            raise PermissionDenied

    def get(self, request, pk, format=None):
        store = self.get_object(pk)
        self.has_permission(store, request.user)
        serializer = StoreSerializer(store)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        store = self.get_object(pk)
        self.has_permission(store, request.user)
        if 'owner' not in request.data:
            request.data['owner'] = store.owner.id
        if 'category' not in request.data:
            request.data['category'] = store.category.id
        if 'name' not in request.data:
            request.data['name'] = store.name
        serializer = StoreSerializer(store, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        store = self.get_object(pk)
        self.has_permission(store, request.user)
        store.delete()
        return Response(status=status.HTTP_200_OK)
        
