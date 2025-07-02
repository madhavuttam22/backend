from rest_framework import serializers
from .models import Products, Category, Size, ProductSize, Color, ProductColor, ProductColorImage

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_code']

class ProductColorImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductColorImage
        fields = ['id', 'image_url', 'is_default', 'order']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class ProductColorSerializer(serializers.ModelSerializer):
    color = ColorSerializer()
    images = ProductColorImageSerializer(many=True)
    
    class Meta:
        model = ProductColor
        fields = ['color', 'is_active', 'images']

class ProductSizeSerializer(serializers.ModelSerializer):
    size = SizeSerializer()
    
    class Meta:
        model = ProductSize
        fields = ['size', 'stock', 'is_active']

# Add this missing serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    colors = serializers.SerializerMethodField()
    sizes = ProductSizeSerializer(many=True, source='productsize_set.all')
    
    class Meta:
        model = Products
        fields = ['id', 'name', 'currentprice', 'orignalprice', 'description', 
                 'colors', 'sizes', 'is_top_product', 'is_best_seller']
    
    def get_colors(self, obj):
        colors = obj.colors.all().order_by('order')
        return ProductColorSerializer(colors, many=True, context=self.context).data