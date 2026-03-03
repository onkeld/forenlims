# accounts/views.py
from allauth.account.forms import ResetPasswordForm
from allauth.account.models import EmailAddress
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from accounts.forms import UserCreateForm
from accounts.models import CustomUser


class AdminUserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """List all users. Requires accounts.view_customuser permission."""

    model = CustomUser
    template_name = 'accounts/admin/user_list.html'
    context_object_name = 'users'
    permission_required = 'accounts.view_customuser'
    ordering = ('email',)


class AdminUserCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Create a new user. Requires accounts.create_customuser permission."""

    permission_required = 'accounts.create_customuser'
    template_name = 'accounts/admin/user_create.html'

    def get(
        self, request: HttpRequest, *args: object, **kwargs: object
    ) -> HttpResponse:
        form = UserCreateForm()
        return render(request, self.template_name, {'form': form})

    def post(
        self, request: HttpRequest, *args: object, **kwargs: object
    ) -> HttpResponse:
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(None)
            user.last_login = timezone.now()
            user.save()
            EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=True,
            )
            reset_form = ResetPasswordForm(data={'email': user.email})
            if reset_form.is_valid():
                reset_form.save(request)
            return redirect('accounts:admin_user_list')
        return render(request, self.template_name, {'form': form})
