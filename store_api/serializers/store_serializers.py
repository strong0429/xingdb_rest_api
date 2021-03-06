"""
2020.02.19
    定义和店铺操作API接口相关的序列化类
"""
from rest_framework import serializers
from ..models import Store, StoreStaff, User

class StoreStaffSerializer(serializers.ModelSerializer):
    staff_name = serializers.ReadOnlyField(source='staff.username')
    store_name = serializers.ReadOnlyField(source='store.name')

    class Meta:
        model = StoreStaff
        exclude = ('id', )

class StoreSerializer(serializers.ModelSerializer):
    #staffs = serializers.SerializerMethodField()
    #owner = serializers.SerializerMethodField()
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Store
        #fields='__all__'
        exclude = ('staffs',)
        
        extra_kwargs = {
            'category': {'write_only': True},
            'id': {'read_only': True},
            }
            
    def get_owner(self, obj):
        staffs = obj.staffs.all()
        #ss = staff.storestaff_set.get(store=obj.id, staff__in=staffs, position='O')
        ss = StoreStaff.objects.get(store=obj.id, staff__in=staffs, position='O')
        return ss.staff.id

    def create(self, validated_data):
        return Store.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.category = validated_data.get('category', instance.category)
        instance.addr_province = validated_data.get('addr_province', instance.addr_province)
        instance.addr_city = validated_data.get('addr_city', instance.addr_city)
        instance.addr_district = validated_data.get('addr_district', instance.addr_district)
        instance.addr_street = validated_data.get('addr_street', instance.addr_street)
        instance.addr_detail = validated_data.get('addr_detail', instance.addr_detail)
        instance.logo = validated_data.get('logo', instance.logo)
        instance.paycode_wec = validated_data.get('paycode_wec', instance.paycode_wec)
        instance.paycode_ali = validated_data.get('paycode_ali', instance.paycode_ali)
        instance.save()
        return instance

