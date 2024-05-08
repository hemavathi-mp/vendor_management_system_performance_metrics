from rest_framework import serializers
from .models import Vendor, PurchaseOrder, HistoricalPerformance


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    # def create(self, validated_data):
    #     vendor = self.context["vendor"]
    #     data = PurchaseOrder.objects.create(vendor=vendor, **self.validated_data)
    #     return data


class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalPerformance
        fields = '__all__'

