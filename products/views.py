from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat, Greatest, Coalesce
from .models import *
from .serializers import ProductSerializer, CategorySerializer
from fuzzywuzzy import fuzz
import re


def product_search(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'status': 'error', 'message': 'Empty search query'})
    
    # Basic search with name and description
    products = Products.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query)
    ).distinct()[:20]  # Limit to 20 results
    
    serializer = ProductSerializer(
        products, 
        many=True, 
        context={'request': request}
    )
    
    return JsonResponse({
        'status': 'success',
        'results': serializer.data
    })

class EnhancedProductSearch(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response(
                {"status": "error", "message": "Empty search query"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Basic search with name and description
        base_queryset = Products.objects.annotate(
            search_text=Concat(
                'name', Value(' '), 'description',
                output_field=CharField()
            )
        )
        
        # Exact matches first
        exact_matches = base_queryset.filter(
            Q(name__iexact=query) | 
            Q(description__iexact=query)
        )
        
        # Partial matches
        partial_matches = base_queryset.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        ).exclude(pk__in=exact_matches.values('pk'))
        
        # Fuzzy matches using fuzzywuzzy
        all_products = list(base_queryset.all())
        fuzzy_threshold = 70  # Adjust this based on your needs
        
        def calculate_score(product, query):
            name_score = fuzz.partial_ratio(query.lower(), product.name.lower())
            desc_score = fuzz.partial_ratio(query.lower(), product.description.lower()) if product.description else 0
            return max(name_score, desc_score)
        
        fuzzy_matched = [
            p for p in all_products 
            if calculate_score(p, query) >= fuzzy_threshold and 
               p.pk not in exact_matches.values_list('pk', flat=True) and
               p.pk not in partial_matches.values_list('pk', flat=True)
        ]
        
        # Combine results with priority: exact > partial > fuzzy
        results = list(exact_matches) + list(partial_matches) + fuzzy_matched
        
        # Limit results and remove duplicates
        seen_ids = set()
        unique_results = []
        for product in results:
            if product.pk not in seen_ids:
                seen_ids.add(product.pk)
                unique_results.append(product)
            if len(unique_results) >= 20:
                break
        
        # Add relevance score to each product
        for product in unique_results:
            product.relevance_score = calculate_score(product, query)
        
        # Sort by relevance score (highest first)
        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        serializer = ProductSerializer(
            unique_results,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'status': 'success',
            'count': len(unique_results),
            'results': serializer.data,
            'query': query
        })
    

from fuzzywuzzy import fuzz
from django.http import JsonResponse
from django.db.models import Q

def get_search_suggestions(request):
    query = request.GET.get('q', '').strip().lower()
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Get all product names and descriptions
    products = Products.objects.all().values('name', 'description')
    
    suggestions = set()
    
    for product in products:
        # Check name matches
        if fuzz.partial_ratio(query, product['name'].lower()) > 70:
            suggestions.add(product['name'])
        
        # Check description keywords
        if product['description']:
            for word in product['description'].split():
                if fuzz.ratio(query, word.lower()) > 80:
                    suggestions.add(word)
    
    return JsonResponse({'suggestions': list(suggestions)[:5]})


class ProductListAPIView(APIView):
    def get(self, request):
        queryset = Products.objects.all()
        is_top = request.query_params.get('is_top')
        is_best = request.query_params.get('is_best')
        
        if is_top:
            queryset = queryset.filter(is_top_product=True)
        if is_best:
            queryset = queryset.filter(is_best_seller=True)
        
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

class ProductDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            product = Products.objects.get(pk=pk)
            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data)
        except Products.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class CategoryListAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class CategoryProductsAPIView(APIView):
    def get(self, request, category_id):
        try:
            category = Category.objects.get(pk=category_id)
            products = Products.objects.filter(category=category)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        


# @api_view(['GET'])
# def get_filter_options(request, category_id=None):
#     try:
#         # Get base queryset
#         if category_id:
#             products = Products.objects.filter(category_id=category_id)
#         else:
#             products = Products.objects.all()
        
#         # Calculate price range
#         price_range = products.aggregate(
#             min_price=Min('currentprice'),
#             max_price=Max('currentprice')
#         )
        
#         # Get all available colors
#         colors = Color.objects.filter(
#             productcolor__product__in=products,
#             productcolor__is_active=True
#         ).distinct().values('id', 'name', 'hex_code')
        
#         # Get all available sizes
#         sizes = Size.objects.filter(
#             productsize__product__in=products,
#             productsize__is_active=True,
#             productsize__stock__gt=0
#         ).distinct().values('id', 'name')
        
#         return Response({
#             'price_range': {
#                 'min': price_range['min_price'] or 0,
#                 'max': price_range['max_price'] or 10000
#             },
#             'colors': colors,
#             'sizes': sizes
#         })
        
#     except Exception as e:
#         return Response(
#             {"error": str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


# class CategoryProductsAPIView(APIView):
#     def get(self, request, category_id):
#         try:
#             # Get filter params from request
#             min_price = request.query_params.get('min_price')
#             max_price = request.query_params.get('max_price')
#             colors = request.query_params.getlist('colors[]')
#             sizes = request.query_params.getlist('sizes[]')
#             availability = request.query_params.get('availability')
            
#             # Base queryset
#             products = Products.objects.filter(category_id=category_id)
            
#             # Apply filters
#             if min_price and max_price:
#                 products = products.filter(
#                     currentprice__gte=min_price,
#                     currentprice__lte=max_price
#                 )
            
#             if colors:
#                 products = products.filter(
#                     colors__color_id__in=colors,
#                     colors__is_active=True
#                 ).distinct()
            
#             if sizes:
#                 products = products.filter(
#                     sizes__size_id__in=sizes,
#                     sizes__is_active=True
#                 ).distinct()
            
#             if availability == 'in_stock':
#                 products = products.filter(
#                     sizes__stock__gt=0
#                 ).distinct()
            
#             serializer = ProductSerializer(products, many=True)
#             return Response(serializer.data)
            
#         except Category.DoesNotExist:
#             return Response(
#                 {"error": "Category not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )