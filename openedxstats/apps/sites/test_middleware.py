from django.apps import apps as proj_apps
from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

PASSWORD = '1234'


class TestAdminView(TestCase):
    """
    Tests of the admin view to verify the middleware functionality.
    """
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_admin_view_with_anonymous_user(self):
        resp = self.client.get(reverse('admin:index'))
        self.assertRedirects(
            resp, settings.LOGIN_URL, target_status_code=200
        )

    def test_admin_view_loads_for_is_superuser(self):
        user = User.objects.create_user(
            'user2', 'test@example.com', PASSWORD,
            is_superuser=True,
            is_staff=True
        )
        self.client.login(username=user.username, password=PASSWORD)
        response = self.client.get(reverse('admin:index'))
        assert response.status_code == 200
        response = self.client.get(reverse('logout'))
        assert response.status_code == 200

    def test_app_configs(self):
        """Verifying apps are loading with django3.2 condition."""
        assert proj_apps.get_app_config('sites').label == 'sites'
        assert proj_apps.get_app_config('slackdata').label == 'slackdata'
