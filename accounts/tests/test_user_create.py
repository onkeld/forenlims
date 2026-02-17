# accounts/tests/test_user_create.py
import pytest
from django.contrib.auth.models import Permission
from django.core import mail
from django.urls import reverse

from accounts.models import CustomUser
from accounts.tests.factories import CustomUserFactory, SuperUserFactory


def user_create_url() -> str:
    return reverse('accounts:admin_user_create')


@pytest.mark.django_db
class TestUserCreateAccess:
    def test_anonymous_user_is_redirected_to_login(self, client) -> None:
        response = client.get(user_create_url())
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']

    def test_authenticated_user_without_permission_gets_403(
        self, client
    ) -> None:
        user = CustomUserFactory()
        client.force_login(user)
        response = client.get(user_create_url())
        assert response.status_code == 403

    def test_user_with_permission_can_access_create_form(self, client) -> None:
        user = CustomUserFactory()
        perm = Permission.objects.get(codename='add_customuser')
        user.user_permissions.add(perm)
        client.force_login(user)
        response = client.get(user_create_url())
        assert response.status_code == 200

    def test_superuser_can_access_create_form(self, client) -> None:
        user = SuperUserFactory()
        client.force_login(user)
        response = client.get(user_create_url())
        assert response.status_code == 200


@pytest.mark.django_db
class TestUserCreateForm:
    def test_valid_data_creates_user(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        client.post(
            user_create_url(),
            {
                'email': 'newuser@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        assert CustomUser.objects.filter(email='newuser@example.com').exists()

    def test_created_user_has_unusable_password(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        client.post(
            user_create_url(),
            {
                'email': 'newuser@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        user = CustomUser.objects.get(email='newuser@example.com')
        assert not user.has_usable_password()

    def test_duplicate_email_shows_form_error(self, client) -> None:
        admin = SuperUserFactory()
        CustomUserFactory(email='existing@example.com')
        client.force_login(admin)
        response = client.post(
            user_create_url(),
            {
                'email': 'existing@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        assert response.status_code == 200
        assert response.context['form'].errors

    def test_missing_email_shows_form_error(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        response = client.post(
            user_create_url(),
            {
                'email': '',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        assert response.status_code == 200
        assert response.context['form'].errors


@pytest.mark.django_db
class TestUserCreateInvitation:
    def test_invitation_mail_is_sent_after_creation(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        client.post(
            user_create_url(),
            {
                'email': 'newuser@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        assert len(mail.outbox) == 1

    def test_invitation_mail_goes_to_new_user(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        client.post(
            user_create_url(),
            {
                'email': 'newuser@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        assert mail.outbox[0].to == ['newuser@example.com']


@pytest.mark.django_db
class TestUserCreateRedirect:
    def test_successful_create_redirects_to_user_list(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        response = client.post(
            user_create_url(),
            {
                'email': 'newuser@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        assert response.status_code == 302
        assert response['Location'] == reverse('accounts:admin_user_list')
