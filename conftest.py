"""
Fixtures and factories shared across all project tests.
"""
# Must stay at the top: it overrides DJANGO_ENVIRONMENT before decouple reads
# the .env, so config/settings/__init__.py loads test.py and not production.py
import os
os.environ['DJANGO_ENVIRONMENT'] = 'test'

import datetime
import io

import factory
import pytest
from django.contrib.auth import get_user_model
from PIL import Image as PILImage

from apps.contacts.models import ContactMessage
from apps.dogs.models import Breed, Dog


# ─── Factories ────────────────────────────────────────────────────────────────

class BreedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Breed

    name = factory.Sequence(lambda n: f'Razza {n}')
    slug = factory.LazyAttribute(lambda o: o.name.lower().replace(' ', '-'))


class DogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dog

    name         = factory.Sequence(lambda n: f'Fido {n}')
    breed        = factory.SubFactory(BreedFactory)
    status       = 'available'
    gender       = 'M'
    size         = 'M'
    is_published = True
    description  = 'Cane da test molto simpatico e socievole.'
    arrival_date = factory.LazyFunction(datetime.date.today)


class ContactMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactMessage

    name       = 'Mario Rossi'
    email      = 'mario@example.com'
    subject    = 'adoption'
    message    = 'Vorrei adottare un cane, sono molto interessato alla vostra struttura.'
    ip_address = '127.0.0.1'


# ─── Image fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def fake_image_jpg():
    """Valid in-memory JPEG, < 5 MB."""
    buf = io.BytesIO()
    PILImage.new('RGB', (100, 100), color='red').save(buf, format='JPEG')
    buf.seek(0)
    buf.name = 'test.jpg'
    return buf


@pytest.fixture
def fake_image_large():
    """File with a .jpg extension but size > 5 MB."""
    buf = io.BytesIO(b'x' * (6 * 1024 * 1024))
    buf.name = 'big.jpg'
    return buf


@pytest.fixture
def fake_file_pdf():
    """PDF file — extension not allowed."""
    buf = io.BytesIO(b'%PDF-1.4 fake content')
    buf.name = 'malware.pdf'
    return buf


@pytest.fixture
def admin_user(db):
    """Superuser for the admin panel tests."""
    User = get_user_model()
    return User.objects.create_superuser(
        username='admin_test',
        email='admin_test@example.com',
        password='Admin1234!'
    )
