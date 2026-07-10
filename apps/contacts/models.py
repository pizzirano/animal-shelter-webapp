"""
Models for Contacts app - Contact messages with spam and security fields
"""
from django.db import models # pyright: ignore[reportMissingModuleSource]
from apps.core.models import TimeStampedModel


class ContactMessage(TimeStampedModel):
    """Contact messages submitted through the form."""
    
    SUBJECT_CHOICES = [
        ('adoption', 'Richiesta adozione'),
        ('info', 'Richiesta informazioni'),
        ('volunteer', 'Volontariato'),
        ('donation', 'Donazioni'),
        ('other', 'Altro'),
    ]
    
    # Sender info
    name = models.CharField(
        'nome completo',
        max_length=100
    )
    email = models.EmailField(
        'email',
        db_index=True
    )
    phone = models.CharField(
        'telefono',
        max_length=20,
        blank=True
    )
    
    # Message details
    subject = models.CharField(
        'oggetto',
        max_length=20,
        choices=SUBJECT_CHOICES,
        db_index=True
    )
    dog = models.ForeignKey(
        'dogs.Dog',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_messages',
        verbose_name='cane di interesse'
    )
    message = models.TextField(
        'messaggio'
    )
    
    # Management fields
    is_read = models.BooleanField(
        'letto',
        default=False,
        db_index=True
    )
    notes = models.TextField(
        'note interne',
        blank=True,
        help_text='Note dello staff (non visibili al mittente)'
    )
    
    # === SECURITY FIELDS ===
    ip_address = models.GenericIPAddressField(
        'indirizzo IP',
        null=True,
        blank=True,
        db_index=True,
        help_text='IP del mittente per sicurezza'
    )
    user_agent = models.CharField(
        'user agent',
        max_length=500,
        blank=True,
        help_text='Browser/dispositivo utilizzato'
    )
    is_spam = models.BooleanField(
        'contrassegnato come spam',
        default=False,
        db_index=True
    )
    spam_score = models.FloatField(
        'punteggio spam',
        default=0.0,
        help_text='Score da reCAPTCHA (0=bot, 1=umano)'
    )
    
    class Meta:
        verbose_name = 'messaggio di contatto'
        verbose_name_plural = 'messaggi di contatto'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_read', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),  # To track spam by IP
            models.Index(fields=['is_spam', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"
    
    def mark_as_spam(self):
        """Mark the message as spam."""
        self.is_spam = True
        self.save(update_fields=['is_spam'])
