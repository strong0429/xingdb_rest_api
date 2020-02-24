"""
2020.02.18
    实现短消息验证码、用户注册、用户登录、修改密码等API接口
"""
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

from django.contrib.auth.hashers import check_password

from public.utils import RegisterAuthentication
from store_api.serializers import (
    AppVersionSerializer, 
    SMSCodeSerializer, 
    UserRegisterSerializer,
    XingUserSerializer)
from store_api.models import XingUser

#获取App版本信息API
class AppVersionView(APIView):
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

#获取短消息验证码API
class SMSCodeView(APIView):
    #permission_classes = ()
    #authentication_classes = ()

    def post(self, request, format=None):
        if request.user.username != 'Token':
            return Response({'error': '未授权'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SMSCodeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            #response_data = jwt_response_payload_handler(token, user, request)
            response_data = {
                'token': token,
                'user': XingUserSerializer(user).data
                }
            user.last_login = timezone.now()
            user.save()
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#用户注册API
class UserRegisterView(APIView):
    permission_classes = ()
    authentication_classes = [RegisterAuthentication]

    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #从token中取出电话号码和校验码进行校验
        try:
            #payload = jwt_decode_handler(token)
            payload = request.auth
            if payload['mobile'] != request.data['mobile'] or\
                payload['sms_code'] != request.data['sms_code']:
                    return Response({'register': ['数据校验不一致']}, 
                        status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'token': ['无效的Token']}, 
                status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
#用户信息查询、更新API
class UserDetailView(APIView):
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
        serializer = XingUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#用户修改密码API
class PasswordView(APIView):
    def put(self, request, pk, format=None):
        #只允许本人修改密码
        if pk != request.user.id:
            raise PermissionDenied

        user = request.user
        print(user.password)
        serializer = PasswordSerializer(user, request.data)
        if serializer.is_valid() and check_password(request.data['old_password'], user.password):
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

