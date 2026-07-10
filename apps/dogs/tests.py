"""
Security and integrity tests for the dogs app.
Coverage: validate_dog_image, slug generation, model validators,
is_available, DogListView (XSS/injection/filters), DogDetailView,
DogAdmin (CRUD, image upload, filters, search).
"""
import datetime
import io
from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image as PILImage

from apps.dogs.models import Breed, Dog
from apps.dogs.validators import validate_dog_image

from conftest import BreedFactory, DogFactory


# ─── Image mock helper ────────────────────────────────────────────────────────

def _mock_image(name, size_bytes):
    """Minimal mock with the .name and .size attributes used by the validator."""
    img = MagicMock()
    img.name = name
    img.size = size_bytes
    return img


# ═══════════════════════════════════════════════════════════════════════════════
# 1. validate_dog_image — extensions
# ═══════════════════════════════════════════════════════════════════════════════

class ValidateDogImageExtensionTest(TestCase):

    def test_jpg_allowed(self):
        validate_dog_image(_mock_image('foto.jpg', 100))

    def test_jpeg_allowed(self):
        validate_dog_image(_mock_image('foto.jpeg', 100))

    def test_png_allowed(self):
        validate_dog_image(_mock_image('foto.png', 100))

    def test_webp_allowed(self):
        validate_dog_image(_mock_image('foto.webp', 100))

    def test_pdf_blocked(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_dog_image(_mock_image('doc.pdf', 100))
        self.assertIn('Formato non supportato', str(ctx.exception))

    def test_exe_blocked(self):
        with self.assertRaises(ValidationError):
            validate_dog_image(_mock_image('virus.exe', 100))

    def test_gif_blocked(self):
        with self.assertRaises(ValidationError):
            validate_dog_image(_mock_image('anim.gif', 100))

    def test_php_blocked(self):
        with self.assertRaises(ValidationError):
            validate_dog_image(_mock_image('shell.php', 100))

    def test_no_extension_blocked(self):
        with self.assertRaises(ValidationError):
            validate_dog_image(_mock_image('noextension', 100))

    def test_extension_uppercase_jpg_allowed(self):
        """The validator uses .lower() — uppercase must pass."""
        validate_dog_image(_mock_image('FOTO.JPG', 100))

    def test_extension_uppercase_png_allowed(self):
        validate_dog_image(_mock_image('FOTO.PNG', 100))

    def test_double_extension_blocked(self):
        """Double-extension file like shell.php.jpg: takes .jpg → accepted."""
        validate_dog_image(_mock_image('shell.php.jpg', 100))


# ═══════════════════════════════════════════════════════════════════════════════
# 2. validate_dog_image — file size
# ═══════════════════════════════════════════════════════════════════════════════

class ValidateDogImageSizeTest(TestCase):

    MAX = 5 * 1024 * 1024  # 5 MB in bytes

    def test_small_file_allowed(self):
        validate_dog_image(_mock_image('small.jpg', 1024))

    def test_file_under_5mb_allowed(self):
        validate_dog_image(_mock_image('ok.jpg', self.MAX - 1))

    def test_file_exactly_5mb_allowed(self):
        """Boundary: the validator uses >, not >=."""
        validate_dog_image(_mock_image('exact.jpg', self.MAX))

    def test_file_over_5mb_blocked(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_dog_image(_mock_image('big.jpg', self.MAX + 1))
        self.assertIn('troppo grande', str(ctx.exception))

    def test_file_6mb_blocked(self):
        with self.assertRaises(ValidationError):
            validate_dog_image(_mock_image('huge.jpg', 6 * 1024 * 1024))


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Slug generation
# ═══════════════════════════════════════════════════════════════════════════════

class SlugGenerationTest(TestCase):

    def test_slug_generated_on_first_save(self):
        dog = DogFactory(name='Fido')
        self.assertEqual(dog.slug, 'fido')

    def test_slug_unique_on_collision(self):
        dog1 = DogFactory(name='Rex')
        dog2 = DogFactory(name='Rex')
        self.assertNotEqual(dog1.slug, dog2.slug)
        self.assertTrue(dog2.slug.startswith('rex'))

    def test_slug_not_overwritten_on_resave(self):
        dog = DogFactory(name='Rex')
        original_slug = dog.slug
        dog.description = 'Descrizione aggiornata.'
        dog.save()
        dog.refresh_from_db()
        self.assertEqual(dog.slug, original_slug)

    def test_slug_from_special_chars(self):
        """Special and accented characters are normalized."""
        dog = DogFactory(name='Bübu & Micio!')
        self.assertRegex(dog.slug, r'^[a-z0-9\-]+$')

    def test_slug_multiple_collisions(self):
        """With three dogs of the same name, all slugs are unique."""
        dogs = [DogFactory(name='Luna') for _ in range(3)]
        slugs = [d.slug for d in dogs]
        self.assertEqual(len(slugs), len(set(slugs)))


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Model validators (age, size, status)
# ═══════════════════════════════════════════════════════════════════════════════

class DogModelValidatorsTest(TestCase):

    def _dog_with(self, **kwargs):
        dog = DogFactory.build(**kwargs)
        return dog

    def test_age_years_max_25(self):
        dog = self._dog_with(age_years=26)
        with self.assertRaises(ValidationError):
            dog.full_clean()

    def test_age_years_negative(self):
        dog = self._dog_with(age_years=-1)
        with self.assertRaises(ValidationError):
            dog.full_clean()

    def test_age_years_zero_valid(self):
        dog = self._dog_with(age_years=0)
        try:
            dog.full_clean()
        except ValidationError as e:
            self.assertNotIn('age_years', e.message_dict)

    def test_age_years_25_valid(self):
        dog = self._dog_with(age_years=25)
        try:
            dog.full_clean()
        except ValidationError as e:
            self.assertNotIn('age_years', e.message_dict)

    def test_age_months_max_11(self):
        dog = self._dog_with(age_months=12)
        with self.assertRaises(ValidationError):
            dog.full_clean()

    def test_age_months_negative(self):
        dog = self._dog_with(age_months=-1)
        with self.assertRaises(ValidationError):
            dog.full_clean()

    def test_age_months_11_valid(self):
        dog = self._dog_with(age_months=11)
        try:
            dog.full_clean()
        except ValidationError as e:
            self.assertNotIn('age_months', e.message_dict)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. is_available property
# ═══════════════════════════════════════════════════════════════════════════════

class DogIsAvailableTest(TestCase):

    def test_is_available_true(self):
        dog = DogFactory(status='available', is_published=True)
        self.assertTrue(dog.is_available)

    def test_is_available_false_when_adopted(self):
        dog = DogFactory(status='adopted', is_published=True)
        self.assertFalse(dog.is_available)

    def test_is_available_false_when_reserved(self):
        dog = DogFactory(status='reserved', is_published=True)
        self.assertFalse(dog.is_available)

    def test_is_available_false_when_unpublished(self):
        dog = DogFactory(status='available', is_published=False)
        self.assertFalse(dog.is_available)

    def test_is_available_false_when_both_false(self):
        dog = DogFactory(status='adopted', is_published=False)
        self.assertFalse(dog.is_available)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. DogListView — filters and input security
# ═══════════════════════════════════════════════════════════════════════════════

class DogListViewTest(TestCase):

    def setUp(self):
        self.published   = DogFactory(is_published=True,  status='available')
        self.unpublished = DogFactory(is_published=False, status='available')
        self.adopted     = DogFactory(is_published=True,  status='adopted')

    def test_list_returns_200(self):
        response = self.client.get(reverse('dogs:list'))
        self.assertEqual(response.status_code, 200)

    def test_list_shows_only_published(self):
        response = self.client.get(reverse('dogs:list'))
        dogs_in_context = list(response.context['dogs'])
        self.assertIn(self.published, dogs_in_context)
        self.assertNotIn(self.unpublished, dogs_in_context)

    def test_list_filter_by_status(self):
        response = self.client.get(reverse('dogs:list'), {'status': 'adopted'})
        dogs_in_context = list(response.context['dogs'])
        self.assertIn(self.adopted, dogs_in_context)
        self.assertNotIn(self.published, dogs_in_context)

    def test_list_xss_in_search_not_reflected_raw(self):
        """An XSS payload in the search parameter does not appear unescaped in the response."""
        payload = '<script>alert(1)</script>'
        response = self.client.get(reverse('dogs:list'), {'search': payload})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, payload)

    def test_list_sql_injection_no_crash(self):
        """SQL injection in the search parameter does not cause 500 errors."""
        response = self.client.get(reverse('dogs:list'),
                                   {'search': "'; DROP TABLE dogs_dog; --"})
        self.assertEqual(response.status_code, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. DogDetailView
# ═══════════════════════════════════════════════════════════════════════════════

class DogDetailViewTest(TestCase):

    def setUp(self):
        self.published   = DogFactory(is_published=True)
        self.unpublished = DogFactory(is_published=False)

    def test_detail_published_returns_200(self):
        response = self.client.get(
            reverse('dogs:detail', kwargs={'slug': self.published.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_detail_unpublished_returns_404(self):
        response = self.client.get(
            reverse('dogs:detail', kwargs={'slug': self.unpublished.slug})
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_wrong_slug_returns_404(self):
        response = self.client.get(
            reverse('dogs:detail', kwargs={'slug': 'slug-inesistente-xyz'})
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_increments_view_count(self):
        count_before = self.published.view_count
        self.client.get(
            reverse('dogs:detail', kwargs={'slug': self.published.slug})
        )
        self.published.refresh_from_db()
        self.assertEqual(self.published.view_count, count_before + 1)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. DogAdmin — CRUD, image upload, filters, search
# ═══════════════════════════════════════════════════════════════════════════════

def _make_jpeg(size=(10, 10)):
    """Valid in-memory 1×1 JPEG as a SimpleUploadedFile."""
    buf = io.BytesIO()
    PILImage.new('RGB', size, color='orange').save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile('foto.jpg', buf.read(), content_type='image/jpeg')


class DogAdminTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser(
            username='admin_test', email='admin@test.com', password='Admin1234!'
        )
        self.client.force_login(self.admin)
        self.breed = BreedFactory()

    def _base_dog_data(self, **overrides):
        data = {
            'name': 'Fido AdminTest',
            'slug': '',
            'microchip_number': '',
            'is_published': 'on',
            'breed': '',
            'is_mixed_breed': '',
            'gender': 'M',
            'size': 'M',
            'age_years': '2',
            'age_months': '0',
            'weight': '',
            'description': 'Cane di test per admin, molto socievole.',
            'special_needs': '',
            'good_with_children': '',
            'good_with_dogs': '',
            'good_with_cats': '',
            'status': 'available',
            'arrival_date': '2024-01-15',
            'adoption_date': '',
            # Inline DogImage management form
            'images-TOTAL_FORMS': '0',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '1000',
            '_save': 'Save',
        }
        data.update(overrides)
        return data

    # ── List access ────────────────────────────────────────────────────────────

    def test_admin_breed_list_returns_200(self):
        response = self.client.get(reverse('admin:dogs_breed_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_admin_dog_list_returns_200(self):
        DogFactory()
        response = self.client.get(reverse('admin:dogs_dog_changelist'))
        self.assertEqual(response.status_code, 200)

    # ── CRUD Breed ─────────────────────────────────────────────────────────────

    def test_admin_breed_create(self):
        count_before = Breed.objects.count()
        self.client.post(reverse('admin:dogs_breed_add'), {
            'name': 'Labrador',
            'slug': '',
            'description': '',
            '_save': 'Save',
        })
        self.assertEqual(Breed.objects.count(), count_before + 1)
        self.assertTrue(Breed.objects.filter(name='Labrador').exists())

    def test_admin_breed_slug_auto_generated(self):
        self.client.post(reverse('admin:dogs_breed_add'), {
            'name': 'Golden Retriever',
            'slug': '',
            'description': '',
            '_save': 'Save',
        })
        breed = Breed.objects.filter(name='Golden Retriever').first()
        self.assertIsNotNone(breed)
        self.assertEqual(breed.slug, 'golden-retriever')

    # ── CRUD Dog ───────────────────────────────────────────────────────────────

    def test_admin_dog_create_no_image(self):
        count_before = Dog.objects.count()
        response = self.client.post(
            reverse('admin:dogs_dog_add'), self._base_dog_data()
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Dog.objects.count(), count_before + 1)

    def test_admin_dog_slug_auto_generated(self):
        self.client.post(reverse('admin:dogs_dog_add'), self._base_dog_data(name='Pallino'))
        dog = Dog.objects.filter(name='Pallino').first()
        self.assertIsNotNone(dog)
        self.assertEqual(dog.slug, 'pallino')

    def test_admin_dog_create_with_valid_image(self):
        data = self._base_dog_data(name='Arancio', main_image=_make_jpeg())
        response = self.client.post(
            reverse('admin:dogs_dog_add'), data, format='multipart'
        )
        self.assertEqual(response.status_code, 302)
        dog = Dog.objects.filter(name='Arancio').first()
        self.assertIsNotNone(dog)
        self.assertTrue(bool(dog.main_image))

    def test_admin_dog_image_invalid_extension_rejected(self):
        gif_file = SimpleUploadedFile('anim.gif', b'GIF89a\x01\x00\x01\x00', content_type='image/gif')
        data = self._base_dog_data(name='GifDog', main_image=gif_file)
        response = self.client.post(
            reverse('admin:dogs_dog_add'), data, format='multipart'
        )
        # Form validation error → stays on the page (200), no redirect
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Dog.objects.filter(name='GifDog').exists())

    def test_admin_dog_image_too_large_rejected(self):
        big_file = SimpleUploadedFile(
            'big.jpg', b'J' * (6 * 1024 * 1024), content_type='image/jpeg'
        )
        data = self._base_dog_data(name='BigDog', main_image=big_file)
        response = self.client.post(
            reverse('admin:dogs_dog_add'), data, format='multipart'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Dog.objects.filter(name='BigDog').exists())

    def test_admin_dog_edit_status(self):
        dog = DogFactory(status='available')
        response = self.client.post(
            reverse('admin:dogs_dog_change', args=[dog.pk]),
            self._base_dog_data(name=dog.name, status='adopted')
        )
        self.assertEqual(response.status_code, 302)
        dog.refresh_from_db()
        self.assertEqual(dog.status, 'adopted')

    def test_admin_dog_delete(self):
        dog = DogFactory()
        pk = dog.pk
        self.client.post(
            reverse('admin:dogs_dog_delete', args=[pk]),
            {'post': 'yes'}
        )
        self.assertFalse(Dog.objects.filter(pk=pk).exists())

    # ── Filters and search ─────────────────────────────────────────────────────

    def test_admin_dog_filter_by_status(self):
        DogFactory(status='available', is_published=True)
        DogFactory(status='adopted', is_published=True)
        response = self.client.get(
            reverse('admin:dogs_dog_changelist'), {'status__exact': 'available'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'available')

    def test_admin_dog_search_by_name(self):
        DogFactory(name='Unico Nomespecialetest')
        response = self.client.get(
            reverse('admin:dogs_dog_changelist'), {'q': 'Unico Nomespecialetest'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unico Nomespecialetest')
