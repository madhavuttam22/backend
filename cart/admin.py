from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'firebase_uid', 'created_at', 'item_count', 'total']
    search_fields = ['firebase_uid']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('firebase_uid_display', 'product', 'quantity', 'price', 'subtotal', 'created_at')
    search_fields = ['cart__firebase_uid', 'product__name']

    def firebase_uid_display(self, obj):
        return obj.cart.firebase_uid
    firebase_uid_display.short_description = 'Firebase UID'
