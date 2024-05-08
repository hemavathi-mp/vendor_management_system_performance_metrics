
from django.urls import path
from .views import vendorlist, vendorcreate, single_vendor_details, update_vendor_details, delete_vendor_details, \
    purchase_order_create, purchase_order_list, single_purchase_order_details, delete_purchase_order_details, \
    update_purchase_order_details, metrics, performance, acknowledge, MyTokenObtainPairView
from . import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('', views.getRoutes),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/vendors', vendorlist, name='vendor_list'),
    path('api/vendorcreate', vendorcreate, name='vendor_create'),
    path('api/vendors/<int:vendor_id>/', single_vendor_details, name='single_vendor_details'),
    path('api/vendors/<int:vendor_id>/', update_vendor_details, name='update_vendor_details'),
    path('api/vendors/<int:vendor_id>/', delete_vendor_details, name='delete_vendor_details'),
    path('api/purchase_orders', purchase_order_list, name='purchase_order_list'),
    path('api/purchase_orders_create', purchase_order_create, name='purchase_order_create'),
    path('api/purchase_orders/<int:po_id>/', single_purchase_order_details, name='single_purchase_order_details'),
    path('api/purchase_orders/<int:po_id>/u', update_purchase_order_details, name='update_purchase_order_details'),
    path('api/purchase_orders/<int:po_id>/', delete_purchase_order_details, name='delete_purchase_order_details'),
    path('api/vendors<int:vendor_id>/performance', performance, name='performance'),
    path('api/purchase_orders/<int:po_id>/acknowledge', acknowledge, name='acknowledge'),
]
