# accounts/urls.py
from django.urls import path

from accounts.views import (
    AdminUserCreateView,
    AdminUserEditView,
    AdminUserListView,
)

app_name = 'accounts'

urlpatterns = [
    path('', AdminUserListView.as_view(), name='admin_user_list'),
    path('create/', AdminUserCreateView.as_view(), name='admin_user_create'),
    path('edit/<int:pk>/',
         AdminUserEditView.as_view(),
         name='admin_user_edit'),
]
