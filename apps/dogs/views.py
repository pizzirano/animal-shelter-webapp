"""
Dogs app Views - Optimized list and detail views for dogs with caching
"""
from django.views.generic import ListView, DetailView # pyright: ignore[reportMissingModuleSource]
from django.db.models import Q, Prefetch # pyright: ignore[reportMissingModuleSource]
from django.core.cache import cache # pyright: ignore[reportMissingModuleSource]
from .models import Dog, Breed, DogImage


class DogListView(ListView):
    """Dog list view with filters."""
    model = Dog
    template_name = 'dogs/dog_list.html'
    context_object_name = 'dogs'
    paginate_by = 12
    
    def get_queryset(self):
        # Optimized query with select_related
        queryset = Dog.objects.published().with_breed().order_by('-created_at')

        # Filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        size = self.request.GET.get('size')
        if size:
            queryset = queryset.filter(size=size)
        
        gender = self.request.GET.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        if self.request.GET.get('good_with_children'):
            queryset = queryset.filter(good_with_children=True)
        if self.request.GET.get('good_with_dogs'):
            queryset = queryset.filter(good_with_dogs=True)
        if self.request.GET.get('good_with_cats'):
            queryset = queryset.filter(good_with_cats=True)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(breed__name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Cache breeds list (30 minutes)
        breeds = cache.get('dog_breeds_list')
        if breeds is None:
            breeds = Breed.objects.all().order_by('name')
            cache.set('dog_breeds_list', breeds, 1800)
        
        context['breeds'] = breeds
        context['size_choices'] = Dog.SIZE_CHOICES
        context['gender_choices'] = Dog.GENDER_CHOICES
        context['status_choices'] = Dog.STATUS_CHOICES
        
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'size': self.request.GET.get('size', ''),
            'gender': self.request.GET.get('gender', ''),
            'search': self.request.GET.get('search', ''),
            'good_with_children': self.request.GET.get('good_with_children', ''),
            'good_with_dogs': self.request.GET.get('good_with_dogs', ''),
            'good_with_cats': self.request.GET.get('good_with_cats', ''),
        }
        
        context['total_count'] = self.get_queryset().count()
        
        return context


class DogDetailView(DetailView):
    """Single dog detail view."""
    model = Dog
    template_name = 'dogs/dog_detail.html'
    context_object_name = 'dog'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        # Prefetch optimized images
        images_prefetch = Prefetch(
            'images',
            queryset=DogImage.objects.order_by('order', 'created_at')
        )
        
        return Dog.objects.published().select_related('breed').prefetch_related(images_prefetch)
    
    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Cache of similar dogs (10 minutes)
        cache_key = f'similar_dogs_{self.object.id}'
        similar_dogs = cache.get(cache_key)
        
        if similar_dogs is None:
            similar_dogs = Dog.objects.available().with_breed().filter(
                size=self.object.size
            ).exclude(
                pk=self.object.pk
            )[:3]
            cache.set(cache_key, similar_dogs, 600)  # 10 minutes
        
        context['similar_dogs'] = similar_dogs
        
        return context
