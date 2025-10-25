from rest_framework import viewsets
from .models import Customer, Product, Invoice, InvoiceItem
from .serializers import CustomerSerializer, ProductSerializer, InvoiceSerializer, InvoiceItemSerializer

# -----------------------
# Müşteri API
# -----------------------
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

# -----------------------
# Ürün API
# -----------------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# -----------------------
# Fatura API
# -----------------------
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

# -----------------------
# Fatura kalemi API
# -----------------------
class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
