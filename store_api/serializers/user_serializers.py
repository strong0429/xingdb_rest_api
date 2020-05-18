"""
2020.02.18
    定义和用户API接口相关的序列化类
"""
import re
from rest_framework import serializers

from public.utils import MobileValidator
from ..models import User, StoreStaff
from . import StoreSerializer, StoreStaffSerializer

#短信验证码的序列化类
class SMSCodeSerializer(serializers.Serializer):
    mobile_validator = MobileValidator()

    mobile = serializers.CharField(max_length=12, validators=[mobile_validator])
    existed = serializers.BooleanField(default=False)

    def validate(self, attrs):
        mobile = attrs.get('mobile')
        existed = attrs.get('existed')

        objs = User.objects.filter(mobile=mobile)
        if existed:   #判断号码是否已注册
            if not objs:
                raise serializers.ValidationError('手机号码未注册。', 'does_not_exit')
        else:
            if objs:
                raise serializers.ValidationError('手机号码已注册。', 'unique')

        return attrs

#用户注册序列化类
class UserRegisterSerializer(serializers.ModelSerializer):
    sms_code = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['mobile', 'password', 'sms_code']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    #'sms_code'只用于传入数据，没有和Model字段对应，反序列化验证时剔除
    def validate(self, attrs):
        del attrs['sms_code']
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

#用户登录、查询、更新(不包括修改密码）序列化类
class UserSerializer(serializers.ModelSerializer):
    #stores = serializers.StringRelatedField(many=True, read_only=True)  #类的字符串
    #stores = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  #类的主键
    #stores = serializers.SlugRelatedField(many=True, read_only=True, slug_field=('id', 'name'))  #slug_field指定的字段
    
    stores = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ('is_admin',)
        #以下属性不被修改
        extra_kwargs = {
            'is_active': {'read_only': True},
            'password': {'write_only': True},
        }
    
    def get_stores(self, obj):
        data = []
        store_staff = obj.storestaff_set.all()
        for ss in store_staff:
            data.append(StoreSerializer(ss.store).data)
            data[-1]['position'] = ss.position
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.autonym = validated_data.get('autonym', instance.autonym)
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.id_card = validated_data.get('id_card', instance.id_card)
        instance.wechat = validated_data.get('wechat', instance.wechat)
        instance.email = validated_data.get('email', instance.email)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.save()
        return instance

#更改用户密码序列化类
class PasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=16, write_only=True)

    class Meta:
        model = User
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
        
    
