"""
Models for the FAQ app.
"""
from django.db import models # pyright: ignore[reportMissingModuleSource]
from django.utils.text import slugify # pyright: ignore[reportMissingModuleSource]
from apps.core.models import TimeStampedModel, PublishableModel


class FAQCategory(TimeStampedModel):
    """Categories to organize the FAQ."""
    name = models.CharField(
        'nome categoria',
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        'slug',
        max_length=100,
        unique=True,
        blank=True
    )
    order = models.PositiveIntegerField(
        'ordine',
        default=0,
        help_text='Ordine di visualizzazione'
    )
    
    class Meta:
        verbose_name = 'categoria FAQ'
        verbose_name_plural = 'categorie FAQ'
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class FAQ(TimeStampedModel, PublishableModel):
    """Frequently asked questions."""
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faqs',
        verbose_name='categoria'
    )
    question = models.CharField(
        'domanda',
        max_length=300
    )
    answer = models.TextField(
        'risposta'
    )
    order = models.PositiveIntegerField(
        'ordine',
        default=0,
        help_text='Ordine di visualizzazione'
    )
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.question[:50]
