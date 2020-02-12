import re
from rest_framework import serializers

from .models import XingUser

class SMSSerializer(serializers.Serializer):
    """
    验证是否为有效手机号码, 支持号码：
    移动：134，135，136，137，138，139，147，150，151，152，157，158，159，178，182，183，184，187，188，198
    联通：130，131，132，145，155，156，166，176，185，186
    电信：133，153，173，177，180，181，189，199
    """

    mobile = serializers.CharField(max_length=12, required=True)
    sms_code = serializers.CharField(max_length=6, required=False)
    
    def validate_mobile(self, value):
        exp = '^1((3[\d])|(4[75])|(5[^3|4])|(66)|(7[3678])|(8[\d])|(9[89]))\d{8}$'
        if re.findall(exp, value):
            return value
        else:
            raise serializers.ValidationError('无效的手机号码')

class XingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = XingUser
        fields = ['username', 'mobile', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = XingUser.objects.create_user(**validated_data)
        user.save()
        return user