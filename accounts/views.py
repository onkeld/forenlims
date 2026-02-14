from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.views.generic import ListView

from accounts.models import CustomUser


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """List all users. Requires accounts.view_customuser permission."""

    model = CustomUser
    template_name = 'accounts/admin/user_list.html'
    context_object_name = 'users'
    permission_required = 'accounts.view_customuser'
    ordering = ('email',)
