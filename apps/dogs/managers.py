"""
Custom managers to optimize queries.
"""
from django.db import models # pyright: ignore[reportMissingModuleSource]


class DogQuerySet(models.QuerySet):
    """Custom QuerySet with optimized methods."""

    def published(self):
        """Published dogs only."""
        return self.filter(is_published=True)

    def available(self):
        """Dogs available for adoption only."""
        return self.filter(status='available', is_published=True)

    def with_related(self):
        """Eager-load breed and images to avoid N+1 queries."""
        return self.select_related('breed').prefetch_related('images')

    def with_breed(self):
        """Eager-load breed only."""
        return self.select_related('breed')

    def recent(self, limit=10):
        """Most recent dogs."""
        return self.order_by('-created_at')[:limit]

    def by_size(self, size):
        """Filter by size."""
        return self.filter(size=size)

    def good_for_families(self):
        """Dogs suitable for families with children."""
        return self.filter(good_with_children=True)


class DogManager(models.Manager):
    """Custom manager for the Dog model."""

    def get_queryset(self):
        """Override the base queryset."""
        return DogQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def available(self):
        return self.get_queryset().available()

    def with_related(self):
        return self.get_queryset().with_related()

    def with_breed(self):
        return self.get_queryset().with_breed()

    def recent(self, limit=10):
        return self.get_queryset().recent(limit)

    def by_size(self, size):
        return self.get_queryset().by_size(size)

    def good_for_families(self):
        return self.get_queryset().good_for_families()
