from django.db.models.signals import post_save
from app.models import PurchaseOrder
from app.views import metrics


def post_save_status(sender, instance, *args,**kwargs):
    if instance.status == "completed":
        metrics(instance.vendor)

post_save.connect(post_save_status, sender=PurchaseOrder)
