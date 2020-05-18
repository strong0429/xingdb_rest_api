from rest_framework import serializers

from ..models import SaleRecord, Purchase, Inventory

class SaleRecordSerializer(serializers.ModelSerializer):
    goods_name = serializers.ReadOnlyField(source='goods.name')
    #goods_barcode = serializers.ReadOnlyField(source='goods.barcode')
    clerk_name = serializers.ReadOnlyField(source='clerk.username')

    class Meta:
        model = SaleRecord
        exclude = ('id', )
        extra_kwargs = {
            'store': {'write_only': True},
            'clerk': {'write_only': True},
            #'goods': {'write_only': True},
        }

    def update(self, instance, validated_data):
        instance.mode = validated_data.get('mode', instance.mode)
        instance.save()
        
        return instance

class PurchaseSerializer(serializers.ModelSerializer):
    goods_name = serializers.ReadOnlyField(source='goods.name')
    buyer_name = serializers.ReadOnlyField(source='buyer.username')
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    #supplier_contactor = serializers.ReadOnlyField(source='supplier.contactor')
    #supplier_phone = serializers.ReadOnlyField(source='supplier.phone')

    #临时字段，配合更新 storage 表
    sale_price = serializers.FloatField(write_only=True)
    def validate(self, attrs):
        del attrs['sale_price']
        return attrs

    class Meta:
        model = Purchase
        exclude = ('id',)
        extra_kwargs = {
            'store': {'write_only': True},
            'buyer': {'write_only': True},
            #'supplier': {'write_only': True},
        }


class StockSerializer(serializers.ModelSerializer):
    goods_name = serializers.ReadOnlyField(source='goods.name')
    barcode = serializers.ReadOnlyField(source='goods.barcode')
    editor_name = serializers.ReadOnlyField(source='editor.username')

    class Meta:
        model = Inventory
        exclude = ('id',)
        extra_kwargs = {
            'store': {'write_only': True},
            'goods': {'write_only': True},
            'editor': {'write_only': True},
        }

    def update(self, instance, validated_data):
        instance.price = validated_data.get('price', instance.price)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.date_ps = validated_data.get('date_ps', instance.date_ps)
        instance.date_pe = validated_data.get('date_pe', instance.date_pe)
        instance.editor = validated_data.get('editor', instance.editor)
        instance.edit_date = validated_data.get('edit_date', instance.edit_date)
        instance.save()
        return instance