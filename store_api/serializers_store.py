"""
2020.02.19
    定义和店铺操作API接口相关的序列化类
"""
from rest_framework import serializers
from .models import Store

class StoreSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Store
        exclude = ('id',)
        
        extra_kwargs = {
            'owner': {'write_only': True},
            'category': {'write_only': True},
            }

    def create(self, validated_data):
        return Store.objects.create(**validated_data)

    def update(self, instance, validated_data):
        owner_id = instance.owner.id
        instance.owner = validated_data.get('owner', instance.owner)
        instance.name = validated_data.get('name', instance.name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.category = validated_data.get('category', instance.category)
        instance.addr_province = validated_data.get('addr_province', instance.addr_province)
        instance.addr_city = validated_data.get('addr_city', instance.addr_city)
        instance.addr_district = validated_data.get('addr_district', instance.addr_district)
        instance.addr_street = validated_data.get('addr_street', instance.addr_street)
        instance.addr_detail = validated_data.get('addr_detail', instance.addr_detail)
        instance.photo_name = validated_data.get('photo_name', instance.photo_name)
        instance.save()

        #判断店主是否更改，更新对应用户的is_staff属性
        if owner_id != instance.owner.id:
            if not Store.objects.filter(owner=owner_id):
                user = XingUser.objects.get(pk=owner_id)
                user.is_staff = False
                user.save()
            user = XingUser.objects.get(pk=instance.owner.id)
            user.is_staff = True
            user.save()

        return instance

    