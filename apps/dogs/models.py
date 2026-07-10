"""
Models for managing the shelter's dogs.
"""
from django.db import models # pyright: ignore[reportMissingModuleSource]
from django.core.validators import MinValueValidator, MaxValueValidator # pyright: ignore[reportMissingModuleSource]
from django.utils.text import slugify # pyright: ignore[reportMissingModuleSource]
from django.urls import reverse # pyright: ignore[reportMissingModuleSource]
from apps.core.models import TimeStampedModel, PublishableModel
from .managers import DogManager
from .validators import validate_dog_image


class Breed(TimeStampedModel):
    """Dog breeds."""
    name = models.CharField(
        'nome razza',
        max_length=100,
        unique=True,
        db_index=True
    )
    slug = models.SlugField(
        'slug',
        max_length=100,
        unique=True,
        blank=True
    )
    description = models.TextField(
        'descrizione',
        blank=True,
        help_text='Descrizione delle caratteristiche della razza'
    )
    
    class Meta:
        verbose_name = 'razza'
        verbose_name_plural = 'razze'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Dog(TimeStampedModel, PublishableModel):
    """
    Main model for the shelter's dogs.
    """
    
    GENDER_CHOICES = [
        ('M', 'Maschio'),
        ('F', 'Femmina'),
    ]
    
    SIZE_CHOICES = [
        ('XS', 'Mini (< 5kg)'),
        ('S', 'Piccola (5-10kg)'),
        ('M', 'Media (10-25kg)'),
        ('L', 'Grande (25-45kg)'),
        ('XL', 'Gigante (> 45kg)'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Disponibile'),
        ('adopted', 'Adottato'),
        ('reserved', 'Prenotato'),
        ('medical', 'In cura'),
    ]
    
    # === Identification fields ===
    name = models.CharField(
        'nome',
        max_length=100,
        db_index=True,
        help_text='Nome del cane'
    )
    slug = models.SlugField(
        'slug',
        max_length=120,
        unique=True,
        blank=True,
        help_text='Generato automaticamente dal nome'
    )
    microchip_number = models.CharField(
        'numero microchip',
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        help_text='Codice identificativo microchip'
    )

    # === Physical characteristics ===
    breed = models.ForeignKey(
        Breed,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dogs',
        verbose_name='razza'
    )
    is_mixed_breed = models.BooleanField(
        'meticcio',
        default=False,
        help_text='Spunta se è un meticcio'
    )
    gender = models.CharField(
        'sesso',
        max_length=1,
        choices=GENDER_CHOICES,
        db_index=True
    )
    size = models.CharField(
        'taglia',
        max_length=2,
        choices=SIZE_CHOICES,
        db_index=True
    )
    age_years = models.IntegerField(
        'età (anni)',
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        default=0
    )
    age_months = models.IntegerField(
        'età (mesi)',
        validators=[MinValueValidator(0), MaxValueValidator(11)],
        default=0,
        help_text='Da 0 a 11 mesi'
    )
    weight = models.DecimalField(
        'peso (kg)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    # === Description ===
    description = models.TextField(
        'descrizione',
        help_text='Storia e carattere del cane'
    )
    special_needs = models.TextField(
        'esigenze speciali',
        blank=True,
        help_text='Diete, terapie o limitazioni particolari'
    )

    # === Compatibility ===
    good_with_children = models.BooleanField(
        'adatto a bambini',
        default=False
    )
    good_with_dogs = models.BooleanField(
        'adatto ad altri cani',
        default=False
    )
    good_with_cats = models.BooleanField(
        'adatto a gatti',
        default=False
    )
    
    # === Status ===
    status = models.CharField(
        'stato',
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        db_index=True
    )
    arrival_date = models.DateField(
        'data arrivo',
        db_index=True,
        help_text='Quando è arrivato al canile'
    )
    adoption_date = models.DateField(
        'data adozione',
        null=True,
        blank=True
    )
    
    # === Media ===
    main_image = models.ImageField(
        'immagine principale',
        upload_to='dogs/main/%Y/%m/',
        help_text='Foto principale per la gallery (jpg/png/webp, max 5 MB)',
        validators=[validate_dog_image],
        blank=True,
        null=True
    )
    
    # === Counters ===
    view_count = models.PositiveIntegerField(
        'visualizzazioni',
        default=0,
        editable=False
    )

    # Custom manager
    objects = DogManager()
    
    class Meta:
        verbose_name = 'cane'
        verbose_name_plural = 'cani'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at'], name='dog_status_created_idx'),
            models.Index(fields=['size', 'gender'], name='dog_size_gender_idx'),
            models.Index(fields=['-arrival_date'], name='dog_arrival_idx'),
            models.Index(fields=['is_published', 'status'], name='dog_published_status_idx'),
            models.Index(fields=['slug'], name='dog_slug_idx'),  # For fast lookup
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Ensure unique slug
            while Dog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"
    
    @property
    def age_display(self):
        """Return the age in a human-readable format."""
        if self.age_years > 0:
            years = f"{self.age_years} {'anno' if self.age_years == 1 else 'anni'}"
            if self.age_months > 0:
                return f"{years} e {self.age_months} {'mese' if self.age_months == 1 else 'mesi'}"
            return years
        return f"{self.age_months} {'mese' if self.age_months == 1 else 'mesi'}"
    
    @property
    def is_available(self):
        """Whether the dog is available for adoption."""
        return self.status == 'available' and self.is_published

    def get_absolute_url(self):
        """URL of the dog's detail page."""
        return reverse('dog-detail', kwargs={'slug': self.slug})


class DogImage(TimeStampedModel):
    """Additional image gallery for each dog."""
    dog = models.ForeignKey(
        Dog,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='cane'
    )
    image = models.ImageField(
        'immagine',
        upload_to='dogs/gallery/%Y/%m/',
        validators=[validate_dog_image]
    )
    caption = models.CharField(
        'didascalia',
        max_length=200,
        blank=True
    )
    order = models.PositiveIntegerField(
        'ordine',
        default=0,
        help_text='Ordine di visualizzazione'
    )
    
    class Meta:
        verbose_name = 'immagine cane'
        verbose_name_plural = 'immagini cani'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Immagine di {self.dog.name}"

