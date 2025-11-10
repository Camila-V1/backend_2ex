from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeliveryZoneViewSet, DeliveryProfileViewSet, DeliveryViewSet,
    WarrantyViewSet, ReturnViewSet, RepairViewSet
)

router = DefaultRouter()
router.register(r'zones', DeliveryZoneViewSet, basename='delivery-zone')
router.register(r'profiles', DeliveryProfileViewSet, basename='delivery-profile')
router.register(r'deliveries', DeliveryViewSet, basename='delivery')
router.register(r'warranties', WarrantyViewSet, basename='warranty')
router.register(r'returns', ReturnViewSet, basename='return')
router.register(r'repairs', RepairViewSet, basename='repair')

urlpatterns = [
    path('', include(router.urls)),
]
