"""
API Views - Dogs app
"""
from rest_framework import viewsets, filters, status # pyright: ignore[reportMissingImports]
from rest_framework.decorators import action # pyright: ignore[reportMissingImports]
from rest_framework.response import Response # pyright: ignore[reportMissingImports]
from django_filters.rest_framework import DjangoFilterBackend # pyright: ignore[reportMissingModuleSource]
from django.db.models import Count, Q # pyright: ignore[reportMissingModuleSource]
from .models import Dog, Breed
from .serializers import DogListSerializer, DogDetailSerializer, BreedSerializer
from .filters import DogFilter


class BreedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for breeds.

    list: List all breeds
    retrieve: Detail of a specific breed
    """
    queryset = Breed.objects.all().annotate(
        dog_count=Count('dogs', filter=Q(dogs__is_published=True))
    ).order_by('name')
    serializer_class = BreedSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'dog_count', 'created_at']
    ordering = ['name']


class DogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for dogs.

    list: List all dogs with advanced filters
    retrieve: Detail of a specific dog
    featured: Featured dogs (latest 6 available)
    stats: Dog statistics
    search: Advanced search
    """
    queryset = Dog.objects.filter(
        is_published=True
    ).select_related('breed').prefetch_related('images').order_by('-created_at')

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DogFilter
    search_fields = ['name', 'description', 'breed__name', 'microchip_number']
    ordering_fields = ['created_at', 'arrival_date', 'name', 'age_years', 'view_count']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Use a different serializer for list and detail."""
        if self.action == 'retrieve':
            return DogDetailSerializer
        return DogListSerializer

    def retrieve(self, request, *args, **kwargs):
        """Override to increment view_count."""
        instance = self.get_object()
        # Increment the counter only if it is not a request from the same session
        if not request.session.get(f'viewed_dog_{instance.id}'):
            instance.view_count += 1
            instance.save(update_fields=['view_count'])
            request.session[f'viewed_dog_{instance.id}'] = True

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Return the featured dogs (latest 6 available).
        GET /api/v1/dogs/featured/
        """
        featured_dogs = self.get_queryset().filter(
            status='available'
        )[:6]
        serializer = self.get_serializer(featured_dogs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Aggregated dog statistics.
        GET /api/v1/dogs/stats/
        """
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'available': queryset.filter(status='available').count(),
            'adopted': queryset.filter(status='adopted').count(),
            'reserved': queryset.filter(status='reserved').count(),
            'in_medical_care': queryset.filter(status='medical').count(),
            'by_size': {},
            'by_gender': {},
            'with_special_needs': queryset.exclude(special_needs='').count(),
            'good_with_children': queryset.filter(good_with_children=True).count(),
            'good_with_dogs': queryset.filter(good_with_dogs=True).count(),
            'good_with_cats': queryset.filter(good_with_cats=True).count(),
        }

        # Stats for size
        for size_code, size_label in Dog.SIZE_CHOICES:
            stats['by_size'][size_code] = {
                'label': size_label,
                'count': queryset.filter(size=size_code).count()
            }

        # Stats for gender
        for gender_code, gender_label in Dog.GENDER_CHOICES:
            stats['by_gender'][gender_code] = {
                'label': gender_label,
                'count': queryset.filter(gender=gender_code).count()
            }

        return Response(stats)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Only dogs available for adoption.
        GET /api/v1/dogs/available/
        """
        available_dogs = self.get_queryset().filter(status='available')

        # Apply the standard filters
        available_dogs = self.filter_queryset(available_dogs)

        page = self.paginate_queryset(available_dogs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(available_dogs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def similar(self, request, slug=None):
        """
        Dogs similar to the given one (same size).
        GET /api/v1/dogs/{slug}/similar/
        """
        dog = self.get_object()
        similar_dogs = self.get_queryset().filter(
            size=dog.size,
            status='available'
        ).exclude(
            id=dog.id
        )[:4]

        serializer = self.get_serializer(similar_dogs, many=True)
        return Response(serializer.data)
