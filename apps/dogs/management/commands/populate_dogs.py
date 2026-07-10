"""
Management command to populate the database with test data.
"""
from django.core.management.base import BaseCommand # pyright: ignore[reportMissingModuleSource]
from django.utils import timezone # pyright: ignore[reportMissingModuleSource]
from datetime import timedelta
import random
from apps.dogs.models import Dog, Breed


class Command(BaseCommand):
    help = 'Populate the database with example dogs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of dogs to create',
        )

    def handle(self, *args, **options):
        count = options['count']

        # Create breeds if they don't exist
        breeds_data = [
            'Labrador Retriever', 'Pastore Tedesco', 'Golden Retriever',
            'Bulldog Francese', 'Beagle', 'Border Collie', 'Boxer',
            'Chihuahua', 'Husky Siberiano', 'Meticcio'
        ]
        
        breeds = []
        for breed_name in breeds_data:
            breed, created = Breed.objects.get_or_create(name=breed_name)
            breeds.append(breed)
            if created:
                self.stdout.write(f'  Breed created: {breed_name}')

        # Dog names
        names = [
            'Max', 'Bella', 'Luna', 'Charlie', 'Lucy', 'Rocky', 'Daisy',
            'Buddy', 'Molly', 'Jack', 'Lola', 'Duke', 'Sadie', 'Zeus',
            'Chloe', 'Bear', 'Sophie', 'Rex', 'Penny', 'Toby', 'Maggie',
            'Oscar', 'Coco', 'Milo', 'Stella', 'Shadow', 'Bailey'
        ]
        
        created_count = 0
        
        for i in range(count):
            name = random.choice(names) + f" {i+1}"
            
            dog = Dog.objects.create(
                name=name,
                breed=random.choice(breeds),
                is_mixed_breed=random.choice([True, False]),
                gender=random.choice(['M', 'F']),
                size=random.choice(['XS', 'S', 'M', 'L', 'XL']),
                age_years=random.randint(0, 12),
                age_months=random.randint(0, 11),
                weight=round(random.uniform(5, 45), 2),
                description=f"Questo è {name}, un cane meraviglioso in cerca di una famiglia amorevole. È affettuoso e adora giocare.",
                special_needs='',
                good_with_children=random.choice([True, False]),
                good_with_dogs=random.choice([True, False]),
                good_with_cats=random.choice([True, False]),
                status=random.choice(['available', 'available', 'available', 'adopted']),  # More available ones
                arrival_date=timezone.now().date() - timedelta(days=random.randint(1, 365)),
                is_published=True,
            )
            
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created {created_count} test dogs!')
        )
