# accounts/urls.py
from django.urls import path

from accounts.views import (
    UserEditView,
    UserProfileView,
)

app_name = 'accounts'

urlpatterns = [
    # User-facing
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
    path('profile/<int:pk>/edit/', UserEditView.as_view(), name='user_edit'),
]
