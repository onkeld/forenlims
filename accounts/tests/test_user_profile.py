# accounts/tests/test_user_profile.py
import pytest

#from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

#from django.core import mail
from django.urls import reverse

from accounts.tests.factories import CustomUserFactory

User = get_user_model()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def user_profile_url(user) -> str:
    return reverse('accounts:user_profile', kwargs={'pk': user.pk})

def user_edit_url(user) -> str:
    return reverse('accounts:user_edit', kwargs={'pk': user.pk})

# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------

class TestUserProfileDetailAccess():
    pytestmark = pytest.mark.django_db
    """
    Only logged in users should be able to access the user profile page.

    """


    def test_anonymous_user_is_redirected_to_login(self, client) -> None:
        user = CustomUserFactory()
        response = client.get(user_profile_url(user))
        assert response.status_code == 302

    def test_logged_in_user_can_access(self, client) -> None:
        user = CustomUserFactory()
        client.force_login(user)
        response = client.get(user_profile_url(user))
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# User Profile Detail Access
# ---------------------------------------------------------------------------
class TestUserProfileView:
    pytestmark = pytest.mark.django_db

    def test_user_can_view_other_users_profile(self, client) -> None:
        user1 = CustomUserFactory()
        user2 = CustomUserFactory()
        client.force_login(user1)
        response = client.get(user_profile_url(user2))
        assert response.status_code == 200

    def test_owner_can_edit_own_profile(self, client) -> None:
        user = CustomUserFactory()
        client.force_login(user)
        response = client.post(
            user_edit_url(user),
            data={
                'first_name': 'New',
                'last_name': 'Name',
            }
        )
        if response.status_code == 200:
            print(response.context['form'].errors)
        assert response.status_code == 302

    def test_other_user_cannot_edit_profile(self, client) -> None:
        user1 = CustomUserFactory()
        user2 = CustomUserFactory()
        client.force_login(user1)
        response = client.post(
            user_edit_url(user2),
            data={
                'first_name': 'New',
                'last_name': 'Name',
            }
        )
        assert response.status_code == 403

    def test_form_is_prefilled_with_current_data(self, client) -> None:
        user = CustomUserFactory()
        client.force_login(user)
        response = client.get(user_edit_url(user))
        assert response.status_code == 200
        assert response.context['form'].initial[
            'first_name'
            ] == user.first_name
