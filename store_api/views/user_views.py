"""
2020.02.18
    实现短消息验证码、用户注册、用户登录、修改密码等API接口
"""
import re
from django.utils import timezone
from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.utils import (
    jwt_payload_handler, 
    jwt_encode_handler,)
from django.contrib.auth.hashers import check_password

from ..models import XingUser, AppVersion
from public.utils import (
    SW_DEBUG,
    PublicAuthentication, 
    TokenPermission,
    SMSPermission,
    handle_api_exception,)
from ..serializers import (
    AppVersionSerializer, 
    AppTokenSerializer,
    SMSCodeSerializer, 
    PasswordSerializer,
    UserRegisterSerializer,
    XingUserSerializer)

# 获取App Token API
class AppTokenView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def handle_exception(self, exc):
        response = handle_api_exception(exc, SW_DEBUG)
        return Response(response, status=exc.status_code)

    def post(self, request, format=None):
        serializer = AppTokenSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        appVersion = serializer.validated_data.get('app_version')
        token = serializer.validated_data.get('token')
        response = {'app_version': appVersion, 'token': token}
        return Response(response)

#获取短消息验证码API
class SMSCodeView(APIView):
    authentication_classes = (PublicAuthentication,)
    permission_classes = (TokenPermission,)

    def handle_exception(self, exc):
        response = handle_api_exception(exc, SW_DEBUG)
        return Response(response, status=exc.status_code)
    
    def post(self, request, format=None):
        serializer = SMSCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']
        #生成随机验证码，向目标手机发送验证码，用手机号码和验证码生成token
        token = jwt_encode_handler({
            'exp': timezone.now() + timezone.timedelta(minutes=5),  #有效期：3分钟
            'mobile': mobile,
            'sms_code': '118590'})
        return Response({'token': token}, status=status.HTTP_200_OK)

#用户登录API
class UserLoginView(APIView):
    authentication_classes = (PublicAuthentication,)
    permission_classes = (TokenPermission,)

    def handle_exception(self, exc):
        response = handle_api_exception(exc, SW_DEBUG)
        return Response(response, status=exc.status_code)

    def post(self, request, *args, **kwargs):
        serializer = JSONWebTokenSerializer(data=request.data)

        # raise_exception=True,保证异常被handle_exception()处理
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user') or request.user
        token = serializer.object.get('token')
        response_data = {
            'user': XingUserSerializer(user).data,
            'token': token,
            }
        user.last_login = timezone.now()
        user.save()
        return Response(response_data, status=status.HTTP_200_OK)

#用户注册API
class UserRegisterView(APIView):
    authentication_classes = [PublicAuthentication]
    permission_classes = [SMSPermission]

    def handle_exception(self, exc):
        response = handle_api_exception(exc, SW_DEBUG)
        return Response(response, status=exc.status_code)
    
    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
#用户信息查询、更新API
class UserDetailView(APIView):
    def handle_exception(self, exc):
        response = handle_api_exception(exc, SW_DEBUG)
        return Response(response, status=exc.status_code)
    
    def get(self, request, pk, format=None):
        #只允许本人和超级用户查看
        if pk != request.user.id and not request.user.is_superuser:
            raise PermissionDenied
        serializer = XingUserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, pk, formate=None):
        #只允许本人更新信息
        if pk != request.user.id:
            raise PermissionDenied

        user = request.user

        if 'username' not in request.data:
            request.data['username'] = user.username
        if 'mobile' in request.data:
            exp = r'^1((3[\d])|(4[75])|(5[^3|4])|(66)|(7[3678])|(8[\d])|(9[89]))\d{8}$'
            if not re.findall(exp, request.data['mobile']):
                raise serializers.ValidationError({'mobile': ['无效的手机号码']})
        else:
            request.data['mobile'] = user.mobile
        if 'id_card' in request.data:
            # 身份证验证
            pass

        serializer = XingUserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        #重新生成鉴权码
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return Response({'username': user.username, 'token': token})

#用户修改密码API
class PasswordView(APIView):
    def handle_exception(self, exc):
        response = handle_api_exception(exc, SW_DEBUG)
        return Response(response, status=exc.status_code)
    
    def put(self, request, pk, format=None):
        #只允许本人修改密码
        if pk != request.user.id:
            raise PermissionDenied

        user = request.user
        serializer = PasswordSerializer(user, request.data)
        serializer.is_valid(raise_exception=True)
        # 修改密码前验证原密码
        if not check_password(request.data['old_password'], user.password):
            raise serializers.ValidationError({'old_password': ['一致性校验错误。']}, 'disaccord')
        serializer.save()
        return Response(status=status.HTTP_200_OK)

