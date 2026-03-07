# accounts/urls.py
from django.urls import path

from accounts.views import (
    UserProfileView,
)

app_name = 'accounts'

urlpatterns = [
    # User-facing
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
]
