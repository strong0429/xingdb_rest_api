from rest_framework import serializers

from ..models import Goods, GoodsCategoryL1, GoodsCategoryL2, Supplier

class GoodsSerializer(serializers.ModelSerializer):
    cl2_name = serializers.ReadOnlyField(source='category.name')
    cl1_name = serializers.ReadOnlyField(source='category.category_l1.name')

    class Meta:
        model = Goods
        exclude = ('id',)
        extra_kwargs = {
            'category': {'write_only': True},
        }

    def validate_barcode(self, value):
        if len(value) == 13 or len(value) == 8:
            return value
        raise serializers.ValidationError('无效的商品条码。')

class SupplierSerializer(serializers.ModelSerializer):
    def validate_phone(self, value):
        return value

    class Meta:
        model = Supplier
        fields = '__all__'
        extra_kwargs = {
            'store': {'write_only': True}
        }

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.addr = validated_data.get('addr', instance.addr)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.contacter = validated_data.get('contacter', instance.contacter)
        instance.save()
        return instance

class GoodsCategory2Serializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryL2
        fields = '__all__'
        extra_kwargs = {
            'category_l1': {'write_only': True},
        }

class GoodsCategory1Serializer(serializers.ModelSerializer):
    sub_category = serializers.SerializerMethodField()

    class Meta:
        model = GoodsCategoryL1
        fields = '__all__'

    def get_sub_category(self, obj):
        subCategories = obj.goodscategoryl2_set.all()
        return GoodsCategory2Serializer(subCategories, many=True).data