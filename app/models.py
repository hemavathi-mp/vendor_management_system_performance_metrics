import uuid

from django.db import models
from django.db.models.signals import post_save, pre_save

from app.static_data import ORDER_STATUS


class Vendor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True,max_length=255)
    contact_details = models.TextField(null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    vendor_code = models.CharField(max_length=255, default=uuid.uuid4)
    on_time_delivery_rate = models.FloatField(null=True,blank=True)
    # on_time_delivery_rate = models.DecimalField(max_digits=10, decimal_places=2)
    quality_rating_avg = models.FloatField(null=True,blank=True)
    average_response_time = models.CharField(max_length=255,null=True, blank=True)
    fulfillment_rate = models.FloatField(null=True,blank=True)

    def __int__(self):
        return self.id

    class Meta:
        ordering = ['name']


class PurchaseOrder(models.Model):
    id = models.AutoField(primary_key=True)
    po_number = models.CharField(max_length=255, default=uuid.uuid4)
    vendor = models.ForeignKey("Vendor",on_delete=models.CASCADE, related_name='purchaseorder')
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(auto_now_add=False,null=True,blank=True)
    items = models.JSONField()
    quantity = models.IntegerField(null=True,blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, null=True, blank=True)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateField(auto_now_add=False,null=True,blank=True)
    acknowledgment_date = models.DateField(auto_now_add=False,null=True,blank=True)

    def __int__(self):
        return self.id

# def post_save_status(sender, instance, *args,**kwargs):
#     print("SSSSSSSSSSSSSSSSS",instance)
#     print("SSSSSSSSSSSSSSSSS",instance.items)
#     if instance.status == "completed":
#         metrics(instance.vendor)
#

# post_save.connect(post_save_status, sender=PurchaseOrder)


class HistoricalPerformance(models.Model):
    id = models.AutoField(primary_key=True)
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE, related_name='historicalperformance')
    date = models.DateField(auto_now_add=True,null=True, blank=True)
    on_time_delivery_rate = models.FloatField(null=True, blank=True)
    quality_rating_avg = models.FloatField(null=True, blank=True)
    average_response_time = models.CharField(max_length=255,null=True, blank=True)
    fulfillment_rate = models.FloatField(null=True, blank=True)

    def __int__(self):
        return self.id

