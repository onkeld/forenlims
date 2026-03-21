# accounts/views.py
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.views.generic import DetailView

from accounts.models import CustomUser


class UserProfileView(LoginRequiredMixin, DetailView):
    """Display User Profile Details. Requires Login."""

    model = CustomUser
    template_name = 'accounts/user_profile.html'
    context_object_name = 'user'
