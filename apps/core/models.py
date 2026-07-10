"""
Reusable abstract models.
"""
from django.db import models # pyright: ignore[reportMissingModuleSource]
from django.utils.translation import gettext_lazy as _ # pyright: ignore[reportMissingModuleSource]


class TimeStampedModel(models.Model):
    """
    Abstract model that adds automatic timestamps.
    """
    created_at = models.DateTimeField(
        _('creato il'),
        auto_now_add=True,
        db_index=True,
        help_text='Data e ora di creazione automatica'
    )
    updated_at = models.DateTimeField(
        _('aggiornato il'),
        auto_now=True,
        help_text='Data e ora ultimo aggiornamento'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class PublishableModel(models.Model):
    """
    Abstract model for publishable content.
    """
    is_published = models.BooleanField(
        _('pubblicato'),
        default=True,
        db_index=True,
        help_text='Spunta per rendere visibile sul sito'
    )

    class Meta:
        abstract = True
