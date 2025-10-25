from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api.views import CustomerViewSet, ProductViewSet, InvoiceViewSet, InvoiceItemViewSet

router = routers.DefaultRouter()
router.register(r'customers',CustomerViewSet)
router.register(r'products', ProductViewSet )
router.register(r'invoices', InvoiceViewSet)
router.register(r'invoice-items', InvoiceItemViewSet)

urlpatterns=[
    path('admin/',admin.site.urls),
    path('api/', include(router.urls)), #tüm API endpointlere burdan erişilebilir

]