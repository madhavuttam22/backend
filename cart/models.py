from django.db import models
from django.conf import settings
from products.models import *  # Your Products model


from django.db import models
from django.conf import settings
from products.models import Products, Size, Color
from users.models import  FirebaseUser as User

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('cod', 'Cash on Delivery'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    firebase_uid = models.CharField(max_length=128)  # For Firebase users
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    
    # Shipping information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    is_direct_purchase = models.BooleanField(default=False)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total(self):
        return self.price * self.quantity

class Cart(models.Model):
        firebase_uid = models.CharField(max_length=128, unique=True)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"Cart - {self.firebase_uid[:8]}..."  # Shortened for display

        @property
        def total(self):
            return sum(item.subtotal for item in self.items.all())

        @property
        def item_count(self):
            return self.items.count()

class CartItem(models.Model):
        cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
        product = models.ForeignKey(Products, on_delete=models.CASCADE)
        size = models.ForeignKey(Size, on_delete=models.CASCADE)
        color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
        quantity = models.PositiveIntegerField(default=1)
        price = models.DecimalField(max_digits=10, decimal_places=2)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            return self.product.name

        @property
        def subtotal(self):
            return self.price * self.quantity

        def username(self):
            return f"Firebase UID: {self.cart.firebase_uid[:8]}..."  # No user field

        username.short_description = 'User UID'

        class Meta:
            unique_together = ('cart', 'product', 'size', 'color')
