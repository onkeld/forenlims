# /accounts/tests/test_adapters.py

import pytest
from django.urls import reverse

from accounts.models import CustomUser


@pytest.mark.django_db
class TestNoSignupAdapter:
    def test_signup_page_is_disabled(self, client) -> None:
        response = client.get(reverse('account_signup'))
        assert response.status_code == 200
        assert 'form' not in response.context

    def test_signup_post_is_rejected(self, client) -> None:
        client.post(
            reverse('account_signup'),
            {
                'email': 'new@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123',
            },
        )

        assert not CustomUser.objects.filter(email='new@example.com').exists()
