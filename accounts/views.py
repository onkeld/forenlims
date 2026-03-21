# accounts/views.py
from allauth.account.forms import ResetPasswordForm
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from accounts.forms import UserCreateForm, UserEditForm
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
            return redirect('admin_portal:accounts_admin:admin_user_list')
        return render(request, self.template_name, {'form': form})

class AdminUserEditView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Edit an existing user. Requires accounts.edit_customuser permission."""

    permission_required = 'accounts.edit_customuser'
    template_name = 'accounts/admin/user_edit.html'

    def get(
        self, request: HttpRequest, *args: object, **kwargs: object
    ) -> HttpResponse:
        user = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
        form = UserEditForm(instance=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request:HttpRequest, *args: object,
             **kwargs: object) ->HttpResponse:
        user = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
        old_email = user.email
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            new_email = user.email
            if old_email != new_email:
                EmailAddress.objects.filter(user=user, email=old_email).update(
                email=new_email
            )
            messages.success(request, 'User successfully updated.')
            return redirect('admin_portal:accounts_admin:admin_user_edit',
                            pk=user.pk)
        return render(request, self.template_name, {'form': form})

class AdminUserDeactivateView(LoginRequiredMixin,
                              PermissionRequiredMixin, View):
    """
    Toggle user active status. Requires accounts.edit_customuser permission.
    """

    permission_required = 'accounts.edit_customuser'

    def post(self, request: HttpRequest, *args: object,
             **kwargs: object) -> HttpResponse:
        user = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User successfully {status}.')
        return redirect('admin_portal:accounts_admin:admin_user_list')

class UserProfileView(LoginRequiredMixin, DetailView):
    """Display User Profile Details. Requires Login."""

    model = CustomUser
    template_name = 'accounts/user_profile.html'
    context_object_name = 'user'
