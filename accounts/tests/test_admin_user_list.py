# accounts/tests/test_admin_user_list.py
import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from accounts.tests.factories import CustomUserFactory, SuperUserFactory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def user_list_url() -> str:
    return reverse('accounts:admin_user_list')


# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------


class TestUserListAccess:
    """
    Only users with accounts.view_customuser permission may access the list.
    """

    def test_anonymous_user_is_redirected_to_login(self, client) -> None:
        response = client.get(user_list_url())
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']

    @pytest.mark.django_db
    def test_authenticated_user_without_permission_gets_403(
        self, client
    ) -> None:
        user = CustomUserFactory()
        client.force_login(user)
        response = client.get(user_list_url())
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_superuser_can_access_user_list(self, client) -> None:
        user = SuperUserFactory()
        client.force_login(user)
        response = client.get(user_list_url())
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_user_with_view_permission_can_access_list(self, client) -> None:
        user = CustomUserFactory()

        perm = Permission.objects.get(codename='view_customuser')
        user.user_permissions.add(perm)
        client.force_login(user)
        response = client.get(user_list_url())
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------


class TestUserListContent:
    """The list must show the correct users with the correct fields."""

    @pytest.mark.django_db
    def test_list_shows_all_users(self, client) -> None:
        admin = SuperUserFactory()
        CustomUserFactory.create_batch(3)
        client.force_login(admin)
        response = client.get(user_list_url())
        # 4 users total: admin + 3 created
        assert len(response.context['users']) == 4

    @pytest.mark.django_db
    def test_list_shows_user_email(self, client) -> None:
        admin = SuperUserFactory()
        user = CustomUserFactory(email='test@example.com')
        client.force_login(admin)
        response = client.get(user_list_url())
        assert user.email.encode() in response.content

    @pytest.mark.django_db
    def test_list_shows_first_and_last_name(self, client) -> None:
        admin = SuperUserFactory()
        CustomUserFactory(first_name='Jane', last_name='Doe')
        client.force_login(admin)
        response = client.get(user_list_url())
        assert b'Jane' in response.content
        assert b'Doe' in response.content

    @pytest.mark.django_db
    def test_list_shows_active_status(self, client) -> None:
        admin = SuperUserFactory()
        CustomUserFactory(is_active=False)
        client.force_login(admin)
        response = client.get(user_list_url())
        assert response.status_code == 200
        # Active status is present in context
        users = response.context['users']
        inactive = [u for u in users if not u.is_active]
        assert len(inactive) == 1

    @pytest.mark.django_db
    def test_list_shows_staff_status(self, client) -> None:
        admin = SuperUserFactory()
        CustomUserFactory(is_staff=True)
        client.force_login(admin)
        response = client.get(user_list_url())
        users = response.context['users']
        staff = [u for u in users if u.is_staff]
        # admin + 1 staff user
        assert len(staff) == 2

    @pytest.mark.django_db
    def test_empty_list_returns_200(self, client) -> None:
        """Edge case: only the admin themselves, no other users."""
        admin = SuperUserFactory()
        client.force_login(admin)
        response = client.get(user_list_url())
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_correct_template_is_used(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        response = client.get(user_list_url())
        assert 'accounts/admin/user_list.html' in [
            t.name for t in response.templates
        ]
