import os
from django.core.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
MAX_IMAGE_SIZE_MB = 5

def validate_dog_image(image):
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Formato non supportato. Usa: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
        )
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f'Immagine troppo grande. Massimo {MAX_IMAGE_SIZE_MB} MB.'
        )
