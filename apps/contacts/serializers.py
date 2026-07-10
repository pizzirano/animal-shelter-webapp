"""
Contacts app serializers - Contact messages serialization
"""
from rest_framework import serializers # pyright: ignore[reportMissingImports]
from .models import ContactMessage
from apps.dogs.models import Dog


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer for contact messages."""
    dog_name = serializers.CharField(source='dog.name', read_only=True, allow_null=True)
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 'subject_display',
            'dog', 'dog_name', 'message', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def validate_dog(self, value):
        """Validate that the dog is available."""
        if value and value.status != 'available':
            raise serializers.ValidationError(
                "Il cane selezionato non è disponibile per l'adozione."
            )
        return value
    
    def create(self, validated_data):
        """Create a new message."""
        return ContactMessage.objects.create(**validated_data)
