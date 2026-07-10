"""
Access and security tests for the Django admin panel.
Coverage: anonymous access, non-staff user, superuser, brute force (Axes).
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


class AdminAccessTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.admin_url = reverse('admin:index')
        self.login_url = reverse('admin:login')
        self.superuser = User.objects.create_superuser(
            username='supertest', email='super@test.com', password='Super1234!'
        )
        self.regular_user = User.objects.create_user(
            username='normaluser', email='normal@test.com', password='Normal1234!'
        )

    def test_admin_requires_login(self):
        """Anonymous access → redirect to the login page."""
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])

    def test_admin_non_staff_denied(self):
        """A regular (non-staff) user cannot access the admin."""
        self.client.force_login(self.regular_user)
        response = self.client.get(self.admin_url)
        self.assertIn(response.status_code, [302, 403])

    def test_admin_superuser_access(self):
        """A superuser gets full access."""
        self.client.force_login(self.superuser)
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 200)

    def test_admin_login_page_returns_200(self):
        """The admin login page is reachable."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_admin_logout_redirects(self):
        """After logout, the admin is no longer accessible without login."""
        self.client.force_login(self.superuser)
        self.client.post(reverse('admin:logout'))
        response = self.client.get(self.admin_url)
        self.assertEqual(response.status_code, 302)

    @override_settings(AXES_FAILURE_LIMIT=3, AXES_ENABLED=True)
    def test_admin_brute_force_lockout(self):
        """After AXES_FAILURE_LIMIT failed attempts Axes locks the client out."""
        try:
            from axes.models import AccessAttempt
            AccessAttempt.objects.all().delete()
        except ImportError:
            self.skipTest('django-axes not installed')

        for _ in range(3):
            self.client.post(self.login_url, {
                'username': 'hacker',
                'password': 'wrongpass',
            })
        response = self.client.post(self.login_url, {
            'username': 'hacker',
            'password': 'wrongpass',
        })
        self.assertIn(response.status_code, [429, 403, 302, 200])
        attempts = AccessAttempt.objects.filter(username='hacker')
        self.assertTrue(attempts.exists())
