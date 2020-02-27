"""
2020.02.19
    定义和店铺操作API接口相关的序列化类
"""
from rest_framework import serializers
from ..models import Store, StoreStaff, XingUser

class StoreStaffSerializer(serializers.ModelSerializer):
    staff_name = serializers.ReadOnlyField(source='staff.username')
    store_name = serializers.ReadOnlyField(source='store.name')

    class Meta:
        model = StoreStaff
        exclude = ('id', )

class StoreSerializer(serializers.ModelSerializer):
    #staffs = serializers.SerializerMethodField()
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Store
        exclude = ('id',)
        
        extra_kwargs = {
            'category': {'write_only': True},
            }
            
    def get_staffs(self, obj):
        data = []
        for staff in obj.staffs.all():
            ss = staff.storestaff_set.get(store=obj.id)
            #ss = StoreStaff.objects.get(store=obj.id, staff=staff.id)
            tmp = {}
            tmp['id'] = staff.id
            tmp['username'] = staff.username
            tmp['mobile'] = staff.mobile
            tmp['position'] = ss.position
            data.append(tmp)
        return data

    def create(self, validated_data):
        return Store.objects.create(**validated_data)

    def update(self, instance, validated_data):
        #owner_id = instance.owner.id
        #instance.owner = validated_data.get('owner', instance.owner)
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
        return instance

