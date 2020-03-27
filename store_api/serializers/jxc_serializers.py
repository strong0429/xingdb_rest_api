from rest_framework import serializers

from ..models import SaleRecord

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