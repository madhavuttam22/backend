from django.urls import path
from .views import (
    ProductListAPIView,
    ProductDetailAPIView,
    CategoryListAPIView,
    CategoryProductsAPIView,EnhancedProductSearch
)
from . import views

urlpatterns = [
    # Product URLs
    path('api/products/', ProductListAPIView.as_view(), name='product-list'),
    path('api/products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    
    # Category URLs
    path('api/categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('api/categories/<int:category_id>/products/', CategoryProductsAPIView.as_view(), name='category-products'),
    # urls.py
    path('api/products/search/', views.product_search, name='product-search'),
    path('api/products/enhanced-search/', EnhancedProductSearch.as_view(), name='enhanced-product-search'),
    path('api/search/suggestions/', views.get_search_suggestions, name='search-suggestions'),
    path('api/categories/<int:category_id>/products/', CategoryProductsAPIView.as_view(), name='category-products'),
    path('api/categories/<int:category_id>/filter-options/', views.get_filter_options, name='category-filter-options'),
    
]