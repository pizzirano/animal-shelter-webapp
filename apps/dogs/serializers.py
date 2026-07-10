"""
Serializers for the Dogs app.
"""
from rest_framework import serializers # pyright: ignore[reportMissingImports]
from .models import Dog, DogImage, Breed


class BreedSerializer(serializers.ModelSerializer):
    """Serializer for breeds."""
    dog_count = serializers.SerializerMethodField()

    class Meta:
        model = Breed
        fields = ['id', 'name', 'slug', 'description', 'dog_count', 'created_at']

    def get_dog_count(self, obj):
        """Count how many dogs have this breed."""
        return obj.dogs.filter(is_published=True).count()


class DogImageSerializer(serializers.ModelSerializer):
    """Serializer for dog images."""

    class Meta:
        model = DogImage
        fields = ['id', 'image', 'caption', 'order']


class DogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the dog list/gallery."""
    breed_name = serializers.CharField(source='breed.name', read_only=True, allow_null=True)
    breed_slug = serializers.CharField(source='breed.slug', read_only=True, allow_null=True)
    age = serializers.CharField(source='age_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Dog
        fields = [
            'id', 'slug', 'name', 'main_image', 'breed_name', 'breed_slug',
            'gender', 'gender_display', 'size', 'size_display',
            'age', 'status', 'status_display', 'arrival_date',
            'good_with_children', 'good_with_dogs', 'good_with_cats',
            'url', 'created_at'
        ]


class DogDetailSerializer(serializers.ModelSerializer):
    """Full serializer for the dog detail."""
    breed = BreedSerializer(read_only=True)
    images = DogImageSerializer(many=True, read_only=True)
    age = serializers.CharField(source='age_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    days_in_shelter = serializers.SerializerMethodField()

    class Meta:
        model = Dog
        fields = [
            'id', 'slug', 'name', 'microchip_number', 'breed',
            'is_mixed_breed', 'gender', 'gender_display', 'size', 'size_display',
            'age', 'age_years', 'age_months', 'weight', 'description', 'special_needs',
            'good_with_children', 'good_with_dogs', 'good_with_cats',
            'status', 'status_display', 'arrival_date', 'adoption_date',
            'main_image', 'images', 'view_count', 'url',
            'days_in_shelter', 'created_at', 'updated_at'
        ]

    def get_days_in_shelter(self, obj):
        """Compute the number of days spent in the shelter."""
        from django.utils import timezone # pyright: ignore[reportMissingModuleSource]
        if obj.status == 'adopted' and obj.adoption_date:
            delta = obj.adoption_date - obj.arrival_date
        else:
            delta = timezone.now().date() - obj.arrival_date
        return delta.days
