"""
API Views for the FAQ app.
"""
from rest_framework import viewsets, filters # pyright: ignore[reportMissingImports]
from rest_framework.decorators import action # pyright: ignore[reportMissingImports]
from rest_framework.response import Response # pyright: ignore[reportMissingImports]
from django.db.models import Count, Q # pyright: ignore[reportMissingModuleSource]
from .models import FAQ, FAQCategory
from .serializers import FAQSerializer, FAQCategorySerializer


class FAQCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for FAQ categories.

    list: List all categories
    retrieve: Category detail with its FAQ
    """
    queryset = FAQCategory.objects.all().annotate(
        faq_count=Count('faqs', filter=Q(faqs__is_published=True))
    ).order_by('order', 'name')
    serializer_class = FAQCategorySerializer
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def faqs(self, request, slug=None):
        """
        List the FAQ of a specific category.
        GET /api/v1/faq-categories/{slug}/faqs/
        """
        category = self.get_object()
        faqs = FAQ.objects.filter(
            category=category,
            is_published=True
        ).order_by('order', '-created_at')
        
        serializer = FAQSerializer(faqs, many=True)
        return Response(serializer.data)


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for FAQ.

    list: List all published FAQ
    retrieve: Detail of a specific FAQ
    by_category: FAQ grouped by category
    """
    queryset = FAQ.objects.filter(
        is_published=True
    ).select_related('category').order_by('order', '-created_at')
    serializer_class = FAQSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['question', 'answer']
    ordering_fields = ['order', 'created_at']
    ordering = ['order', '-created_at']
    
    def get_queryset(self):
        """Filter by category if specified."""
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        FAQ grouped by category.
        GET /api/v1/faqs/by_category/
        """
        categories = FAQCategory.objects.all().order_by('order', 'name')
        result = []
        
        for category in categories:
            faqs = self.get_queryset().filter(category=category)
            if faqs.exists():
                result.append({
                    'category': FAQCategorySerializer(category).data,
                    'faqs': FAQSerializer(faqs, many=True).data
                })
        
        # FAQ without a category
        uncategorized_faqs = self.get_queryset().filter(category__isnull=True)
        if uncategorized_faqs.exists():
            result.append({
                'category': {'name': 'Generali', 'slug': 'generali'},
                'faqs': FAQSerializer(uncategorized_faqs, many=True).data
            })
        
        return Response(result)
