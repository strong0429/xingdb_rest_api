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

# 调试开关
SW_DEBUG = True

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
        return request.user.username != 'Authenticator'

#APIView异常处理函数
def handle_api_exception(exc, debug=False):
    if debug:
        print('args:', exc.args)
        print('default_code:', exc.default_code)
        print('default_detail:', exc.default_detail)
        print('get_codes:', exc.get_codes())
        print('get_full_details:', exc.get_full_details())
        print('status_code:', exc.status_code)

    if not isinstance(exc, exceptions.APIException):
        if debug:
            print('Exception type:', type(exc))
        return {'code': 777, 'detail': '未知原因的错误。'}

    #if exc.default_code == 'authentication_failed':
    #    return {'code': exc.status_code, 'detail': exc.args[0]}
    
    if exc.default_code == 'invalid':
        field, code = exc.get_codes().popitem()
        detail = {'field': field, 'message': exc.args[0][field][0]}
        if code[0] == 'unique': # 唯一性冲突
            response = {'code': 701, 'detail': detail}
        elif code[0] == 'required': # 缺失关键参数
            response = {'code': 702, 'detail': detail}
        elif code[0] == 'disabled': # user account is disabled
            response = {'code': 703, 'detail': detail}
        elif code[0] == 'disaccord':
            response = {'code': 704, 'detail': detail}
        else: #if code in ('does_not_exit', 'null', 'incorrect_type'): #无效的参数
            response = {'code': 705, 'detail': detail}
    else:
        detail = {'field': 'non_field_errors', 'message': exc.default_detail}
        response = {'code': exc.status_code, 'detail': detail}

    return response
