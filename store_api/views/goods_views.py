from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from public.utils import PublicView
from ..models import Goods, Supplier, Store, GoodsCategoryL1
from ..serializers import GoodsSerializer, SupplierSerializer, GoodsCategory1Serializer

class GoodsListView(PublicView):
    def get(self, request, format=None):
        goods = Goods.objects.all()
        serializer = GoodsSerializer(goods, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = GoodsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class GoodsDetailView(PublicView):
    def get(self, request, barcode, format=None):
        goods = Goods.objects.filter(barcode='123456')
        if not goods:
            raise ValidationError({'goods': ['查询对象不存在。']}, 'does_not_exit')

        serializer = GoodsSerializer(goods)
        return Response(serializer.data)

class SupplierView(PublicView):
    def get(self, request, format=None):
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SupplierSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

class GoodsCategoryView(PublicView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, format=None):
        rds = GoodsCategoryL1.objects.all()
        serializer = GoodsCategory1Serializer(rds, many=True)
        return Response(serializer.data)
