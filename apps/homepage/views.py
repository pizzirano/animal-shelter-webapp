"""
Homepage Views
"""
from django.views.generic import TemplateView # pyright: ignore[reportMissingModuleSource]
from django.core.cache import cache # pyright: ignore[reportMissingModuleSource]
from apps.dogs.models import Dog
from apps.faq.models import FAQ


class HomeView(TemplateView):
    template_name = 'homepage/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Cache for 5 minutes
        cache_key_featured = 'homepage_featured_dogs'
        cache_key_stats = 'homepage_stats'
        cache_key_faqs = 'homepage_featured_faqs'
        
        # Featured dogs with cache
        featured_dogs = cache.get(cache_key_featured)
        if featured_dogs is None:
            featured_dogs = Dog.objects.available().with_breed().recent(6)
            cache.set(cache_key_featured, featured_dogs, 300)  # 5 minutes
        context['featured_dogs'] = featured_dogs
        
        # Stats with cache
        stats = cache.get(cache_key_stats)
        if stats is None:
            total_dogs = Dog.objects.published().count()
            stats = {
                'total_dogs': total_dogs,
                'available_dogs': Dog.objects.available().count(),
                'adopted_dogs': Dog.objects.filter(
                    status='adopted',
                    is_published=True
                ).count(),
            }
            cache.set(cache_key_stats, stats, 300)  # 5 minutes
        context['stats'] = stats

        # FAQ with cache
        featured_faqs = cache.get(cache_key_faqs)
        if featured_faqs is None:
            featured_faqs = FAQ.objects.filter(
                is_published=True
            ).select_related('category').order_by('order')[:3]
            cache.set(cache_key_faqs, featured_faqs, 600)  # 10 minutes
        context['featured_faqs'] = featured_faqs
        
        return context
