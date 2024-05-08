from django.db.models import Count, Sum, Avg, F, Q
from rest_framework import status
from rest_framework.generics import get_object_or_404
from django.db import models

from app.models import Vendor, PurchaseOrder, HistoricalPerformance
from app.serializer import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token',
        '/api/token/refresh',
    ]

    return Response(routes)


@api_view(['POST'])
def vendorcreate(request):
    serializer = VendorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendorlist(request):
    task_vendor_list= Vendor.objects.all()
    serializer = VendorSerializer(task_vendor_list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def single_vendor_details(request, vendor_id):
    details = Vendor.objects.get(id=vendor_id)
    if details:
        serializer = VendorSerializer(details, many=False)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_vendor_details(request, vendor_id):
    details = Vendor.objects.get(id=vendor_id)
    serializer = VendorSerializer(instance=details, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_vendor_details(request, vendor_id):
    data = get_object_or_404(Vendor, id=vendor_id)
    data.delete()
    return Response(status=status.HTTP_202_ACCEPTED)


# --------------------------------Purchase Order Tracking opertion----------------------------

@api_view(['POST'])
def purchase_order_create(request):
    try:
        vendor_id = Vendor.objects.get(id=request.data.get("vendor"))
    except Vendor.DoesNotExist:
        return False
    request.data["vendor"] = vendor_id
    result = PurchaseOrder.objects.create(**request.data)

    serializer = PurchaseOrderSerializer(PurchaseOrder.objects.get(id=result), many=False)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_order_list(request):
    po_list= PurchaseOrder.objects.all()
    serializer = PurchaseOrderSerializer(po_list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def single_purchase_order_details(request, po_id):
    details = PurchaseOrder.objects.get(id=po_id)
    if details:
        serializer = PurchaseOrderSerializer(details, many=False)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_purchase_order_details(request, po_id):
    details = PurchaseOrder.objects.get(id=po_id)
    serializer = PurchaseOrderSerializer(instance=details, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_purchase_order_details(request, po_id):
    data = get_object_or_404(PurchaseOrder, id=po_id)
    data.delete()
    return Response(status=status.HTTP_202_ACCEPTED)


# -------------------------------- Backend Logic for Performance Metrics----------------------------

def metrics(vendor_id):
    # -------------------On-Time Delivery Rate:-------------------
    # number of completed POs delivered on or before delivery_date
    p_sum = (PurchaseOrder.objects.filter(delivery_date__isnull=False,vendor=vendor_id)
                                          .aggregate(Count('id')))
    #  the total number of completed POs for that vendor.
    v_sum = PurchaseOrder.objects.filter(vendor=vendor_id, status="completed").aggregate(Count('id'))
    on_time_delivery_rate = 0
    try:
        on_time_delivery_rate = p_sum['id__count']/v_sum['id__count']
    except Exception as e:
        raise e

    # ---------------------------Quality Rating Average:------------------------
    quality_rating_avg=(PurchaseOrder.objects.filter(vendor=vendor_id, status="completed").exclude(quality_rating = None)
                        .aggregate(quality_rating_avg=Avg('id')))

    # -----------------------------Average Response Time--------------------------
    average_response_time = PurchaseOrder.objects.filter(acknowledgment_date__isnull = False, vendor=vendor_id).aggregate(
        average_response_time=Avg(
            F('issue_date') - F('acknowledgment_date'),
            output_field=models.DateField()
        )
    )

    # ----------------------------Fulfilment Rate-----------------

    total = PurchaseOrder.objects.filter(status='completed').aggregate(Count('id'))
    fulfillment_rate=0
    try:
        fulfillment_rate = total['id__count']/v_sum['id__count']
    except Exception as e:
        raise e

    data = {'on_time_delivery_rate':on_time_delivery_rate,
            'quality_rating_avg':(quality_rating_avg['quality_rating_avg']),
            'average_response_time':average_response_time['average_response_time'],
            'fulfillment_rate':fulfillment_rate}

    vendor_data = Vendor.objects.get(id=vendor_id)

    if vendor_data is not None:
        # Update Vendor details
        serializer = VendorSerializer(instance=vendor_data, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

    data["vendor"] = vendor_data

    hp = HistoricalPerformance.objects.get(vendor=vendor_id)
    if hp is not None:
        serializer = HistoricalPerformanceSerializer(instance=hp, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
    else:
        result = HistoricalPerformance.objects.create(**data)
        h_serializer = HistoricalPerformanceSerializer(HistoricalPerformance.objects.get(id=result), many=True)
        return Response(h_serializer.data)

    return Response(serializer.data)

# ------------------------- VendorPerformanceEndpoint(GET/api/vendors/{vendor_id}/performance)----------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def performance(request, vendor_id):
    details = Vendor.objects.filter(id=vendor_id).values('on_time_delivery_rate','quality_rating_avg',
                                                         'average_response_time','fulfillment_rate')
    if details:
        return Response(details)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


# ----------------------------- UpdateAcknowledgmentEndpoint:----------------------
@api_view(['POST'])
def acknowledge(request, po_id):
    details = PurchaseOrder.objects.get(id=po_id)
    serializer = PurchaseOrderSerializer(instance=details, data=request.data, partial=True)
    print(details.vendor)
    if serializer.is_valid():
        serializer.save()
        metrics(details.vendor)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
