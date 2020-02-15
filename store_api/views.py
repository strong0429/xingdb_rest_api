from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from rest_framework_jwt.utils import jwt_encode_handler, jwt_decode_handler

from .models import *
from .serializers import *

# Create your views here.

class SMSCode(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, format=None):
        serializer = SMSSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            mobile = serializer.validated_data['mobile']

            #手机是否已注册过
            if XingUser.objects.filter(mobile=mobile):
                return Response({'sms_code': '手机已注册'}, status=status.HTTP_400_BAD_REQUEST)

            #生成随机验证码，向目标手机发送验证码，用手机号码和验证码生成token
            token = jwt_encode_handler({
                'mobile': serializer.validated_data['mobile'],
                'sms_code': '118590'})
            return Response({'token': token}, status=status.HTTP_200_OK)

class UserRegisterView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, format=None):
        try:
            token = request.data['token']
        except:
            return Response({'token': ['该字段是必填项']}, 
                status=status.HTTP_400_BAD_REQUEST)
        try:
            sms_code = request.data['sms_code']
        except:
            return Response({'sms_code': ['该字段是必填项']}, 
                status=status.HTTP_400_BAD_REQUEST)
            
        serializer = XingUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #从token中取出电话号码和校验码进行校验
        try:
            payload = jwt_decode_handler(token)
            t_mobile = payload['mobile']
            t_sms_code = payload['sms_code']
        except:
            return Response({'token': ['无效的Token']}, 
                status=status.HTTP_400_BAD_REQUEST)
        if t_mobile != serializer.validated_data['mobile'] or\
            t_sms_code != sms_code:
            return Response({'register': ['数据校验不一致']}, 
                status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class StoreListView(APIView):
    def get(self, request, format=None):
        #stores = Store.objects.all()
        stores = Store.objects.filter(owner_id=request.user.id)
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        request.data['owner_id'] = request.user.id
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        if 'owner_id' not in request.data:
            request.data['owner_id'] = store.owner.id
        if 'category_id' not in request.data:
            request.data['category_id'] = store.category.id
        if 'pay_mode_id' not in request.data:
            request.data['pay_mode_id'] = store.pay_mode.id
        serializer = StoreSerializer(store, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        store = self.get_object(pk)
        self.has_permission(store, request.user)
        store.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)