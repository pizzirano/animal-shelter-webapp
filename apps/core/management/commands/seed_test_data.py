"""
Management command to seed the development database with test data.
Usage: DJANGO_ENVIRONMENT=development python3 manage.py seed_test_data
"""
import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.contacts.models import ContactMessage
from apps.dogs.models import Breed, Dog
from apps.faq.models import FAQ, FAQCategory


class Command(BaseCommand):
    help = 'Seed the database with realistic test data for development.'

    def handle(self, *args, **options):
        self._seed_breeds()
        self._seed_dogs()
        self._seed_faqs()
        self._seed_contacts()
        self._seed_admin_user()
        self.stdout.write(self.style.SUCCESS('Test data inserted successfully.'))

    def _seed_breeds(self):
        races = [
            ('Labrador Retriever', 'labrador-retriever', 'Razza amichevole e paziente.'),
            ('Meticcio', 'meticcio', 'Cane di razza mista.'),
            ('Pastore Tedesco', 'pastore-tedesco', 'Razza intelligente e fedele.'),
        ]
        for name, slug, desc in races:
            Breed.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc}
            )
        self.stdout.write('  ✓ Breeds created')

    def _seed_dogs(self):
        labrador = Breed.objects.get(slug='labrador-retriever')
        meticcio = Breed.objects.get(slug='meticcio')
        pastore = Breed.objects.get(slug='pastore-tedesco')

        dogs_data = [
            {
                'name': 'Rex',
                'breed': labrador,
                'gender': 'M',
                'size': 'L',
                'age_years': 3,
                'age_months': 0,
                'description': 'Rex è un labrador dolcissimo, adora i bambini.',
                'status': 'available',
                'is_published': True,
                'good_with_children': True,
                'good_with_dogs': True,
                'arrival_date': datetime.date(2024, 3, 1),
            },
            {
                'name': 'Luna',
                'breed': meticcio,
                'gender': 'F',
                'size': 'M',
                'age_years': 2,
                'age_months': 6,
                'description': 'Luna è una meticcia affettuosa e vivace.',
                'status': 'adopted',
                'is_published': True,
                'good_with_children': True,
                'good_with_dogs': False,
                'arrival_date': datetime.date(2023, 11, 15),
                'adoption_date': datetime.date(2024, 2, 10),
            },
            {
                'name': 'Thor',
                'breed': pastore,
                'gender': 'M',
                'size': 'L',
                'age_years': 5,
                'age_months': 0,
                'description': 'Thor è in cura veterinaria, ha bisogno di cure speciali.',
                'status': 'medical',
                'is_published': True,
                'special_needs': 'Terapia antibiotica settimanale.',
                'arrival_date': datetime.date(2024, 1, 20),
            },
        ]

        for data in dogs_data:
            Dog.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
        self.stdout.write('  ✓ Dogs created')

    def _seed_faqs(self):
        cat, _ = FAQCategory.objects.get_or_create(
            slug='adozione',
            defaults={'name': 'Adozione', 'order': 1}
        )
        faqs = [
            ('Come si adotta un cane?',
             'Contattaci per prenotare una visita. Ti abbineremo al cane più adatto.'),
            ('Quali documenti servono?',
             'Documento di identità e residenza. Per i minori serve la firma di un genitore.'),
        ]
        for question, answer in faqs:
            FAQ.objects.get_or_create(
                question=question,
                defaults={'category': cat, 'answer': answer, 'is_published': True}
            )
        self.stdout.write('  ✓ FAQ created')

    def _seed_contacts(self):
        ContactMessage.objects.get_or_create(
            email='test@example.com',
            defaults={
                'name': 'Mario Rossi (test)',
                'subject': 'adoption',
                'message': 'Sono interessato ad adottare Rex. Potrei venire sabato mattina?',
                'ip_address': '127.0.0.1',
            }
        )
        self.stdout.write('  ✓ Contact message created')

    def _seed_admin_user(self):
        User = get_user_model()
        if not User.objects.filter(username='admin_test').exists():
            User.objects.create_superuser(
                username='admin_test',
                email='admin_test@example.com',
                password='Admin1234!'
            )
            self.stdout.write('  ✓ Superuser admin_test created (password: Admin1234!)')
        else:
            self.stdout.write('  ⚡ Superuser admin_test already exists')
