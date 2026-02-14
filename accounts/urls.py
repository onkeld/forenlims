# accounts/urls.py
from django.urls import path

from accounts.views import UserListView

app_name = 'accounts'

urlpatterns = [
    path('', UserListView.as_view(), name='admin_user_list'),
]
