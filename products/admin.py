from django.contrib import admin
from django.utils.html import format_html
from .models import *

class ProductColorImageInline(admin.TabularInline):
    model = ProductColorImage
    extra = 1
    fields = ['image', 'is_default', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    inlines = [ProductColorImageInline]
    fields = ['color', 'is_active', 'order']  
    show_change_link = True

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    fields = ['size', 'stock', 'is_active']

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductColorInline, ProductSizeInline]
    list_display = ('name', 'category', 'currentprice', 'orignalprice')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    inlines = [ProductColorImageInline]
    list_display = ('product', 'color', 'is_active')
    list_filter = ('is_active', 'product__category')

@admin.register(ProductColorImage)
class ProductColorImageAdmin(admin.ModelAdmin):
    list_display = ('product_color', 'image_preview', 'is_default', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

# Register other models
admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Color)