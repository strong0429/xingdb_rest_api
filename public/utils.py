import jwt
from django.utils import timezone
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions, permissions
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_decode_handler, jwt_payload_handler

from rest_framework.authentication import (
    BaseAuthentication, 
    get_authorization_header)

from store_api.serializers import XingUserSerializer

# 用户注册时的鉴权类
class RegisterAuthentication(BaseAuthentication):
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

def jwt_response_payload_handler(token, user=None, request=None):
    response = {'token': token}
    if user:
        response['user'] = XingUserSerializer(user).data

    return response

# 定义获取Token的权限
class TokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        #限制 Authenticator 不能执行操作
        print(request.user.username)
        return request.user.username != 'Authenticator'

