"""
Views for the FAQ app.
"""
from django.views.generic import ListView # pyright: ignore[reportMissingModuleSource]
from .models import FAQ, FAQCategory


class FAQListView(ListView):
    """FAQ list view."""
    model = FAQ
    template_name = 'faq/faq_list.html'
    context_object_name = 'faqs'

    def get_queryset(self):
        """Return only published FAQ."""
        return FAQ.objects.filter(
            is_published=True
        ).select_related('category').order_by('order', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Categories for the filter
        context['categories'] = FAQCategory.objects.all().order_by('order')

        # Filter by category if specified
        category_slug = self.request.GET.get('category')
        if category_slug:
            context['selected_category'] = FAQCategory.objects.filter(
                slug=category_slug
            ).first()
            context['faqs'] = context['faqs'].filter(
                category__slug=category_slug
            )
        
        # Group FAQ by category
        faqs_by_category = {}
        for faq in context['faqs']:
            category = faq.category.name if faq.category else 'Generali'
            if category not in faqs_by_category:
                faqs_by_category[category] = []
            faqs_by_category[category].append(faq)
        
        context['faqs_by_category'] = faqs_by_category
        
        return context
