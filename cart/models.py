from django.db import models
from django.conf import settings
from products.models import *  # Your Products model

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
