"""
2020.02.18
    实现短消息验证码、用户注册、用户登录、修改密码等API接口
"""
import re
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_jwt.utils import jwt_encode_handler
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

from django.contrib.auth.hashers import check_password

from public.utils import RegisterAuthentication, TokenPermission
from ..models import XingUser
from ..serializers import (
    AppVersionSerializer, 
    TokenSerializer,
    SMSCodeSerializer, 
    PasswordSerializer,
    UserRegisterSerializer,
    XingUserSerializer)

#获取App版本信息API
class AppVersionView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        if 'app_name' in request.query_params:
            app_name = request.query_params['app_name']
        elif 'app_name' in request.data:
            #为了兼容http测试工具
            app_name = request.data['app_name']
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            app = AppVersion.objects.get(app_name=app_name)
        except AppVersion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AppVersionSerializer(app)
        return Response(serializer.data)

# 获取Token API
class TokenView(JSONWebTokenAPIView):
    serializer_class = TokenSerializer

#获取短消息验证码API
class SMSCodeView(APIView):
    permission_classes = ()
    #authentication_classes = ()

    def handle_exception(self, exc):
        if exc.default_code == 'invalid':
            # {'mobile': ['registered']}
            if exc.get_codes()['mobile'][0] == 'registered':
                response = {'code': 701, 'detail': '手机号码已注册。'}
            else:
                response = {'code': 702, 'detail': '无效的手机号码。'}
        else:
            response = {'code': exc.status_code, 'detail': exc.default_detail}
        return Response(response, status=exc.status_code)
    
    def post(self, request, format=None):
        if request.user.username != 'Authenticator':
            raise PermissionDenied

        serializer = SMSCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']
        #生成随机验证码，向目标手机发送验证码，用手机号码和验证码生成token
        token = jwt_encode_handler({
            'exp': timezone.now() + timezone.timedelta(minutes=3),  #有效期：3分钟
            'mobile': mobile,
            'sms_code': '118590'})
        return Response({'token': token}, status=status.HTTP_200_OK)

#用户登录API
class UserLoginView(JSONWebTokenAPIView):
    authentication_classes = (JSONWebTokenAuthentication,)

    serializer_class = JSONWebTokenSerializer
    
    def handle_exception(self, exc):
        if exc.default_code == 'invalid':
            response = {'code': 700, 'detail': '用户名不存在或密码错误。'}
        else:
            response = {'code': exc.status_code, 'detail': exc.default_detail}
        return Response(response, status=exc.status_code)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # raise_exception=True,保证异常被handle_exception()处理
        serializer.is_valid(raise_exception=True)
        user = serializer.object.get('user') or request.user
        token = serializer.object.get('token')
        response_data = {
            'token': token,
            'user': XingUserSerializer(user).data
            }
        user.last_login = timezone.now()
        user.save()
        return Response(response_data, status=status.HTTP_200_OK)

#用户注册API
class UserRegisterView(APIView):
    permission_classes = ()
    authentication_classes = [RegisterAuthentication]

    def handle_exception(self, exc):
        if exc.default_code == 'invalid':
            try:
                if exc.get_codes()['username'][0] == 'unique':
                    response = {'code': 701, 'detail': '用户名已存在。'}
                else:
                    response = {'code': 703, 'detail': '缺失关键参数。'}
            except:
                    response = {'code': 703, 'detail': '缺失关键参数。'}
        else:
            response = {'code': exc.status_code, 'detail': exc.default_detail}
        return Response(response, status=exc.status_code)
    
    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        #从token中取出电话号码和校验码进行校验
        try:
            #payload = jwt_decode_handler(token)
            payload = request.auth
            if payload['mobile'] != request.data['mobile'] or\
                payload['sms_code'] != request.data['sms_code']:
                return Response({'code': 704, 'detail': '手机和验证码不一致'}, 
                        status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'code': 401, 'detail': '无效的Token'}, 
                status=status.HTTP_401_UNAUTHORIZED)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
#用户信息查询、更新API
class UserDetailView(APIView):
    def handle_exception(self, exc):
        if exc.default_code == 'invalid':
            codes = exc.get_codes()
            if 'username' in codes and codes['username'][0] == 'unique':
                response = {'code': 701, 'detail': '用户名已存在。'}
            elif 'mobile' in codes and codes['mobile'][0] == 'unique':
                response = {'code': 701, 'detail': '手机号码已存在。'}
            elif 'id_card' in codes and codes['id_card'][0] == 'unique':
                response = {'code': 701, 'detail': '身份证号码重复。'}
            else:
                response = {'code': 703, 'detail': '缺失关键参数。'}
        else:
            response = {'code': exc.status_code, 'detail': exc.default_detail}
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
            exp = '^1((3[\d])|(4[75])|(5[^3|4])|(66)|(7[3678])|(8[\d])|(9[89]))\d{8}$'
            if not re.findall(exp, request.data['mobile']):
                response = {'code': 702, 'detail': '无效的手机号码。'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
        if exc.default_code == 'invalid':
            response = {'code': 703, 'detail': '缺失关键参数。'}
        else:
            response = {'code': exc.status_code, 'detail': exc.default_detail}
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
            response = {'code': 700, 'detail': '密码错误。'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

