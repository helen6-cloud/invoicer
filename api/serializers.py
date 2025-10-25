from rest_framework import serializers
from .models import Customer, Product, Invoice, InvoiceItem

# -----------------------
# Customer Serializer
# -----------------------
class CustomerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Customer
        fields = '__all__'

# -----------------------
# Product Serializer
# -----------------------
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# -----------------------
# InvoiceItem Serializer
# -----------------------
class InvoiceItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product', queryset=Product.objects.all(), write_only=True
    )

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceItem
        fields = ['id','product','product_id','quantity','unit_price','total_price']

    def get_total_price(self, obj):
        return obj.total_price()

# -----------------------
# Invoice Serializer
# -----------------------
class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        source='customer', queryset=Customer.objects.all(), write_only=True
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ['id','customer','customer_id','date','due_date','notes','items','total']

    def get_total(self, obj):
        return obj.total()

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)
        for item in items_data:
            prod = item.pop('product')
            InvoiceItem.objects.create(invoice=invoice, product=prod, **item)
        return invoice
