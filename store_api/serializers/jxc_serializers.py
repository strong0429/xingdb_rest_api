from rest_framework import serializers

from ..models import SaleRecord, Purchase

class SaleRecordSerializer(serializers.ModelSerializer):
    goods_name = serializers.ReadOnlyField(source='goods.name')
    goods_barcode = serializers.ReadOnlyField(source='goods.barcode')
    clerk_name = serializers.ReadOnlyField(source='clerk.username')

    class Meta:
        model = SaleRecord
        exclude = ('id', )
        extra_kwargs = {
            'store': {'write_only': True},
            'clerk': {'write_only': True},
            'goods': {'write_only': True},
        }

    def update(self, instance, validated_data):
        instance.mode = validated_data.get('mode', instance.mode)
        instance.save()
        
        return instance

class PurchaseSerializer(serializers.ModelSerializer):
    goods_name = serializers.ReadOnlyField(source='goods.name')
    buyer_name = serializers.ReadOnlyField(source='buyer.username')
    #supplier_name = serializers.ReadOnlyField(source='supplier.name')
    #supplier_contactor = serializers.ReadOnlyField(source='supplier.contactor')
    #supplier_phone = serializers.ReadOnlyField(source='supplier.phone')

    class Meta:
        model = Purchase
        exclude = ('id',)
        extra_kwargs = {
            'store': {'write_only': True},
            'buyer': {'write_only': True},
            #'supplier': {'write_only': True},
        }
