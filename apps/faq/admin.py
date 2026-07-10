"""
Admin configuration for the FAQ app.
"""
from django.contrib import admin # pyright: ignore[reportMissingModuleSource]
from .models import FAQCategory, FAQ


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_published', 'order']
    list_filter = ['is_published', 'category']
    search_fields = ['question', 'answer']
    prepopulated_fields = {}
    
    fieldsets = (
        (None, {
            'fields': ('category', 'question', 'answer')
        }),
        ('Pubblicazione', {
            'fields': ('is_published', 'order')
        }),
    )
