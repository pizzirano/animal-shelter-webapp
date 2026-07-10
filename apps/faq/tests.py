"""
Tests for the faq app.
Coverage: FAQAdmin (category, question, publishing, ordering).
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.faq.models import FAQ, FAQCategory


class FAQAdminTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser(
            username='faq_admin', email='faq@test.com', password='Admin1234!'
        )
        self.client.force_login(self.admin)

    # ── List ───────────────────────────────────────────────────────────────────

    def test_admin_category_list_returns_200(self):
        response = self.client.get(reverse('admin:faq_faqcategory_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_admin_faq_list_returns_200(self):
        response = self.client.get(reverse('admin:faq_faq_changelist'))
        self.assertEqual(response.status_code, 200)

    # ── CRUD FAQCategory ───────────────────────────────────────────────────────

    def test_admin_category_create(self):
        count_before = FAQCategory.objects.count()
        self.client.post(reverse('admin:faq_faqcategory_add'), {
            'name': 'Adozione',
            'slug': '',
            'order': '0',
            '_save': 'Save',
        })
        self.assertEqual(FAQCategory.objects.count(), count_before + 1)
        self.assertTrue(FAQCategory.objects.filter(name='Adozione').exists())

    def test_admin_category_slug_auto_generated(self):
        self.client.post(reverse('admin:faq_faqcategory_add'), {
            'name': 'Come Adottare',
            'slug': '',
            'order': '1',
            '_save': 'Save',
        })
        cat = FAQCategory.objects.filter(name='Come Adottare').first()
        self.assertIsNotNone(cat)
        self.assertEqual(cat.slug, 'come-adottare')

    # ── CRUD FAQ ───────────────────────────────────────────────────────────────

    def test_admin_faq_create(self):
        cat = FAQCategory.objects.create(name='Test Cat')
        count_before = FAQ.objects.count()
        self.client.post(reverse('admin:faq_faq_add'), {
            'category': cat.pk,
            'question': 'Come si adotta un cane?',
            'answer': 'Si contatta il canile e si prenota una visita.',
            'is_published': 'on',
            'order': '0',
            '_save': 'Save',
        })
        self.assertEqual(FAQ.objects.count(), count_before + 1)

    def test_admin_faq_create_no_category(self):
        """A FAQ without a category (nullable) must be saved correctly."""
        count_before = FAQ.objects.count()
        self.client.post(reverse('admin:faq_faq_add'), {
            'category': '',
            'question': 'Domanda senza categoria?',
            'answer': 'Risposta di test completa.',
            'is_published': 'on',
            'order': '0',
            '_save': 'Save',
        })
        self.assertEqual(FAQ.objects.count(), count_before + 1)

    def test_admin_faq_publish_toggle(self):
        cat = FAQCategory.objects.create(name='Cat Pub')
        faq = FAQ.objects.create(
            category=cat,
            question='Domanda?',
            answer='Risposta.',
            is_published=False,
        )
        self.client.post(
            reverse('admin:faq_faq_change', args=[faq.pk]),
            {
                'category': cat.pk,
                'question': faq.question,
                'answer': faq.answer,
                'is_published': 'on',
                'order': '0',
                '_save': 'Save',
            }
        )
        faq.refresh_from_db()
        self.assertTrue(faq.is_published)

    def test_admin_faq_ordering(self):
        """FAQ are ordered by the order field."""
        cat = FAQCategory.objects.create(name='Cat Ord')
        FAQ.objects.create(category=cat, question='Q1', answer='A1', order=2)
        FAQ.objects.create(category=cat, question='Q2', answer='A2', order=1)
        faqs = list(FAQ.objects.filter(category=cat))
        self.assertEqual(faqs[0].order, 1)
        self.assertEqual(faqs[1].order, 2)

    def test_admin_faq_delete(self):
        cat = FAQCategory.objects.create(name='Cat Del')
        faq = FAQ.objects.create(category=cat, question='Da eliminare?', answer='Sì.')
        pk = faq.pk
        self.client.post(
            reverse('admin:faq_faq_delete', args=[pk]),
            {'post': 'yes'}
        )
        self.assertFalse(FAQ.objects.filter(pk=pk).exists())
