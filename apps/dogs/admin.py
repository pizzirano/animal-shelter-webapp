"""
Admin configuration for the Dogs app.
"""
from django.contrib import admin # pyright: ignore[reportMissingModuleSource]
from django.utils.html import format_html # pyright: ignore[reportMissingModuleSource]
from .models import Breed, Dog, DogImage


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class DogImageInline(admin.TabularInline):
    """Inline to manage the additional images."""
    model = DogImage
    extra = 1
    fields = ['image', 'caption', 'order']


@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'breed', 'gender', 'size', 'age_display',
        'status', 'is_published', 'arrival_date', 'image_preview'
    ]
    list_filter = [
        'status', 'gender', 'size', 'is_published',
        'good_with_children', 'good_with_dogs', 'good_with_cats'
    ]
    search_fields = ['name', 'description', 'microchip_number']
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'arrival_date'
    
    fieldsets = (
        ('Informazioni Base', {
            'fields': ('name', 'slug', 'microchip_number', 'is_published')
        }),
        ('Caratteristiche', {
            'fields': (
                'breed', 'is_mixed_breed', 'gender', 'size',
                'age_years', 'age_months', 'weight'
            )
        }),
        ('Descrizione', {
            'fields': ('description', 'special_needs')
        }),
        ('Compatibilità', {
            'fields': (
                'good_with_children', 'good_with_dogs', 'good_with_cats'
            )
        }),
        ('Status', {
            'fields': ('status', 'arrival_date', 'adoption_date')
        }),
        ('Media', {
            'fields': ('main_image',)
        }),
    )
    
    inlines = [DogImageInline]
    
    def image_preview(self, obj):
        """Image thumbnail in the list view."""
        if obj.main_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.main_image.url
            )
        return '-'
    image_preview.short_description = 'Foto'
    
    def age_display(self, obj):
        return obj.age_display
    age_display.short_description = 'Età'


@admin.register(DogImage)
class DogImageAdmin(admin.ModelAdmin):
    list_display = ['dog', 'caption', 'order', 'created_at']
    list_filter = ['dog']
    search_fields = ['dog__name', 'caption']
