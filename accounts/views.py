# accounts/views.py
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, View

from accounts.forms import UserEditForm
from accounts.models import CustomUser


class UserProfileView(LoginRequiredMixin, DetailView):
    """Display User Profile Details. Requires Login."""

    model = CustomUser
    template_name = 'accounts/user_profile.html'
    context_object_name = 'user'

class UserEditView(LoginRequiredMixin, View):
    """Edit your own user profile."""

    template_name = 'accounts/user_edit.html'

    def get(
        self, request: HttpRequest, *args: object, **kwargs: object
    ) -> HttpResponse:
        user = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
        form = UserEditForm(instance=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request:HttpRequest, *args: object,
             **kwargs: object) ->HttpResponse:

        if request.user.pk != self.kwargs['pk']:
            return HttpResponseForbidden()

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
            return redirect('accounts:user_edit',
                            pk=user.pk)
        return render(request, self.template_name, {'form': form})
