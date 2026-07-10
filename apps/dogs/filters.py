"""
Filters for the Dogs app - Advanced filtering for Dog model
"""
import django_filters # pyright: ignore[reportMissingModuleSource]
from .models import Dog


class DogFilter(django_filters.FilterSet):
    """Advanced filters for searching dogs."""
    
    # Basic filters
    name = django_filters.CharFilter(lookup_expr='icontains', label='Nome')
    breed = django_filters.CharFilter(field_name='breed__name', lookup_expr='icontains', label='Razza')
    
    # Age range filters
    age_min = django_filters.NumberFilter(field_name='age_years', lookup_expr='gte', label='Età minima')
    age_max = django_filters.NumberFilter(field_name='age_years', lookup_expr='lte', label='Età massima')
    
    # Weight range filters
    weight_min = django_filters.NumberFilter(field_name='weight', lookup_expr='gte', label='Peso minimo')
    weight_max = django_filters.NumberFilter(field_name='weight', lookup_expr='lte', label='Peso massimo')
    
    # Arrival date range filters
    arrival_date_from = django_filters.DateFilter(field_name='arrival_date', lookup_expr='gte', label='Arrivato dal')
    arrival_date_to = django_filters.DateFilter(field_name='arrival_date', lookup_expr='lte', label='Arrivato fino al')
    
    class Meta:
        model = Dog
        fields = {
            'gender': ['exact'],
            'size': ['exact', 'in'],
            'status': ['exact', 'in'],
            'is_mixed_breed': ['exact'],
            'good_with_children': ['exact'],
            'good_with_dogs': ['exact'],
            'good_with_cats': ['exact'],
        }
