# accounts/tests/test_admin_user_list.py
import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from accounts.tests.factories import CustomUserFactory, SuperUserFactory
from accounts.tests.mixins import AccessControlMixin

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def admin_user_list_url() -> str:
    return reverse('accounts:admin_user_list')

def admin_user_create_url() -> str:
    return reverse('accounts:admin_user_create')

#class TestAdminUserEditAccess(AccessControlMixin):
#    # Edit-URL needs a database object, so we set it up in a fixture
#    @pytest.fixture(autouse=True)
#    def setup_edit_user(self) -> None:
#        self.edit_user = CustomUserFactory()
#        self.url_for_anonymous = admin_user_edit_url(self.edit_user)
#        self.url_for_authenticated = admin_user_edit_url(self.edit_user)
#        self.url_for_permitted = admin_user_edit_url(self.edit_user)
#
#    required_permission = 'change_customuser'

# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------

class TestUserListAccess(AccessControlMixin):
    """
    Only users with accounts.view_customuser permission may access the list.
    """
    url_for_anonymous = admin_user_list_url()
    url_for_authenticated = admin_user_list_url()
    url_for_permitted = admin_user_list_url()
    required_permission = 'view_customuser'

class TestAdminUserCreateAccess(AccessControlMixin):
    """
    Only users with accounts.create_customuser permission may access the admin_
    user_create form.
    """
    url_for_anonymous = admin_user_create_url()
    url_for_authenticated = admin_user_create_url()
    url_for_permitted = admin_user_create_url()
    required_permission = 'create_customuser'

#class TestAdminUserEditAccess(AccessControlMixin):
#    """
#    Only users with accounts.edit_customuser permission may access the
#    edit form.
#    """
#    url_for_anonymous = admin_user_edit_url()
#    url_for_authenticated = admin_user_edit_url()
#    url_for_permitted = admin_user_edit_url()
#    required_permission = 'edit_customuser'

# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Admin User List
# ---------------------------------------------------------------------------


class TestUserListContent:
    pytestmark = pytest.mark.django_db
    """The list must show the correct users with the correct fields."""

    def test_list_shows_all_users(self, client) -> None:
        admin = SuperUserFactory()
        CustomUserFactory.create_batch(3)
        client.force_login(admin)
        response = client.get(admin_user_list_url())
        # 4 users total: admin + 3 created
        assert len(response.context['users']) == 4

    def test_list_shows_user_email(self, client) -> None:
        admin = SuperUserFactory()
        user = CustomUserFactory(email='test@example.com')
        client.force_login(admin)
        response = client.get(admin_user_list_url())
        assert user.email.encode() in response.content

    def test_list_shows_first_and_last_name(self, client) -> None:
        admin = SuperUserFactory()
        CustomUserFactory(first_name='Jane', last_name='Doe')
        client.force_login(admin)
        response = client.get(admin_user_list_url())
        assert b'Jane' in response.content
        assert b'Doe' in response.content

    def test_list_shows_active_status(self, client) -> None:
        admin = SuperUserFactory()
        CustomUserFactory(is_active=False)
        client.force_login(admin)
        response = client.get(admin_user_list_url())
        assert response.status_code == 200
        # Active status is present in context
        users = response.context['users']
        inactive = [u for u in users if not u.is_active]
        assert len(inactive) == 1

    def test_list_shows_staff_status(self, client) -> None:
        admin = SuperUserFactory()
        CustomUserFactory(is_staff=True)
        client.force_login(admin)
        response = client.get(admin_user_list_url())
        users = response.context['users']
        staff = [u for u in users if u.is_staff]
        # admin + 1 staff user
        assert len(staff) == 2

    def test_empty_list_returns_200(self, client) -> None:
        """Edge case: only the admin themselves, no other users."""
        admin = SuperUserFactory()
        client.force_login(admin)
        response = client.get(admin_user_list_url())
        assert response.status_code == 200

    def test_correct_template_is_used(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        response = client.get(admin_user_list_url())
        assert 'accounts/admin/user_list.html' in [
            t.name for t in response.templates
        ]
# ---------------------------------------------------------------------------
# Admin User Create
# ---------------------------------------------------------------------------

class TestUserCreateForm:
    pytestmark = pytest.mark.django_db

    def test_valid_data_creates_user(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        client.post(
            admin_user_create_url(),
            {
                'email': 'newuser@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_created_user_has_unusable_password(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        client.post(
            admin_user_create_url(),
            {
                'email': 'newuser@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        user = User.objects.get(email='newuser@example.com')
        assert not user.has_usable_password()

    def test_duplicate_email_shows_form_error(self, client) -> None:
        admin = SuperUserFactory()
        CustomUserFactory(email='existing@example.com')
        client.force_login(admin)
        response = client.post(
            admin_user_create_url(),
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
            admin_user_create_url(),
            {
                'email': '',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        assert response.status_code == 200
        assert response.context['form'].errors


class TestUserCreatePasswordEmail:
    pytestmark = pytest.mark.django_db

    def test_invitation_mail_is_sent_after_creation(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        client.post(
            admin_user_create_url(),
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
            admin_user_create_url(),
            {
                'email': 'newuser@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        assert mail.outbox[0].to == ['newuser@example.com']


class TestUserCreateRedirect:
    pytestmark = pytest.mark.django_db
    def test_successful_create_redirects_to_user_list(self, client) -> None:
        admin = SuperUserFactory()
        client.force_login(admin)
        response = client.post(
            admin_user_create_url(),
            {
                'email': 'newuser@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
            },
        )
        assert response.status_code == 302
        assert response['Location'] == reverse('accounts:admin_user_list')
