"""
Signals that invalidate the cache when data changes.
"""
from django.db.models.signals import post_save, post_delete # pyright: ignore[reportMissingModuleSource]
from django.dispatch import receiver # pyright: ignore[reportMissingModuleSource]
from django.core.cache import cache # pyright: ignore[reportMissingModuleSource]
from .models import Dog, Breed


@receiver([post_save, post_delete], sender=Dog)
def invalidate_dog_cache(sender, instance, **kwargs):
    """Invalidate the cache when a dog is changed or deleted."""
    # Homepage cache
    cache.delete('homepage_featured_dogs')
    cache.delete('homepage_stats')
    
    # Similar dogs cache
    cache.delete(f'similar_dogs_{instance.id}')
    
    # Breed cache (dog count)
    cache.delete('dog_breeds_list')


@receiver([post_save, post_delete], sender=Breed)
def invalidate_breed_cache(sender, instance, **kwargs):
    """Invalidate the breed cache."""
    cache.delete('dog_breeds_list')
