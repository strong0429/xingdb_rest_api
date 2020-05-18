from django.utils import timezone
from django.conf import settings
from rest_framework import serializers
from django.utils.translation import ugettext as _
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
        apps = AppVersion.objects.filter(app_name=attrs.get('name')).order_by('-date_pub')
        if not apps:
            raise serializers.ValidationError('对象不存在。', 'dose_not_exit')

        payload = {
            'app_name': apps[0].app_name,
            'ver_code': apps[0].ver_code,
            'exp': timezone.now() + settings.JWT_AUTH['APP_TOKEN_EXP_DELTA']
            }

        return {
            'token': jwt_encode_handler(payload),
            'app_version': AppVersionSerializer(apps[0]).data
        }

