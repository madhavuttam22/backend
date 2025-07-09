from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.models import Products, Size, Color

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    size_name = serializers.CharField(source='size.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True, allow_null=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'size', 'size_name', 
                 'color', 'color_name', 'quantity', 'price', 'total']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'