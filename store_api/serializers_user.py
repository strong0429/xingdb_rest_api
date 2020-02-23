"""
2020.02.18
    定义和用户API接口相关的序列化类
"""
import re
from rest_framework import serializers

from .models import XingUser,AppVersion, StoreStaff
from .serializers_store import StoreSerializer, StoreStaffSerializer

#App版本序列化类
class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        exclude = ('id',)
        extra_kwargs = {
            'ver_code': {'read_only': True},
            'ver_txt': {'read_only': True},
        }

#短信验证码的序列化类
class SMSCodeSerializer(serializers.Serializer):
    """
    验证是否为有效手机号码, 支持号码：
    移动：134，135，136，137，138，139，147，150，151，152，157，158，159，178，182，183，184，187，188，198
    联通：130，131，132，145，155，156，166，176，185，186
    电信：133，153，173，177，180，181，189，199
    """
    mobile = serializers.CharField(max_length=12, required=True)

    def validate_mobile(self, value):
        exp = '^1((3[\d])|(4[75])|(5[^3|4])|(66)|(7[3678])|(8[\d])|(9[89]))\d{8}$'
        if re.findall(exp, value):
            #判断号码是否已注册
            if XingUser.objects.filter(mobile=value):
                raise serializers.ValidationError('手机号码已注册')
            return value
        else:
            raise serializers.ValidationError('无效的手机号码')

#用户注册序列化类
class UserRegisterSerializer(serializers.ModelSerializer):
    sms_code = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        model = XingUser
        fields = ['username', 'password', 'mobile', 'sms_code']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    #'sms_code'只用于传入数据，没有和Model字段对应，反序列化验证时剔除
    def validate(self, attrs):
        del attrs['sms_code']
        return attrs
    
    def create(self, validated_data):
        user = XingUser.objects.create_user(**validated_data)
        user.save()
        return user

#用户登录、查询、更新(不包括修改密码）序列化类
class XingUserSerializer(serializers.ModelSerializer):
    #stores = StoreSerializer(many=True, read_only=True)  #整个类
    #stores = serializers.StringRelatedField(many=True, read_only=True)  #类的字符串
    #stores = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  #类的主键
    #stores = serializers.SlugRelatedField(many=True, read_only=True, slug_field=('id', 'name'))  #slug_field指定的字段

    stores = serializers.SerializerMethodField()

    class Meta:
        model = XingUser
        exclude = ('password', 'is_superuser', 'is_staff')
        #以下属性不被修改
        extra_kwargs = {
            'is_active': {'read_only': True},
        }

    def get_stores(self, obj):
        data = []
        for store in obj.store_set.all():
            tmp = {}
            tmp['id'] = store.id
            tmp['name'] = store.name
            ss = StoreStaff.objects.get(store=store.id, staff=obj.id)
            tmp['position'] = ss.position
            data.append(tmp)
        return data

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.id_card = validated_data.get('id_card', instance.id_card)
        instance.save()
        return instance

#更改用户密码序列化类
class PasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=8, write_only=True)

    class Meta:
        model = XingUser
        fields = ['password', 'old_password']
        extra_kwargs = {
            'password': {'write_only': True},
        }
        
    def validate(self, attrs):
        del attrs['old_password']
        return attrs
    
    def update(self, instance, validated_data):
        #set_password()对密码进行了加密处理
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
        
    
