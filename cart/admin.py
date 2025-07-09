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


from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    readonly_fields = ['product', 'size', 'color', 'quantity', 'price', 'total_display']  # ✅ total_display must be here only

    fields = ['product', 'size', 'color', 'quantity', 'price', 'total_display']  # ✅ Now it's safe to use here

    def total_display(self, obj):
        return f"₹{obj.price * obj.quantity:.2f}"
    total_display.short_description = 'Total'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_info', 'status', 'payment_status', 'total_display', 'created_short']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'firebase_uid', 'email', 'first_name', 'last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'total_display']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Details', {
            'fields': ('order_number', 'status', 'payment_status', 'payment_method')
        }),
        ('Customer', {
            'fields': (('first_name', 'last_name'), 'email', 'phone', 'firebase_uid')
        }),
        ('Shipping', {
            'fields': ('address', ('city', 'state'), ('zip_code', 'country'))
        }),
        ('Payment', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': (('subtotal', 'tax'), ('shipping', 'discount'), 'total')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_display(self, obj):
        return f"₹{obj.total:.2f}"
    total_display.short_description = 'Total'
    
    def customer_info(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    customer_info.short_description = 'Customer'
    
    def created_short(self, obj):
        return obj.created_at.strftime("%b %d, %Y")
    created_short.short_description = 'Created'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'product_link', 'size', 'color', 'quantity', 'price_display', 'total_display']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'product__name']
    readonly_fields = ['order', 'product', 'size', 'color', 'quantity', 'price']
    
    def order_link(self, obj):
        return f"Order #{obj.order.order_number}"
    order_link.short_description = 'Order'
    order_link.admin_order_field = 'order__order_number'
    
    def product_link(self, obj):
        return obj.product.name
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'
    
    def price_display(self, obj):
        return f"₹{obj.price:.2f}"
    price_display.short_description = 'Price'
    
    def total_display(self, obj):
        return f"₹{obj.price * obj.quantity:.2f}"
    total_display.short_description = 'Total'