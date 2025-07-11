from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.models import *

# serializers.py
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    size_name = serializers.CharField(source='size.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True, allow_null=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'size', 'size_name', 
                 'color', 'color_name', 'quantity', 'price', 'total', 'image']
    
    def get_image(self, obj):
        if obj.color:
            # Get the first image for this product+color combination
            product_color = ProductColor.objects.filter(
                product=obj.product,
                color=obj.color
            ).first()
            if product_color and product_color.images.exists():
                request = self.context.get('request')
                image = product_color.images.first()
                return request.build_absolute_uri(image.image.url)
        
        # Fallback to product's main image
        if obj.product.images.exists():
            request = self.context.get('request')
            image = obj.product.images.first()
            return request.build_absolute_uri(image.image.url)
        
        return None

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure all numeric fields are numbers, not strings
        numeric_fields = ['total', 'subtotal', 'shipping', 'tax', 'discount']
        for field in numeric_fields:
            if field in data and data[field] is not None:
                data[field] = float(data[field])
        return data