from rest_framework.views import APIView
from rest_framework.response import Response

from public.utils import PublicView
from ..models import Goods, Supplier
from ..serializers import GoodsSerializer, SupplierSerializer

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