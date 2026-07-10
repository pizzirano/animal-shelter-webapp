"""
Serializers for the FAQ app.
"""
from rest_framework import serializers # pyright: ignore[reportMissingImports]
from .models import FAQ, FAQCategory


class FAQCategorySerializer(serializers.ModelSerializer):
    """Serializer for FAQ categories."""
    faq_count = serializers.SerializerMethodField()

    class Meta:
        model = FAQCategory
        fields = ['id', 'name', 'slug', 'order', 'faq_count']

    def get_faq_count(self, obj):
        """Count the published FAQ in this category."""
        return obj.faqs.filter(is_published=True).count()


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ."""
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True, allow_null=True)
    
    class Meta:
        model = FAQ
        fields = [
            'id', 'category', 'category_name', 'category_slug',
            'question', 'answer', 'order', 'is_published', 'created_at'
        ]
