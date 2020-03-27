from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Goods
from ..serializers import GoodsSerializer
from public.utils import handle_api_exception

class GoodsListView(APIView):
    def handle_exception(self, exc):
        response = handle_api_exception(exc)
        return Response(response, status=exc.status_code)

    def get(self, request, format=None):
        goods = Goods.objects.all()
        serializer = GoodsSerializer(goods, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = GoodsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)