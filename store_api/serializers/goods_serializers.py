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
            'store': {'write_only': True},
        }