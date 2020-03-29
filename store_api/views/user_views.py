"""
2020.02.18
    实现短消息验证码、用户注册、用户登录、修改密码等API接口
"""
import re
import jwt

from django.utils import timezone
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from django.contrib.auth.hashers import check_password

from rest_framework import status
from rest_framework import serializers
from rest_framework import exceptions, permissions

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.utils import jwt_payload_handler, jwt_decode_handler, jwt_encode_handler

from public.utils import PublicView
from ..models import XingUser, AppVersion
from ..serializers import (
    AppVersionSerializer, 
    AppTokenSerializer,
    SMSCodeSerializer, 
    PasswordSerializer,
    UserRegisterSerializer,
    XingUserSerializer)

# App token鉴权lei,用户登录、获取验证码、用户注册时使用
class PublicAuthentication(BaseAuthentication):
    #重写鉴权认证方法
    def authenticate(self, request):
        #获取请求头中的Token内容
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            msg = _('Authentication is required.')
            raise exceptions.AuthenticationFailed(msg)
        #Token需要采用JWT格式
        if smart_text(auth[0].lower()) != auth_header_prefix:
            msg = _("Invalid Authentication prefix. Prefix is 'JWT' or 'jwt'")
            raise exceptions.AuthenticationFailed(msg)
        #判断Token值    
        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        #读取Token中的payload
        try:
            payload = jwt_decode_handler(auth[1])
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        return(None, payload)

class TokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            app_name = request.auth['app_name']
            ver_code = request.auth['ver_code']
            AppVersion.objects.get(app_name=app_name, ver_code=ver_code)
            return True
        except:
            return False

class SMSPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        sms_sth = {
            'mobile': request.auth.get('mobile'),
            'sms_code': request.auth.get('sms_code')
        }
        if all(sms_sth):
            return (sms_sth['mobile'] == request.data.get('mobile') and\
                sms_sth['sms_code'] == request.data.get('sms_code'))
        return False

# 获取App Token API
class AppTokenView(PublicView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, format=None):
        serializer = AppTokenSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        appVersion = serializer.validated_data.get('app_version')
        token = serializer.validated_data.get('token')
        response = {'app_version': appVersion, 'token': token}
        return Response(response)

#获取短消息验证码API
class SMSCodeView(PublicView):
    authentication_classes = (PublicAuthentication,)
    permission_classes = (TokenPermission,)

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
class UserLoginView(PublicView):
    authentication_classes = (PublicAuthentication,)
    permission_classes = (TokenPermission,)

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
class UserRegisterView(PublicView):
    authentication_classes = [PublicAuthentication]
    permission_classes = [SMSPermission]

    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
#用户信息查询、更新API
class UserDetailView(PublicView):
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

        if 'mobile' in request.data:
            exp = r'^1((3[\d])|(4[75])|(5[^3|4])|(66)|(7[3678])|(8[\d])|(9[89]))\d{8}$'
            if not re.findall(exp, request.data['mobile']):
                raise serializers.ValidationError({'mobile': ['无效的手机号码']})
        if 'id_card' in request.data:
            # 身份证验证
            pass
        # 设置partial=True，允许只提供需要更新的字段；
        serializer = XingUserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        #重新生成鉴权码
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return Response({'username': user.username, 'token': token})

#用户修改密码API
class PasswordView(PublicView):
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

