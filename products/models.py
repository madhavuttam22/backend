from django.db import models
from django.utils.text import slugify

class Size(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    category = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.category

class Color(models.Model):
    name = models.CharField(max_length=100)
    hex_code = models.CharField(max_length=7, blank=True)

    def __str__(self):
        return self.name

class Products(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    currentprice = models.PositiveIntegerField()
    orignalprice = models.PositiveIntegerField()
    description = models.TextField()
    is_top_product = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    sizes = models.ManyToManyField(Size, through='ProductSize')
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class ProductColor(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='colors')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)  # नया फील्ड जोड़ें
    
    class Meta:
        unique_together = ('product', 'color')
        ordering = ['order']  # ऑर्डर के अनुसार सॉर्टिंग
    
    def __str__(self):
        return f"{self.product.name} - {self.color.name}"

class ProductColorImage(models.Model):
    product_color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_color_images/')
    is_default = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)  # for ordering images
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.product_color} - Image {self.id}"

class ProductSize(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('product', 'size')