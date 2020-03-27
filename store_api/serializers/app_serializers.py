from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _
from rest_framework.exceptions import PermissionDenied
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from ..models import AppVersion

#App版本序列化类
class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        exclude = ('id',)
        extra_kwargs = {
            'ver_code': {'read_only': True},
            'ver_txt': {'read_only': True},
        }


# App Token 序列化类
class AppTokenSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        if not attrs.get('name'):
            msg = _('必须提供App名字。')
            raise serializers.ValidationError(msg)
        apps = AppVersion.objects.filter(app_name=attrs.get('name'))
        if not apps:
            raise serializers.ValidationError('对象不存在。', 'dose_not_exit')

        payload = {
            'app_name': apps[len(apps)-1].app_name,
            'ver_code': apps[len(apps)-1].ver_code,
            'exp': timezone.now() + timezone.timedelta(seconds=5000)}

        return {
            'token': jwt_encode_handler(payload),
            'app_version': AppVersionSerializer(apps[len(apps)-1]).data
        }

