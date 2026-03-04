# accounts/tests/mixins.py
import pytest
from django.contrib.auth.models import Permission

from accounts.tests.factories import CustomUserFactory, SuperUserFactory


class ViewAccessTestMixin:
    """
    Reusable Access Control Tests.

    Subclasses have to define:
        url_for_anonymous: str         — URL for the anonymous user test
        url_for_authenticated: str     — URL for the authenticated user without
                                         permission test (can be same as
                                         url_for_anonymous)
        required_permission: str       — codename only (e.g. 'view_customuser')
                                         the View must use the full
                                         'app_label.codename'
                                         format (e.g.
                                         'accounts.view_customuser')
        url_for_permitted: str         — URL for the permitted user/superuser
                                         test
    """

    http_method: str = 'get'  # default
    expected_status_code: int = 200 #default


    pytestmark = pytest.mark.django_db
    url_for_anonymous: str
    url_for_authenticated: str
    required_permission: str
    url_for_permitted: str

    def test_anonymous_user_is_redirected_to_login(self, client) -> None:
        response = client.get(self.url_for_anonymous)
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']

    def test_authenticated_user_without_permission_gets_403(
            self, client
            ) -> None:
        user = CustomUserFactory()
        client.force_login(user)
        response = client.get(self.url_for_authenticated)
        assert response.status_code == 403

    def test_user_with_permission_can_access(self, client) -> None:
        user = CustomUserFactory()
        perm = Permission.objects.get(codename=self.required_permission)
        user.user_permissions.add(perm)
        user = user.__class__.objects.get(pk=user.pk)
        client.force_login(user)
        response = getattr(client, self.http_method)(self.url_for_permitted)
        assert response.status_code == self.expected_status_code

    def test_superuser_can_access(self, client) -> None:
        user = SuperUserFactory()
        client.force_login(user)
        response = getattr(client, self.http_method)(self.url_for_permitted)
        assert response.status_code == self.expected_status_code
