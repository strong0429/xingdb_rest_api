from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_jwt.utils import jwt_encode_handler, jwt_decode_handler

from .models import XingUser
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

class UserRegister(APIView):
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
        
